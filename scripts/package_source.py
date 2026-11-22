#!/usr/bin/env python3
"""Create deterministic source archives for MarketCouncil's final snapshot."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import stat
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT.parent
ARCHIVE_BASE = "MarketCouncil-1.0.0-FINAL"
EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "venv",
    "build",
    "dist",
}
EXCLUDED_LOCAL_DATA_DIRS = {"data", "var", "reports"}
EXCLUDED_FILES = {".DS_Store", "Thumbs.db"}


def is_sensitive_source_path(path: Path) -> bool:
    """Identify local secrets, databases, and user data that never belong in releases."""
    rel = path.relative_to(ROOT)
    if any(part.lower() in EXCLUDED_LOCAL_DATA_DIRS for part in rel.parts[:-1]):
        return True

    name = path.name.lower()
    if name.endswith(".env.example"):
        return False
    if name in {".env", ".envrc", "id_rsa", "id_ed25519"}:
        return True
    if name.startswith(".env.") or name.endswith(".env"):
        return True
    if Path(name).suffix.lower() in {".pem", ".p12", ".pfx", ".key"}:
        return True
    return any(
        name.endswith(suffix)
        for suffix in (
            ".sqlite", ".sqlite3", ".sqlite-wal", ".sqlite-shm", ".sqlite-journal",
            ".db", ".db-wal", ".db-shm", ".db-journal",
        )
    )


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in rel.parts):
        return False
    if path.name in EXCLUDED_FILES or path.name.endswith((".pyc", ".pyo", ".log")):
        return False
    if path.name.endswith(".egg-info"):
        return False
    if is_sensitive_source_path(path):
        return False
    if path.is_symlink() or not path.is_file():
        return False
    return True

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = sorted((path for path in ROOT.rglob("*") if include(path)), key=lambda p: p.as_posix())
    zip_path = output_dir / f"{ARCHIVE_BASE}.zip"
    tar_path = output_dir / f"{ARCHIVE_BASE}.tar.gz"

    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in files:
            info = zipfile.ZipInfo(
                (Path(ROOT.name) / path.relative_to(ROOT)).as_posix(),
                date_time=(2020, 1, 1, 0, 0, 0),
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    # Normalise tar metadata and gzip headers so identical source bytes produce
    # identical archive bytes across runs on the same Python/zlib toolchain.
    with tar_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_output, mtime=0, compresslevel=9) as gz_output:
            with tarfile.open(fileobj=gz_output, mode="w") as archive:
                for path in files:
                    name = (Path(ROOT.name) / path.relative_to(ROOT)).as_posix()
                    content = path.read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size = len(content)
                    info.mode = 0o644
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    archive.addfile(info, io.BytesIO(content))

    wheel = output_dir / "marketcouncil-1.0.0-py3-none-any.whl"
    artifacts = [zip_path, tar_path]
    if wheel.is_file():
        artifacts.append(wheel)

    sums_path = output_dir / "MarketCouncil-1.0.0-SHA256SUMS.txt"
    sums_path.write_text(
        "".join(f"{sha256(artifact)}  {artifact.name}\n" for artifact in artifacts),
        encoding="utf-8",
    )
    return artifacts + [sums_path]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"artifact destination (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()
    created = build(args.output_dir.resolve())
    for path in created:
        print(f"{path}  {path.stat().st_size:,} bytes")
    print(f"Source files packaged: {sum(1 for p in ROOT.rglob('*') if include(p))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
