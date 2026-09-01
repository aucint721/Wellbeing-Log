# File Triage — gather, view, decide (local, no extra iCloud)

You already have the specialist apps. You just put a **2 TB SSD** in the iMac. Do **not** buy more iCloud, and do **not** buy another management app.

The job is to **get the ~200 GB off iCloud onto that SSD**, then sort it. Duplicate Detective, Photo Sweeper, Calibre, and Hazel each do one lane. They are not a substitute for walking the document pile.

## What each tool is for

| Tool | Use it for | Do not use it for |
|---|---|---|
| **This File Triage app** | The ~200 GB document dump: largest first, preview, Current / Keep / Archive / Delete | Photos library, Kindle/ebook library, ongoing Downloads hygiene |
| **Photo Sweeper** | Photos and image dumps only | PDFs, Word, Drive folders |
| **Calibre** | Ebooks (`.epub` / `.mobi` / `.azw`). Import keepers, then delete loose copies | Scanning the whole Drive |
| **Duplicate Detective** | After size-first triage, **one folder** of leftover exact copies | First pass; Photos (use Photo Sweeper); “I might need this” |
| **Hazel** | **Going forward**: Downloads, screenshots, installers, “files older than 30 days” | The historical 200 GB pile (rules will misfire on old work) |
| **iCloud** | Optional: a handful of files you truly need on the phone | Storing the 200 GB. Do not upgrade the plan. |

## Get off iCloud first (2 TB iMac is the store)

1. On the iMac, open iCloud Drive in Finder and wait until files are **downloaded** (not the cloud-only placeholder icon).
2. Copy the Drive folder onto the SSD, e.g. `~/From-iCloud-Drive`. Confirm the copy size matches (~200 GB).
3. Turn **off** iCloud Drive and Desktop & Documents (System Settings → Apple ID → iCloud). Copy keepers **before** this; turning sync off does not magically move files home.
4. On the iPhone: trim or turn off iCloud Backup of huge apps. You do not need a 46 GB phone backup in iCloud if the iMac holds the files.
5. Empty iCloud **Recently Deleted** after you are sure the local copy is good. That is how the quota actually drops.
6. Point File Triage at `~/From-iCloud-Drive` (or Documents / Downloads) — **not** at iCloud anymore.

200 GB on a 2 TB disk is about 10%. There is no storage emergency on the iMac; the emergency is decision-making.

## Four buckets (all on the iMac)

| Bucket | Meaning | Default folder |
|---|---|---|
| **Current** | Need often (passport, insurance, this year’s work). Tiny. | `~/Current` |
| **Keep local** | Keep it, not in the cloud. This is most of the 200 GB. | `~/Documents-Local` |
| **Archive** | Old, might need someday. Still on the 2 TB disk. | `~/Archive` |
| **Delete** | Junk, installer, extra copy | `~/Documents-Local/_TriageTrash` |

If you hesitate, choose **Archive**, not Current. Current is not iCloud.

After a session, send **ebooks** you marked Keep into Calibre, and **photo folders** into Photo Sweeper. Then let Duplicate Detective mop exact leftovers in one folder. Set Hazel rules only after the pile is sorted.

## Run File Triage

```bash
cd ~/Wellbeing-Log
source venv/bin/activate   # after Setup
python scripts/make_triage_demo.py   # optional sample pile
python file_triage_ui.py             # http://127.0.0.1:5051
```

Desktop: `python desktop_file_triage.py` or **5. Open File Triage**.

```bash
python file_triage.py scan "~/From-iCloud-Drive"
python file_triage.py summary outputs/file_triage/<session>.json
python file_triage.py apply outputs/file_triage/<session>.json          # dry run
python file_triage.py apply outputs/file_triage/<session>.json --execute
```

## Safe defaults

- Scan only **lists** files. Nothing is moved until **Apply decisions**.
- **Delete** is a move into Triage Trash, not Empty Trash / empty iCloud Recently Deleted.
- Destinations default to **local folders on this Mac**, not iCloud Drive.
- The UI listens on **127.0.0.1**.
- Duplicate detection hashes only files that already share the same size.
- Sessions save under `outputs/file_triage/` so you can stop after 30–45 minutes.

## Suggested order

1. Local copy of Drive on the 2 TB SSD; turn iCloud Drive off.
2. File Triage: largest files / folders, then videos / DMGs / ZIPs, then PDFs, then duplicates.
3. Photo Sweeper on photo dumps. Calibre on ebooks.
4. Duplicate Detective on one leftover folder, Move to Trash on, review before delete.
5. Hazel: new Downloads older than 30 days, screenshots, `.dmg`/`.pkg` after install.
6. Empty Triage Trash only when you are sure. Do not buy more iCloud.

## Keys in the UI

`1` Current · `2` Keep local · `3` Archive · `4` Delete · **hover** the queue to preview · `S` Skip · `J` / `K` next / previous · `Space` optional full-screen zoom (Esc closes)

Run the mouse down the file list — a preview pane opens on the right so you do not have to press Space for every file.
