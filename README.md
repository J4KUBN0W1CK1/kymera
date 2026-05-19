<div align="center">

<img src="assets/img/preview.webp" width="100%" alt="KYMERA — kymera-art.com"/>

<br><br>

<h1>KYMERA</h1>

<p><em>Lidská forma protkaná soukolím. Každé dílo originál.</em></p>

<br>

[![Live](https://img.shields.io/badge/🌐_live-kymera--art.com-c8a96a?style=for-the-badge&labelColor=0c0b08)](https://kymera-art.com)

<br>

![HTML](https://img.shields.io/badge/HTML-pure-c8a96a?style=flat-square&labelColor=15140f)
![CSS](https://img.shields.io/badge/CSS-vanilla-c8a96a?style=flat-square&labelColor=15140f)
![JS](https://img.shields.io/badge/JS-vanilla-c8a96a?style=flat-square&labelColor=15140f)
![Vercel](https://img.shields.io/badge/Vercel-deployed-c8a96a?style=flat-square&labelColor=15140f)
![No build](https://img.shields.io/badge/build_step-none-c8a96a?style=flat-square&labelColor=15140f)

<br>

![Performance](https://img.shields.io/badge/Performance-92-orange?style=flat-square&logo=lighthouse&logoColor=white)
![Accessibility](https://img.shields.io/badge/Accessibility-100-brightgreen?style=flat-square&logo=lighthouse&logoColor=white)
![Best Practices](https://img.shields.io/badge/Best_Practices-96-brightgreen?style=flat-square&logo=lighthouse&logoColor=white)
![SEO](https://img.shields.io/badge/SEO-100-brightgreen?style=flat-square&logo=lighthouse&logoColor=white)

</div>

<br>

---

## Obsah

| Sekce | Soubor | Popis |
|---|---|---|
| 🏠 Hlavní stránka | `index.html` | Celý web — hero, galerie, kontakt |
| 🎨 Styly | `style.css` | Hlavní stylesheet |
| ⚙️ Skripty | `script.js` | Menu, formulář, lightbox, cookies |
| 🔒 Security | `vercel.json` | CSP, HSTS, X-Frame-Options |
| ⚖️ GDPR | `legal/gdpr.html` | Zásady zpracování osobních údajů |
| 📄 Podmínky | `legal/podminky.html` | Obchodní podmínky |
| 🍪 Cookies | `legal/cookies.html` | Cookie politika |

---

## Struktura projektu

```
kymera/
├── index.html
├── style.css
├── script.js
├── vercel.json
├── robots.txt
├── sitemap.xml
├── legal/
│   ├── gdpr.html
│   ├── podminky.html
│   └── cookies.html
└── assets/
    ├── fonts/        ← Inter + Cormorant Garamond (lokální .woff2)
    ├── img/          ← hero · kolekce · díla · about (.webp, RGBA)
    └── galerie/      ← 12 děl pro lightbox (.webp)
```

---

## Díla

<div align="center">

| Figurální objekty | Hlavy a busty | Mechanické figury |
|:---:|:---:|:---:|
| <img src="assets/img/collection-figurative.webp" width="180"/> | <img src="assets/img/collection-busts.webp" width="180"/> | <img src="assets/img/collection-industrial.webp" width="180"/> |

</div>

---

## Spuštění

```bash
# lokálně — žádný install, žádný build
python3 -m http.server 8080
```

**Jediné nastavení před ostrým provozem:**

```html
<!-- index.html — kontaktní formulář -->
<input type="hidden" name="access_key" value="YOUR_WEB3FORMS_ACCESS_KEY" />
```

→ Klíč na [web3forms.com](https://web3forms.com) · free tier stačí

---

## Deploy

```bash
git add .
git commit -m "..."
git push origin main   # → automatický deploy přes Vercel
```

> **Vercel nastavení:** Framework `Other` · Build Command prázdné · Output Directory prázdné

---

## Brand

<div align="center">

`#0c0b08` &nbsp;·&nbsp; `#15140f` &nbsp;·&nbsp; `#c8a96a` &nbsp;·&nbsp; Cormorant Garamond &nbsp;·&nbsp; Inter

</div>

---

<div align="center">

<sub>© 2026 Jakub Nowicki &nbsp;·&nbsp; KYMERA &nbsp;·&nbsp; Atelier Třinec, ČR</sub>

</div>
