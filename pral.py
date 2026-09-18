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
import os
import sys
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent

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

FDC_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
FDC_NUTRIENT_IDS = {
    1003: "protein",
    1087: "calcium",
    1090: "magnesium",
    1091: "phosphorus",
    1092: "potassium",
}


def _food_from_record(rec: dict[str, Any]) -> dict[str, Any]:
    per_100 = {
        "protein": float(rec.get("protein") or 0),
        "phosphorus": float(rec.get("phosphorus") or 0),
        "potassium": float(rec.get("potassium") or 0),
        "magnesium": float(rec.get("magnesium") or 0),
        "calcium": float(rec.get("calcium") or 0),
    }
    per_100_result = calculate_pral(per_100, grams=100)
    fid = str(rec["id"])
    name = str(rec["name"])
    category = str(rec.get("category") or "Extras")
    source = rec.get("source") or "local"
    return {
        "id": fid,
        "name": name,
        "category": category,
        "default_grams": int(rec.get("default_grams") or 100),
        "per_100": per_100,
        "pral_per_100": per_100_result["pral"],
        "label_per_100": per_100_result["label"],
        "search": f"{fid} {name} {category}".lower(),
        "source": source,
        "incomplete": bool(rec.get("incomplete")),
        "detail": rec.get("detail") or "",
    }


@lru_cache(maxsize=1)
def foods() -> tuple[dict[str, Any], ...]:
    path = ROOT / "pral_foods.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return tuple(_food_from_record(rec) for rec in payload["foods"])


def categories() -> list[str]:
    seen: list[str] = []
    for item in foods():
        if item["category"] not in seen:
            seen.append(item["category"])
    return seen


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


def _usda_api_key() -> str:
    return (
        os.getenv("USDA_FDC_API_KEY")
        or os.getenv("FDC_API_KEY")
        or "DEMO_KEY"
    )


def _usda_category(raw: str) -> str:
    text = (raw or "").lower()
    mapping = (
        (("beef", "pork", "lamb", "veal", "poultry", "chicken", "turkey", "fish",
          "seafood", "sausage", "finfish", "shellfish", "cured meat", "frankfurter",
          "meat"), "Meat & fish"),
        (("dairy", "cheese", "milk", "yogurt", "egg"), "Dairy & eggs"),
        (("vegetable", "potato", "tomato", "lettuce", "cabbage"), "Vegetables"),
        (("fruit", "berry", "melon"), "Fruit"),
        (("nut", "seed"), "Nuts & seeds"),
        (("legume", "bean", "pea", "soy", "tofu"), "Legumes"),
        (("grain", "bread", "cereal", "pasta", "rice", "baked product"), "Grains"),
        (("beverage", "alcohol", "drink", "juice"), "Drinks"),
    )
    for needles, label in mapping:
        if any(n in text for n in needles):
            return label
    return "Extras"


def _usda_default_grams(food: dict[str, Any]) -> int:
    measures = food.get("foodMeasures") or []
    for item in measures:
        if (item.get("disseminationText") or "").lower() == "quantity not specified":
            weight = item.get("gramWeight")
            if weight:
                return max(1, int(round(float(weight))))
    for item in sorted(measures, key=lambda row: row.get("rank") or 99):
        weight = float(item.get("gramWeight") or 0)
        if 15 <= weight <= 250:
            return int(round(weight))
    return 100


def _usda_nutrients(food: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    values = {key: 0.0 for key in MULTIPLIERS}
    found: set[str] = set()
    for nutrient in food.get("foodNutrients") or []:
        nid = nutrient.get("nutrientId")
        key = FDC_NUTRIENT_IDS.get(nid)
        if not key:
            continue
        amount = nutrient.get("value")
        if amount is None:
            continue
        values[key] = float(amount)
        found.add(key)
    missing = [key for key in MULTIPLIERS if key not in found]
    return values, missing


def search_usda(query: str, limit: int = 15) -> dict[str, Any]:
    """Search USDA FoodData Central and compute PRAL from the five nutrients."""
    q = (query or "").strip()
    if len(q) < 2:
        return {"ok": False, "error": "Type at least 2 characters to search USDA.", "foods": []}
    payload = {
        "query": q,
        "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
        "pageSize": max(1, min(int(limit), 25)),
    }
    body = json.dumps(payload).encode("utf-8")
    url = f"{FDC_SEARCH_URL}?api_key={_usda_api_key()}"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:200]
        if exc.code == 429:
            return {
                "ok": False,
                "error": "USDA rate limit hit. Wait a minute and try again, or get a free key at fdc.nal.usda.gov.",
                "foods": [],
            }
        return {"ok": False, "error": f"USDA search failed ({exc.code}). {detail}", "foods": []}
    except urllib.error.URLError:
        return {"ok": False, "error": "Could not reach USDA FoodData Central. Check the network.", "foods": []}

    foods_out = []
    for raw in data.get("foods") or []:
        nutrients, missing = _usda_nutrients(raw)
        if len(missing) == 5:
            continue
        name = (raw.get("description") or "USDA food").strip()
        rec = {
            "id": f"fdc:{raw.get('fdcId')}",
            "name": name[:80],
            "category": _usda_category(str(raw.get("foodCategory") or "")),
            "default_grams": _usda_default_grams(raw),
            "source": "usda",
            "incomplete": bool(missing),
            "detail": raw.get("dataType") or "",
            **nutrients,
        }
        item = _food_from_record(rec)
        foods_out.append(item)
    return {
        "ok": True,
        "query": q,
        "total": data.get("totalHits"),
        "foods": foods_out,
        "source": "USDA FoodData Central",
    }


def catalog_payload() -> dict[str, Any]:
    catalog = list(foods())
    return {
        "formula": formula_text(),
        "multipliers": dict(MULTIPLIERS),
        "units": dict(NUTRIENT_UNITS),
        "labels": dict(NUTRIENT_LABELS),
        "categories": categories(),
        "foods": catalog,
        "food_count": len(catalog),
        "online_search": True,
        "note": (
            "Positive PRAL is acid-forming; negative is alkaline-forming. "
            "Taste (lemon) is not the same as renal acid load. Estimate only."
        ),
    }


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
            "Examples (Mac: python3, or ./pral …):\n"
            "  python3 pral.py calc -p 20 -P 200 -k 300 -m 25 -c 10\n"
            "  python3 pral.py food banana\n"
            "  python3 pral.py food cheddar --grams 30\n"
            "  python3 pral.py search cheese\n"
            "  python3 pral.py search kimchi --online\n"
            "  python3 pral.py meal banana:118 cheddar:30 potato:170\n"
            "  python3 pral.py --list-foods\n"
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
    search_cmd.add_argument("--online", action="store_true", help="Also search USDA FoodData Central")

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
        print(f"{'Food':<36} {'Category':<14} {'PRAL/100g':>10}  Usual serving")
        for item in rows:
            print(
                f"{item['name']:<36} {item['category']:<14} "
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
                print(f"No food matched {args.name!r}. Try: python3 pral.py search {args.name}")
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
        if args.online:
            remote = search_usda(args.query)
            if not remote.get("ok"):
                print(remote.get("error") or "USDA search failed.")
                if not rows:
                    return 1
            else:
                seen = {item["id"] for item in rows}
                for item in remote["foods"]:
                    if item["id"] not in seen:
                        rows.append(item)
        if args.json:
            print(json.dumps(rows, indent=2))
            return 0
        if not rows:
            print("No matches. Try --online to search USDA FoodData Central.")
            return 1
        for item in rows:
            tag = " USDA" if item.get("source") == "usda" else ""
            print(f"{item['pral_per_100']:+6.1f}  {item['name']}  ({item['category']}){tag}")
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
