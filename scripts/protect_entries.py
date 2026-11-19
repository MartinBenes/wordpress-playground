"""Wrap the upstream Playground entry documents after project-path rewrites."""
import argparse
import base64
import html
from pathlib import Path
import re
import shutil

MARKER = 'data-playground-entry="'
ENGINE_DIR = re.compile(r"wp-(?:\d+\.\d+|beta|nightly|trunk)$")

def protect(root, base):
    if not re.fullmatch(r"/(?:[\w-]+/)*", base):
        raise ValueError("base must be an absolute directory, such as /wordpress-playground/")
    if not (root / "index.html").is_file() or not (root / "remote.html").is_file():
        raise ValueError("Expected upstream index.html and remote.html")
    gate = Path(__file__).with_name("entry-gate.js")
    shutil.copyfile(gate, root / gate.name)
    for entry in sorted(root.rglob("*.html")):
        relative = entry.relative_to(root)
        # WordPress themes and block templates are data loaded by the engine.
        if any(ENGINE_DIR.fullmatch(part) for part in relative.parts[:-1]):
            continue
        content = entry.read_bytes()
        name = entry.name
        role = "page"
        if (name == "api.html" or name == "remote.html" or
                name.startswith("remote-") or name.startswith("wordpress-bridge")):
            role = "frame"
        elif name == "playground-block-frame.html":
            role = "block"
        elif name == "wordpress-popup.html":
            role = "popup"
        if MARKER.encode() in content:
            refreshed = re.sub(rb'data-playground-entry="[^"]+"',
                               f'data-playground-entry="{role}"'.encode(), content, count=1)
            if refreshed != content:
                entry.write_bytes(refreshed)
            continue
        source = base64.b64encode(content).decode("ascii")
        # Keep app markup inert until the checks have succeeded. Network errors
        # loading entry-gate.js must also leave the original code inactive.
        entry.write_text(f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WordPress Playground</title>
<script src="{base}entry-gate.js" defer></script></head>
<body data-playground-entry="{role}" data-base="{base}">
<main hidden><h1>WordPress Playground</h1><p></p>
<button type="button" hidden>Spustit nastavení z odkazu</button>
<a href="{html.escape(base)}" target="_blank" rel="noopener noreferrer">Otevřít čistý Playground</a></main>
<noscript>Pro spuštění Playgroundu zapni JavaScript.</noscript>
<script type="application/octet-stream" id="original-entry">{source}</script>
</body></html>''', encoding="utf-8")
        print(relative)

if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("directory", type=Path)
    cli.add_argument("base")
    args = cli.parse_args()
    protect(args.directory, args.base)
