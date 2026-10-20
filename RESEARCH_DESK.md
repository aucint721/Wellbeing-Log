# Research Desk — M.Ed. open-access finder & study path

Local tool for a Master of Education student (inclusion & special education) studying **research methods**, with the working topic:

> Improving learning outcomes for special education students using Minecraft Education

It does three jobs:

1. **Open-access finder** — curated OA portals + live OpenAlex search filtered to `open_access.is_oa:true`
2. **Source organizer** — local reading queue (`research_data/sources.json`) with notes/tags; export RIS/BibTeX to Zotero
3. **Library workflow** — university discovery → ILL → OA portals, with Zotero / Calibre / Hazel kept in their lanes

Plus a **postgraduate research-methods study path** tailored to that topic.

## Hard rules (legal access only)

- OpenAlex queries always include an OA filter (`open_access.is_oa:true`).
- Portal links go to ERIC, DOAJ, CORE, Google Scholar, Semantic Scholar, Unpaywall, OER Commons, Open Textbook Library.
- No Sci-Hub, no paywall bypass, no DRM / read-only book scraping.
- Save metadata and *your* notes for works you access legally (OA, uni licence, or ILL).

## Run it (Mac)

macOS does not ship a `python` command. Use **`python3`**, from the project folder:

```zsh
cd ~/Wellbeing-Log
python3 research_desk_ui.py          # http://127.0.0.1:5053
```

Or the launcher:

```zsh
cd ~/Wellbeing-Log
./research                           # web UI
./research desktop                   # native window (pywebview → browser fallback)
./research search "Minecraft Education special education"
./research presets
./research curated
./research path
./research workflow
./research sources
./research add --title "Example OA paper" --url https://… --tags minecraft,inclusion
./research export --format ris
```

Override host/port with `RESEARCH_HOST`, `RESEARCH_PORT`, or `PORT`. Default bind is **127.0.0.1:5053** (localhost only).

## Suggested weekly flow

1. Run a preset (Inclusion, GBL, or Minecraft Education) in **Find OA**.
2. Open OA landing pages; save keepers to the **Sources** queue with a one-line note.
3. Follow the **Study path** steps (question → design → ethics → data → proposal).
4. Export RIS → import into **Zotero** collections (Methods / Inclusion / GBL / Minecraft / Ethics).
5. For gaps, use **Library workflow**: uni discovery → ILL → Unpaywall — never unofficial PDF hosts.

## Data

Local queue lives in `research_data/` (gitignored). Safe to delete if you want a clean slate; Zotero remains your long-term library.
