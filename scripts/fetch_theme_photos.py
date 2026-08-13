#!/usr/bin/env python3
"""
Download / refresh Unsplash scenic photos used by photo themes.

Photos are stored locally under theme_assets/ so generation works offline.
Unsplash license: free to use; attribution appreciated (https://unsplash.com/license).

Usage:
  python scripts/fetch_theme_photos.py
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "theme_assets"

# filename → Unsplash CDN URL (1600×900 crop)
PHOTOS = {
    "photo_ocean.jpg": "https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=1600&h=900&fit=crop&q=80",
    "photo_forest.jpg": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1600&h=900&fit=crop&q=80",
    "photo_sunset.jpg": "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=1600&h=900&fit=crop&q=80",
    "photo_mountain.jpg": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600&h=900&fit=crop&q=80",
    "photo_city_night.jpg": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1600&h=900&fit=crop&q=80",
    "photo_desert.jpg": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=1600&h=900&fit=crop&q=80",
    "photo_classroom.jpg": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=1600&h=900&fit=crop&q=80",
    "photo_library.jpg": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1600&h=900&fit=crop&q=80",
    "photo_chalkboard.jpg": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1600&h=900&fit=crop&q=80",
    "photo_aurora.jpg": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=1600&h=900&fit=crop&q=80",
    "photo_beach.jpg": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1600&h=900&fit=crop&q=80",
    "photo_workspace.jpg": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=1600&h=900&fit=crop&q=80",
    "photo_flowers.jpg": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=1600&h=900&fit=crop&q=80",
    "photo_lake.jpg": "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=1600&h=900&fit=crop&q=80",
    "photo_snow.jpg": "https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=1600&h=900&fit=crop&q=80",
    "photo_rain.jpg": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?w=1600&h=900&fit=crop&q=80",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ok = 0
    for name, url in PHOTOS.items():
        dest = OUT / name
        req = urllib.request.Request(url, headers={"User-Agent": "Wellbeing-Log-ThemeFetcher/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if len(data) < 5000:
            raise RuntimeError(f"{name} download too small ({len(data)} bytes)")
        dest.write_bytes(data)
        print(f"✓ {name} ({len(data):,} bytes)")
        ok += 1
    print(f"\nSaved {ok} photos into {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
