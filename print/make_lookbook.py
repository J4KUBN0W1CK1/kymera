"""KYMERA — lookbook A4 portrait. Editorial PDF prospekt pro architekty a sběratele.
Strany: cover · manifest · proces · kolekce 01-03 · vybraná díla 01-03 · pro architekty · kontakt
"""
import os
import urllib.request
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT = os.path.dirname(__file__)
FONTS_DIR = os.path.join(ROOT, "fonts")
IMG_DIR = os.path.join(os.path.dirname(ROOT), "assets", "img")

# Palette
GRAPHITE = (24/255, 23/255, 22/255)
GRAPHITE_DARK = (14/255, 13/255, 12/255)
IVORY = (240/255, 232/255, 215/255)
IVORY_SOFT = (220/255, 213/255, 197/255)
BRASS = (200/255, 169/255, 106/255)
MUTED = (148/255, 144/255, 138/255)


def register_fonts():
    pairs = [
        ("InstrumentSerif", "InstrumentSerif-Regular.ttf"),
        ("InstrumentSerif-Italic", "InstrumentSerif-Italic.ttf"),
        ("Inter", "Inter-Regular.ttf"),
        ("Inter-Medium", "Inter-Medium.ttf"),
    ]
    for name, fname in pairs:
        path = os.path.join(FONTS_DIR, fname)
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception as e:
                print(f"  ! {name}: {e}")


PAGE_W, PAGE_H = A4


def font(name, size, c):
    try:
        c.setFont(name, size)
    except Exception:
        fallback = {
            "InstrumentSerif": "Helvetica",
            "InstrumentSerif-Italic": "Helvetica-Oblique",
            "Inter": "Helvetica",
            "Inter-Medium": "Helvetica-Bold",
        }
        c.setFont(fallback.get(name, "Helvetica"), size)


def fill_bg(c, color=GRAPHITE):
    c.setFillColorRGB(*color)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def draw_eyebrow(c, x, y, text):
    font("Inter-Medium", 7, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(x, y, text)


def draw_running_header(c, page_label):
    """Vertikálně zarovnaný header — KYMERA vlevo, číslo strany vpravo."""
    font("Inter-Medium", 7, c)
    c.setFillColorRGB(*MUTED)
    c.drawString(20 * mm, PAGE_H - 12 * mm, "K Y M E R A")
    c.drawRightString(PAGE_W - 20 * mm, PAGE_H - 12 * mm, page_label)
    # tenká linka
    c.setStrokeColorRGB(*BRASS)
    c.setLineWidth(0.3)
    c.line(20 * mm, PAGE_H - 14 * mm, PAGE_W - 20 * mm, PAGE_H - 14 * mm)


def draw_running_footer(c):
    font("Inter", 6.5, c)
    c.setFillColorRGB(*MUTED)
    c.drawString(20 * mm, 12 * mm, "kymera.art")
    c.drawCentredString(PAGE_W / 2, 12 * mm,
                        "ORIGINÁLNÍ UMĚLECKÁ DÍLA — KAŽDÝ KUS JEDEN V JEDNOM")
    c.drawRightString(PAGE_W - 20 * mm, 12 * mm, "+420 734 548 884")


def wrap_text(c, text, max_w, font_name, size, leading):
    """Zalomí odstavec na řádky podle šířky."""
    words = text.split()
    lines = []
    current = ""
    font(font_name, size, c)
    for w in words:
        trial = (current + " " + w).strip()
        if c.stringWidth(trial, font_name, size) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def draw_paragraph(c, x, y, text, max_w, font_name="Inter", size=10, leading=15, color=IVORY):
    lines = wrap_text(c, text, max_w, font_name, size, leading)
    c.setFillColorRGB(*color)
    font(font_name, size, c)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)
    return y - len(lines) * leading


# ============ STRANY ============

def page_cover(c):
    fill_bg(c, GRAPHITE_DARK)

    # Hero fotka — pravá polovina
    img = os.path.join(IMG_DIR, "hero.jpg")
    if os.path.exists(img):
        # zarovnat doprava, nakreslit s fade-out gradient přes levou část
        c.drawImage(ImageReader(img), 0, 0, PAGE_W, PAGE_H,
                    preserveAspectRatio=True, anchor='c', mask='auto')
    # tmavá vinetta zleva (gradient simulujeme více obdélníky)
    for i in range(40):
        alpha = 1.0 - (i / 40) * 0.85
        if alpha < 0: alpha = 0
        # ReportLab nemá přímo alpha, použijeme polo-transparentní kombinaci
        c.setFillColorRGB(*GRAPHITE_DARK, alpha=alpha * 0.95)
        c.rect(i * (PAGE_W * 0.7 / 40), 0, (PAGE_W * 0.7 / 40) + 0.2, PAGE_H,
               fill=1, stroke=0)
    c.setFillColorRGB(*GRAPHITE_DARK, alpha=0.5)
    c.rect(0, 0, PAGE_W, 40 * mm, fill=1, stroke=0)
    c.setFillColorRGB(*GRAPHITE_DARK, alpha=1)

    # KYMERA monogram nahoře
    font("Inter-Medium", 9, c)
    c.setFillColorRGB(*IVORY)
    c.drawString(20 * mm, PAGE_H - 25 * mm, "K Y M E R A")

    font("Inter", 7, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(20 * mm, PAGE_H - 30 * mm, "LOOKBOOK 2026")

    # Velký serif title
    font("InstrumentSerif", 64, c)
    c.setFillColorRGB(*IVORY)
    c.drawString(20 * mm, PAGE_H / 2 + 10 * mm, "Tichá síla")

    font("InstrumentSerif-Italic", 64, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(20 * mm, PAGE_H / 2 - 10 * mm, "v lidské formě.")

    # subtitle
    font("Inter", 11, c)
    c.setFillColorRGB(*IVORY_SOFT)
    c.drawString(20 * mm, PAGE_H / 2 - 25 * mm,
                 "Originální umělecká díla pro privátní sběratele,")
    c.drawString(20 * mm, PAGE_H / 2 - 30 * mm,
                 "architekty a reprezentativní interiéry.")

    # spodní info
    font("Inter-Medium", 7, c)
    c.setFillColorRGB(*MUTED)
    c.drawString(20 * mm, 22 * mm, "AUTOR")
    font("InstrumentSerif", 12, c)
    c.setFillColorRGB(*IVORY)
    c.drawString(20 * mm, 16 * mm, "Jakub Nowicki")

    font("Inter-Medium", 7, c)
    c.setFillColorRGB(*MUTED)
    c.drawRightString(PAGE_W - 20 * mm, 22 * mm, "ATELIÉR")
    font("InstrumentSerif", 12, c)
    c.setFillColorRGB(*IVORY)
    c.drawRightString(PAGE_W - 20 * mm, 16 * mm, "Třinec, ČR")


def page_manifest(c):
    fill_bg(c)
    draw_running_header(c, "01 / Manifest")
    draw_running_footer(c)

    y = PAGE_H - 50 * mm
    draw_eyebrow(c, 20 * mm, y, "MANIFEST")
    y -= 15 * mm

    font("InstrumentSerif", 32, c)
    c.setFillColorRGB(*IVORY)
    c.drawString(20 * mm, y, "Mezi tělem a strojem.")
    y -= 12 * mm
    font("InstrumentSerif-Italic", 32, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(20 * mm, y, "Mezi tichem a technikou.")

    y -= 25 * mm
    txt1 = ("KYMERA vzniká z napětí. Mezi tím, co je živé, a tím, co bylo do živého "
            "vloženo. Mezi řemeslem a strojem. Mezi pomalou prací rukou a precizí "
            "soukolí, které kdysi sloužilo motoru a teď slouží příběhu.")
    y = draw_paragraph(c, 20 * mm, y, txt1, PAGE_W - 40 * mm,
                       "InstrumentSerif", 13, 19, IVORY)

    y -= 8 * mm
    txt2 = ("Každá socha je originál. Žádné edice, žádné reprodukce. Jeden v jednom. "
            "Pro toho, kdo už nehledá další předmět — hledá charakter prostoru.")
    y = draw_paragraph(c, 20 * mm, y, txt2, PAGE_W - 40 * mm,
                       "Inter", 11, 17, IVORY_SOFT)

    # quote block
    y -= 25 * mm
    c.setStrokeColorRGB(*BRASS)
    c.setLineWidth(0.6)
    c.line(20 * mm, y + 5 * mm, 30 * mm, y + 5 * mm)
    y -= 5 * mm
    font("InstrumentSerif-Italic", 18, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(20 * mm, y, "„Tělo jako nosič příběhu,")
    y -= 8 * mm
    c.drawString(20 * mm, y, "ne jako ozdoba.“")

    y -= 15 * mm
    font("Inter-Medium", 7, c)
    c.setFillColorRGB(*MUTED)
    c.drawString(20 * mm, y, "JAKUB NOWICKI · KYMERA")


def page_process(c):
    fill_bg(c)
    draw_running_header(c, "02 / Proces")
    draw_running_footer(c)

    y = PAGE_H - 50 * mm
    draw_eyebrow(c, 20 * mm, y, "PROCES")
    y -= 15 * mm
    font("InstrumentSerif", 32, c)
    c.setFillColorRGB(*IVORY)
    c.drawString(20 * mm, y, "Dřevo. Mechanika.")
    y -= 12 * mm
    font("InstrumentSerif-Italic", 32, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(20 * mm, y, "Povrch.")

    y -= 25 * mm
    txt = ("Základem každé sochy je vyřezané dřevo. Tělo, hlava, charakter. "
           "Do něj se chirurgicky implantují technické díly — ozubená kola, "
           "písty, převody, pružiny, strojní detaily. Každý prvek má své místo. "
           "Nic není dekorace.")
    y = draw_paragraph(c, 20 * mm, y, txt, PAGE_W - 40 * mm,
                       "Inter", 11, 17, IVORY_SOFT)

    y -= 8 * mm
    txt2 = ("Celé dílo dostává finální povrch. Kov, mosaz, patina, nebo barva "
            "podle přání sběratele. Standard je tichý — patinovaná surovost, "
            "která zraje s prostorem. Na vyžádání jakýkoli odstín.")
    y = draw_paragraph(c, 20 * mm, y, txt2, PAGE_W - 40 * mm,
                       "Inter", 11, 17, IVORY_SOFT)

    # 4 kroky procesu
    y -= 20 * mm
    steps = [
        ("I.", "DŘEVO", "Vyřezání tělové formy z masivu. Tvar a charakter."),
        ("II.", "MECHANIKA", "Implantace technických dílů. Ozubení, písty, převody."),
        ("III.", "POVRCH", "Finální nátěr — kov, mosaz, patina nebo barva na míru."),
        ("IV.", "CERTIFIKÁT", "Číslování, podpis, papírový a kovový certifikát."),
    ]
    col_w = (PAGE_W - 40 * mm - 6 * mm * 3) / 4
    for i, (num, title, desc) in enumerate(steps):
        x = 20 * mm + i * (col_w + 6 * mm)
        font("InstrumentSerif-Italic", 22, c)
        c.setFillColorRGB(*BRASS)
        c.drawString(x, y, num)
        font("Inter-Medium", 8, c)
        c.setFillColorRGB(*IVORY)
        c.drawString(x, y - 8 * mm, title)
        # popis
        lines = wrap_text(c, desc, col_w, "Inter", 8, 12)
        font("Inter", 8, c)
        c.setFillColorRGB(*MUTED)
        for j, line in enumerate(lines):
            c.drawString(x, y - 14 * mm - j * 11, line)


def page_collection(c, idx, num, title_top, title_bottom, body, image_name):
    fill_bg(c)
    draw_running_header(c, f"0{idx} / Kolekce")
    draw_running_footer(c)

    # left: text, right: image
    img_w = PAGE_W * 0.42
    img_x = PAGE_W - img_w - 20 * mm
    img_h = PAGE_H - 70 * mm
    img_y = (PAGE_H - img_h) / 2

    img_path = os.path.join(IMG_DIR, image_name)
    if os.path.exists(img_path):
        c.drawImage(ImageReader(img_path), img_x, img_y, img_w, img_h,
                    preserveAspectRatio=True, anchor='c', mask='auto')

    # Text vlevo
    y = PAGE_H - 55 * mm
    font("Inter-Medium", 7, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(20 * mm, y, f"KOLEKCE {num}")
    y -= 14 * mm

    font("InstrumentSerif", 34, c)
    c.setFillColorRGB(*IVORY)
    c.drawString(20 * mm, y, title_top)
    if title_bottom:
        y -= 13 * mm
        font("InstrumentSerif-Italic", 34, c)
        c.setFillColorRGB(*BRASS)
        c.drawString(20 * mm, y, title_bottom)

    y -= 22 * mm
    text_w = img_x - 30 * mm
    y = draw_paragraph(c, 20 * mm, y, body, text_w,
                       "Inter", 11, 17, IVORY_SOFT)


def page_work(c, idx, total, title, materials, year, dimensions, body, image_name):
    fill_bg(c)
    draw_running_header(c, f"{idx} / Vybraná díla")
    draw_running_footer(c)

    # full-bleed image vpravo
    img_w = PAGE_W * 0.55
    img_x = PAGE_W - img_w
    img_h = PAGE_H - 60 * mm
    img_y = 30 * mm

    img_path = os.path.join(IMG_DIR, image_name)
    if os.path.exists(img_path):
        c.drawImage(ImageReader(img_path), img_x, img_y, img_w, img_h,
                    preserveAspectRatio=True, anchor='c', mask='auto')

    # tag vpravo nahoře přes obrázek
    c.setFillColorRGB(*BRASS, alpha=1)
    c.rect(img_x + img_w - 30 * mm, img_y + img_h - 10 * mm,
           25 * mm, 6 * mm, fill=1, stroke=0)
    font("Inter-Medium", 6, c)
    c.setFillColorRGB(*GRAPHITE)
    c.drawCentredString(img_x + img_w - 30 * mm + 12.5 * mm,
                        img_y + img_h - 10 * mm + 2 * mm, "ORIGINÁL")

    # Text vlevo
    y = PAGE_H - 55 * mm
    font("Inter-Medium", 7, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(20 * mm, y, f"VYBRANÁ DÍLA · {idx}")
    y -= 14 * mm

    font("InstrumentSerif", 32, c)
    c.setFillColorRGB(*IVORY)
    c.drawString(20 * mm, y, title)

    # tech specs blok
    y -= 18 * mm
    c.setStrokeColorRGB(*BRASS)
    c.setLineWidth(0.4)
    c.line(20 * mm, y + 3 * mm, 35 * mm, y + 3 * mm)
    y -= 5 * mm
    specs = [
        ("MATERIÁL", materials),
        ("ROK", year),
        ("ROZMĚRY", dimensions),
        ("CENA", "Na vyžádání"),
    ]
    for label, val in specs:
        font("Inter-Medium", 6.5, c)
        c.setFillColorRGB(*MUTED)
        c.drawString(20 * mm, y, label)
        font("Inter", 9, c)
        c.setFillColorRGB(*IVORY)
        c.drawString(20 * mm, y - 5 * mm, val)
        y -= 14 * mm

    # popis
    y -= 5 * mm
    text_w = img_x - 30 * mm
    y = draw_paragraph(c, 20 * mm, y, body, text_w,
                       "Inter", 9.5, 15, IVORY_SOFT)


def page_trade(c):
    fill_bg(c)
    draw_running_header(c, "08 / Pro architekty a partnery")
    draw_running_footer(c)

    y = PAGE_H - 50 * mm
    draw_eyebrow(c, 20 * mm, y, "PRO ARCHITEKTY A PARTNERY")
    y -= 15 * mm
    font("InstrumentSerif", 32, c)
    c.setFillColorRGB(*IVORY)
    c.drawString(20 * mm, y, "Spolupráce")
    y -= 12 * mm
    font("InstrumentSerif-Italic", 32, c)
    c.setFillColorRGB(*BRASS)
    c.drawString(20 * mm, y, "na míru.")

    y -= 22 * mm
    txt = ("Pro architektonická studia, designéry, hotely, showroomy a privátní "
           "klienty připravujeme díla s ohledem na konkrétní prostor, světlo "
           "a charakter projektu. Všechno je domluvitelné — rozměr, povrch, "
           "instalace, transport, doprovodný certifikát.")
    y = draw_paragraph(c, 20 * mm, y, txt, PAGE_W - 40 * mm,
                       "Inter", 11, 17, IVORY_SOFT)

    # 4 sekce
    y -= 20 * mm
    items = [
        ("I.", "PRIVÁTNÍ SBĚRATELÉ",
         "Dlouhodobá diskrétní spolupráce. Dílo jako součást domu."),
        ("II.", "ARCHITEKTI A STUDIA",
         "Příprava děl pro konkrétní realizaci. Materiály, měřítko, instalace."),
        ("III.", "HOTELY A SHOWROOMY",
         "Reprezentativní objekty pro lobby, suity a značkové prostory."),
        ("IV.", "FIREMNÍ INTERIÉRY",
         "Tichý a sebevědomý charakter pro prostor, který má co říct."),
    ]
    col_w = (PAGE_W - 40 * mm - 8 * mm) / 2
    for i, (num, title, desc) in enumerate(items):
        col = i % 2
        row = i // 2
        x = 20 * mm + col * (col_w + 8 * mm)
        block_y = y - row * 35 * mm

        font("InstrumentSerif-Italic", 22, c)
        c.setFillColorRGB(*BRASS)
        c.drawString(x, block_y, num)

        font("Inter-Medium", 9, c)
        c.setFillColorRGB(*IVORY)
        c.drawString(x + 14 * mm, block_y, title)

        # description
        lines = wrap_text(c, desc, col_w - 14 * mm, "Inter", 9, 13)
        font("Inter", 9, c)
        c.setFillColorRGB(*MUTED)
        for j, line in enumerate(lines):
            c.drawString(x + 14 * mm, block_y - 7 * mm - j * 12, line)


def page_contact(c):
    fill_bg(c, GRAPHITE_DARK)
    draw_running_header(c, "09 / Kontakt")

    y = PAGE_H / 2 + 40 * mm
    font("Inter-Medium", 7, c)
    c.setFillColorRGB(*BRASS)
    c.drawCentredString(PAGE_W / 2, y, "PRIVÁTNÍ POPTÁVKA")

    y -= 25 * mm
    font("InstrumentSerif", 48, c)
    c.setFillColorRGB(*IVORY)
    c.drawCentredString(PAGE_W / 2, y, "Pojďme si o tom")
    y -= 18 * mm
    font("InstrumentSerif-Italic", 48, c)
    c.setFillColorRGB(*BRASS)
    c.drawCentredString(PAGE_W / 2, y, "promluvit.")

    y -= 30 * mm
    # vodorovná linka
    c.setStrokeColorRGB(*BRASS)
    c.setLineWidth(0.4)
    c.line(PAGE_W / 2 - 15 * mm, y, PAGE_W / 2 + 15 * mm, y)

    y -= 18 * mm
    font("InstrumentSerif", 18, c)
    c.setFillColorRGB(*IVORY)
    c.drawCentredString(PAGE_W / 2, y, "Jakub Nowicki")
    y -= 8 * mm
    font("Inter-Medium", 8, c)
    c.setFillColorRGB(*MUTED)
    c.drawCentredString(PAGE_W / 2, y, "AUTOR / FOUNDER")

    y -= 18 * mm
    font("Inter", 13, c)
    c.setFillColorRGB(*IVORY)
    c.drawCentredString(PAGE_W / 2, y, "+420 734 548 884")
    y -= 8 * mm
    c.drawCentredString(PAGE_W / 2, y, "kymera.art")

    y -= 14 * mm
    font("Inter", 10, c)
    c.setFillColorRGB(*MUTED)
    c.drawCentredString(PAGE_W / 2, y, "Frýdecká 851, 739 61 Třinec, ČR")

    # spodní quote
    font("InstrumentSerif-Italic", 11, c)
    c.setFillColorRGB(*BRASS)
    c.drawCentredString(PAGE_W / 2, 25 * mm,
                        "„Žádná edice. Žádná reprodukce. Jeden v jednom.“")


# ============ MAIN ============

def main():
    register_fonts()
    out = os.path.join(ROOT, "kymera-lookbook.pdf")
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle("KYMERA — Lookbook 2026")
    c.setAuthor("Perplexity Computer")

    # Cover
    page_cover(c); c.showPage()

    # Manifest
    page_manifest(c); c.showPage()

    # Proces
    page_process(c); c.showPage()

    # Kolekce 1
    page_collection(c, 3, "01",
                    "Figurální", "objekty.",
                    "Lidské figury vyřezané ze dřeva s chirurgicky implantovanou "
                    "mechanikou. Tělo jako nosič příběhu, ne jako ozdoba. "
                    "Vhodné pro centrální umístění v reprezentativním prostoru — "
                    "obývací pokoj, hotelové lobby, showroom, foyer.",
                    "collection-figurative.jpg")
    c.showPage()

    # Kolekce 2
    page_collection(c, 4, "02",
                    "Hlavy a", "busty.",
                    "Dřevěné portréty s vsazenými ozubenými koly, písty a strojními "
                    "detaily. Dramatický detail pro intimní prostor — pracovnu, "
                    "knihovnu, suite, soukromou galerii. Diktují pomalé pozorování.",
                    "collection-busts.jpg")
    c.showPage()

    # Kolekce 3
    page_collection(c, 5, "03",
                    "Mechanické", "figury.",
                    "Dřevěná těla s technickými prvky a finálním nátěrem — "
                    "patinovaný kov, mosaz, nebo barevný odstín na míru sběrateli. "
                    "Každý kus originál, vzniká jednou. Možnost objednání s "
                    "konkrétním materiálem či povrchem dle projektu.",
                    "collection-industrial.jpg")
    c.showPage()

    # Vybraná díla
    page_work(c, "I.", 3, "Vestální I.",
              "Dřevo, mechanika, mosazný nátěr",
              "2025", "180 × 65 × 55 cm",
              "Stojící ženská figura s implantovanou převodovkou v hrudníku a "
              "ozubenými detaily v končetinách. Patinovaný mosazný povrch zdůrazňuje "
              "křivky těla a technický detail mechaniky. Originál, jeden v jednom.",
              "work-01.jpg")
    c.showPage()

    page_work(c, "II.", 3, "Anatomia Bronzê",
              "Dřevo, mechanika, patinovaný povrch",
              "2025", "92 × 48 × 42 cm",
              "Bust s otevřeným hrudním košem. Soukolí, písty a hadičky se mísí "
              "s anatomií krku a ramen. Patinovaný povrch v tónu starého bronzu, "
              "určeno pro intimní prostor — knihovnu, kabinet, soukromou galerii.",
              "work-02.jpg")
    c.showPage()

    page_work(c, "III.", 3, "Membrana",
              "Dřevo, mechanika, kovový nátěr",
              "2025", "145 × 60 × 50 cm",
              "Polosedící figura s odhalenou mechanikou v zádech a páteři. "
              "Tělo jako napínané membrány mezi tichem a strojem. Kovový nátěr s "
              "lehkou patinou. Vhodné na podstavec ve výšce 60-80 cm.",
              "work-03.jpg")
    c.showPage()

    # Pro architekty
    page_trade(c); c.showPage()

    # Kontakt
    page_contact(c); c.showPage()

    c.save()
    print(f"\n✓ {out}")
    return out


if __name__ == "__main__":
    main()
