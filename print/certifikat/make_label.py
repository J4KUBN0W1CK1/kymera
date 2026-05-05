#!/usr/bin/env python3
"""
KYMERA — Mosazný štítek originality
Výrobní podklad pro rytce / laserovou gravírovnu.
A4 PDF, 3 strany: 1) návrh 1:1 + 3:1 s kótami, 2) specifikace, 3) 6 mock-up variant.
"""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

# --- Fonty ---
FONT_DIR = Path("/home/user/workspace/kymera/print/fonts")
pdfmetrics.registerFont(TTFont("Inter", str(FONT_DIR / "Inter-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Inter-Medium", str(FONT_DIR / "Inter-Medium.ttf")))
pdfmetrics.registerFont(TTFont("InstrumentSerif", str(FONT_DIR / "InstrumentSerif-Regular.ttf")))
pdfmetrics.registerFont(TTFont("InstrumentSerif-Italic", str(FONT_DIR / "InstrumentSerif-Italic.ttf")))

# --- Barvy ---
BLACK = (0, 0, 0)
GRAY = (0.45, 0.45, 0.45)
LIGHT_GRAY = (0.78, 0.78, 0.78)
PALE = (0.94, 0.94, 0.92)
BRASS = (0.722, 0.573, 0.353)  # #b8925a

# --- Rozměry destičky (mm) ---
LABEL_W = 60.0
LABEL_H = 30.0
CORNER_R = 3.0
HOLE_D = 1.5
HOLE_INSET = 4.0  # vzdálenost středu otvoru od rohu

PAGE_W, PAGE_H = A4  # body
MARGIN = 18 * mm


def set_rgb(c, rgb):
    c.setStrokeColorRGB(*rgb)
    c.setFillColorRGB(*rgb)


def draw_label(c, x_mm, y_mm, scale=1.0, show_holes=True, line_w_mm=0.18,
               kym_number="KYM — 2026 — 001", artwork_title="Tichá síla I.",
               draw_outline=True):
    """
    Nakreslí destičku se středem vlevo-dolu na (x_mm, y_mm) v milimetrech, ve zvoleném měřítku.
    Souřadnice počítáme v mm a převedeme na body (1 mm = mm konstanta z reportlabu).
    """
    s = scale
    x = x_mm * mm
    y = y_mm * mm
    w = LABEL_W * s * mm
    h = LABEL_H * s * mm
    r = CORNER_R * s * mm

    # Tělo destičky — jemný obrys
    if draw_outline:
        c.setLineWidth(line_w_mm * mm)
        set_rgb(c, BLACK)
        # Velmi jemně tonovaná výplň pro náznak mosazi (jen vizuální preview)
        c.setFillColorRGB(*PALE)
        c.roundRect(x, y, w, h, r, stroke=1, fill=1)
        set_rgb(c, BLACK)

    # Otvory pro upevnění — 2x v rozích (vlevo dole, vpravo dole — typické pro plaketu)
    if show_holes:
        d = HOLE_D * s * mm
        inset = HOLE_INSET * s * mm
        for cx, cy in [(x + inset, y + inset), (x + w - inset, y + inset),
                       (x + inset, y + h - inset), (x + w - inset, y + h - inset)]:
            c.setLineWidth(line_w_mm * mm)
            set_rgb(c, BLACK)
            c.circle(cx, cy, d / 2, stroke=1, fill=0)

    # --- Gravírovaný obsah ---
    # Vertikální layout (zhora dolů) — proporční pozice v mm vůči destičce
    # Logo "K Y M E R A" — Inter Medium, prostrkáno
    logo_text = "K Y M E R A"
    logo_size_mm = 4.2
    c.setFont("Inter-Medium", logo_size_mm * s * mm / mm * (mm / mm))  # převod
    # Reportlab používá body pro velikost fontu; 1 mm ≈ 2.8346 bodu
    logo_size_pt = logo_size_mm * s * 2.8346
    c.setFont("Inter-Medium", logo_size_pt)
    set_rgb(c, BLACK)

    # Tracking (prostrkání) realizujeme ručně — vypočteme šířku znaků a roztáhneme
    def draw_tracked(text, font, size_pt, cx, cy, tracking_em=0.35):
        # tracking_em — extra mezera mezi znaky jako podíl velikosti fontu
        widths = [pdfmetrics.stringWidth(ch, font, size_pt) for ch in text]
        extra = tracking_em * size_pt
        total = sum(widths) + extra * (len(text) - 1)
        x0 = cx - total / 2
        cur = x0
        c.setFont(font, size_pt)
        for ch, wch in zip(text, widths):
            c.drawString(cur, cy, ch)
            cur += wch + extra
        return total

    # Y pozice (od horního okraje destičky), v mm
    cx_mm = x_mm + LABEL_W * s / 2
    # Logo: 9 mm od horního okraje
    logo_y_mm = y_mm + LABEL_H * s - 9.0 * s
    draw_tracked("K Y M E R A", "Inter-Medium", logo_size_pt,
                 cx_mm * mm, logo_y_mm * mm, tracking_em=0.30)

    # Tenká linka pod logem
    line_y_mm = logo_y_mm - 2.2 * s
    line_half = 9.0 * s  # poloviční šířka linky v mm
    c.setLineWidth(0.12 * mm * s)
    set_rgb(c, BLACK)
    c.line((cx_mm - line_half) * mm, line_y_mm * mm,
           (cx_mm + line_half) * mm, line_y_mm * mm)

    # Číslo díla — Inter Regular, malé
    num_size_pt = 2.5 * s * 2.8346
    c.setFont("Inter", num_size_pt)
    num_y_mm = line_y_mm - 3.2 * s
    set_rgb(c, BLACK)
    c.drawCentredString(cx_mm * mm, num_y_mm * mm, kym_number)

    # Název díla — Instrument Serif Italic
    title_size_pt = 4.0 * s * 2.8346
    c.setFont("InstrumentSerif-Italic", title_size_pt)
    title_y_mm = num_y_mm - 4.6 * s
    c.drawCentredString(cx_mm * mm, title_y_mm * mm, artwork_title)

    # Dole malé "kymera.art"
    web_size_pt = 1.9 * s * 2.8346
    c.setFont("Inter", web_size_pt)
    set_rgb(c, GRAY)
    web_y_mm = y_mm + 2.6 * s
    c.drawCentredString(cx_mm * mm, web_y_mm * mm, "kymera.art")
    set_rgb(c, BLACK)


# ---------- POMOCNÉ ----------

def text(c, x_mm, y_mm, s, font="Inter", size_pt=8, color=BLACK):
    set_rgb(c, color)
    c.setFont(font, size_pt)
    c.drawString(x_mm * mm, y_mm * mm, s)


def text_right(c, x_mm, y_mm, s, font="Inter", size_pt=8, color=BLACK):
    set_rgb(c, color)
    c.setFont(font, size_pt)
    c.drawRightString(x_mm * mm, y_mm * mm, s)


def line_mm(c, x1, y1, x2, y2, w_mm=0.15, color=BLACK, dash=None):
    set_rgb(c, color)
    c.setLineWidth(w_mm * mm)
    if dash:
        c.setDash(dash)
    else:
        c.setDash()
    c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)
    c.setDash()


def arrow(c, x1, y1, x2, y2, color=BRASS, w_mm=0.18, head=1.5):
    """Šipka z (x1,y1) do (x2,y2) v mm. Head v mm."""
    import math
    set_rgb(c, color)
    c.setLineWidth(w_mm * mm)
    c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)
    ang = math.atan2(y2 - y1, x2 - x1)
    hx = x2 - head * math.cos(ang - math.radians(22))
    hy = y2 - head * math.sin(ang - math.radians(22))
    hx2 = x2 - head * math.cos(ang + math.radians(22))
    hy2 = y2 - head * math.sin(ang + math.radians(22))
    p = c.beginPath()
    p.moveTo(x2 * mm, y2 * mm)
    p.lineTo(hx * mm, hy * mm)
    p.lineTo(hx2 * mm, hy2 * mm)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def page_header(c, title, subtitle=None, page_num="", total=3):
    # Horní lišta
    set_rgb(c, BLACK)
    c.setFont("Inter-Medium", 9)
    c.drawString(MARGIN, PAGE_H - MARGIN, "KYMERA")
    c.setFont("Inter", 8)
    set_rgb(c, GRAY)
    c.drawString(MARGIN + 18 * mm, PAGE_H - MARGIN, "Mosazný štítek originality — výrobní podklad")
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN, f"List {page_num} / {total}")

    # Jemná linka
    set_rgb(c, LIGHT_GRAY)
    c.setLineWidth(0.2)
    c.line(MARGIN, PAGE_H - MARGIN - 3 * mm, PAGE_W - MARGIN, PAGE_H - MARGIN - 3 * mm)

    # Titul
    set_rgb(c, BLACK)
    c.setFont("Inter-Medium", 14)
    c.drawString(MARGIN, PAGE_H - MARGIN - 11 * mm, title)
    if subtitle:
        c.setFont("Inter", 9)
        set_rgb(c, GRAY)
        c.drawString(MARGIN, PAGE_H - MARGIN - 16 * mm, subtitle)

    # Patička
    set_rgb(c, LIGHT_GRAY)
    c.setLineWidth(0.2)
    c.line(MARGIN, MARGIN, PAGE_W - MARGIN, MARGIN)
    set_rgb(c, GRAY)
    c.setFont("Inter", 7)
    c.drawString(MARGIN, MARGIN - 4 * mm, "KYMERA · kymera.art")
    c.drawCentredString(PAGE_W / 2, MARGIN - 4 * mm, "Výkres není v měřítku tisku — kóty jsou závazné.")
    c.drawRightString(PAGE_W - MARGIN, MARGIN - 4 * mm, "Kontakt: Jakub Nowicki · +420 734 548 884")


# ---------- STRANA 1 ----------

def page1(c):
    page_header(c, "List 1 — Návrh destičky", "Skutečná velikost (1:1) a zvětšenina (2:1) s kótami", "1")

    # --- 1:1 vpravo nahoře (aby nezasahovalo do header textu vlevo) ---
    label_x_mm = PAGE_W / mm - MARGIN / mm - LABEL_W - 5
    label_y_mm = PAGE_H / mm - 65
    # popisek
    text(c, label_x_mm, label_y_mm + LABEL_H + 5, "Měřítko 1 : 1 (skutečná velikost)",
         font="Inter-Medium", size_pt=9)
    text(c, label_x_mm, label_y_mm + LABEL_H + 1.8, "Tisk PDF na 100 % bez přizpůsobení.",
         font="Inter", size_pt=7.5, color=GRAY)
    draw_label(c, label_x_mm, label_y_mm, scale=1.0)

    # Jednoduché kóty pod 1:1
    # šířka
    cy = label_y_mm - 4
    line_mm(c, label_x_mm, cy, label_x_mm + LABEL_W, cy, w_mm=0.12, color=GRAY)
    line_mm(c, label_x_mm, cy - 1.2, label_x_mm, cy + 1.2, w_mm=0.12, color=GRAY)
    line_mm(c, label_x_mm + LABEL_W, cy - 1.2, label_x_mm + LABEL_W, cy + 1.2, w_mm=0.12, color=GRAY)
    text(c, label_x_mm + LABEL_W / 2 - 5, cy - 3.5, "60 mm", font="Inter", size_pt=7, color=GRAY)
    # výška
    cx = label_x_mm + LABEL_W + 4
    line_mm(c, cx, label_y_mm, cx, label_y_mm + LABEL_H, w_mm=0.12, color=GRAY)
    line_mm(c, cx - 1.2, label_y_mm, cx + 1.2, label_y_mm, w_mm=0.12, color=GRAY)
    line_mm(c, cx - 1.2, label_y_mm + LABEL_H, cx + 1.2, label_y_mm + LABEL_H, w_mm=0.12, color=GRAY)
    text(c, cx + 1.5, label_y_mm + LABEL_H / 2 - 1, "30 mm", font="Inter", size_pt=7, color=GRAY)

    # --- 2:1 níže (měřítko 2:1 — destička 120×60 mm — vejde se s pop. po stranách) ---
    SC = 2.0
    big_w = LABEL_W * SC
    big_h = LABEL_H * SC
    big_x = (PAGE_W / mm - big_w) / 2  # vycentrovat
    big_y = MARGIN / mm + 50  # nad patičkou

    text(c, big_x, big_y + big_h + 6, "Měřítko 2 : 1 (zvětšenina s technickými popisky)",
         font="Inter-Medium", size_pt=9)
    draw_label(c, big_x, big_y, scale=SC)

    # --- Popisky šipkami (brass) ---
    # 1) Rozměr šířky 60 mm — pod destičkou
    cy = big_y - 8
    line_mm(c, big_x, cy, big_x + big_w, cy, w_mm=0.18, color=BRASS)
    line_mm(c, big_x, cy - 1.5, big_x, cy + 1.5, w_mm=0.18, color=BRASS)
    line_mm(c, big_x + big_w, cy - 1.5, big_x + big_w, cy + 1.5, w_mm=0.18, color=BRASS)
    text(c, big_x + big_w / 2 - 8, cy - 5, "60 mm", font="Inter-Medium", size_pt=8.5, color=BRASS)

    # Strany: mají cca (210 - 120) / 2 = 45 mm na popisky.
    # Levý a pravý sloupec textových popisků.
    LX = big_x - 38  # začátek levého sloupce popisků
    RX = big_x + big_w + 19  # začátek pravého sloupce popisků (165 + 19 = 184; margin = 192)

    # 2) Rozměr výšky 30 mm — těsně vpravo od destičky (mezi destinkou a textovým sloupcem)
    cx = big_x + big_w + 14
    line_mm(c, cx, big_y, cx, big_y + big_h, w_mm=0.18, color=BRASS)
    line_mm(c, cx - 1.5, big_y, cx + 1.5, big_y, w_mm=0.18, color=BRASS)
    line_mm(c, cx - 1.5, big_y + big_h, cx + 1.5, big_y + big_h, w_mm=0.18, color=BRASS)
    text(c, cx + 2, big_y + big_h / 2 - 1, "30 mm", font="Inter-Medium", size_pt=8.5, color=BRASS)

    # 3) Zaoblený roh R3 — šipka do levého horního rohu
    rx = big_x + CORNER_R * SC * 0.3
    ry = big_y + big_h - CORNER_R * SC * 0.3
    arrow(c, LX + 18, big_y + big_h + 4, rx, ry, color=BRASS)
    text(c, LX, big_y + big_h + 6, "Rohy R3 (zaoblené)",
         font="Inter-Medium", size_pt=8, color=BRASS)

    # 4) Otvor Ø 1.5 mm — šipka na otvor (pravý horní)
    hole_x = big_x + big_w - HOLE_INSET * SC
    hole_y = big_y + big_h - HOLE_INSET * SC
    arrow(c, RX + 8, big_y + big_h + 4, hole_x + 1, hole_y + 1, color=BRASS)
    text(c, RX, big_y + big_h + 6, "Otvor Ø 1.5 (4×)",
         font="Inter-Medium", size_pt=8, color=BRASS)

    # 5) Logo — font Inter Medium, prostrkáno (levý sloupec)
    logo_target_x = big_x + big_w / 2
    logo_target_y = big_y + big_h - 9 * SC
    arrow(c, LX + 38, logo_target_y + 1, logo_target_x - 14, logo_target_y + 1, color=BRASS)
    text(c, LX, logo_target_y + 3, "Logo: Inter Medium", font="Inter-Medium", size_pt=8, color=BRASS)
    text(c, LX, logo_target_y, "tracking +30, v 4.2 mm", font="Inter", size_pt=6.8, color=BRASS)

    # 6) Tenká linka pod logem (pravý sloupec)
    line_target_y = logo_target_y - 2.2 * SC
    arrow(c, RX - 4, line_target_y, big_x + big_w - 4, line_target_y, color=BRASS)
    text(c, RX, line_target_y + 2.5, "Linka 0.12 mm", font="Inter-Medium", size_pt=8, color=BRASS)
    text(c, RX, line_target_y - 0.3, "šířka 18 mm", font="Inter", size_pt=6.8, color=BRASS)

    # 7) Číslo díla — Inter Regular (levý sloupec)
    num_target_y = line_target_y - 3.2 * SC
    arrow(c, LX + 38, num_target_y, big_x + 4, num_target_y, color=BRASS)
    text(c, LX, num_target_y + 2.5, "Číslo: Inter Regular", font="Inter-Medium", size_pt=8, color=BRASS)
    text(c, LX, num_target_y - 0.3, "výška 2.5 mm", font="Inter", size_pt=6.8, color=BRASS)

    # 8) Název díla — Instrument Serif Italic (pravý sloupec)
    title_target_y = num_target_y - 4.6 * SC
    arrow(c, RX - 4, title_target_y, big_x + big_w - 4, title_target_y, color=BRASS)
    text(c, RX, title_target_y + 2.5, "Inst. Serif Italic",
         font="Inter-Medium", size_pt=8, color=BRASS)
    text(c, RX, title_target_y - 0.3, "výška 4.0 mm", font="Inter", size_pt=6.8, color=BRASS)

    # 9) kymera.art dole (levý sloupec)
    web_target_y = big_y + 2.6 * SC
    arrow(c, LX + 38, web_target_y, big_x + big_w / 2 - 6, web_target_y, color=BRASS)
    text(c, LX, web_target_y + 2.5, "kymera.art", font="Inter-Medium", size_pt=8, color=BRASS)
    text(c, LX, web_target_y - 0.3, "Inter Regular, 1.9 mm", font="Inter", size_pt=6.8, color=BRASS)

    # 10) Hloubka gravírování — souhrnný popisek pod 3:1 vlevo
    text(c, big_x, big_y - 18, "Hloubka gravírování: 0.3 mm",
         font="Inter-Medium", size_pt=9, color=BRASS)
    text(c, big_x, big_y - 21.5,
         "Veškerý text a linka jsou gravírovány laserem do kartáčované mosazi.",
         font="Inter", size_pt=7.5, color=GRAY)

    c.showPage()


# ---------- STRANA 2 ----------

def page2(c):
    page_header(c, "List 2 — Specifikace pro výrobce",
                "Závazné parametry pro rytí / laserovou gravírovnu (česky, v mm)", "2")

    y = PAGE_H / mm - 42  # mm od dolního okraje stránky (reportlab Y roste vzhůru)
    x = MARGIN / mm

    def row(label, value, y_mm):
        text(c, x, y_mm, label, font="Inter-Medium", size_pt=9.5)
        text(c, x + 55, y_mm, value, font="Inter", size_pt=9.5)
        # jemná linka pod
        set_rgb(c, LIGHT_GRAY)
        c.setLineWidth(0.15)
        c.line(x * mm, (y_mm - 2.5) * mm, (PAGE_W / mm - MARGIN / mm) * mm, (y_mm - 2.5) * mm)

    rows = [
        ("Materiál", "mosaz, tloušťka 1.5 mm"),
        ("Povrch", "kartáčovaná (broušená podélně), patina volitelně"),
        ("Rozměry", "60 × 30 mm (š × v)"),
        ("Tloušťka", "1.5 mm"),
        ("Rohy", "zaoblené R3 (rádius 3 mm, všechny 4 rohy)"),
        ("Otvory", "2× Ø 1.5 mm v dolních rozích, 4 mm od hran"),
        ("Alternativa fixace", "lepené spojení (oboustranná páska 3M VHB nebo epoxid)"),
        ("Gravírování", "laserové, hloubka 0.3 mm"),
        ("Font — logo a text", "Inter Medium / Inter Regular"),
        ("Font — název díla", "Instrument Serif Italic"),
        ("Velikost — logo „K Y M E R A“", "výška 4.2 mm, prostrkání +30"),
        ("Velikost — linka pod logem", "šířka 18 mm, tloušťka 0.12 mm"),
        ("Velikost — číslo díla", "výška 2.5 mm (Inter Regular)"),
        ("Velikost — název díla", "výška 4.0 mm (Instrument Serif Italic)"),
        ("Velikost — kymera.art", "výška 1.9 mm (Inter Regular)"),
        ("Tolerance rozměrů", "± 0.2 mm"),
        ("Hrany", "odjehleno, jemně sraženo"),
        ("Balení", "po 1 ks v sáčku s ochrannou fólií"),
    ]

    line_y = y
    for label, value in rows:
        row(label, value, line_y)
        line_y -= 7

    # --- Box: Schválení ---
    box_y = line_y - 6
    box_h = 26
    set_rgb(c, BRASS)
    c.setLineWidth(0.4)
    c.rect(x * mm, (box_y - box_h) * mm, ((PAGE_W / mm - 2 * MARGIN / mm)) * mm, box_h * mm,
           stroke=1, fill=0)
    text(c, x + 3, box_y - 5, "Schválení vzorku před sériovou výrobou",
         font="Inter-Medium", size_pt=10, color=BRASS)
    text(c, x + 3, box_y - 10,
         "Před sériovou výrobou prosíme o zaslání 1 ks vzorku k odsouhlasení.",
         font="Inter", size_pt=9, color=BLACK)
    text(c, x + 3, box_y - 14.5,
         "Kontakt na schválení a obchodní komunikaci:",
         font="Inter", size_pt=9, color=BLACK)
    text(c, x + 3, box_y - 19,
         "Jakub Nowicki  ·  +420 734 548 884  ·  KYMERA  ·  kymera.art",
         font="Inter-Medium", size_pt=9.5, color=BLACK)

    # --- Poznámky ---
    notes_y = box_y - box_h - 8
    text(c, x, notes_y, "Poznámky", font="Inter-Medium", size_pt=9.5)
    notes = [
        "• Gravírování musí být ostré, čitelné, bez otřepů.",
        "• Po gravírování očistit a chránit před oxidací (matný lak nebo ochranná fólie).",
        "• Číslo díla a název jsou variabilní — finální podklad pro každý kus dodá KYMERA jako vektor / textový soubor.",
        "• Layout všech variant zachovává stejné pozice — viz List 3 (mock-up).",
        "• PDF není určeno k tisku ve výrobním měřítku — výroba probíhá dle kót, ne dle náhledu.",
    ]
    ny = notes_y - 5
    for n in notes:
        text(c, x, ny, n, font="Inter", size_pt=8.5, color=BLACK)
        ny -= 5

    c.showPage()


# ---------- STRANA 3 ----------

def page3(c):
    page_header(c, "List 3 — Mock-up variant číslování",
                "6 reálných příkladů, jak budou destičky vypadat po gravírování", "3")

    samples = [
        ("KYM — 2026 — 001", "Tichá síla I."),
        ("KYM — 2026 — 002", "Tichá síla II."),
        ("KYM — 2026 — 003", "Mlčení kamene"),
        ("KYM — 2026 — 004", "Černý ranní pták"),
        ("KYM — 2026 — 005", "Pole bez stínu"),
        ("KYM — 2026 — 006", "Zlomená orchidea"),
    ]

    # Mřížka 2 sloupce × 3 řádky, každý kus v měřítku 1.8:1 pro lepší čitelnost
    SC = 1.8
    cell_w = LABEL_W * SC
    cell_h = LABEL_H * SC

    cols = 2
    rows = 3
    total_w = PAGE_W / mm - 2 * MARGIN / mm
    total_h = PAGE_H / mm - 2 * MARGIN / mm - 30  # nad header
    gap_x = (total_w - cols * cell_w) / (cols + 1)
    gap_y = ((total_h - 8) - rows * cell_h) / (rows + 1)

    start_x = MARGIN / mm + gap_x
    start_y_top = PAGE_H / mm - MARGIN / mm - 28  # pod headerem

    for i, (num, title) in enumerate(samples):
        col = i % cols
        row = i // cols
        x_mm = start_x + col * (cell_w + gap_x)
        y_mm = start_y_top - (row + 1) * cell_h - row * gap_y

        draw_label(c, x_mm, y_mm, scale=SC,
                   kym_number=num, artwork_title=title)

        # Popisek pod destičkou — "Příklad N"
        text(c, x_mm, y_mm - 5, f"Příklad {i + 1}",
             font="Inter-Medium", size_pt=8.5, color=BLACK)
        text(c, x_mm, y_mm - 8.2, f"{num}  ·  „{title}“",
             font="Inter", size_pt=7.5, color=GRAY)

    # Spodní poznámka
    nx = MARGIN / mm
    ny = MARGIN / mm + 8
    text(c, nx, ny, "Poznámka k mock-upu",
         font="Inter-Medium", size_pt=9, color=BLACK)
    text(c, nx, ny - 4,
         "Náhled je v měřítku 1.8 : 1 pro čitelnost. Skutečná velikost destičky zůstává 60 × 30 mm (viz List 1).",
         font="Inter", size_pt=8, color=GRAY)
    text(c, nx, ny - 7.5,
         "Layout, fonty a velikosti jsou identické pro všechny varianty — mění se pouze pořadové číslo a název díla.",
         font="Inter", size_pt=8, color=GRAY)

    c.showPage()


# ---------- MAIN ----------

def main():
    out = Path("/home/user/workspace/kymera/print/certifikat/kymera-stitek-vyroba.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out), pagesize=A4)
    c.setTitle("KYMERA — Mosazný štítek originality (výrobní podklad)")
    c.setAuthor("KYMERA / Jakub Nowicki")
    c.setSubject("Výrobní podklad pro rytce / laserovou gravírovnu")

    page1(c)
    page2(c)
    page3(c)

    c.save()
    print(f"OK: {out}")


if __name__ == "__main__":
    main()
