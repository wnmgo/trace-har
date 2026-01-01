from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from trace_har import __version__
from trace_har.source import TraceSource

TEXT_MIME_SUBSTRINGS = (
    "json",
    "javascript",
    "xml",
    "html",
    "x-www-form-urlencoded",
    "svg",
    "css",
)


def convert_trace_to_har(trace_path: Path) -> dict[str, Any]:
    with TraceSource.open(trace_path) as source:
        context_options = _load_context_options(source)
        entries = _iter_entries(source)
        pages = _build_pages(entries)

    log: dict[str, Any] = {
        "version": "1.2",
        "creator": {
            "name": "trace-har",
            "version": __version__,
        },
        "pages": pages,
        "entries": entries,
    }

    browser_name = context_options.get("browserName") or "unknown"
    browser_version = context_options.get("playwrightVersion") or ""
    log["browser"] = {"name": browser_name, "version": browser_version}

    return {"log": log}


def _load_context_options(source: TraceSource) -> dict[str, Any]:
    if not source.has_file("trace.trace"):
        return {}
    for line in source.iter_lines("trace.trace"):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("type") == "context-options":
            return payload
    return {}


def _iter_entries(source: TraceSource) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not source.has_file("trace.network"):
        return entries
    for line in source.iter_lines("trace.network"):
        if not line:
            continue
        payload = json.loads(line)
        if payload.get("type") != "resource-snapshot":
            continue
        entry = payload["snapshot"]
        _hydrate_request(entry, source)
        _hydrate_response(entry, source)
        entries.append(entry)
    return entries


def _hydrate_request(entry: dict[str, Any], source: TraceSource) -> None:
    request = entry.get("request", {})
    post_data = request.get("postData")
    if not post_data:
        return
    sha1 = post_data.get("_sha1")
    if not sha1:
        return
    data = source.read_bytes(f"resources/{sha1}")
    text, encoding = _decode_content_bytes(data, post_data.get("mimeType"))
    post_data["text"] = text
    if encoding:
        post_data["encoding"] = encoding
    post_data.pop("_sha1", None)


def _hydrate_response(entry: dict[str, Any], source: TraceSource) -> None:
    response = entry.get("response", {})
    content = response.get("content")
    if not content:
        return
    sha1 = content.get("_sha1")
    if not sha1:
        return
    data = source.read_bytes(f"resources/{sha1}")
    text, encoding = _decode_content_bytes(data, content.get("mimeType"))
    content["text"] = text
    if encoding:
        content["encoding"] = encoding
    content.pop("_sha1", None)


def _build_pages(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pages: dict[str, dict[str, Any]] = {}
    for entry in entries:
        pageref = entry.get("pageref")
        if not pageref:
            continue
        if pageref in pages:
            continue
        started = entry.get("startedDateTime")
        title = entry.get("request", {}).get("url", pageref)
        pages[pageref] = {
            "id": pageref,
            "title": title,
            "startedDateTime": started,
            "pageTimings": {"onContentLoad": -1, "onLoad": -1},
        }
    return list(pages.values())


def _decode_content_bytes(data: bytes, mime_type: str | None) -> tuple[str, str | None]:
    if _is_text_mime(mime_type):
        charset = _charset_from_mime(mime_type) or "utf-8"
        try:
            return data.decode(charset), None
        except UnicodeDecodeError:
            pass
    return base64.b64encode(data).decode("ascii"), "base64"


def _is_text_mime(mime_type: str | None) -> bool:
    if not mime_type:
        return False
    base = mime_type.split(";", 1)[0].strip().lower()
    if base.startswith("text/"):
        return True
    return any(token in base for token in TEXT_MIME_SUBSTRINGS)


def _charset_from_mime(mime_type: str | None) -> str | None:
    if not mime_type:
        return None
    parts = [part.strip() for part in mime_type.split(";")]
    for part in parts[1:]:
        if part.lower().startswith("charset="):
            return part.split("=", 1)[1].strip()
    return None
