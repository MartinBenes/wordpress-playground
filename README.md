# WordPress Playground pro výuku

[Spustit školní WordPress](https://benes.dev/wordpress-playground/?site-slug=skolni-web&language=cs_CZ&url=/wp-admin/) · [Otevřít výchozí Playground](https://benes.dev/wordpress-playground/)

GitHub Pages tohoto repozitáře servírují oficiální rozhraní WordPress Playground, PHP ve WebAssembly, WordPress a ovladač SQLite. Školní odkaz používá pojmenovaný web `skolni-web` v úložišti prohlížeče. Po prvním spuštění počkej, až horní lišta zobrazí **Saved**. Stejný odkaz pak ve stejném profilu prohlížeče znovu otevře tvůj web. Pro přesun na jiný počítač použij v panelu Playgroundu **Export** a stáhni ZIP.

## Volné plátno

[Otevřít editor webu s blokovou šablonou](https://benes.dev/wordpress-playground/platno/). První otevření vytvoří pojmenovaný web `volne-platno`, aktivuje šablonu a připraví prázdnou úvodní stránku. Stejný odkaz později otevře uloženou práci v daném profilu prohlížeče. V editoru lze měnit i záhlaví, navigaci, zápatí a styly. [Šablonu lze také stáhnout jako ZIP](https://benes.dev/wordpress-playground/platno/volne-platno.zip).

## Sestavení a nasazení

Základem je oficiální [sestavení pro vlastní hosting](https://github.com/WordPress/wordpress-playground/actions/runs/44362016932) z [revize 6ae629d](https://github.com/WordPress/wordpress-playground/tree/6ae629de715f159d8a00e95b6138d33406a45f7f). Původní archiv je uložený jako [vydání tohoto repozitáře](https://github.com/MartinBenes/wordpress-playground/releases/tag/upstream-6ae629d). Workflow ověřuje SHA-256, připraví adresář pro Pages a publikuje změny větve `main`.

`scripts/prepare.py` upraví adresy aplikace, cesty virtuálních webů, rozsah service workeru a úložiště pro projektovou cestu `/wordpress-playground/`. Zachovává dodávané verze WordPressu a PHP. Statické soubory jednotlivých verzí WordPressu se před prvním vykreslením rozbalí z oficiálních archivů přímo v prohlížeči.

Tato školní instance se používá v samostatné kartě. Vlastní konfiguraci z externího odkazu uživatel spouští kliknutím. Kód pluginů pracuje v kontextu domény `benes.dev`; používej vlastní výukové materiály a důvěryhodné pluginy. Aktivace doplňků z katalogu, překlady a galerie Blueprintů mohou využívat externí služby. GitHub Pages neposkytují PHP endpoint pro serverový GitHub OAuth.
