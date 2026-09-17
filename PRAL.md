# PRAL Checker — food acidity from the main multipliers

PRAL (Potential Renal Acid Load) estimates how acid- or alkaline-forming a food is for the kidneys. This app uses the five **Remer & Manz (1995)** multipliers — it does not look up a published score.

Positive PRAL = acid-forming. Negative PRAL = alkaline-forming. Taste is not the same thing: lemon is sour, but alkaline-forming.

This is a dietary estimate, not a medical test.

## The five multipliers

```
PRAL (mEq) = 0.49 × protein (g)
           + 0.037 × phosphorus (mg)
           − 0.021 × potassium (mg)
           − 0.026 × magnesium (mg)
           − 0.013 × calcium (mg)
```

| Nutrient | Multiplier | Direction |
|---|---|---|
| Protein | +0.49 per g | Acid |
| Phosphorus | +0.037 per mg | Acid |
| Potassium | −0.021 per mg | Alkaline |
| Magnesium | −0.026 per mg | Alkaline |
| Calcium | −0.013 per mg | Alkaline |

Enter amounts **per 100 g**, then set the serving. The app scales the same way for built-in foods.

## Run it

```bash
python pral_ui.py              # http://127.0.0.1:5052
python desktop_pral.py         # native window
python pral.py --multipliers
python pral.py food banana
python pral.py calc -p 20 -P 200 -k 300 -m 25 -c 10 --grams 100
python pral.py meal banana:118 cheddar:30 potato:170
python pral.py search cheese
python pral.py --list-foods
```

Desktop shortcut (after `./install_desktop_shortcuts.sh`): **6. Open PRAL Checker**.

Override host/port with `PRAL_HOST`, `PRAL_PORT`, or `PORT`.

## How to read the number

| PRAL (mEq) | Label |
|---|---|
| ≤ −8 | Strongly alkaline-forming |
| −8 to −3 | Alkaline-forming |
| −3 to +3 | Roughly neutral |
| +3 to +15 | Acid-forming |
| ≥ +15 | Strongly acid-forming |

Cheese, meat, and eggs tend to land acid. Potatoes, greens, and most fruit tend to land alkaline. A mixed plate is the useful check — one cheddar serving plus a baked potato often nets closer to neutral than either food alone.
