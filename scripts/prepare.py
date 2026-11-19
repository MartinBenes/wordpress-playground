"""Build the static GitHub Pages directory from the unmodified official build."""
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile
from adapt_assets import BASE, rebase_assets
from prepare_assets import prepare
from protect_entries import protect

scripts = Path(__file__).resolve().parent
source, target = map(Path, sys.argv[1:])
prepare(source, target)
subprocess.run([sys.executable, scripts / "patch_runtime.py", target], check=True)
rebase_assets(target)
# GitHub Pages only serves files. Exclude the upstream host's PHP endpoints.
for path in list(target.glob("*.php")) + list((target / "builder").glob("*.php")):
    path.unlink()
(target / ".htaccess").unlink(missing_ok=True)
protect(target, BASE)
shutil.copyfile(scripts.parent / "LICENSE", target / "LICENSE")
# Publish the opt-in starter separately from the upstream Playground shell.
starter = target / "platno"
shutil.copytree(scripts.parent / "starter", starter)
theme = scripts.parent / "themes" / "volne-platno"
with ZipFile(starter / "volne-platno.zip", "w", compression=ZIP_DEFLATED) as archive:
    for path in sorted(theme.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(theme.parent))
(target / ".nojekyll").touch()
