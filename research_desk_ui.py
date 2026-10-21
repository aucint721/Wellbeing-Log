#!/usr/bin/env python3
"""
Research Desk web UI.

Default bind is 127.0.0.1:5053. Override with RESEARCH_HOST / RESEARCH_PORT / PORT.
Open-access finder + reading queue + library workflow — no paywall bypass.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, Response, jsonify, render_template, request

from research_desk import (
    DEFAULT_TOPIC,
    LIBRARY_WORKFLOW,
    STUDY_PATH,
    TOOL_LANES,
    add_source,
    bootstrap_payload,
    delete_source,
    export_sources,
    filter_curated,
    load_sources,
    portal_links,
    search_openalex,
    update_source,
)

app = Flask(__name__, template_folder=str(ROOT / "templates"))


@app.get("/")
def home():
    return render_template("research_desk.html")


@app.get("/api/bootstrap")
def bootstrap():
    return jsonify(bootstrap_payload())


@app.get("/api/curated")
def curated_api():
    return jsonify(
        {
            "curated": filter_curated(
                request.args.get("tag"),
                request.args.get("q"),
            )
        }
    )


@app.get("/api/portals")
def portals_api():
    q = request.args.get("q", DEFAULT_TOPIC)
    return jsonify({"query": q, "portals": portal_links(q)})


@app.get("/api/path")
def path_api():
    return jsonify({"topic": DEFAULT_TOPIC, "study_path": STUDY_PATH})


@app.get("/api/workflow")
def workflow_api():
    return jsonify({"library_workflow": LIBRARY_WORKFLOW, "tool_lanes": TOOL_LANES})


@app.get("/api/search")
def search_api():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"ok": False, "error": "Query is required.", "results": []}), 400
    try:
        # UI uses per_page; CLI-style clients may send n=
        per_page = int(request.args.get("per_page") or request.args.get("n") or 12)
        year_raw = request.args.get("year_from")
        year_from = int(year_raw) if year_raw else None
        payload = search_openalex(query, per_page=per_page, year_from=year_from)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc), "results": []}), 502
    if not payload.get("ok"):
        return jsonify(payload), 502
    payload["portals"] = portal_links(query)
    return jsonify(payload)


@app.get("/api/sources")
def sources_list():
    status = request.args.get("status", "")
    rows = load_sources()
    if status:
        rows = [r for r in rows if r.get("status") == status]
    return jsonify({"sources": rows})


@app.post("/api/sources")
def sources_add():
    data = request.get_json(silent=True) or {}
    try:
        result = add_source(data)
    except (TypeError, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(result)


@app.patch("/api/sources/<source_id>")
@app.post("/api/sources/<source_id>")
def sources_update(source_id: str):
    data = request.get_json(silent=True) or {}
    result = update_source(source_id, data)
    if not result.get("ok"):
        return jsonify(result), 404
    return jsonify(result)


@app.delete("/api/sources/<source_id>")
@app.post("/api/sources/<source_id>/delete")
def sources_delete(source_id: str):
    result = delete_source(source_id)
    if not result.get("ok"):
        return jsonify(result), 404
    return jsonify(result)


@app.get("/api/export")
@app.post("/api/export")
def export_api():
    data = request.get_json(silent=True) or {}
    fmt = request.args.get("format") or data.get("format") or "ris"
    ids = data.get("ids")
    result = export_sources(fmt, ids)
    if not result.get("ok"):
        return jsonify(result), 400
    download = request.args.get("download") or data.get("download")
    if download:
        return Response(
            result["text"],
            mimetype=result["mime"],
            headers={
                "Content-Disposition": f'attachment; filename="{result["filename"]}"',
            },
        )
    return jsonify(result)


def main() -> None:
    host = os.getenv("RESEARCH_HOST", "127.0.0.1")
    port = int(os.getenv("RESEARCH_PORT") or os.getenv("PORT") or 5053)
    print("=" * 60)
    print("Research Desk — OA finder · sources · library workflow")
    print("=" * 60)
    print(f"Open: http://{host}:{port}")
    print(f"Topic: {DEFAULT_TOPIC}")
    print("Legal OA + uni library / ILL only. No paywall bypass.")
    print("=" * 60)
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
