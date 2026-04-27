"""KYMERA — vizitky 85×55 mm (CZ standard), 3 varianty + řezné značky.
Výstup: business-cards.pdf — připraveno pro tisk (CMYK pro tiskaře nutno převést externě, RGB výstup pro náhled).
"""
import os
import urllib.request
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(__file__)
FONTS_DIR = os.path.join(ROOT, "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

FONT_URLS = {
    "InstrumentSerif-Regular.ttf":
        "https://github.com/Instrument/instrument-serif/raw/main/fonts/ttf/InstrumentSerif-Regular.ttf",
    "InstrumentSerif-Italic.ttf":
        "https://github.com/Instrument/instrument-serif/raw/main/fonts/ttf/InstrumentSerif-Italic.ttf",
    "Inter-Regular.ttf":
        "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.otf",
    "Inter-Medium.ttf":
        "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Medium.otf",
}


def ensure_font(name):
    path = os.path.join(FONTS_DIR, name)
    if not os.path.exists(path):
        try:
            print(f"  ↓ {name}")
            urllib.request.urlretrieve(FONT_URLS[name], path)
        except Exception as e:
            print(f"  ! {name}: {e}")
            return None
    return path


def register_fonts():
    pairs = [
        ("InstrumentSerif", "InstrumentSerif-Regular.ttf"),
        ("InstrumentSerif-Italic", "InstrumentSerif-Italic.ttf"),
        ("Inter", "Inter-Regular.ttf"),
        ("Inter-Medium", "Inter-Medium.ttf"),
    ]
    for name, fname in pairs:
        path = ensure_font(fname)
        if path and os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception as e:
                print(f"  ! register {name}: {e}")


# Barvy (KYMERA paleta)
GRAPHITE = (24/255, 23/255, 22/255)
IVORY = (240/255, 232/255, 215/255)
BRASS = (200/255, 169/255, 106/255)
MUTED = (148/255, 144/255, 138/255)

CARD_W = 85 * mm
CARD_H = 55 * mm

# A4 layout: 2 sloupce × 5 řad = 10 vizitek
PAGE_W, PAGE_H = A4
COLS, ROWS = 2, 5
GAP_X = 6 * mm
GAP_Y = 4 * mm
TOTAL_W = COLS * CARD_W + (COLS - 1) * GAP_X
TOTAL_H = ROWS * CARD_H + (ROWS - 1) * GAP_Y
ORIGIN_X = (PAGE_W - TOTAL_W) / 2
ORIGIN_Y = (PAGE_H - TOTAL_H) / 2


def draw_card_front_v1(c, x, y):
    """Var. 1: Klasický front — velké K monogram + KYMERA text vlevo."""
    # Pozadí
    c.setFillColorRGB(*GRAPHITE)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)

    # Monogram K v rámečku (vlevo)
    c.setStrokeColorRGB(*BRASS)
    c.setLineWidth(0.6)
    box = 14 * mm
    bx = x + 6 * mm
    by = y + (CARD_H - box) / 2
    c.rect(bx, by, box, box, fill=0, stroke=1)
    c.setFillColorRGB(*IVORY)
    try:
        c.setFont("InstrumentSerif", 22)
    except Exception:
        c.setFont("Helvetica", 22)
    c.drawCentredString(bx + box / 2, by + box / 2 - 3.5 * mm + 1, "K")

    # KYMERA wordmark
    try:
        c.setFont("Inter-Medium", 9)
    except Exception:
        c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(*IVORY)
    c.drawString(bx + box + 4 * mm, by + box / 2 + 0.5 * mm, "KYMERA")

    # Tagline
    try:
        c.setFont("Inter", 5.5)
    except Exception:
        c.setFont("Helvetica", 5.5)
    c.setFillColorRGB(*MUTED)
    c.drawString(bx + box + 4 * mm, by + box / 2 - 2.5 * mm,
                 "ORIGINÁLNÍ UMĚLECKÁ DÍLA")


def draw_card_back_v1(c, x, y):
    """Var. 1: Back — kontakty."""
    c.setFillColorRGB(*GRAPHITE)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)

    # Jméno
    try:
        c.setFont("InstrumentSerif", 14)
    except Exception:
        c.setFont("Helvetica", 14)
    c.setFillColorRGB(*IVORY)
    c.drawString(x + 6 * mm, y + CARD_H - 10 * mm, "Jakub Nowicki")

    # Role
    try:
        c.setFont("Inter", 6)
    except Exception:
        c.setFont("Helvetica", 6)
    c.setFillColorRGB(*BRASS)
    c.drawString(x + 6 * mm, y + CARD_H - 14 * mm, "AUTOR / FOUNDER")

    # Linka
    c.setStrokeColorRGB(*BRASS)
    c.setLineWidth(0.4)
    c.line(x + 6 * mm, y + CARD_H - 17 * mm,
           x + 6 * mm + 12 * mm, y + CARD_H - 17 * mm)

    # Kontakty
    try:
        c.setFont("Inter", 7)
    except Exception:
        c.setFont("Helvetica", 7)
    c.setFillColorRGB(*IVORY)
    c.drawString(x + 6 * mm, y + 17 * mm, "+420 734 548 884")
    c.drawString(x + 6 * mm, y + 13 * mm, "kymera.art")
    c.setFillColorRGB(*MUTED)
    try:
        c.setFont("Inter", 5.8)
    except Exception:
        c.setFont("Helvetica", 5.8)
    c.drawString(x + 6 * mm, y + 8 * mm, "Frýdecká 851, 739 61 Třinec")


def draw_card_front_v2(c, x, y):
    """Var. 2: Minimal — jen serif K na čistém pozadí."""
    c.setFillColorRGB(*GRAPHITE)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)

    # Velké K vystředěné
    try:
        c.setFont("InstrumentSerif-Italic", 60)
    except Exception:
        c.setFont("Helvetica-Oblique", 60)
    c.setFillColorRGB(*BRASS)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 - 8 * mm, "K")

    # Drobný wordmark dole
    try:
        c.setFont("Inter-Medium", 5.5)
    except Exception:
        c.setFont("Helvetica-Bold", 5.5)
    c.setFillColorRGB(*IVORY)
    c.drawCentredString(x + CARD_W / 2, y + 6 * mm, "K Y M E R A")


def draw_card_back_v2(c, x, y):
    """Var. 2: Back — sazba na střed."""
    c.setFillColorRGB(*GRAPHITE)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)

    cy = y + CARD_H / 2

    try:
        c.setFont("InstrumentSerif", 11)
    except Exception:
        c.setFont("Helvetica", 11)
    c.setFillColorRGB(*IVORY)
    c.drawCentredString(x + CARD_W / 2, cy + 8 * mm, "Jakub Nowicki")

    try:
        c.setFont("Inter", 5.5)
    except Exception:
        c.setFont("Helvetica", 5.5)
    c.setFillColorRGB(*BRASS)
    c.drawCentredString(x + CARD_W / 2, cy + 4 * mm, "AUTOR")

    # decorative line
    c.setStrokeColorRGB(*BRASS)
    c.setLineWidth(0.3)
    c.line(x + CARD_W / 2 - 5 * mm, cy + 1 * mm,
           x + CARD_W / 2 + 5 * mm, cy + 1 * mm)

    try:
        c.setFont("Inter", 7)
    except Exception:
        c.setFont("Helvetica", 7)
    c.setFillColorRGB(*IVORY)
    c.drawCentredString(x + CARD_W / 2, cy - 3 * mm, "+420 734 548 884")
    c.drawCentredString(x + CARD_W / 2, cy - 7 * mm, "kymera.art")

    try:
        c.setFont("Inter", 5.5)
    except Exception:
        c.setFont("Helvetica", 5.5)
    c.setFillColorRGB(*MUTED)
    c.drawCentredString(x + CARD_W / 2, cy - 12 * mm,
                        "Frýdecká 851, 739 61 Třinec")


def draw_card_front_v3(c, x, y):
    """Var. 3: Editorial — typografická."""
    c.setFillColorRGB(*GRAPHITE)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)

    # Velký serif KYMERA
    try:
        c.setFont("InstrumentSerif", 24)
    except Exception:
        c.setFont("Helvetica", 24)
    c.setFillColorRGB(*IVORY)
    c.drawString(x + 6 * mm, y + CARD_H / 2 + 1 * mm, "KYMERA")

    # Italic descriptor pod tím
    try:
        c.setFont("InstrumentSerif-Italic", 8)
    except Exception:
        c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(*BRASS)
    c.drawString(x + 6 * mm, y + CARD_H / 2 - 4 * mm,
                 "tichá síla v lidské formě")

    # Mini info dole
    try:
        c.setFont("Inter", 5)
    except Exception:
        c.setFont("Helvetica", 5)
    c.setFillColorRGB(*MUTED)
    c.drawString(x + 6 * mm, y + 5 * mm,
                 "ORIGINÁLNÍ UMĚLECKÁ DÍLA  ·  CZ / EN / PL")


def draw_card_back_v3(c, x, y):
    """Var. 3: Back — pravo-zarovnaný typografický."""
    c.setFillColorRGB(*GRAPHITE)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)

    # right-aligned column
    rx = x + CARD_W - 6 * mm

    try:
        c.setFont("InstrumentSerif", 13)
    except Exception:
        c.setFont("Helvetica", 13)
    c.setFillColorRGB(*IVORY)
    c.drawRightString(rx, y + CARD_H - 10 * mm, "Jakub Nowicki")

    try:
        c.setFont("Inter-Medium", 5.5)
    except Exception:
        c.setFont("Helvetica-Bold", 5.5)
    c.setFillColorRGB(*BRASS)
    c.drawRightString(rx, y + CARD_H - 13 * mm, "AUTOR / FOUNDER")

    # vertical brass line
    c.setStrokeColorRGB(*BRASS)
    c.setLineWidth(0.3)
    c.line(rx - 22 * mm, y + 6 * mm, rx - 22 * mm, y + CARD_H - 6 * mm)

    # block of contacts
    try:
        c.setFont("Inter", 7)
    except Exception:
        c.setFont("Helvetica", 7)
    c.setFillColorRGB(*IVORY)
    c.drawRightString(rx, y + 19 * mm, "+420 734 548 884")
    c.drawRightString(rx, y + 14 * mm, "kymera.art")

    try:
        c.setFont("Inter", 5.5)
    except Exception:
        c.setFont("Helvetica", 5.5)
    c.setFillColorRGB(*MUTED)
    c.drawRightString(rx, y + 8 * mm, "Frýdecká 851")
    c.drawRightString(rx, y + 5 * mm, "739 61 Třinec")


def draw_crop_marks(c, x, y):
    """Řezné značky kolem karty (3mm offset)."""
    c.setStrokeColorRGB(0.3, 0.3, 0.3)
    c.setLineWidth(0.2)
    m = 3 * mm
    L = 2 * mm
    # 4 rohy
    corners = [
        (x, y),                              # bottom-left
        (x + CARD_W, y),                     # bottom-right
        (x, y + CARD_H),                     # top-left
        (x + CARD_W, y + CARD_H),            # top-right
    ]
    for cx, cy in corners:
        # horizontal
        c.line(cx - m - L, cy, cx - m, cy)
        c.line(cx + m, cy, cx + m + L, cy)
        # vertical
        c.line(cx, cy - m - L, cx, cy - m)
        c.line(cx, cy + m, cx, cy + m + L)


def draw_grid(c, draw_fn, label):
    """Nakresli 10× kartu na A4."""
    # title
    try:
        c.setFont("Inter-Medium", 8)
    except Exception:
        c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(15 * mm, PAGE_H - 12 * mm, label)
    c.drawString(15 * mm, PAGE_H - 16 * mm,
                 "Formát 85×55 mm  ·  s řeznými značkami  ·  pro tisk přidat 3 mm spadávku")

    for r in range(ROWS):
        for col in range(COLS):
            x = ORIGIN_X + col * (CARD_W + GAP_X)
            y = ORIGIN_Y + (ROWS - 1 - r) * (CARD_H + GAP_Y)
            draw_crop_marks(c, x, y)
            draw_fn(c, x, y)


def main():
    register_fonts()
    out = os.path.join(ROOT, "kymera-business-cards.pdf")
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle("KYMERA — vizitky (3 varianty)")
    c.setAuthor("Perplexity Computer")

    layouts = [
        (draw_card_front_v1, "VARIANTA 01 / FRONT  —  Monogram + wordmark"),
        (draw_card_back_v1,  "VARIANTA 01 / BACK   —  Klasické rozložení"),
        (draw_card_front_v2, "VARIANTA 02 / FRONT  —  Minimal italic K"),
        (draw_card_back_v2,  "VARIANTA 02 / BACK   —  Vystředěná sazba"),
        (draw_card_front_v3, "VARIANTA 03 / FRONT  —  Editorial typografie"),
        (draw_card_back_v3,  "VARIANTA 03 / BACK   —  Pravo-zarovnaný blok"),
    ]
    for fn, label in layouts:
        draw_grid(c, fn, label)
        c.showPage()

    c.save()
    print(f"\n✓ {out}")


if __name__ == "__main__":
    main()
