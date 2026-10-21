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

## How this fits Zotero, Calibre, and Hazel

You already have the right stack. Research Desk does **not** replace them.

| Tool | Your job with it |
|---|---|
| **Zotero** | Source of truth for citations, PDFs you may keep, Word/Docs citing. Use the **Zotero Connector** on ERIC/DOAJ/publisher pages. Create collections: Methods / Inclusion / GBL / Minecraft / Ethics. |
| **Research Desk** | Find legal OA hits fast, stage a short queue with study notes, **Export RIS or BibTeX** → Zotero File → Import. |
| **Calibre** | Open textbooks and ebooks you own (`.epub` / `.mobi`). Not journal PDFs. |
| **Hazel** | Ongoing automation only — e.g. browser downloads of research PDFs → `~/Zotero/storage-inbox`, rename `YYYY-Author-Title.pdf`. Do not auto-delete research PDFs. |

### Zotero import (two paths)

1. **From this desk:** Sources tab → Export RIS → Zotero **File → Import…**
2. **From the browser:** Zotero Connector while reading ERIC / DOAJ / OA publisher pages (best for metadata quality).

Optional Hazel: watch `~/Downloads` for `.pdf`, move into a folder Zotero is set to check, or into `storage-inbox` you import in batches.

## Find tab — set criteria before you search

On **Find OA**, choose criteria first, then click **Search open access**. Presets only fill the query — they do **not** auto-run.

| Field | Notes |
|---|---|
| **Query** | Required. Presets or free text. |
| **Year from / Year to** | Optional inclusive range (`from_publication_date` / `to_publication_date`). |
| **Results** | `per_page` (8–50). |
| **Sort** | Relevance, most cited, newest, or oldest (OpenAlex sorts). |
| **Work type** | Optional: article, review, book, book-chapter, dissertation. |

An **About to search** summary shows the active criteria above the results. Last-used criteria are restored from `localStorage` when you return. OA-only (`open_access.is_oa:true`) is always on.

CLI mirrors the same options:

```zsh
./research search "Minecraft Education" -n 20 --year-from 2018 --year-to 2025 --sort cited --type article
```

## Suggested weekly flow

1. On **Find OA**, pick a preset (Inclusion, GBL, or Minecraft Education), adjust years/sort/count if needed, then Search.
2. Open OA landing pages; save keepers to the **Sources** queue with a one-line note (or grab with the Zotero Connector).
3. Follow the **Study path** steps (question → design → ethics → data → proposal).
4. Export RIS → import into **Zotero** collections (Methods / Inclusion / GBL / Minecraft / Ethics).
5. For gaps, use **Library workflow**: uni discovery → ILL → Unpaywall — never unofficial PDF hosts.
6. Put openly licensed / purchased education ebooks in **Calibre**; leave articles in Zotero.

## Data

Local queue lives in `research_data/` (gitignored). Safe to delete if you want a clean slate; **Zotero remains your long-term library.**
