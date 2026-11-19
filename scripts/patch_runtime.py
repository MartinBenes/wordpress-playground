"""Adapt the official portable Playground release to its GitHub Pages project URL.

Run against an unpacked, pinned upstream build. Its PHP filesystem continues to
use ordinary WordPress paths. The project prefix applies to browser URLs only.
"""
import argparse
import re
from pathlib import Path


def patch_js(code, base):
    # Scopes normally occupy the first URL path component. Pages adds one.
    scope = base + '/scope:'
    base_in_regex = base.replace('/', r'\/')
    offset = base.count('/') + 1
    code = code.replace('pathname.startsWith("/scope:")', f'pathname.startsWith("{scope}")')
    code = code.replace('pathname.split("/")[1].split(":")[1]',
                        f'pathname.split("/")[{offset}].split(":")[1]')
    code = re.sub(r'(\.pathname\.split\("/"\);)([\w$]+)\[1\](=\s*`scope:)',
                  lambda m: f'{m[1]}{m[2]}[{offset}]{m[3]}', code)
    code = code.replace('pathname=`/scope:', f'pathname=`{scope}')
    # removeURLScope() intentionally returns the PHP-relative pathname.
    code = re.sub(r'(\.pathname\.split\("/"\);return [\w$]+\.pathname="/"\+[\w$]+\.slice\()2(\)\.join\("/"\))',
                  lambda m: f'{m[1]}{offset+1}{m[2]}', code)
    # Accommodate urls already beginning with the project path, such as the
    # shell URL when transferring a scoped request to a different runtime.
    code = re.sub(r'(const ([\w$]+)=([\w$]+)\.pathname)==="/"\?"":\3\.pathname;\3\.pathname=`' + re.escape(scope),
                  lambda m: f'const {m[2]}={m[3]}.pathname==="/"?"":{m[3]}.pathname.replace(/^{base_in_regex}(?=\\/|$)/,"");{m[3]}.pathname=`{scope}', code)
    # A scoped service worker still sees subresources initiated by its clients
    # outside the project. Leave those responses to the owning site.
    code = re.sub(r'(function [\w$]+\(([\w$]+)\)\{return )(self\.location\.origin!==[\w$]+\?!1:\2\.href\.includes\("wordpress-static\.zip"\))',
                  lambda m: m[1] + f'!{m[2]}.pathname.startsWith("{base}/")?!1:' + m[3], code)
    if 'self.clients.claim()' in code:
        # The manifest lists shell assets relative to the website and adds the
        # homepage separately. Cache the project's own homepage for offline use.
        code = re.sub(r'\["/",(\.\.\.await\(await [\w$]+\("[^"]*assets-required-for-offline-mode\.json"\)\)\.json\(\)\])',
                      lambda m: f'["{base}/",' + m[1], code)
        # Gutenberg's document iframe must navigate inside this Playground's
        # service worker scope, including the active WordPress site identifier.
        code = code.replace("'/wp-includes/empty.html' +",
                            f"location.pathname.split('/').slice(0,{offset+1}).join('/') + '/wp-includes/empty.html' +", 1) if "const emptyHtmlUrl =\n\t\t\t'/wp-includes/empty.html'" in code else code
        # The network-first shell route is the project directory.
        code = re.sub(r'((?P<u>[\w$]+)\.pathname==="[^"]*api.html"\|\|(?P=u)\.pathname===)"/"',
                      lambda m: m[1] + f'"{base}/"', code)
    # Embedded PHP/JS helpers use these explicit patterns when resolving a
    # scoped URL back into the virtual filesystem and importing a backup.
    code = code.replace("'#^/scope:[^/]+#'", f"'#^(?:{base})?/scope:[^/]+#'")
    code = code.replace(r'.match(/\/scope:[^/]+\/?/)', '.match(/(?:' + base_in_regex + r')?\/scope:[^/]+\/?/)')
    # Both the service worker and its PHP-injected thumbnail bridge validate
    # the renderer path. The embedded script's slash escapes are doubled.
    for separator in (r'\/', r'\\/'):
        renderer_start = '/^' + separator + 'capture-site-thumbnail-'
        project_renderer = '/^' + base.replace('/', separator) + separator + 'capture-site-thumbnail-'
        code = code.replace(renderer_start, project_renderer)
    # This constant feeds the static archive and manifest URL builders.
    code = code.replace('releaseBase="/"', f'releaseBase="{base}/"')
    # The portable layout has no /releases/<id>/ and no root-host bridge.
    # Minified copies may use short identifiers for these configuration fields.
    code = re.sub(r'(new URL\("/",\(import\.meta\|\|\{\}\)\.url\),[\w$]+=[\w$]+\.origin,)([\w$]+)="/",([\w$]+)=\2!=="/"',
                  lambda m: f'{m[1]}{m[2]}="{base}/",{m[3]}=false', code)
    project = base.strip('/').replace('/', '-')
    # Cache maintenance must target this project's own namespace.
    code = code.replace('"playground-cache"', '"github-pages-' + project + '-playground-cache"')
    # Scope all upstream uses of the origin-private filesystem to a site-owned
    # directory, including metadata and the dedicated worker mount.
    code = re.sub(r'navigator\.storage\.getDirectory\(\)(?!\.then\(root=>root\.getDirectoryHandle\()',
                        'navigator.storage.getDirectory().then(root=>root.getDirectoryHandle("' + project + '",{create:true}))', code)
    # The full static tree is already included in each upstream archive. Load
    # that archive before exposing the API as ready, including on a cold cache.
    delayed = re.compile(r'([\w$]+)&&\(await ([\w$]+)\.hasCachedStaticFilesRemovedFromMinifiedBuild\(\)\?await \2\.backfillStaticFilesRemovedFromMinifiedBuild\(\):[\w$]+\.addEventListener\("load",\(\)=>\{\2\.backfillStaticFilesRemovedFromMinifiedBuild\(\)\}\)\)')
    pending = delayed.search(code)
    if pending:
        guard, api = pending.group(1, 2)
        code = code[:pending.start()] + code[pending.end():]
        ready = re.compile(r'(await [\w$]+\.isReady\(\),)')
        if len(ready.findall(code)) != 1:
            raise ValueError("Unexpected upstream readiness sequence")
        code = ready.sub(lambda m: m[1] + f'{guard}&&await {api}.backfillStaticFilesRemovedFromMinifiedBuild(),', code)
    return code

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    parser.add_argument('--base', default='/wordpress-playground')
    args = parser.parse_args()
    base = '/' + args.base.strip('/')
    if not re.fullmatch(r'/[\w-]+(?:/[\w-]+)*', base):
        parser.error('Invalid project base path')
    changed = []
    for folder in [args.site, args.site/'assets', args.site/'client']:
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob('*.js')):
            before = path.read_text()
            after = patch_js(before, base)
            if before != after:
                path.write_text(after)
                changed.append(str(path.relative_to(args.site)))
    print(f'Adapted {len(changed)} runtime modules')
if __name__ == '__main__':
    main()
