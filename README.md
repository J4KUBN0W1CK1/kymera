<div align="center">

<br>

```
  ██╗  ██╗██╗   ██╗███╗   ███╗███████╗██████╗  █████╗
  ██║ ██╔╝╚██╗ ██╔╝████╗ ████║██╔════╝██╔══██╗██╔══██╗
  █████╔╝  ╚████╔╝ ██╔████╔██║█████╗  ██████╔╝███████║
  ██╔═██╗   ╚██╔╝  ██║╚██╔╝██║██╔══╝  ██╔══██╗██╔══██║
  ██║  ██╗   ██║   ██║ ╚═╝ ██║███████╗██║  ██║██║  ██║
  ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

**Originální industriální umělecká díla**

<br>

[![Live](https://img.shields.io/badge/live-kymera--art.com-c8a96a?style=flat-square&labelColor=0c0b08)](https://kymera-art.com)
![HTML](https://img.shields.io/badge/HTML-pure-c8a96a?style=flat-square&labelColor=0c0b08)
![CSS](https://img.shields.io/badge/CSS-vanilla-c8a96a?style=flat-square&labelColor=0c0b08)
![JS](https://img.shields.io/badge/JS-vanilla-c8a96a?style=flat-square&labelColor=0c0b08)
[![Vercel](https://img.shields.io/badge/deploy-Vercel-c8a96a?style=flat-square&labelColor=0c0b08)](https://vercel.com)

<br>

</div>

---

## Struktura

```
kymera/
│
├── index.html              ← celý web (kritické CSS inline, JS defer)
├── style.css               ← hlavní stylesheet
├── script.js               ← menu · formulář · lightbox · cookies
├── vercel.json             ← CSP · HSTS · X-Frame-Options
├── robots.txt · sitemap.xml
│
├── legal/
│   ├── gdpr.html           ← zásady zpracování osobních údajů
│   ├── podminky.html       ← obchodní podmínky
│   └── cookies.html        ← cookie politika
│
└── assets/
    ├── fonts/              ← Inter + Cormorant Garamond (lokální .woff2)
    ├── img/                ← hero · kolekce · díla · about (.webp)
    └── galerie/            ← 12 děl pro lightbox (.webp)
```

---

## Nastavení

Jediná věc která chybí před ostrým provozem:

```html
<!-- index.html, sekce kontakt -->
<input type="hidden" name="access_key" value="YOUR_WEB3FORMS_ACCESS_KEY" />
```

→ Klíč na [web3forms.com](https://web3forms.com) · free tier stačí

---

## Lokální spuštění

```bash
python3 -m http.server 8080
```

`http://localhost:8080` — žádný build, žádné závislosti.

---

## Deploy

Push do `main` = automatický deploy přes Vercel.

```bash
git add .
git commit -m "..."
git push origin main
```

> Vercel: Framework **Other** · Build Command prázdné · Output Directory prázdné

---

## Brand

<div align="center">

| | Token | Hodnota |
|---|---|---|
| ⬛ | Pozadí | `#0c0b08` |
| 🟫 | Povrch | `#15140f` |
| 🟡 | Mosaz | `#c8a96a` |
| 🔤 | Serif | Cormorant Garamond |
| 🔤 | Sans | Inter |

</div>

---

<div align="center">

<sub>© 2026 Jakub Nowicki · KYMERA · Třinec, ČR</sub>

</div>
