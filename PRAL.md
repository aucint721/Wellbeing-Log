# PRAL Checker — food acidity from the main multipliers

PRAL (Potential Renal Acid Load) estimates how acid- or alkaline-forming a food is for the kidneys. This app uses the five **Remer & Manz (1995)** multipliers — it does not look up a published score.

Positive PRAL = acid-forming. Negative PRAL = alkaline-forming. Taste is not the same thing: lemon is sour, but not acid-forming.

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

Enter amounts **per 100 g**, then set the serving. The app scales the same way for built-in and USDA foods.

The Common foods list includes **~240 everyday items**. Type to filter it. Press **Enter** or **Search USDA** to look up anything else in [USDA FoodData Central](https://fdc.nal.usda.gov/) (protein, phosphorus, potassium, magnesium, calcium → PRAL). Optional: set `USDA_FDC_API_KEY` for a higher rate limit; otherwise the public demo key is used.

```zsh
python3 pral.py search kimchi --online
```

## Run it (Mac)

macOS does not ship a `python` command. Use **`python3`**, and run from the project folder — not `~`.

```zsh
cd ~/Wellbeing-Log
python3 pral_ui.py              # http://127.0.0.1:5052
```

Or the launcher (finds `python3` and the project folder for you):

```zsh
cd ~/Wellbeing-Log
./pral                          # web UI
./pral desktop                  # native window
./pral food banana
./pral calc -p 20 -P 200 -k 300 -m 25 -c 10 --grams 100
./pral meal banana:118 cheddar:30 potato:170
./pral search cheese
./pral --list-foods
```

Double-click **Launch PRAL Checker.command** in the project folder, or after `./install_desktop_shortcuts.sh` use **6. Open PRAL Checker** on the Desktop.

If `python3` is also missing: double-click **1. Setup Presentation Generator**, or run `xcode-select --install`.

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
