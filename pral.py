#!/usr/bin/env python3
"""
PRAL (Potential Renal Acid Load) checker.

Uses the five Remer & Manz "main multipliers" to estimate how acid- or
alkaline-forming a food is, in mEq. Positive = acid-forming, negative =
alkaline-forming. This is a dietary estimate, not a medical test.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Iterable

# Remer & Manz 1995 — the commonly rounded main multipliers.
# Protein and phosphorus push PRAL up (acid). Potassium, magnesium, and
# calcium pull it down (alkaline). Units: protein in grams; minerals in mg.
MULTIPLIERS: dict[str, float] = {
    "protein": 0.49,
    "phosphorus": 0.037,
    "potassium": -0.021,
    "magnesium": -0.026,
    "calcium": -0.013,
}

NUTRIENT_UNITS: dict[str, str] = {
    "protein": "g",
    "phosphorus": "mg",
    "potassium": "mg",
    "magnesium": "mg",
    "calcium": "mg",
}

NUTRIENT_LABELS: dict[str, str] = {
    "protein": "Protein",
    "phosphorus": "Phosphorus",
    "potassium": "Potassium",
    "magnesium": "Magnesium",
    "calcium": "Calcium",
}

# Typical values per 100 g (USDA-style). Default serving is a usual portion.
# id, name, category, default_grams, protein_g, P_mg, K_mg, Mg_mg, Ca_mg
_FOOD_ROWS: list[tuple] = [
    ("beef_cooked", "Beef, cooked", "Meat & fish", 100, 26.1, 199, 318, 21, 18),
    ("chicken_breast", "Chicken breast, cooked", "Meat & fish", 100, 31.0, 228, 256, 29, 15),
    ("pork_cooked", "Pork, cooked", "Meat & fish", 100, 27.3, 226, 362, 24, 19),
    ("turkey", "Turkey, cooked", "Meat & fish", 100, 29.0, 213, 249, 27, 14),
    ("salmon", "Salmon, cooked", "Meat & fish", 120, 22.1, 252, 384, 30, 15),
    ("tuna_canned", "Tuna, canned in water", "Meat & fish", 85, 23.6, 164, 237, 23, 11),
    ("cod", "Cod, cooked", "Meat & fish", 100, 22.8, 138, 244, 32, 14),
    ("cheddar", "Cheddar cheese", "Dairy & eggs", 30, 24.9, 512, 98, 28, 721),
    ("parmesan", "Parmesan cheese", "Dairy & eggs", 20, 35.8, 694, 92, 44, 1184),
    ("cottage", "Cottage cheese", "Dairy & eggs", 110, 11.1, 159, 104, 8, 83),
    ("milk_whole", "Whole milk", "Dairy & eggs", 244, 3.3, 84, 132, 10, 113),
    ("yogurt_plain", "Plain yogurt", "Dairy & eggs", 170, 3.5, 95, 155, 12, 121),
    ("egg", "Egg, whole", "Dairy & eggs", 50, 12.6, 198, 138, 12, 56),
    ("butter", "Butter", "Dairy & eggs", 14, 0.9, 24, 24, 2, 24),
    ("white_bread", "White bread", "Grains", 30, 8.9, 98, 115, 23, 151),
    ("wheat_bread", "Whole-wheat bread", "Grains", 30, 12.4, 180, 230, 75, 107),
    ("white_rice", "White rice, cooked", "Grains", 150, 2.7, 43, 35, 12, 10),
    ("brown_rice", "Brown rice, cooked", "Grains", 150, 2.6, 83, 86, 39, 10),
    ("oats", "Oats, dry", "Grains", 40, 13.2, 410, 362, 138, 52),
    ("pasta", "Pasta, cooked", "Grains", 140, 5.8, 58, 44, 18, 7),
    ("quinoa", "Quinoa, cooked", "Grains", 150, 4.4, 152, 172, 64, 17),
    ("potato", "Potato, baked", "Vegetables", 170, 2.5, 70, 535, 28, 15),
    ("sweet_potato", "Sweet potato, baked", "Vegetables", 130, 2.0, 54, 475, 27, 38),
    ("spinach", "Spinach, raw", "Vegetables", 30, 2.9, 49, 558, 79, 99),
    ("broccoli", "Broccoli, cooked", "Vegetables", 80, 2.4, 67, 293, 21, 40),
    ("carrot", "Carrot, raw", "Vegetables", 61, 0.9, 35, 320, 12, 33),
    ("tomato", "Tomato, raw", "Vegetables", 120, 0.9, 24, 237, 11, 10),
    ("cucumber", "Cucumber", "Vegetables", 100, 0.7, 24, 147, 13, 16),
    ("lettuce", "Romaine lettuce", "Vegetables", 50, 1.2, 30, 247, 14, 33),
    ("onion", "Onion, raw", "Vegetables", 70, 1.1, 29, 146, 10, 23),
    ("kale", "Kale, raw", "Vegetables", 30, 4.3, 92, 491, 47, 254),
    ("zucchini", "Zucchini, cooked", "Vegetables", 100, 1.1, 40, 264, 18, 18),
    ("bell_pepper", "Bell pepper, raw", "Vegetables", 80, 0.9, 20, 211, 12, 10),
    ("mushroom", "Mushrooms, cooked", "Vegetables", 70, 2.2, 86, 318, 9, 6),
    ("celery", "Celery, raw", "Vegetables", 40, 0.7, 24, 260, 11, 40),
    ("banana", "Banana", "Fruit", 118, 1.1, 22, 358, 27, 5),
    ("apple", "Apple", "Fruit", 182, 0.3, 11, 107, 5, 6),
    ("orange", "Orange", "Fruit", 131, 0.9, 14, 181, 10, 40),
    ("lemon", "Lemon", "Fruit", 60, 1.1, 16, 138, 8, 26),
    ("strawberry", "Strawberries", "Fruit", 152, 0.7, 24, 153, 13, 16),
    ("raisins", "Raisins", "Fruit", 40, 3.1, 101, 749, 32, 50),
    ("avocado", "Avocado", "Fruit", 50, 2.0, 52, 485, 29, 12),
    ("blueberries", "Blueberries", "Fruit", 148, 0.7, 12, 77, 6, 6),
    ("watermelon", "Watermelon", "Fruit", 152, 0.6, 11, 112, 10, 7),
    ("grapes", "Grapes", "Fruit", 151, 0.7, 20, 191, 7, 10),
    ("almonds", "Almonds", "Nuts & seeds", 28, 21.2, 481, 733, 270, 269),
    ("walnuts", "Walnuts", "Nuts & seeds", 28, 15.2, 346, 441, 158, 98),
    ("peanuts", "Peanuts", "Nuts & seeds", 28, 25.8, 376, 705, 168, 92),
    ("pumpkin_seeds", "Pumpkin seeds", "Nuts & seeds", 28, 30.2, 1233, 809, 592, 46),
    ("lentils", "Lentils, cooked", "Legumes", 100, 9.0, 180, 369, 36, 19),
    ("chickpeas", "Chickpeas, cooked", "Legumes", 100, 8.9, 168, 291, 48, 49),
    ("black_beans", "Black beans, cooked", "Legumes", 100, 8.9, 140, 355, 70, 27),
    ("tofu", "Tofu, firm", "Legumes", 80, 8.1, 97, 121, 30, 350),
    ("soy_milk", "Soy milk", "Legumes", 240, 2.9, 52, 118, 18, 25),
    ("coffee", "Coffee, black", "Drinks", 240, 0.1, 7, 49, 3, 2),
    ("tea", "Tea, black", "Drinks", 240, 0.0, 1, 37, 3, 0),
    ("cola", "Cola", "Drinks", 355, 0.0, 11, 2, 1, 2),
    ("beer", "Beer", "Drinks", 356, 0.5, 14, 27, 6, 4),
    ("red_wine", "Red wine", "Drinks", 147, 0.1, 23, 127, 12, 8),
    ("olive_oil", "Olive oil", "Extras", 14, 0.0, 0, 1, 0, 1),
    ("honey", "Honey", "Extras", 21, 0.3, 4, 52, 2, 6),
    ("white_sugar", "White sugar", "Extras", 12, 0.0, 0, 2, 0, 1),
]


def _food_from_row(row: tuple) -> dict[str, Any]:
    fid, name, category, default_grams, protein, phosphorus, potassium, magnesium, calcium = row
    per_100 = {
        "protein": float(protein),
        "phosphorus": float(phosphorus),
        "potassium": float(potassium),
        "magnesium": float(magnesium),
        "calcium": float(calcium),
    }
    per_100_result = calculate_pral(per_100, grams=100)
    return {
        "id": fid,
        "name": name,
        "category": category,
        "default_grams": int(default_grams),
        "per_100": per_100,
        "pral_per_100": per_100_result["pral"],
        "label_per_100": per_100_result["label"],
        "search": f"{fid} {name} {category}".lower(),
    }


def calculate_pral(nutrients: dict[str, float], grams: float = 100.0) -> dict[str, Any]:
    """Return PRAL in mEq for the given nutrients (values are per 100 g)."""
    if grams < 0:
        raise ValueError("grams must be 0 or greater")
    scale = grams / 100.0
    contributions: dict[str, float] = {}
    scaled: dict[str, float] = {}
    for key, multiplier in MULTIPLIERS.items():
        amount = float(nutrients.get(key) or 0)
        if amount < 0:
            raise ValueError(f"{key} must be 0 or greater")
        scaled[key] = round(amount * scale, 3)
        contributions[key] = multiplier * amount * scale
    total = sum(contributions.values())
    return {
        "pral": round(total, 2),
        "grams": grams,
        "label": classify(total),
        "contributions": {k: round(v, 2) for k, v in contributions.items()},
        "nutrients": scaled,
        "nutrients_per_100": {k: float(nutrients.get(k) or 0) for k in MULTIPLIERS},
        "multipliers": dict(MULTIPLIERS),
    }


def classify(pral: float) -> dict[str, str]:
    if pral <= -8:
        return {"id": "strongly_alkaline", "name": "Strongly alkaline-forming", "tone": "alkaline"}
    if pral <= -3:
        return {"id": "alkaline", "name": "Alkaline-forming", "tone": "alkaline"}
    if pral < 3:
        return {"id": "neutral", "name": "Roughly neutral", "tone": "neutral"}
    if pral < 15:
        return {"id": "acid", "name": "Acid-forming", "tone": "acid"}
    return {"id": "strongly_acid", "name": "Strongly acid-forming", "tone": "acid"}


def foods() -> list[dict[str, Any]]:
    return [_food_from_row(row) for row in _FOOD_ROWS]


def categories() -> list[str]:
    seen: list[str] = []
    for row in _FOOD_ROWS:
        if row[2] not in seen:
            seen.append(row[2])
    return seen


def find_food(query: str) -> dict[str, Any] | None:
    q = (query or "").strip().lower()
    if not q:
        return None
    catalog = foods()
    for item in catalog:
        if item["id"] == q:
            return item
    matches = [item for item in catalog if q in item["search"]]
    if len(matches) == 1:
        return matches[0]
    exact_name = [item for item in matches if item["name"].lower() == q]
    if len(exact_name) == 1:
        return exact_name[0]
    return matches[0] if len(matches) == 1 else None


def search_foods(query: str = "", category: str = "") -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    cat = (category or "").strip().lower()
    results = []
    for item in foods():
        if cat and item["category"].lower() != cat:
            continue
        if q and q not in item["search"]:
            continue
        results.append(item)
    return results


def food_pral(food: dict[str, Any], grams: float | None = None) -> dict[str, Any]:
    serving = food["default_grams"] if grams is None else grams
    result = calculate_pral(food["per_100"], grams=serving)
    result["food"] = {
        "id": food["id"],
        "name": food["name"],
        "category": food["category"],
        "default_grams": food["default_grams"],
    }
    return result


def meal_pral(items: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """items: [{id or name, grams?}] or already-resolved foods with grams."""
    lines = []
    totals = {key: 0.0 for key in MULTIPLIERS}
    total_pral = 0.0
    total_grams = 0.0
    for raw in items:
        query = str(raw.get("id") or raw.get("name") or "").strip()
        food = find_food(query)
        if food is None:
            raise ValueError(f"Unknown food: {query}")
        grams = float(raw["grams"]) if raw.get("grams") is not None else food["default_grams"]
        line = food_pral(food, grams)
        lines.append(line)
        total_pral += line["pral"]
        total_grams += grams
        for key in MULTIPLIERS:
            totals[key] += line["contributions"][key]
    return {
        "pral": round(total_pral, 2),
        "grams": round(total_grams, 1),
        "label": classify(total_pral),
        "contributions": {k: round(v, 2) for k, v in totals.items()},
        "items": lines,
        "count": len(lines),
        "multipliers": dict(MULTIPLIERS),
    }


def formula_text() -> str:
    return (
        "PRAL (mEq) = 0.49 × protein (g) + 0.037 × phosphorus (mg) "
        "− 0.021 × potassium (mg) − 0.026 × magnesium (mg) − 0.013 × calcium (mg)"
    )


def catalog_payload() -> dict[str, Any]:
    catalog = foods()
    return {
        "formula": formula_text(),
        "multipliers": dict(MULTIPLIERS),
        "units": dict(NUTRIENT_UNITS),
        "labels": dict(NUTRIENT_LABELS),
        "categories": categories(),
        "foods": catalog,
        "note": (
            "Positive PRAL is acid-forming; negative is alkaline-forming. "
            "Taste (lemon) is not the same as renal acid load. Estimate only."
        ),
    }


def _print_result(result: dict[str, Any], title: str | None = None) -> None:
    if title:
        print(title)
    label = result["label"]["name"]
    print(f"  PRAL  {result['pral']:+.2f} mEq   ({label})")
    print(f"  Serving  {result['grams']:g} g")
    print("  From the main multipliers:")
    for key in MULTIPLIERS:
        amount = result["nutrients"][key]
        unit = NUTRIENT_UNITS[key]
        contrib = result["contributions"][key]
        print(
            f"    {NUTRIENT_LABELS[key]:<12} {amount:>8.2f} {unit:<2}  × "
            f"{MULTIPLIERS[key]:+.3f}  =  {contrib:+.2f}"
        )


def _parse_meal_token(token: str) -> dict[str, Any]:
    if ":" not in token:
        return {"id": token}
    name, grams = token.rsplit(":", 1)
    return {"id": name, "grams": float(grams)}


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check food acidity (PRAL) from the five main multipliers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python pral.py calc -p 20 -P 200 -k 300 -m 25 -c 10\n"
            "  python pral.py food banana\n"
            "  python pral.py food cheddar --grams 30\n"
            "  python pral.py search cheese\n"
            "  python pral.py meal banana:118 cheddar:30 potato:170\n"
            "  python pral.py --list-foods\n"
        ),
    )
    parser.add_argument("--list-foods", action="store_true", help="List built-in foods")
    parser.add_argument("--multipliers", action="store_true", help="Print the five multipliers")
    sub = parser.add_subparsers(dest="cmd")

    calc = sub.add_parser("calc", help="PRAL from nutrient amounts (per 100 g)")
    calc.add_argument("-p", "--protein", type=float, required=True, help="Protein g / 100 g")
    calc.add_argument("-P", "--phosphorus", type=float, required=True, help="Phosphorus mg / 100 g")
    calc.add_argument("-k", "--potassium", type=float, required=True, help="Potassium mg / 100 g")
    calc.add_argument("-m", "--magnesium", type=float, required=True, help="Magnesium mg / 100 g")
    calc.add_argument("-c", "--calcium", type=float, required=True, help="Calcium mg / 100 g")
    calc.add_argument("--grams", type=float, default=100.0)

    food_cmd = sub.add_parser("food", help="PRAL for a built-in food")
    food_cmd.add_argument("name")
    food_cmd.add_argument("--grams", type=float, default=None)

    search_cmd = sub.add_parser("search", help="Search built-in foods")
    search_cmd.add_argument("query")
    search_cmd.add_argument("--json", action="store_true")

    list_cmd = sub.add_parser("list", help="List built-in foods")
    list_cmd.add_argument("--category", default="")
    list_cmd.add_argument("--json", action="store_true")

    meal_cmd = sub.add_parser("meal", help="Sum PRAL for foods (name:grams)")
    meal_cmd.add_argument("items", nargs="+", help="e.g. banana:118 cheddar:30")
    meal_cmd.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.multipliers:
        print(formula_text())
        for key, value in MULTIPLIERS.items():
            sign = "acid" if value > 0 else "alkaline"
            print(f"  {NUTRIENT_LABELS[key]:<12} {value:+.3f}  ({sign}, {NUTRIENT_UNITS[key]})")
        return 0

    if args.list_foods or args.cmd == "list":
        category = getattr(args, "category", "") or ""
        rows = search_foods(category=category)
        if getattr(args, "json", False):
            print(json.dumps(rows, indent=2))
            return 0
        print(f"{'Food':<28} {'Category':<14} {'PRAL/100g':>10}  Usual serving")
        for item in rows:
            print(
                f"{item['name']:<28} {item['category']:<14} "
                f"{item['pral_per_100']:>+10.1f}  {item['default_grams']} g"
            )
        return 0

    if args.cmd == "calc":
        result = calculate_pral(
            {
                "protein": args.protein,
                "phosphorus": args.phosphorus,
                "potassium": args.potassium,
                "magnesium": args.magnesium,
                "calcium": args.calcium,
            },
            grams=args.grams,
        )
        _print_result(result, "From nutrients")
        return 0

    if args.cmd == "food":
        food = find_food(args.name)
        if food is None:
            matches = search_foods(args.name)
            if not matches:
                print(f"No food matched {args.name!r}. Try: python pral.py search {args.name}")
                return 1
            if len(matches) > 1:
                print(f"Several foods matched {args.name!r}:")
                for item in matches:
                    print(f"  {item['id']:16}  {item['name']}")
                return 1
            food = matches[0]
        result = food_pral(food, args.grams)
        _print_result(result, f"{food['name']}")
        return 0

    if args.cmd == "search":
        rows = search_foods(args.query)
        if args.json:
            print(json.dumps(rows, indent=2))
            return 0
        if not rows:
            print("No matches.")
            return 1
        for item in rows:
            print(f"{item['pral_per_100']:+6.1f}  {item['name']}  ({item['category']})")
        return 0

    if args.cmd == "meal":
        try:
            parsed = [_parse_meal_token(token) for token in args.items]
            result = meal_pral(parsed)
        except ValueError as exc:
            print(str(exc))
            return 1
        if args.json:
            print(json.dumps(result, indent=2))
            return 0
        print(f"Meal  {result['pral']:+.2f} mEq  ({result['label']['name']})  {result['grams']:g} g")
        for line in result["items"]:
            print(f"  {line['pral']:+6.2f}  {line['food']['name']}  ({line['grams']:g} g)")
        print("  From the main multipliers:")
        for key in MULTIPLIERS:
            print(f"    {NUTRIENT_LABELS[key]:<12} {result['contributions'][key]:+.2f}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(cli())
