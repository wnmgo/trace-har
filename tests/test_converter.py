from __future__ import annotations

import base64
import zipfile
from pathlib import Path

import pytest

from trace_har.converter import convert_trace_to_har


@pytest.fixture()
def sample_trace_dir() -> Path:
    return Path("tests/fixtures/sample_trace")


def test_convert_trace_directory(sample_trace_dir: Path) -> None:
    har = convert_trace_to_har(sample_trace_dir)
    log = har["log"]

    assert log["creator"]["name"] == "trace-har"
    assert log["browser"]["name"] == "chromium"
    assert len(log["pages"]) == 1
    assert log["pages"][0]["id"] == "page@1"

    entries = log["entries"]
    assert len(entries) == 2

    first = entries[0]
    assert first["request"]["postData"]["text"].strip() == '{"hello":"world"}'
    assert "_sha1" not in first["request"]["postData"]

    content = first["response"]["content"]
    assert content["text"].strip() == '{"ok":true}'
    assert "encoding" not in content
    assert "_sha1" not in content

    second = entries[1]
    binary = second["response"]["content"]
    expected = base64.b64encode(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x00").decode("ascii")
    assert binary["encoding"] == "base64"
    assert binary["text"] == expected


def test_convert_trace_zip(sample_trace_dir: Path, tmp_path: Path) -> None:
    zip_path = tmp_path / "trace.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in sample_trace_dir.rglob("*"):
            archive.write(path, path.relative_to(sample_trace_dir))

    har = convert_trace_to_har(zip_path)
    assert len(har["log"]["entries"]) == 2
