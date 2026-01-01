from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class TraceSource:
    root: Path
    archive: zipfile.ZipFile | None = None

    @classmethod
    def open(cls, path: Path) -> "TraceSource":
        if path.is_dir():
            return cls(root=path)
        if path.is_file() and path.suffix == ".zip":
            return cls(root=path, archive=zipfile.ZipFile(path))
        raise ValueError(f"Unsupported trace path: {path}")

    def close(self) -> None:
        if self.archive:
            self.archive.close()
            self.archive = None

    def __enter__(self) -> "TraceSource":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def has_file(self, relative: str) -> bool:
        if self.archive:
            try:
                self.archive.getinfo(relative)
            except KeyError:
                return False
            return True
        return (self.root / relative).exists()

    def read_text(self, relative: str) -> str:
        if self.archive:
            return self.archive.read(relative).decode("utf-8")
        return (self.root / relative).read_text(encoding="utf-8")

    def read_bytes(self, relative: str) -> bytes:
        if self.archive:
            return self.archive.read(relative)
        return (self.root / relative).read_bytes()

    def iter_lines(self, relative: str) -> Iterator[str]:
        if self.archive:
            data = self.archive.read(relative).decode("utf-8").splitlines()
            for line in data:
                yield line
            return
        with (self.root / relative).open("r", encoding="utf-8") as handle:
            for line in handle:
                yield line.rstrip("\n")
