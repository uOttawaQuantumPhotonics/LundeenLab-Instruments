#!/usr/bin/env python3
"""One-time maintainer tool: import original CERCuO Python files losslessly.

Usage:
    python scripts/import_cercuo.py --source ../Python
    python scripts/import_cercuo.py --download [--ref main]

This script imports only .py source from Core. It does not download manuals,
measurement data or vendor binaries. Source contents are copied verbatim.
It does not imply that redistribution rights have been granted.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import urllib.request
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEST = PROJECT_ROOT / "src" / "lundeen_instruments" / "legacy"
UPSTREAM = "https://github.com/CERCuO/Python"


def source_files(source: Path):
    """Yield relative paths and exact bytes of all Python files in Core."""
    # Allow passing either the repository root or its Core/ directory.
    core = source / "Core" if (source / "Core").is_dir() else source
    if not all((core / folder).is_dir() for folder in ("Dependencies", "Drivers", "Methods")):
        raise ValueError("Source must be the CERCuO/Python checkout (or its Core directory)")
    for f in sorted(core.rglob("*.py")):
        if not f.is_file():
            continue
        yield Path("Core") / f.relative_to(core), f.read_bytes()


def archive_files(ref: str):
    from urllib.parse import quote
    url = f"https://api.github.com/repos/CERCuO/Python/zipball/{quote(ref, safe='')}"
    req = urllib.request.Request(url, headers={"User-Agent": "LundeenLab-Instruments-import/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        zip_bytes = response.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for name in sorted(archive.namelist()):
            parts = PurePosixPath(name).parts
            if len(parts) < 3 or parts[1] != "Core" or not name.endswith(".py"):
                continue
            # Archive may contain nested paths; reject anything unexpected.
            if any(x in {"..", "."} for x in parts):
                raise ValueError(f"Unsafe archive path: {name}")
            relative = Path(*parts[1:])
            yield relative, archive.read(name)


def copy_sources(items, destination: Path, origin: str, overwrite: bool = False) -> int:
    items = list(items)
    if not items:
        raise ValueError("No CERCuO Python source files found")
    if not any(path.parts[:2] == ("Core", "Drivers") for path, _ in items):
        raise ValueError("No instrument drivers found: unexpected repository layout")
    destination.mkdir(parents=True, exist_ok=True)

    # Preflight: do not partially overwrite imported source without permission.
    for relative, content in items:
        path = destination / relative
        if path.exists() and path.read_bytes() != content and not overwrite:
            raise FileExistsError(f"{path} has different contents; pass --force to overwrite it")

    manifest = {"source": UPSTREAM, "revision": origin, "files": {}}
    for relative, content in items:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        manifest["files"][relative.as_posix()] = hashlib.sha256(content).hexdigest()

    # Packaging helpers are new files, not modifications to the originals.
    for path in [destination / "Core", *[p for p in (destination / "Core").iterdir() if p.is_dir()]]:
        init = path / "__init__.py"
        if not init.exists():
            init.write_text('"""Preserved CERCuO source. Do not edit without attribution."""\n', encoding="utf-8")
    (destination / "CERCUO_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return len(items)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", type=Path, help="local CERCuO/Python checkout or its Core folder")
    group.add_argument("--download", action="store_true", help="download an upstream archive from GitHub")
    parser.add_argument("--ref", default="main", help="CERCuO tag, branch or commit for --download")
    parser.add_argument("--destination", type=Path, default=DEFAULT_DEST, help=argparse.SUPPRESS)
    parser.add_argument("--force", action="store_true", help="overwrite previously imported files")
    args = parser.parse_args()
    if args.download:
        items = archive_files(args.ref)
        origin = f"{UPSTREAM}/tree/{args.ref}"
    else:
        if not args.source.is_dir():
            parser.error(f"Source folder not found: {args.source}")
        items = source_files(args.source)
        origin = str(args.source.resolve())
    try:
        count = copy_sources(items, args.destination, origin, overwrite=args.force)
    except (FileExistsError, ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Imported {count} CERCuO Python source files unchanged into {args.destination}")
    print("Read docs/provenance.md; obtain redistribution authorization before committing publicly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
