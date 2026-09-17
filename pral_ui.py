#!/usr/bin/env python3
"""
PRAL food-acidity checker web UI.

Default bind is 127.0.0.1:5052. Override with PRAL_HOST / PRAL_PORT / PORT.
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

from pral import catalog_payload, calculate_pral, find_food, food_pral, meal_pral, search_foods

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("pral.html")


@app.get("/api/bootstrap")
def bootstrap():
    return jsonify(catalog_payload())


@app.get("/api/foods")
def foods_api():
    query = request.args.get("q", "")
    category = request.args.get("category", "")
    return jsonify({"foods": search_foods(query, category)})


@app.post("/api/calc")
def calc_api():
    data = request.get_json(silent=True) or {}
    try:
        grams = float(data.get("grams") if data.get("grams") is not None else 100)
        result = calculate_pral(
            {
                "protein": data.get("protein") or 0,
                "phosphorus": data.get("phosphorus") or 0,
                "potassium": data.get("potassium") or 0,
                "magnesium": data.get("magnesium") or 0,
                "calcium": data.get("calcium") or 0,
            },
            grams=grams,
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify({"ok": True, **result})


@app.post("/api/food")
def food_api():
    data = request.get_json(silent=True) or {}
    query = str(data.get("id") or data.get("name") or "").strip()
    food = find_food(query)
    if food is None:
        matches = search_foods(query)
        if len(matches) == 1:
            food = matches[0]
        else:
            return jsonify({"ok": False, "error": f"Unknown food: {query}", "matches": matches}), 404
    grams = data.get("grams")
    try:
        result = food_pral(food, None if grams is None else float(grams))
    except (TypeError, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify({"ok": True, **result})


@app.post("/api/meal")
def meal_api():
    data = request.get_json(silent=True) or {}
    items = data.get("items") or []
    if not items:
        return jsonify({"ok": False, "error": "Add at least one food."}), 400
    try:
        result = meal_pral(items)
    except (TypeError, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify({"ok": True, **result})


def main() -> None:
    host = os.getenv("PRAL_HOST", "127.0.0.1")
    port = int(os.getenv("PRAL_PORT") or os.getenv("PORT") or 5052)
    print("=" * 60)
    print("PRAL Checker — food acidity from the main multipliers")
    print("=" * 60)
    print(f"Open: http://{host}:{port}")
    print("Positive PRAL = acid-forming. Negative = alkaline-forming.")
    print("=" * 60)
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
