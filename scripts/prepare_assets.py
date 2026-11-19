#!/usr/bin/env python3
"""Copy a pinned, unpacked Playground web distribution for GitHub Pages.

The browser runtime must await Playground's own static-asset backfill at
startup. That installs each selected version's complete wordpress-static.zip.
Its unpacked duplicates under wp-*/ are therefore unnecessary to publish.
"""
import argparse
import os
from pathlib import Path
import re
import shutil
import zipfile
import zlib

WP_RELEASE = re.compile(r"wp-(?:\d+\.\d+|nightly|trunk|beta)")
STATIC_DIRS = {"wp-admin", "wp-includes", "wp-content"}
PAGES_LIMIT = 1_000_000_000

def prepare(source, destination):
    if not (source / "index.html").is_file() or not (source / "remote.html").is_file():
        raise SystemExit("The source directory must contain the unpacked upstream Playground distribution.")
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit("Choose an empty output directory to preserve any existing work.")
    source = source.resolve()
    destination = destination.resolve()
    if destination == source or source in destination.parents:
        raise SystemExit("Choose an output directory outside the source distribution.")
    destination.mkdir(parents=True, exist_ok=True)

    retained = 0
    files = 0
    versions = {}
    omitted = 0
    for directory, dirs, names in os.walk(source):
        directory = Path(directory)
        relative = directory.relative_to(source)
        if len(relative.parts) == 1 and WP_RELEASE.fullmatch(relative.name):
            static_dirs = [d for d in dirs if d in STATIC_DIRS]
            if static_dirs:
                archive = directory / "wordpress-static.zip"
                with zipfile.ZipFile(archive) as zipped:
                    versions[relative.name] = {i.filename.removeprefix("./"): i for i in zipped.infolist()}
        target_dir = destination / relative
        for name in names:
            item = directory / name
            # Certain legacy/nightly asset trees include additional theme and
            # admin files. Preserve those, plus any file differing from its ZIP.
            if len(relative.parts) >= 2 and relative.parts[0] in versions and relative.parts[1] in STATIC_DIRS:
                entry = versions[relative.parts[0]].get((Path(*relative.parts[1:]) / name).as_posix())
                if entry is not None and entry.file_size == item.stat().st_size and entry.CRC == zlib.crc32(item.read_bytes()):
                    omitted += 1
                    continue
            target_dir.mkdir(exist_ok=True, parents=True)
            if item.is_symlink():
                raise SystemExit(f"Unexpected symlink in upstream distribution: {item}")
            shutil.copy2(item, target_dir / name)
            retained += item.stat().st_size
            files += 1
    if not omitted:
        raise SystemExit("No duplicated release asset directories were found.")
    print(f"{files} files with {retained:,} bytes. Omitted {omitted} duplicate files. Kept full static ZIPs for {', '.join(sorted(versions))}.")
    if retained > PAGES_LIMIT:
        raise SystemExit(f"Site exceeds the {PAGES_LIMIT:,} byte budget.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    prepare(args.source, args.destination)
