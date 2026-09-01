# File Triage — gather, view, decide

Do **not** buy a document-management app for this. Those tools help after you already know what to keep. Your bottleneck is a 146 GB iCloud Drive pile plus a 46 GB iPhone backup: look at the big stuff, put each file in a bucket, move it, repeat in short sessions.

This repo now has a **local** File Triage app for that loop. It runs on your Mac, does not upload files, and does not need Claude.

## What this is (and is not)

| Buy / skip | Why |
|---|---|
| Skip Duplicate Detective *first* | It only finds exact copies. It will not shrink Photos, backups, or “I might need this PDF someday.” |
| Skip DEVONthink / EagleFiler / similar | Organizers. Useful later for the small **Critical** set, not for emptying Drive. |
| Use this triage tool | Inventory a folder, sort by size, preview, mark Critical / Keep local / Archive / Delete, then apply moves. |
| Use Finder + iCloud settings too | Turn off bulk sync (Desktop & Documents, extra backups, Photos if you store photos elsewhere). The app cannot change Apple account switches. |

## Four buckets

| Bucket | Meaning | Where it goes |
|---|---|---|
| **Critical** | Need on phone + Mac, and actually important | iCloud Drive `Critical` |
| **Keep local** | Need it, not in the cloud | `~/Documents-Local` |
| **Archive** | Old, might need someday | `~/Archive` or an external drive |
| **Delete** | Junk, installer, extra copy | `~/Documents-Local/_TriageTrash` (recoverable) |

If you hesitate, choose **Archive**, not Critical.

## Run it

```bash
cd ~/Wellbeing-Log
source venv/bin/activate   # after Setup
python scripts/make_triage_demo.py   # optional sample pile
python file_triage_ui.py             # http://127.0.0.1:5051
```

Desktop window:

```bash
python desktop_file_triage.py
```

After `./install_desktop_shortcuts.sh`, use **5. Open File Triage** on the Desktop.

CLI (scan / summary / dry-run apply):

```bash
python file_triage.py scan "/path/to/folder"
python file_triage.py summary outputs/file_triage/<session>.json
python file_triage.py apply outputs/file_triage/<session>.json          # dry run
python file_triage.py apply outputs/file_triage/<session>.json --execute
```

On a Mac, iCloud Drive is usually:

`~/Library/Mobile Documents/com~apple~CloudDocs`

Do not start with the entire home folder. Scan the Drive folder, or one huge subfolder.

## Safe defaults

- Scan only **lists** files. Nothing is moved until **Apply decisions**.
- **Delete** is a move into Triage Trash, not Empty Trash / empty iCloud Recently Deleted.
- The UI listens on **127.0.0.1** so other machines on the network cannot see your file list.
- Duplicate detection hashes only files that already share the same size (so a 146 GB scan is not hashing every byte twice).
- Sessions save under `outputs/file_triage/` so you can stop after 30–45 minutes and continue later.

## Suggested order (same as before, now with a queue)

1. On iPhone: trim the **46 GB backup** (Settings → iCloud → Manage → Backups) for headroom.
2. On the Mac, scan iCloud Drive with File Triage.
3. Work **largest files / folders first**, then Videos / DMGs / ZIPs, then PDFs, then duplicates.
4. Apply moves. Empty Triage Trash only after you are sure.
5. Empty iCloud **Recently Deleted** if you deleted from Drive (that still counts against quota until it is gone).

## Keys in the UI

`1` Critical · `2` Keep local · `3` Archive · `4` Delete · `Space` Skip · `J` / `K` next / previous
