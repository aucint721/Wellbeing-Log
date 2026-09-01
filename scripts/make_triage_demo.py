#!/usr/bin/env python3
"""
Build a synthetic folder tree for File Triage demos and tests.
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path


PDF_BYTES = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >> endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer << /Size 4 /Root 1 0 R >>
startxref
190
%%EOF
"""


def _write(path: Path, data: bytes, age_days: int = 0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    if age_days:
        when = time.time() - age_days * 86400
        os.utime(path, (when, when))


def make_demo(root: Path) -> Path:
    if root.exists():
        # Keep existing extra files; overwrite known demo names
        pass
    root.mkdir(parents=True, exist_ok=True)

    keepers = root / "Current-Work"
    junk = root / "Downloads-Dump"
    photos = root / "Photo-Dump"
    old_tax = root / "Taxes-2018"
    videos = root / "Old-Videos"
    dupes = root / "Duplicates"

    _write(
        keepers / "passport-scan.txt",
        b"PASSPORT scan notes - keep in Critical.\nExpiry 2031.\n",
    )
    _write(
        keepers / "insurance-policy.txt",
        b"Home insurance policy 2026. Keep in Critical.\n",
    )
    _write(
        keepers / "lesson-plan.txt",
        b"Week 3 lesson plan - current work, keep local.\n",
        age_days=12,
    )

    _write(junk / "Installer.dmg", b"X" * (2 * 1024 * 1024), age_days=800)
    _write(junk / "random-notes.txt", b"scratch notes from 2019\n", age_days=900)
    _write(junk / "statement-scan.pdf", PDF_BYTES, age_days=400)
    _write(junk / "old-archive.zip", b"PK\x03\x04" + b"Z" * (512 * 1024), age_days=1100)

    _write(photos / "holiday.jpg", b"\xff\xd8\xff" + b"J" * (300 * 1024), age_days=600)
    _write(photos / "holiday-copy.jpg", b"\xff\xd8\xff" + b"J" * (300 * 1024), age_days=600)
    _write(photos / "screenshot.png", b"\x89PNG\r\n\x1a\n" + b"P" * (80 * 1024), age_days=40)

    _write(old_tax / "tax-return-2018.txt", b"Tax return 2018 - archive, not Critical.\n", age_days=2500)
    _write(old_tax / "receipts.txt", b"Receipts 2018\n" + b"line\n" * 40, age_days=2500)

    _write(videos / "family-clip.mp4", b"ftypmp42" + b"V" * (3 * 1024 * 1024), age_days=1500)

    payload = b"IDENTICAL-DOCUMENT-BODY-" + b"D" * 4096
    _write(dupes / "report-final.txt", payload, age_days=100)
    _write(dupes / "report-final-copy.txt", payload, age_days=90)
    _write(root / "Inbox" / "report-final.txt", payload, age_days=80)

    readme = root / "README-DEMO.txt"
    _write(
        readme,
        (
            "This is a fake iCloud-style folder for File Triage.\n"
            "Try: largest files first, then Duplicates, then decide:\n"
            "  Critical / Keep local / Archive / Delete\n"
        ).encode(),
    )
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a sample folder for File Triage")
    parser.add_argument(
        "-o",
        "--output",
        default=str(Path(__file__).resolve().parent.parent / "outputs" / "triage_demo"),
    )
    args = parser.parse_args()
    root = make_demo(Path(args.output).expanduser())
    print(f"Demo folder: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
