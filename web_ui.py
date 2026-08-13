#!/usr/bin/env python3
"""
Web UI for AI Presentation Generator (Enhanced Designer)

Supports generation history, outline preview, and re-theming saved outlines
without calling the AI again.
"""

from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from presentation_generator import PresentationGenerator
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "outputs"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

generator = PresentationGenerator()


def _meta_path(presentation_id: str) -> str:
    return os.path.join(app.config["UPLOAD_FOLDER"], f"{presentation_id}.json")


def _save_meta(meta: dict) -> None:
    with open(_meta_path(meta["id"]), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def _load_meta(presentation_id: str):
    path = _meta_path(presentation_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _list_presentations(limit: int = 30):
    items = []
    folder = app.config["UPLOAD_FOLDER"]
    for name in os.listdir(folder):
        if not name.endswith(".json"):
            continue
        path = os.path.join(folder, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            pptx = meta.get("filename")
            if pptx and os.path.exists(os.path.join(folder, pptx)):
                items.append(
                    {
                        "id": meta["id"],
                        "title": meta.get("title", "Untitled"),
                        "theme": meta.get("theme"),
                        "theme_name": generator.themes.get(meta.get("theme"), {}).get(
                            "name", meta.get("theme")
                        ),
                        "model": meta.get("model"),
                        "num_slides": meta.get("num_slides"),
                        "created_at": meta.get("created_at"),
                        "filename": pptx,
                        "download_url": f"/download/{pptx}",
                    }
                )
        except Exception:
            continue

    items.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return items[:limit]


def _public_detail(meta: dict) -> dict:
    theme_key = meta.get("theme")
    return {
        "id": meta["id"],
        "title": meta.get("title", "Untitled"),
        "theme": theme_key,
        "theme_name": generator.themes.get(theme_key, {}).get("name", theme_key),
        "model": meta.get("model"),
        "num_slides": meta.get("num_slides"),
        "created_at": meta.get("created_at"),
        "filename": meta.get("filename"),
        "download_url": f"/download/{meta.get('filename')}",
        "outline": meta.get("outline", {}),
        "slide_transition": meta.get("slide_transition", "fade"),
        "bullet_animation": meta.get("bullet_animation", "appear"),
    }


@app.route("/")
def index():
    """Main page"""
    models = generator.list_models()
    themes = generator.themes
    defaults = generator.config.get("presentation", {})
    anim = generator.config.get("animations", {})
    return render_template(
        "index.html",
        models=models,
        themes=themes,
        default_model=defaults.get("default_model", "claude"),
        default_theme=defaults.get("default_theme", "sunset_gradient"),
        default_slides=defaults.get("default_slides", 10),
        default_slide_transition=defaults.get("default_slide_transition", "fade"),
        default_bullet_animation=defaults.get("default_bullet_animation", "appear"),
        slide_transitions=anim.get("slide_transitions", {}),
        bullet_animations=anim.get("bullet_animations", {}),
    )


@app.route("/api/models")
def get_models():
    """Get available models"""
    return jsonify(generator.list_models())


@app.route("/api/themes")
def get_themes():
    """Get available themes"""
    return jsonify(generator.list_themes())


@app.route("/theme_assets/<path:filename>")
def theme_assets(filename):
    """Serve photo theme preview/background images"""
    return send_from_directory("theme_assets", filename)


@app.route("/api/presentations")
def list_presentations():
    """List recently generated presentations"""
    return jsonify({"presentations": _list_presentations()})


@app.route("/api/presentations/<presentation_id>")
def get_presentation(presentation_id):
    """Get one presentation (outline preview + download info)"""
    safe_id = os.path.basename(presentation_id)
    meta = _load_meta(safe_id)
    if not meta:
        return jsonify({"error": "Presentation not found"}), 404
    return jsonify(_public_detail(meta))


@app.route("/api/presentations/<presentation_id>/retheme", methods=["POST"])
def retheme_presentation(presentation_id):
    """Rebuild PPTX from saved outline with a new theme (no AI call)."""
    try:
        safe_id = os.path.basename(presentation_id)
        meta = _load_meta(safe_id)
        if not meta:
            return jsonify({"error": "Presentation not found"}), 404

        data = request.json or {}
        theme = data.get("theme", meta.get("theme", "sunset_gradient"))
        if theme not in generator.themes:
            return jsonify({"error": f"Unknown theme: {theme}"}), 400

        outline = meta.get("outline")
        if not outline or not outline.get("slides"):
            return jsonify({"error": "Saved outline missing; regenerate from content"}), 400

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_id = uuid.uuid4().hex[:12]
        filename = f"presentation_{timestamp}_{new_id}.pptx"
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        slide_transition = data.get("slide_transition", meta.get("slide_transition", "fade"))
        bullet_animation = data.get("bullet_animation", meta.get("bullet_animation", "appear"))
        generator.create_presentation(
            outline,
            theme,
            output_path,
            slide_transition=slide_transition,
            bullet_animation=bullet_animation,
        )

        new_meta = {
            "id": new_id,
            "title": outline.get("title", meta.get("title", "Untitled")),
            "outline": outline,
            "theme": theme,
            "model": meta.get("model"),
            "num_slides": len(outline.get("slides", [])),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "filename": filename,
            "slide_transition": slide_transition,
            "bullet_animation": bullet_animation,
            "source_id": safe_id,
            "retheme_of": safe_id,
        }
        _save_meta(new_meta)

        return jsonify({"success": True, **_public_detail(new_meta)})
    except Exception as e:
        print(f"Retheme error: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def generate():
    """Generate presentation and save outline for later preview/re-theme"""
    try:
        data = request.json

        content = data.get("content", "").strip()
        model_key = data.get("model", "claude")
        num_slides = int(data.get("num_slides", 10))
        theme = data.get("theme", "sunset_gradient")
        slide_transition = data.get("slide_transition", "fade")
        bullet_animation = data.get("bullet_animation", "appear")

        if not content:
            return jsonify({"error": "No content provided"}), 400

        if num_slides < 5 or num_slides > 30:
            return jsonify({"error": "Number of slides must be between 5 and 30"}), 400

        if model_key not in generator.models:
            return jsonify({"error": f"Unknown model: {model_key}"}), 400

        if theme not in generator.themes:
            return jsonify({"error": f"Unknown theme: {theme}"}), 400

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        presentation_id = uuid.uuid4().hex[:12]
        filename = f"presentation_{timestamp}_{presentation_id}.pptx"
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Keep outline so we can preview and re-theme without another AI call
        outline = generator.generate_outline(content, model_key, num_slides)
        generator.create_presentation(
            outline,
            theme,
            output_path,
            slide_transition=slide_transition,
            bullet_animation=bullet_animation,
        )

        meta = {
            "id": presentation_id,
            "title": outline.get("title", "Untitled"),
            "outline": outline,
            "theme": theme,
            "model": model_key,
            "num_slides": len(outline.get("slides", [])),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "filename": filename,
            "slide_transition": slide_transition,
            "bullet_animation": bullet_animation,
            "content_preview": content[:500],
        }
        _save_meta(meta)

        return jsonify({"success": True, **_public_detail(meta)})

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download(filename):
    """Download generated presentation (browser-friendly attachment)."""
    safe_name = os.path.basename(filename)
    if not safe_name.endswith(".pptx"):
        return "File not found", 404
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_name,
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    return "File not found", 404


@app.route("/api/save-to-downloads/<filename>", methods=["POST"])
def save_to_downloads(filename):
    """Copy a generated PPTX into the user's Downloads folder (desktop/browser fallback)."""
    import shutil
    from pathlib import Path

    safe_name = os.path.basename(filename)
    if not safe_name.endswith(".pptx"):
        return jsonify({"ok": False, "error": "Only .pptx files can be saved"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    if not os.path.exists(file_path):
        return jsonify({"ok": False, "error": "File not found"}), 404

    downloads = Path.home() / "Downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    dest = downloads / safe_name
    shutil.copy2(file_path, dest)
    return jsonify({"ok": True, "path": str(dest)})


if __name__ == "__main__":
    # Default 5050 — macOS often reserves 5000 for AirPlay Receiver
    port = int(os.getenv("PORT", "5050"))

    print("\n" + "=" * 70)
    print("✨ AI Presentation Generator - Enhanced Designer Web UI")
    print("=" * 70)
    print(f"\nStarting server at http://localhost:{port}")
    print("Press Ctrl+C to stop\n")

    app.run(debug=True, host="0.0.0.0", port=port)
