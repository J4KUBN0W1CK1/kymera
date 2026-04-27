# KYMERA — statický web

Originální industriální umělecká díla. Statický web, bez frameworku, bez build kroku. Připraveno pro **GitHub** a **Vercel**.

## Struktura

```
kymera/
├── index.html
├── style.css
├── script.js
├── README.md
└── assets/
    └── img/
        ├── hero.jpg                  # foto 1 – hlavní hero
        ├── collection-figurative.jpg # linie 01 – figurální
        ├── collection-busts.jpg      # linie 02 – hlavy a busty
        ├── collection-industrial.jpg # linie 03 – industriální obrazy
        ├── work-01.jpg               # vybraná díla (foto 2)
        ├── work-02.jpg               # foto 3 – hlava / dramatický detail
        ├── work-03.jpg
        ├── work-04.jpg
        └── about.jpg
```

## Co dosadit

1. **Fotky** do `assets/img/` (názvy přesně jak nahoře). Pokud fotku nedoplníš, web má stylový fallback a nerozsype se.
2. **Web3Forms access key** v `index.html` – řádek `<input type="hidden" name="access_key" value="YOUR_WEB3FORMS_ACCESS_KEY" />`. Klíč si vygeneruj na [web3forms.com](https://web3forms.com).
3. **E-mail** v `index.html` (sekce kontakt + footer): aktuálně `atelier@kymera.art`.

## Jazykové mutace (CZ / EN / PL)

V hlavičce je připravený přepínač CZ / EN / PL. Default je čeština. Pro EN a PL později založ:

```
/en/index.html
/pl/index.html
```

a přepínač nasměruj na `/`, `/en/`, `/pl/`. Žádný refactor není potřeba.

## Lokální spuštění

Stačí otevřít `index.html` v prohlížeči, nebo:

```bash
python3 -m http.server 8080
```

## Nasazení

### GitHub
```bash
git init
git add .
git commit -m "KYMERA — initial site"
git branch -M main
git remote add origin git@github.com:USER/kymera.git
git push -u origin main
```

### Vercel
1. Import projektu v dashboardu Vercel.
2. **Framework Preset: Other**, Build Command prázdné, Output Directory prázdné.
3. Deploy.

## Brand & design

- Paleta: grafit `#15140f`, slonová `#ece3cd`, mosaz `#c8a96a`.
- Typo: Cormorant Garamond (serif, nadpisy) + Inter (sans, UI).
- Tón: dark editorial luxury, galerie, klid, sebevědomí.
