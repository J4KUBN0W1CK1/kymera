# KYMERA — kymera-art.com

> Originální industriální umělecká díla. Statický web bez frameworku, bez build kroku.

**Stack:** HTML · CSS · Vanilla JS · Vercel · GitHub

---

## Struktura

```
kymera/
├── index.html          # celý web (inline kritické CSS + JS defer)
├── style.css           # hlavní stylesheet
├── script.js           # menu, formulář, lightbox, cookie banner
├── vercel.json         # security headers (CSP, HSTS, X-Frame)
├── robots.txt
├── sitemap.xml
├── legal/
│   ├── gdpr.html
│   ├── podminky.html
│   └── cookies.html
└── assets/
    ├── fonts/          # Inter + Cormorant Garamond (.woff2, lokálně)
    ├── img/            # hero, kolekce, díla, about (.webp)
    └── galerie/        # 12 děl pro lightbox (.webp)
```

---

## Nastavení před spuštěním

**Web3Forms** — kontaktní formulář v `index.html`:
```html
<input type="hidden" name="access_key" value="YOUR_WEB3FORMS_ACCESS_KEY" />
```
Klíč si vygeneruj na [web3forms.com](https://web3forms.com) (free tier stačí).

---

## Lokální spuštění

```bash
python3 -m http.server 8080
# → http://localhost:8080
```

---

## Nasazení

Repo je napojeno na **Vercel** přes GitHub — push do `main` = automatický deploy.

```bash
git add .
git commit -m "popis změny"
git push origin main
```

Vercel nastavení: Framework Preset **Other**, Build Command prázdné, Output Directory prázdné.

---

## Brand

| Token | Hodnota |
|-------|---------|
| Pozadí | `#0c0b08` |
| Písmo | `#ece3cd` |
| Mosaz | `#c8a96a` |
| Serif | Cormorant Garamond |
| Sans | Inter |
