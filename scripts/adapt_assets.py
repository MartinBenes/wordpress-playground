"""Rebase the official Vite output onto the GitHub Pages project directory."""
import json
import re
import sys
from pathlib import Path

BASE = "/wordpress-playground/"


def rebase_assets(directory):
    # Use only HTTP asset names present in this distribution. The same bundles
    # also contain paths in the virtual PHP filesystem, which must stay intact.
    names = {path.name for path in directory.iterdir() if not path.name.startswith(".")}
    names.update({"blueprints-index.json", "assets"})
    alternatives = "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))
    root_reference = re.compile(
        r"""(?P<quote>["'`(])/(?=(?:%s)(?:[/?"'`)#]|$))""" % alternatives
    )
    entrypoints = list(directory.glob("*.html")) + list(directory.glob("*.js"))
    for folder in ("assets", "builder", "client"):
        entrypoints.extend(
            path for path in (directory / folder).rglob("*")
            if path.suffix in {".js", ".css", ".html"}
        )
    for path in entrypoints:
        original = path.read_text(encoding="utf-8")
        content = original.replace("/dynamic-manifest.json.php", "/manifest.json")
        content = root_reference.sub(lambda match: match["quote"] + BASE, content)
        if path.suffix == ".html":
            content = content.replace('<base href="/">', f'<base href="{BASE}">')
        # Vite's module preloader adds the root to dependencies such as
        # "assets/main.css", separately from the literal import specifiers.
        if "modulepreload" in content:
            content = re.sub(
                r'(function\((\w+)\)\{return\s*)"/"\+\2\}',
                lambda match: match[1] + json.dumps(BASE) + "+" + match[2] + "}",
                content,
            )
        if content != original:
            path.write_text(content, encoding="utf-8")
    offline_index = directory / "assets-required-for-offline-mode.json"
    resources = json.loads(offline_index.read_text())
    resources = [BASE + url.lstrip("/")
                 for url in resources if not url.endswith(".php")]
    offline_index.write_text(json.dumps(resources, indent=2) + "\n")
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    builder = directory / "builder"
    if (builder / "builder.html").exists():
        # Upstream uses a PHP redirect for this route.
        (builder / "index.html").write_text(
            '<!doctype html><meta charset="utf-8"><title>Blueprint Builder</title>'
            '<meta http-equiv="refresh" content="0;url=builder.html">'
            '<a href="builder.html">Blueprint Builder</a>\n'
        )
    manifest.update(id=BASE, scope=BASE, start_url=BASE)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    rebase_assets(Path(sys.argv[1]))
