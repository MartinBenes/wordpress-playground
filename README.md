# WordPress Playground pro výuku

[Spustit školní WordPress](https://benes.dev/wordpress-playground/?site-slug=skolni-web) · [Otevřít výchozí Playground](https://benes.dev/wordpress-playground/)

GitHub Pages tohoto repozitáře servírují oficiální rozhraní WordPress Playground, PHP ve WebAssembly, WordPress a ovladač SQLite. Školní odkaz používá pojmenovaný web `skolni-web` v úložišti prohlížeče. Každý student pracuje ve vlastním profilu. Pro přesun na jiný počítač použij v panelu Playgroundu **Export** a stáhni ZIP.

## Sestavení a nasazení

Základem je oficiální [sestavení pro vlastní hosting](https://github.com/WordPress/wordpress-playground/actions/runs/44362016932) z [revize 6ae629d](https://github.com/WordPress/wordpress-playground/tree/6ae629de715f159d8a00e95b6138d33406a45f7f). Původní archiv je uložený jako [vydání tohoto repozitáře](https://github.com/MartinBenes/wordpress-playground/releases/tag/upstream-6ae629d). Workflow ověřuje SHA-256, připraví adresář pro Pages a publikuje změny větve `main`.

`scripts/prepare.py` upraví adresy aplikace, cesty virtuálních webů, rozsah service workeru a úložiště pro projektovou cestu `/wordpress-playground/`. Zachovává dodávané verze WordPressu a PHP. Statické soubory jednotlivých verzí WordPressu se před prvním vykreslením rozbalí z oficiálních archivů přímo v prohlížeči.

Tato školní instance se používá v samostatné kartě. Vlastní konfiguraci z externího odkazu uživatel spouští kliknutím. Kód pluginů pracuje v kontextu domény `benes.dev`; používej vlastní výukové materiály a důvěryhodné pluginy. Aktivace doplňků z katalogu, překlady a galerie Blueprintů mohou využívat externí služby. GitHub Pages neposkytují PHP endpoint pro serverový GitHub OAuth.
