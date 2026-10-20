#!/usr/bin/env python3
"""
Research Desk — open-access finder + reading queue for M.Ed. research.

Legal OA discovery only (OpenAlex is_oa + curated portals). Does not scrape
paywalled or DRM/"read-only" books. Zotero stays the citation library;
this tool exports RIS/BibTeX into it. Calibre = owned ebooks; Hazel = file rules.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urlencode

import requests

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "research_data"
SOURCES_PATH = DATA_DIR / "sources.json"
DEFAULT_TOPIC = (
    "Improving learning outcomes for special education students using Minecraft Education"
)
OPENALEX_WORKS = "https://api.openalex.org/works"
USER_AGENT = "ResearchDesk/1.0 (M.Ed. study tool; mailto:research-desk@localhost)"

# ---------------------------------------------------------------------------
# Curated open-access / legal portals (deep links, not scraped content)
# ---------------------------------------------------------------------------

PORTALS: list[dict[str, str]] = [
    {
        "id": "eric",
        "name": "ERIC (Education)",
        "blurb": "US education research index — many full-text PDFs are free.",
        "home": "https://eric.ed.gov/",
        "search_tpl": "https://eric.ed.gov/?q={q}",
    },
    {
        "id": "doaj",
        "name": "DOAJ",
        "blurb": "Directory of Open Access Journals — peer-reviewed OA only.",
        "home": "https://doaj.org/",
        "search_tpl": "https://doaj.org/search/articles?ref=homepage-box&source=%7B%22query%22%3A%7B%22query_string%22%3A%7B%22query%22%3A%22{q}%22%7D%7D%7D",
    },
    {
        "id": "openalex",
        "name": "OpenAlex",
        "blurb": "Scholarly graph with OA filter; this app queries it live.",
        "home": "https://openalex.org/",
        "search_tpl": "https://openalex.org/works?page=1&filter=open_access.is_oa%3Atrue&q={q}",
    },
    {
        "id": "core",
        "name": "CORE",
        "blurb": "Aggregates open-access research papers from repositories.",
        "home": "https://core.ac.uk/",
        "search_tpl": "https://core.ac.uk/search?q={q}",
    },
    {
        "id": "semantic",
        "name": "Semantic Scholar",
        "blurb": "AI-assisted paper search; use PDF links only when marked free.",
        "home": "https://www.semanticscholar.org/",
        "search_tpl": "https://www.semanticscholar.org/search?q={q}",
    },
    {
        "id": "scholar",
        "name": "Google Scholar",
        "blurb": "Broad search — pair with uni “Find it” / library link resolver.",
        "home": "https://scholar.google.com/",
        "search_tpl": "https://scholar.google.com/scholar?q={q}",
    },
    {
        "id": "unpaywall",
        "name": "Unpaywall / OA button",
        "blurb": "Browser extension finds legal OA PDFs beside paywalled pages.",
        "home": "https://unpaywall.org/products/extension",
        "search_tpl": "https://unpaywall.org/",
    },
    {
        "id": "oercommons",
        "name": "OER Commons",
        "blurb": "Open educational resources, including research-methods primers.",
        "home": "https://www.oercommons.org/",
        "search_tpl": "https://www.oercommons.org/search?f.search={q}",
    },
    {
        "id": "opentextbook",
        "name": "Open Textbook Library",
        "blurb": "Free, openly licensed textbooks (methods, education, inclusion).",
        "home": "https://open.umn.edu/opentextbooks/",
        "search_tpl": "https://open.umn.edu/opentextbooks/textbooks?q={q}",
    },
]

TOOL_LANES: list[dict[str, str]] = [
    {
        "tool": "Research Desk (this app)",
        "use_for": "Find legal OA papers, study research methods, stage a short reading queue, export to Zotero",
        "not_for": "Long-term citation library, DRM books, paywall bypass",
    },
    {
        "tool": "Zotero",
        "use_for": "Grab from the browser, organise collections/tags, cite in Word/Google Docs, store PDFs you are allowed to keep",
        "not_for": "Discovering OA (use this desk + ERIC/DOAJ); file-system cleanup",
    },
    {
        "tool": "Calibre",
        "use_for": "Ebooks you own or that are openly licensed (.epub/.mobi)",
        "not_for": "Journal PDFs (use Zotero); scanning Drive",
    },
    {
        "tool": "Hazel",
        "use_for": "Ongoing rules: Downloads → Zotero watched folder, rename OCR PDFs, archive old loose files",
        "not_for": "First-pass literature search or citation metadata",
    },
    {
        "tool": "University library",
        "use_for": "Licensed databases, “Find it @ uni”, interlibrary loan, librarian consults",
        "not_for": "Skipping ethics or access agreements",
    },
]

SEARCH_PRESETS: list[dict[str, str]] = [
    {
        "id": "methods_ed",
        "label": "Educational research methods",
        "query": "educational research methods postgraduate qualitative quantitative mixed methods",
    },
    {
        "id": "action_research",
        "label": "Action / practitioner research",
        "query": "action research education practitioner teacher classroom intervention",
    },
    {
        "id": "inclusion_sped",
        "label": "Inclusion & special education",
        "query": "inclusive education special education learning outcomes students with disabilities",
    },
    {
        "id": "gbl",
        "label": "Game-based learning",
        "query": "game-based learning educational games student engagement learning outcomes",
    },
    {
        "id": "minecraft_ed",
        "label": "Minecraft Education",
        "query": "Minecraft Education Edition learning outcomes special education inclusive",
    },
    {
        "id": "topic_full",
        "label": "Your full topic",
        "query": DEFAULT_TOPIC,
    },
    {
        "id": "ethics_sped",
        "label": "Ethics with special education participants",
        "query": "research ethics children disability special education informed consent school-based research",
    },
]

CURATED: list[dict[str, Any]] = [
    {
        "id": "cur-eric-home",
        "title": "ERIC — Education Resources Information Center",
        "authors": ["Institute of Education Sciences"],
        "year": None,
        "kind": "portal",
        "tags": ["methods", "special-education", "portal"],
        "url": "https://eric.ed.gov/",
        "oa_url": "https://eric.ed.gov/",
        "blurb": "Primary free index for education research. Filter to “Full text available on ERIC”.",
        "why": "Best first stop for M.Ed. literature before (or beside) paid databases.",
    },
    {
        "id": "cur-doaj-edu",
        "title": "DOAJ — Education subject browse",
        "authors": ["DOAJ"],
        "year": None,
        "kind": "portal",
        "tags": ["portal", "open-access"],
        "url": "https://doaj.org/search/journals?source=%7B%22query%22%3A%7B%22query_string%22%3A%7B%22query%22%3A%22education%22%7D%7D%7D",
        "oa_url": "https://doaj.org/",
        "blurb": "Peer-reviewed open-access journals in education and related fields.",
        "why": "Guarantees OA journals rather than incidental free PDFs.",
    },
    {
        "id": "cur-otl-research",
        "title": "Open Textbook Library — research / education texts",
        "authors": ["Open Education Network"],
        "year": None,
        "kind": "oer",
        "tags": ["methods", "oer"],
        "url": "https://open.umn.edu/opentextbooks/subjects/education",
        "oa_url": "https://open.umn.edu/opentextbooks/subjects/education",
        "blurb": "Freely licensed textbooks suitable for studying research design without a bookstore bill.",
        "why": "Study research methods from legal full texts before buying commercial handbooks.",
    },
    {
        "id": "cur-oer-methods",
        "title": "OER Commons — research methods",
        "authors": ["OER Commons"],
        "year": None,
        "kind": "oer",
        "tags": ["methods", "oer"],
        "url": "https://www.oercommons.org/search?f.search=research+methods+education",
        "oa_url": "https://www.oercommons.org/search?f.search=research+methods+education",
        "blurb": "Modules and primers on educational research methods.",
        "why": "Short study units that match a research-methods course week.",
    },
    {
        "id": "cur-unesco-inclusion",
        "title": "UNESCO — inclusion in education",
        "authors": ["UNESCO"],
        "year": None,
        "kind": "report",
        "tags": ["inclusion", "special-education", "policy"],
        "url": "https://www.unesco.org/en/inclusion-education",
        "oa_url": "https://www.unesco.org/en/inclusion-education",
        "blurb": "Policy framing for inclusive education (useful background / lit review context).",
        "why": "Grounds “inclusion” language in international education frameworks.",
    },
    {
        "id": "cur-minecraft-edu",
        "title": "Minecraft Education — official education hub",
        "authors": ["Microsoft / Minecraft Education"],
        "year": None,
        "kind": "practitioner",
        "tags": ["minecraft", "game-based-learning", "practitioner"],
        "url": "https://education.minecraft.net/",
        "oa_url": "https://education.minecraft.net/",
        "blurb": "Lesson kits, standards mapping, and case stories. Practitioner, not peer-reviewed.",
        "why": "Intervention description for your topic — cite as grey literature / tool documentation.",
    },
    {
        "id": "cur-minecraft-research",
        "title": "Minecraft Education — research & impact pages",
        "authors": ["Microsoft / Minecraft Education"],
        "year": None,
        "kind": "practitioner",
        "tags": ["minecraft", "outcomes"],
        "url": "https://education.minecraft.net/en-us/resources/research",
        "oa_url": "https://education.minecraft.net/en-us/resources/research",
        "blurb": "Vendor-published research summaries and classroom impact notes.",
        "why": "Useful for describing the tool; triangulate with independent peer-reviewed studies.",
    },
    {
        "id": "cur-frontiers-edu",
        "title": "Frontiers in Education (OA journal)",
        "authors": ["Frontiers"],
        "year": None,
        "kind": "journal",
        "tags": ["open-access", "education"],
        "url": "https://www.frontiersin.org/journals/education",
        "oa_url": "https://www.frontiersin.org/journals/education",
        "blurb": "Open-access education journal — search within for GBL / inclusion papers.",
        "why": "Peer-reviewed OA venue often indexed in OpenAlex with free PDFs.",
    },
    {
        "id": "cur-edtech-society",
        "title": "Educational Technology & Society (journal home)",
        "authors": ["IFETS"],
        "year": None,
        "kind": "journal",
        "tags": ["edtech", "game-based-learning"],
        "url": "https://www.j-ets.net/",
        "oa_url": "https://www.j-ets.net/",
        "blurb": "Long-running ed-tech journal; many volumes are openly readable.",
        "why": "Strong for game-based / technology-supported learning outcomes.",
    },
    {
        "id": "cur-acer",
        "title": "ACER Research Repository",
        "authors": ["Australian Council for Educational Research"],
        "year": None,
        "kind": "repository",
        "tags": ["australia", "education", "methods"],
        "url": "https://research.acer.edu.au/",
        "oa_url": "https://research.acer.edu.au/",
        "blurb": "Australian education research — many reports are free to download.",
        "why": "Relevant if your uni / schooling context is Australian.",
    },
]

STUDY_PATH: list[dict[str, Any]] = [
    {
        "step": 1,
        "title": "What counts as postgraduate research?",
        "focus": "Clarify purpose: generate knowledge (even small-scale) with a transparent method, not only describe practice.",
        "do_next": [
            "Read one OER chapter on educational research paradigms (positivist / interpretive / critical).",
            "Write 5 sentences: what you want to know about Minecraft Education and special education learners.",
        ],
        "preset_id": "methods_ed",
        "tags": ["methods"],
    },
    {
        "step": 2,
        "title": "Frame a researchable question",
        "focus": "Turn the topic into a question with population, intervention, and outcome.",
        "do_next": [
            "Draft: “In what ways does Minecraft Education affect [outcome] for [learners] in [setting]?”",
            "List outcomes you can actually measure or observe (engagement, collaboration, curriculum task completion, IEP goals).",
        ],
        "preset_id": "topic_full",
        "tags": ["design"],
    },
    {
        "step": 3,
        "title": "Choose a design that fits M.Ed. practice",
        "focus": "Action research, case study, or mixed-methods classroom inquiry are common and appropriate.",
        "do_next": [
            "Compare action research cycles vs single-case / small-n designs for special education.",
            "Decide: exploratory (understand experience) vs evaluative (did outcomes improve?).",
        ],
        "preset_id": "action_research",
        "tags": ["methods", "design"],
    },
    {
        "step": 4,
        "title": "Literature map (legal OA first)",
        "focus": "Build a Zotero collection before writing. Separate: methods, inclusion/sped, GBL, Minecraft-specific.",
        "do_next": [
            "Run presets Inclusion, GBL, and Minecraft Education; save keepers to the queue; export RIS → Zotero.",
            "In Zotero, create collections: Methods / Inclusion / GBL / Minecraft / Ethics.",
        ],
        "preset_id": "minecraft_ed",
        "tags": ["literature"],
    },
    {
        "step": 5,
        "title": "Ethics with special education students",
        "focus": "Consent, assent, gatekeepers, data minimisation, and power dynamics in schools.",
        "do_next": [
            "Read your uni HREC/ethics guidelines for research with children and disability.",
            "Note what you will collect (screenshots, chat logs, assessments) and how you will anonymise.",
        ],
        "preset_id": "ethics_sped",
        "tags": ["ethics"],
    },
    {
        "step": 6,
        "title": "Data & learning outcomes",
        "focus": "Align instruments with the outcome definition — avoid “engagement” with no operational measure.",
        "do_next": [
            "Pick 1–2 primary outcomes and 1 process measure (e.g. time-on-task, peer collaboration rubric).",
            "Plan a simple pre/post or repeated probe if evaluating improvement.",
        ],
        "preset_id": "inclusion_sped",
        "tags": ["data"],
    },
    {
        "step": 7,
        "title": "Proposal skeleton",
        "focus": "Background → gap → question → design → participants → data → analysis → ethics → timeline.",
        "do_next": [
            "Fill a one-page outline from Zotero notes (not from memory).",
            "Book a librarian consult for database coverage your uni pays for.",
        ],
        "preset_id": "methods_ed",
        "tags": ["writing"],
    },
]

LIBRARY_WORKFLOW: list[dict[str, str]] = [
    {
        "phase": "1. Start free / OA",
        "detail": "Use this desk’s OpenAlex OA search, ERIC full-text, DOAJ, and curated OERs. Save candidates to the reading queue.",
    },
    {
        "phase": "2. Export into Zotero",
        "detail": "Export RIS or BibTeX from the queue. File → Import in Zotero (or drop into a Hazel-watched folder that Zotero monitors).",
    },
    {
        "phase": "3. Uni discovery",
        "detail": "For gaps, search your library catalogue / Primo / EDS with the same keywords. Use “Find it @ [uni]” from Google Scholar library settings.",
    },
    {
        "phase": "4. Interlibrary loan",
        "detail": "If only a citation exists, request via ILL / document delivery — legal copy through the library.",
    },
    {
        "phase": "5. Unpaywall as a helper",
        "detail": "Install Unpaywall. When a publisher page is paywalled, the extension shows a legal OA PDF if one exists — still no DRM bypass.",
    },
    {
        "phase": "6. Calibre lane",
        "detail": "Open textbooks or purchased education ebooks go in Calibre. Journal articles and thesis PDFs stay in Zotero.",
    },
    {
        "phase": "7. Hazel lane",
        "detail": "Example: Downloads/*.pdf tagged from browsers → move to ~/Zotero/storage-inbox; rename YYYY-Author-Title.pdf. Do not auto-delete research PDFs.",
    },
]


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_sources() -> list[dict[str, Any]]:
    _ensure_data_dir()
    if not SOURCES_PATH.exists():
        return []
    try:
        data = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, list):
        return data
    return data.get("sources", [])


def save_sources(sources: list[dict[str, Any]]) -> None:
    _ensure_data_dir()
    SOURCES_PATH.write_text(
        json.dumps({"updated": _now_iso(), "sources": sources}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _norm_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").strip().lower())


# ---------------------------------------------------------------------------
# OpenAlex OA search
# ---------------------------------------------------------------------------


def _author_names(work: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for auth in work.get("authorships") or []:
        author = auth.get("author") or {}
        name = author.get("display_name")
        if name:
            names.append(name)
    return names


def _normalize_openalex(work: dict[str, Any]) -> dict[str, Any]:
    oa = work.get("open_access") or {}
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    return {
        "id": work.get("id") or "",
        "title": work.get("display_name") or work.get("title") or "Untitled",
        "authors": _author_names(work),
        "year": work.get("publication_year"),
        "doi": doi or None,
        "cited_by": work.get("cited_by_count") or 0,
        "oa_status": oa.get("oa_status"),
        "is_oa": bool(oa.get("is_oa")),
        "oa_url": oa.get("oa_url") or primary.get("pdf_url") or primary.get("landing_page_url"),
        "landing_url": primary.get("landing_page_url") or work.get("id"),
        "venue": source.get("display_name"),
        "type": work.get("type"),
        "abstract_inverted": work.get("abstract_inverted_index"),
    }


def reconstruct_abstract(inverted: dict[str, list[int]] | None) -> str | None:
    if not inverted:
        return None
    positions: dict[int, str] = {}
    for word, idxs in inverted.items():
        for i in idxs:
            positions[i] = word
    if not positions:
        return None
    return " ".join(positions[i] for i in sorted(positions))


def search_openalex(query: str, *, per_page: int = 15, year_from: int | None = None) -> dict[str, Any]:
    q = (query or "").strip()
    if not q:
        return {"ok": False, "error": "Enter a search query.", "results": []}
    filters = ["open_access.is_oa:true"]
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")
    params = {
        "search": q,
        "filter": ",".join(filters),
        "per_page": max(1, min(per_page, 50)),
        "sort": "relevance_score:desc",
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(OPENALEX_WORKS, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        return {"ok": False, "error": f"OpenAlex request failed: {exc}", "results": []}

    results = []
    for work in payload.get("results") or []:
        item = _normalize_openalex(work)
        if not item["is_oa"]:
            continue
        item["abstract"] = reconstruct_abstract(item.pop("abstract_inverted", None))
        results.append(item)
    return {
        "ok": True,
        "query": q,
        "count": len(results),
        "meta": payload.get("meta") or {},
        "results": results,
    }


def portal_links(query: str) -> list[dict[str, str]]:
    q = quote_plus((query or DEFAULT_TOPIC).strip())
    links = []
    for p in PORTALS:
        tpl = p.get("search_tpl") or p["home"]
        links.append(
            {
                "id": p["id"],
                "name": p["name"],
                "blurb": p["blurb"],
                "home": p["home"],
                "url": tpl.format(q=q) if "{q}" in tpl else p["home"],
            }
        )
    return links


def filter_curated(tag: str | None = None, q: str | None = None) -> list[dict[str, Any]]:
    items = CURATED
    if tag:
        t = tag.lower().strip()
        items = [c for c in items if t in [x.lower() for x in c.get("tags") or []] or t in (c.get("kind") or "").lower()]
    if q:
        needle = q.lower().strip()
        items = [
            c
            for c in items
            if needle in (c.get("title") or "").lower()
            or needle in (c.get("blurb") or "").lower()
            or any(needle in t.lower() for t in c.get("tags") or [])
        ]
    return items


# ---------------------------------------------------------------------------
# Reading queue (staging → Zotero)
# ---------------------------------------------------------------------------


def add_source(entry: dict[str, Any]) -> dict[str, Any]:
    sources = load_sources()
    title = (entry.get("title") or "").strip()
    if not title:
        raise ValueError("Title is required.")
    doi = (entry.get("doi") or "").strip() or None
    url = (entry.get("url") or entry.get("oa_url") or entry.get("landing_url") or "").strip() or None

    for existing in sources:
        if doi and existing.get("doi") and existing["doi"].lower() == doi.lower():
            return {"ok": True, "duplicate": True, "source": existing}
        if _norm_title(existing.get("title", "")) == _norm_title(title) and (
            not url or existing.get("url") == url or existing.get("oa_url") == url
        ):
            return {"ok": True, "duplicate": True, "source": existing}

    authors = entry.get("authors") or []
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(";") if a.strip()]

    source = {
        "id": entry.get("id") or f"local-{uuid.uuid4().hex[:10]}",
        "title": title,
        "authors": authors,
        "year": entry.get("year"),
        "doi": doi,
        "url": url,
        "oa_url": entry.get("oa_url") or url,
        "venue": entry.get("venue"),
        "status": entry.get("status") or "to-read",
        "notes": (entry.get("notes") or "").strip(),
        "tags": entry.get("tags") or [],
        "added": _now_iso(),
        "origin": entry.get("origin") or "manual",
    }
    sources.insert(0, source)
    save_sources(sources)
    return {"ok": True, "duplicate": False, "source": source}


def update_source(source_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    sources = load_sources()
    for i, src in enumerate(sources):
        if src.get("id") != source_id:
            continue
        for key in ("title", "notes", "status", "url", "oa_url", "venue", "doi", "year"):
            if key in patch and patch[key] is not None:
                src[key] = patch[key]
        if "authors" in patch and patch["authors"] is not None:
            authors = patch["authors"]
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(";") if a.strip()]
            src["authors"] = authors
        if "tags" in patch and patch["tags"] is not None:
            tags = patch["tags"]
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            src["tags"] = tags
        src["updated"] = _now_iso()
        sources[i] = src
        save_sources(sources)
        return {"ok": True, "source": src}
    return {"ok": False, "error": "Source not found."}


def delete_source(source_id: str) -> dict[str, Any]:
    sources = load_sources()
    kept = [s for s in sources if s.get("id") != source_id]
    if len(kept) == len(sources):
        return {"ok": False, "error": "Source not found."}
    save_sources(kept)
    return {"ok": True, "deleted": source_id}


# ---------------------------------------------------------------------------
# Zotero export (RIS + BibTeX)
# ---------------------------------------------------------------------------


def _ris_escape(text: str) -> str:
    return (text or "").replace("\r\n", "\n").replace("\r", "\n")


def to_ris(sources: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for src in sources:
        lines = ["TY  - JOUR"]
        lines.append(f"TI  - {_ris_escape(src.get('title') or 'Untitled')}")
        for author in src.get("authors") or []:
            lines.append(f"AU  - {_ris_escape(author)}")
        if src.get("year"):
            lines.append(f"PY  - {src['year']}")
        if src.get("venue"):
            lines.append(f"JO  - {_ris_escape(src['venue'])}")
        if src.get("doi"):
            lines.append(f"DO  - {_ris_escape(src['doi'])}")
        url = src.get("oa_url") or src.get("url")
        if url:
            lines.append(f"UR  - {_ris_escape(url)}")
        if src.get("notes"):
            for note_line in _ris_escape(src["notes"]).split("\n"):
                lines.append(f"N1  - {note_line}")
        for tag in src.get("tags") or []:
            lines.append(f"KW  - {_ris_escape(tag)}")
        lines.append("ER  - ")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def _bib_key(src: dict[str, Any]) -> str:
    authors = src.get("authors") or []
    last = "anon"
    if authors:
        last = re.sub(r"[^A-Za-z0-9]", "", authors[0].split()[-1])[:24] or "anon"
    year = src.get("year") or "n.d."
    slug = re.sub(r"[^A-Za-z0-9]+", "", (src.get("title") or "item")[:20]) or "item"
    return f"{last}{year}{slug}"


def _bib_escape(text: str) -> str:
    return (text or "").replace("{", "\\{").replace("}", "\\}").replace("&", "\\&")


def to_bibtex(sources: list[dict[str, Any]]) -> str:
    entries: list[str] = []
    for src in sources:
        key = _bib_key(src)
        authors = " and ".join(src.get("authors") or ["Unknown"])
        fields = [
            f"  title = {{{_bib_escape(src.get('title') or 'Untitled')}}}",
            f"  author = {{{_bib_escape(authors)}}}",
        ]
        if src.get("year"):
            fields.append(f"  year = {{{src['year']}}}")
        if src.get("venue"):
            fields.append(f"  journal = {{{_bib_escape(src['venue'])}}}")
        if src.get("doi"):
            fields.append(f"  doi = {{{_bib_escape(src['doi'])}}}")
        url = src.get("oa_url") or src.get("url")
        if url:
            fields.append(f"  url = {{{_bib_escape(url)}}}")
        if src.get("notes"):
            fields.append(f"  note = {{{_bib_escape(src['notes'])}}}")
        entries.append(f"@article{{{key},\n" + ",\n".join(fields) + "\n}")
    return "\n\n".join(entries) + ("\n" if entries else "")


def export_sources(fmt: str = "ris", source_ids: list[str] | None = None) -> dict[str, Any]:
    sources = load_sources()
    if source_ids:
        wanted = set(source_ids)
        sources = [s for s in sources if s.get("id") in wanted]
    fmt = (fmt or "ris").lower().strip()
    if fmt in ("ris", "application/x-research-info-systems"):
        text = to_ris(sources)
        ext = "ris"
        mime = "application/x-research-info-systems"
    elif fmt in ("bib", "bibtex"):
        text = to_bibtex(sources)
        ext = "bib"
        mime = "application/x-bibtex"
    else:
        return {"ok": False, "error": f"Unknown format: {fmt}"}
    _ensure_data_dir()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = DATA_DIR / f"zotero-export-{stamp}.{ext}"
    path.write_text(text, encoding="utf-8")
    return {
        "ok": True,
        "format": ext,
        "mime": mime,
        "count": len(sources),
        "path": str(path),
        "filename": path.name,
        "text": text,
    }


# ---------------------------------------------------------------------------
# Bootstrap payload for UI
# ---------------------------------------------------------------------------


def bootstrap_payload() -> dict[str, Any]:
    return {
        "topic": DEFAULT_TOPIC,
        "portals": portal_links(DEFAULT_TOPIC),
        "presets": SEARCH_PRESETS,
        "curated": CURATED,
        "study_path": STUDY_PATH,
        "library_workflow": LIBRARY_WORKFLOW,
        "tool_lanes": TOOL_LANES,
        "sources": load_sources(),
        "zotero_tips": [
            "Install the Zotero Connector for Safari/Chrome — one-click save from ERIC, DOAJ, publisher pages.",
            "Create collections: Methods, Inclusion, GBL, Minecraft, Ethics.",
            "Import this desk’s RIS/BibTeX via File → Import (or Hazel-watch a folder Zotero imports from).",
            "Attach only PDFs you obtained legally (OA, uni licence, or ILL).",
            "Use Zotero notes for critique; keep this desk’s queue short (staging only).",
        ],
        "legal_note": (
            "This tool searches open-access records and links to legal portals only. "
            "It does not bypass paywalls or copy DRM/read-only books. "
            "Use your university library and interlibrary loan for licensed material."
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Research Desk — OA finder + Zotero export for M.Ed. research",
    )
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("search", help="Search OpenAlex for open-access works")
    sp.add_argument("query", nargs="?", default=DEFAULT_TOPIC)
    sp.add_argument("-n", "--per-page", type=int, default=10)
    sp.add_argument("--year-from", type=int, default=None)

    sub.add_parser("presets", help="List search presets")
    sub.add_parser("curated", help="List curated OA starting points")
    sub.add_parser("path", help="Show research-methods study path")
    sub.add_parser("workflow", help="Show library + Zotero workflow")
    sub.add_parser("lanes", help="Show Zotero / Calibre / Hazel lanes")
    sub.add_parser("portals", help="Print portal deep links for the default topic")

    lp = sub.add_parser("sources", help="List reading-queue sources")
    lp.add_argument("--json", action="store_true")

    ap = sub.add_parser("add", help="Add a source to the reading queue")
    ap.add_argument("--title", required=True)
    ap.add_argument("--authors", default="")
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--url", default="")
    ap.add_argument("--doi", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--tags", default="")

    dp = sub.add_parser("delete", help="Delete a source by id")
    dp.add_argument("id")

    ep = sub.add_parser("export", help="Export queue to RIS/BibTeX for Zotero")
    ep.add_argument("--format", choices=("ris", "bibtex"), default="ris")
    ep.add_argument("--stdout", action="store_true")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0

    if args.cmd == "search":
        result = search_openalex(args.query, per_page=args.per_page, year_from=args.year_from)
        if not result.get("ok"):
            print(result.get("error"), file=sys.stderr)
            return 1
        for i, item in enumerate(result["results"], 1):
            authors = ", ".join(item.get("authors") or [])[:80]
            print(f"{i}. {item['title']}")
            print(f"   {authors} ({item.get('year') or 'n.d.'}) · cited {item.get('cited_by')}")
            print(f"   OA: {item.get('oa_url') or item.get('landing_url')}")
            print()
        print(f"{result['count']} open-access hits for: {result['query']}")
        return 0

    if args.cmd == "presets":
        for preset in SEARCH_PRESETS:
            print(f"{preset['id']:16}  {preset['label']}")
            print(f"                  {preset['query']}")
        return 0

    if args.cmd == "curated":
        for item in CURATED:
            print(f"- {item['title']}")
            print(f"  {item['url']}")
            print(f"  {item['why']}")
            print()
        return 0

    if args.cmd == "path":
        for step in STUDY_PATH:
            print(f"Step {step['step']}: {step['title']}")
            print(f"  {step['focus']}")
            for action in step["do_next"]:
                print(f"  • {action}")
            print()
        return 0

    if args.cmd == "workflow":
        for row in LIBRARY_WORKFLOW:
            print(f"{row['phase']}")
            print(f"  {row['detail']}")
            print()
        return 0

    if args.cmd == "lanes":
        for row in TOOL_LANES:
            print(f"{row['tool']}")
            print(f"  Use for:  {row['use_for']}")
            print(f"  Not for:  {row['not_for']}")
            print()
        return 0

    if args.cmd == "portals":
        for link in portal_links(DEFAULT_TOPIC):
            print(f"{link['name']}: {link['url']}")
        return 0

    if args.cmd == "sources":
        sources = load_sources()
        if args.json:
            _print_json(sources)
        elif not sources:
            print("Reading queue is empty. Add keepers, then export to Zotero.")
        else:
            for src in sources:
                print(f"[{src.get('status')}] {src.get('id')} — {src.get('title')}")
        return 0

    if args.cmd == "add":
        result = add_source(
            {
                "title": args.title,
                "authors": args.authors,
                "year": args.year,
                "url": args.url,
                "oa_url": args.url,
                "doi": args.doi,
                "notes": args.notes,
                "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
                "origin": "cli",
            }
        )
        _print_json(result)
        return 0

    if args.cmd == "delete":
        result = delete_source(args.id)
        _print_json(result)
        return 0 if result.get("ok") else 1

    if args.cmd == "export":
        result = export_sources(args.format)
        if not result.get("ok"):
            print(result.get("error"), file=sys.stderr)
            return 1
        if args.stdout:
            print(result["text"], end="")
        else:
            print(f"Wrote {result['count']} items → {result['path']}")
            print("In Zotero: File → Import… and choose that file.")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
