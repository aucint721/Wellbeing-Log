#!/usr/bin/env python3
"""
Local file triage: gather, view, and decide.

This is the engine behind the File Triage UI / CLI. It never talks to iCloud
or a cloud API — you point it at a folder on this Mac and it inventories
files, finds likely duplicates, and applies keep / archive / delete moves
only after you confirm.

Decisions:
  critical   — small Current set on this Mac (not more iCloud)
  keep_local — the bulk of what you keep on the internal SSD
  archive    — old, might need someday (still on this Mac)
  delete     — move into a recoverable Triage Trash folder
  skip       — reviewed, leave in place for now
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

DECISIONS = ("critical", "keep_local", "archive", "delete", "skip")

SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".Trash",
    "Trash",
    "Caches",
    "Cache",
    ".cache",
}

TYPE_GROUPS = {
    "pdf": {".pdf"},
    "office": {
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".pages",
        ".numbers",
        ".key",
        ".odt",
        ".ods",
        ".odp",
    },
    "image": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".heic",
        ".heif",
        ".bmp",
        ".tif",
        ".tiff",
        ".raw",
        ".dng",
        ".svg",
    },
    "video": {".mov", ".mp4", ".m4v", ".avi", ".mkv", ".wmv", ".webm"},
    "audio": {".mp3", ".m4a", ".wav", ".aac", ".flac", ".aiff"},
    "archive": {".zip", ".dmg", ".pkg", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "ebook": {".epub", ".mobi", ".azw", ".azw3", ".fb2"},
    "text": {".txt", ".md", ".rtf", ".csv", ".json", ".yaml", ".yml", ".log"},
}

TEXT_PREVIEW_EXTS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
    ".log",
    ".py",
    ".html",
    ".css",
    ".js",
    ".xml",
    ".rtf",
}
IMAGE_PREVIEW_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
VIDEO_PREVIEW_EXTS = {".mov", ".mp4", ".m4v", ".webm"}
AUDIO_PREVIEW_EXTS = {".mp3", ".m4a", ".wav", ".aac", ".ogg"}

HASH_CHUNK = 1024 * 1024
PREVIEW_CHARS = 4000


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_id_for(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8", errors="replace")).hexdigest()[:16]


def type_group_for(ext: str) -> str:
    ext = (ext or "").lower()
    for group, exts in TYPE_GROUPS.items():
        if ext in exts:
            return group
    if ext:
        return "other"
    return "no_extension"


def format_bytes(n: int) -> str:
    n = max(0, int(n or 0))
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{n} B"


def default_destinations(home: Optional[Path] = None) -> dict[str, str]:
    """Local-first destinations. Nothing here points at iCloud on purpose."""
    home = home or Path.home()
    keep = home / "Documents-Local"
    return {
        "critical": str(home / "Current"),
        "keep_local": str(keep),
        "archive": str(home / "Archive"),
        "delete": str(keep / "_TriageTrash"),
    }


def suggested_scan_roots(home: Optional[Path] = None) -> list[dict[str, str]]:
    home = home or Path.home()
    candidates = [
        ("iCloud Drive", home / "Library" / "Mobile Documents" / "com~apple~CloudDocs"),
        ("Documents", home / "Documents"),
        ("Desktop", home / "Desktop"),
        ("Downloads", home / "Downloads"),
        ("Home", home),
    ]
    out = []
    for label, path in candidates:
        out.append(
            {
                "label": label,
                "path": str(path),
                "exists": path.exists(),
            }
        )
    return out


def _should_skip_dir(path: Path, skip_hidden: bool) -> bool:
    name = path.name
    if name in SKIP_DIR_NAMES:
        return True
    if skip_hidden and name.startswith(".") and name not in (".", ".."):
        return True
    return False


def _sha256_file(path: Path) -> Optional[str]:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(HASH_CHUNK)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _safe_dest(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    parent = dest.parent
    n = 2
    while True:
        candidate = parent / f"{stem} (triage {n}){suffix}"
        if not candidate.exists():
            return candidate
        n += 1


class TriageSession:
    def __init__(self) -> None:
        self.id = uuid.uuid4().hex[:12]
        self.created_at = _now_iso()
        self.updated_at = self.created_at
        self.root = ""
        self.destinations = default_destinations()
        self.files: dict[str, dict[str, Any]] = {}
        self.errors: list[str] = []
        self.scan_seconds = 0.0
        self.hashed_files = 0

    # --- scan -------------------------------------------------------------

    def scan(
        self,
        root: str,
        skip_hidden: bool = True,
        follow_symlinks: bool = False,
        progress: Optional[Callable[[dict[str, Any]], None]] = None,
    ) -> None:
        root_path = Path(root).expanduser().resolve()
        if not root_path.exists() or not root_path.is_dir():
            raise FileNotFoundError(f"Folder not found: {root_path}")

        self.root = str(root_path)
        self.files = {}
        self.errors = []
        self.hashed_files = 0
        started = time.time()
        visited = 0

        if progress:
            progress({"phase": "listing", "visited": 0, "root": self.root})

        for dirpath, dirnames, filenames in os.walk(root_path, followlinks=follow_symlinks):
            current = Path(dirpath)
            dirnames[:] = [
                name
                for name in dirnames
                if not _should_skip_dir(current / name, skip_hidden)
            ]
            dirnames.sort()
            for name in filenames:
                if skip_hidden and name.startswith("."):
                    continue
                visited += 1
                path = current / name
                if path.is_symlink() and not follow_symlinks:
                    continue
                try:
                    stat = path.stat()
                except OSError as exc:
                    self.errors.append(f"{path}: {exc}")
                    continue
                if not os.path.isfile(path):
                    continue
                rel = str(path.relative_to(root_path))
                ext = path.suffix.lower()
                fid = file_id_for(str(path))
                self.files[fid] = {
                    "id": fid,
                    "path": str(path),
                    "rel_path": rel,
                    "name": name,
                    "ext": ext,
                    "type_group": type_group_for(ext),
                    "size": int(stat.st_size),
                    "mtime": int(stat.st_mtime),
                    "parent": str(path.parent),
                    "sha256": None,
                    "dup_group": None,
                    "decision": None,
                    "decided_at": None,
                }
                if progress and visited % 200 == 0:
                    progress(
                        {
                            "phase": "listing",
                            "visited": visited,
                            "files": len(self.files),
                            "root": self.root,
                        }
                    )

        if progress:
            progress(
                {
                    "phase": "hashing",
                    "visited": visited,
                    "files": len(self.files),
                    "hashed": 0,
                    "to_hash": 0,
                    "root": self.root,
                }
            )
        self._detect_duplicates(progress)
        self.scan_seconds = round(time.time() - started, 2)
        self.updated_at = _now_iso()
        if progress:
            progress(
                {
                    "phase": "done",
                    "visited": visited,
                    "files": len(self.files),
                    "seconds": self.scan_seconds,
                    "root": self.root,
                }
            )

    def _detect_duplicates(self, progress: Optional[Callable[[dict[str, Any]], None]] = None) -> None:
        by_size: dict[int, list[str]] = defaultdict(list)
        for fid, rec in self.files.items():
            if rec["size"] > 0:
                by_size[rec["size"]].append(fid)

        candidates = [ids for ids in by_size.values() if len(ids) > 1]
        to_hash = [fid for group in candidates for fid in group]
        total = len(to_hash)
        if progress:
            progress(
                {
                    "phase": "hashing",
                    "hashed": 0,
                    "to_hash": total,
                    "files": len(self.files),
                }
            )

        for index, fid in enumerate(to_hash, start=1):
            rec = self.files[fid]
            rec["sha256"] = _sha256_file(Path(rec["path"]))
            self.hashed_files += 1
            if progress and (index == total or index % 25 == 0):
                progress(
                    {
                        "phase": "hashing",
                        "hashed": index,
                        "to_hash": total,
                        "files": len(self.files),
                    }
                )

        by_hash: dict[str, list[str]] = defaultdict(list)
        for fid, rec in self.files.items():
            digest = rec.get("sha256")
            if digest:
                by_hash[digest].append(fid)

        for digest, ids in by_hash.items():
            if len(ids) < 2:
                continue
            group_id = digest[:12]
            for fid in ids:
                self.files[fid]["dup_group"] = group_id

    # --- query ------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        total_size = sum(rec["size"] for rec in self.files.values())
        decided = [rec for rec in self.files.values() if rec.get("decision")]
        pending_apply = [
            rec
            for rec in decided
            if rec.get("decision") in ("critical", "keep_local", "archive", "delete")
        ]
        type_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "size": 0})
        for rec in self.files.values():
            group = rec.get("type_group") or "other"
            type_counts[group]["count"] += 1
            type_counts[group]["size"] += rec["size"]

        dup_groups = self.duplicate_groups()
        wasted = sum(group["wasted"] for group in dup_groups)

        decision_counts: dict[str, int] = {key: 0 for key in DECISIONS}
        decision_counts["undecided"] = 0
        for rec in self.files.values():
            key = rec.get("decision") or "undecided"
            decision_counts[key] = decision_counts.get(key, 0) + 1

        return {
            "id": self.id,
            "root": self.root,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "file_count": len(self.files),
            "total_size": total_size,
            "total_size_label": format_bytes(total_size),
            "scan_seconds": self.scan_seconds,
            "hashed_files": self.hashed_files,
            "error_count": len(self.errors),
            "errors": self.errors[:25],
            "folder_count": len({rec["parent"] for rec in self.files.values()}),
            "duplicate_groups": len(dup_groups),
            "duplicate_files": sum(len(group["files"]) for group in dup_groups),
            "duplicate_wasted": wasted,
            "duplicate_wasted_label": format_bytes(wasted),
            "decided_count": len(decided),
            "pending_apply": len(pending_apply),
            "undecided_count": decision_counts["undecided"],
            "decision_counts": decision_counts,
            "type_counts": dict(type_counts),
            "destinations": self.destinations,
            "top_folders": self.folder_rollups()[:15],
        }

    def folder_rollups(self) -> list[dict[str, Any]]:
        buckets: dict[str, dict[str, Any]] = {}
        root = Path(self.root) if self.root else None
        for rec in self.files.values():
            parent = Path(rec["parent"])
            try:
                rel = str(parent.relative_to(root)) if root else rec["parent"]
            except ValueError:
                rel = rec["parent"]
            if rel in (".", ""):
                rel = "(scan folder)"
            top = rel.split(os.sep, 1)[0]
            bucket = buckets.setdefault(
                top, {"folder": top, "count": 0, "size": 0, "undecided": 0}
            )
            bucket["count"] += 1
            bucket["size"] += rec["size"]
            if not rec.get("decision"):
                bucket["undecided"] += 1
        rows = list(buckets.values())
        rows.sort(key=lambda row: row["size"], reverse=True)
        for row in rows:
            row["size_label"] = format_bytes(row["size"])
        return rows

    def duplicate_groups(self) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for rec in self.files.values():
            group_id = rec.get("dup_group")
            if group_id:
                grouped[group_id].append(rec)
        out = []
        for group_id, items in grouped.items():
            items = sorted(items, key=lambda rec: rec["path"])
            size = items[0]["size"] if items else 0
            extra = max(0, len(items) - 1)
            out.append(
                {
                    "id": group_id,
                    "count": len(items),
                    "size": size,
                    "size_label": format_bytes(size),
                    "wasted": size * extra,
                    "wasted_label": format_bytes(size * extra),
                    "files": [
                        {
                            "id": rec["id"],
                            "name": rec["name"],
                            "path": rec["path"],
                            "rel_path": rec["rel_path"],
                            "mtime": rec["mtime"],
                            "decision": rec.get("decision"),
                        }
                        for rec in items
                    ],
                }
            )
        out.sort(key=lambda row: row["wasted"], reverse=True)
        return out

    def list_files(
        self,
        *,
        q: str = "",
        type_group: str = "",
        decision: str = "",
        folder: str = "",
        duplicates_only: bool = False,
        min_size: int = 0,
        older_than_days: int = 0,
        sort: str = "size",
        limit: int = 80,
        offset: int = 0,
    ) -> dict[str, Any]:
        q = (q or "").strip().lower()
        now = time.time()
        rows = []
        for rec in self.files.values():
            if type_group and rec.get("type_group") != type_group:
                continue
            if decision == "undecided":
                if rec.get("decision"):
                    continue
            elif decision and rec.get("decision") != decision:
                continue
            if folder:
                parent = rec.get("parent") or ""
                rel = rec.get("rel_path") or ""
                if folder not in parent and not rel.startswith(folder):
                    continue
            if duplicates_only and not rec.get("dup_group"):
                continue
            if rec["size"] < min_size:
                continue
            if older_than_days > 0:
                age_days = (now - rec["mtime"]) / 86400
                if age_days < older_than_days:
                    continue
            if q and q not in rec["name"].lower() and q not in rec["rel_path"].lower():
                continue
            rows.append(rec)

        reverse = True
        key = "size"
        if sort == "name":
            key, reverse = "name", False
        elif sort == "age":
            key = "mtime"
        elif sort == "recent":
            key, reverse = "mtime", True
        rows.sort(key=lambda rec: rec.get(key) or 0, reverse=reverse)

        total = len(rows)
        page = rows[offset : offset + limit]
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": [self._public_file(rec) for rec in page],
        }

    def get_file(self, fid: str) -> Optional[dict[str, Any]]:
        rec = self.files.get(fid)
        if not rec:
            return None
        return self._public_file(rec, detail=True)

    def _public_file(self, rec: dict[str, Any], detail: bool = False) -> dict[str, Any]:
        age_days = max(0, int((time.time() - rec["mtime"]) / 86400))
        out = {
            "id": rec["id"],
            "name": rec["name"],
            "path": rec["path"],
            "rel_path": rec["rel_path"],
            "parent": rec["parent"],
            "ext": rec["ext"],
            "type_group": rec["type_group"],
            "size": rec["size"],
            "size_label": format_bytes(rec["size"]),
            "mtime": rec["mtime"],
            "mtime_label": datetime.fromtimestamp(rec["mtime"]).strftime("%Y-%m-%d"),
            "age_days": age_days,
            "dup_group": rec.get("dup_group"),
            "decision": rec.get("decision"),
        }
        if detail:
            out["sha256"] = rec.get("sha256")
            out["preview"] = preview_for(Path(rec["path"]), rec["ext"])
        return out

    # --- decisions --------------------------------------------------------

    def set_destinations(self, destinations: dict[str, str]) -> None:
        merged = dict(self.destinations)
        for key in ("critical", "keep_local", "archive", "delete"):
            if key in destinations and destinations[key]:
                merged[key] = str(Path(destinations[key]).expanduser())
        self.destinations = merged
        self.updated_at = _now_iso()

    def decide(self, fid: str, decision: Optional[str]) -> dict[str, Any]:
        if fid not in self.files:
            raise KeyError(f"Unknown file: {fid}")
        if decision in ("", "none", None):
            self.files[fid]["decision"] = None
            self.files[fid]["decided_at"] = None
        else:
            if decision not in DECISIONS:
                raise ValueError(f"Unknown decision: {decision}")
            self.files[fid]["decision"] = decision
            self.files[fid]["decided_at"] = _now_iso()
        self.updated_at = _now_iso()
        return self._public_file(self.files[fid])

    def decide_many(self, ids: Iterable[str], decision: Optional[str]) -> int:
        count = 0
        for fid in ids:
            if fid in self.files:
                self.decide(fid, decision)
                count += 1
        return count

    def decide_folder(self, folder: str, decision: Optional[str]) -> int:
        ids = [
            fid
            for fid, rec in self.files.items()
            if rec["parent"] == folder
            or rec["rel_path"].startswith(folder.rstrip("/") + "/")
            or rec["parent"].endswith(os.sep + folder)
            or rec["rel_path"].split(os.sep, 1)[0] == folder
        ]
        return self.decide_many(ids, decision)

    def decide_duplicates(self, group_id: str, keep_id: str) -> int:
        group = [rec for rec in self.files.values() if rec.get("dup_group") == group_id]
        if not group:
            raise KeyError(f"Unknown duplicate group: {group_id}")
        count = 0
        for rec in group:
            if rec["id"] == keep_id:
                self.decide(rec["id"], "skip")
            else:
                self.decide(rec["id"], "delete")
            count += 1
        return count

    # --- apply ------------------------------------------------------------

    def planned_actions(self) -> list[dict[str, Any]]:
        actions = []
        for rec in self.files.values():
            decision = rec.get("decision")
            if decision not in ("critical", "keep_local", "archive", "delete"):
                continue
            dest_root = Path(self.destinations[decision]).expanduser()
            dest = _safe_dest(dest_root / rec["rel_path"])
            actions.append(
                {
                    "id": rec["id"],
                    "decision": decision,
                    "src": rec["path"],
                    "dest": str(dest),
                    "name": rec["name"],
                    "size": rec["size"],
                    "size_label": format_bytes(rec["size"]),
                }
            )
        actions.sort(key=lambda row: (row["decision"], row["src"]))
        return actions

    def apply(self, dry_run: bool = True) -> dict[str, Any]:
        actions = self.planned_actions()
        results = []
        moved = 0
        failed = 0
        for action in actions:
            src = Path(action["src"])
            dest = Path(action["dest"])
            entry = dict(action)
            if dry_run:
                entry["status"] = "planned"
                if not src.exists():
                    entry["status"] = "missing"
                results.append(entry)
                continue
            try:
                if not src.exists():
                    raise FileNotFoundError("file no longer exists")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest = _safe_dest(dest)
                if src.resolve() == dest.resolve():
                    entry["status"] = "skipped"
                    entry["error"] = "source and destination are the same"
                    results.append(entry)
                    continue
                shutil.move(str(src), str(dest))
                entry["dest"] = str(dest)
                entry["status"] = "moved"
                moved += 1
                # Drop from the live inventory so we do not apply twice
                self.files.pop(action["id"], None)
            except OSError as exc:
                entry["status"] = "error"
                entry["error"] = str(exc)
                failed += 1
            results.append(entry)
        self.updated_at = _now_iso()
        return {
            "dry_run": dry_run,
            "count": len(actions),
            "moved": moved,
            "failed": failed,
            "actions": results,
        }

    # --- persist ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "root": self.root,
            "destinations": self.destinations,
            "scan_seconds": self.scan_seconds,
            "hashed_files": self.hashed_files,
            "errors": self.errors,
            "files": list(self.files.values()),
        }

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)
        return path

    @classmethod
    def load(cls, path: str | Path) -> "TriageSession":
        with Path(path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        session = cls()
        session.id = data.get("id") or session.id
        session.created_at = data.get("created_at") or session.created_at
        session.updated_at = data.get("updated_at") or session.updated_at
        session.root = data.get("root") or ""
        session.destinations = data.get("destinations") or default_destinations()
        session.scan_seconds = data.get("scan_seconds") or 0
        session.hashed_files = data.get("hashed_files") or 0
        session.errors = data.get("errors") or []
        session.files = {rec["id"]: rec for rec in data.get("files") or []}
        return session


def preview_for(path: Path, ext: str) -> dict[str, Any]:
    ext = (ext or "").lower()
    preview = {"kind": "none", "text": "", "note": ""}
    if not path.exists():
        preview["note"] = "File is no longer on disk."
        return preview
    if ext in IMAGE_PREVIEW_EXTS:
        preview["kind"] = "image"
        return preview
    if ext in VIDEO_PREVIEW_EXTS:
        preview["kind"] = "video"
        preview["note"] = "Space for Quick Look."
        return preview
    if ext in AUDIO_PREVIEW_EXTS:
        preview["kind"] = "audio"
        preview["note"] = "Space for Quick Look."
        return preview
    if ext == ".pdf":
        text, note = _pdf_preview(path)
        preview["kind"] = "pdf"
        preview["text"] = text
        preview["note"] = note or "Space for Quick Look."
        return preview
    if ext in TEXT_PREVIEW_EXTS:
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            preview["note"] = str(exc)
            return preview
        preview["kind"] = "text"
        preview["text"] = raw[:PREVIEW_CHARS]
        if len(raw) > PREVIEW_CHARS:
            preview["note"] = f"Showing first {PREVIEW_CHARS:,} characters."
        return preview
    preview["note"] = f"No in-app preview for {ext or 'this file type'}. Space still shows name and path. Open it on your Mac if you need the real file."
    return preview


def _pdf_preview(path: Path) -> tuple[str, str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return "", "Install pypdf to preview PDF text (pip install pypdf)."
    try:
        reader = PdfReader(str(path))
        if getattr(reader, "is_encrypted", False):
            return "", "This PDF is password-protected."
        chunks = []
        for page in reader.pages[:4]:
            chunks.append(page.extract_text() or "")
        text = "\n".join(chunks).strip()
        if not text:
            return "", "No extractable text (likely a scan / image PDF)."
        return text[:PREVIEW_CHARS], f"{len(reader.pages)} page(s)."
    except Exception as exc:
        return "", f"Could not read PDF: {exc}"


def session_dir(root: Optional[Path] = None) -> Path:
    base = root or Path(__file__).resolve().parent
    path = base / "outputs" / "file_triage"
    path.mkdir(parents=True, exist_ok=True)
    return path


def cli(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gather, view, and decide what to do with local files (no iCloud API).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    scan = sub.add_parser("scan", help="Inventory a folder and write a session JSON")
    scan.add_argument("folder")
    scan.add_argument("-o", "--output", help="Session JSON path")
    scan.add_argument("--include-hidden", action="store_true")

    summary = sub.add_parser("summary", help="Print counts from a session JSON")
    summary.add_argument("session")

    dups = sub.add_parser("duplicates", help="List duplicate groups")
    dups.add_argument("session")

    apply_cmd = sub.add_parser("apply", help="Apply pending moves from a session JSON")
    apply_cmd.add_argument("session")
    apply_cmd.add_argument("--dry-run", action="store_true", default=True)
    apply_cmd.add_argument("--execute", action="store_true", help="Actually move files")

    args = parser.parse_args(argv)

    if args.cmd == "scan":

        def _progress(info: dict[str, Any]) -> None:
            phase = info.get("phase")
            if phase == "listing":
                print(f"\rListing… {info.get('files', 0)} files", end="", flush=True)
            elif phase == "hashing":
                print(
                    f"\rHashing likely duplicates… {info.get('hashed', 0)}/{info.get('to_hash', '?')}",
                    end="",
                    flush=True,
                )
            elif phase == "done":
                print(f"\nScan complete: {info.get('files')} files in {info.get('seconds')}s")

        session = TriageSession()
        session.scan(args.folder, skip_hidden=not args.include_hidden, progress=_progress)
        out = Path(args.output) if args.output else session_dir() / f"{session.id}.json"
        session.save(out)
        stats = session.summary()
        print(f"Session: {out}")
        print(f"Files:   {stats['file_count']}")
        print(f"Size:    {stats['total_size_label']}")
        print(f"Dups:    {stats['duplicate_groups']} groups, wasted {stats['duplicate_wasted_label']}")
        print("Open the UI with: python file_triage_ui.py")
        return 0

    if args.cmd == "summary":
        session = TriageSession.load(args.session)
        stats = session.summary()
        print(json.dumps(stats, indent=2))
        return 0

    if args.cmd == "duplicates":
        session = TriageSession.load(args.session)
        for group in session.duplicate_groups():
            print(f"{group['id']}  {group['count']} copies  wasted {group['wasted_label']}")
            for item in group["files"]:
                print(f"  {item['path']}")
        return 0

    if args.cmd == "apply":
        session = TriageSession.load(args.session)
        dry = not args.execute
        result = session.apply(dry_run=dry)
        print(json.dumps({k: result[k] for k in ("dry_run", "count", "moved", "failed")}, indent=2))
        if args.execute:
            session.save(args.session)
        else:
            print("This was a dry run. Pass --execute to move files.")
        return 0 if result["failed"] == 0 else 1

    return 1


if __name__ == "__main__":
    sys.exit(cli())
