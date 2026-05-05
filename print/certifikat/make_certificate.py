"""
KYMERA — Papírový certifikát originality (A5, na výšku)
Luxusní layout, brass akcenty, Instrument Serif + Inter.
Použití: python3 make_certificate.py
"""
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os

FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'fonts')
pdfmetrics.registerFont(TTFont('Inter', os.path.join(FONT_DIR, 'Inter-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Inter-Medium', os.path.join(FONT_DIR, 'Inter-Medium.ttf')))
pdfmetrics.registerFont(TTFont('Serif', os.path.join(FONT_DIR, 'InstrumentSerif-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Serif-Italic', os.path.join(FONT_DIR, 'InstrumentSerif-Italic.ttf')))

# Paleta
INK = HexColor('#1a1a1a')           # Téměř černá
BRASS = HexColor('#b8925a')         # Mosaz
BRASS_LIGHT = HexColor('#d4aa72')   # Světlejší mosaz pro akcenty
PAPER = HexColor('#faf6ef')         # Krémová bílá (papír)
MUTED = HexColor('#7a7166')         # Tlumená pro popisky
HAIRLINE = HexColor('#cdc4b3')      # Tenká linka

PAGE_W, PAGE_H = A5  # 148 x 210 mm
MARGIN = 14 * mm

def draw_certificate(c, data):
    """data = dict s klíči: cislo, nazev, autor, datum_vyroby, materialy, povrch, rozmery, hmotnost, kupujici (volitelné)"""
    # Pozadí krémové
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # ── Vnější tenký rámeček (mosaz) ──
    c.setStrokeColor(BRASS)
    c.setLineWidth(0.5)
    inset = 8 * mm
    c.rect(inset, inset, PAGE_W - 2*inset, PAGE_H - 2*inset, fill=0, stroke=1)

    # ── Vnitřní decorative line ──
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.3)
    inset2 = 10 * mm
    c.rect(inset2, inset2, PAGE_W - 2*inset2, PAGE_H - 2*inset2, fill=0, stroke=1)

    # ── Header: KYMERA ──
    c.setFillColor(INK)
    c.setFont('Inter-Medium', 11)
    title = "K Y M E R A"
    c.drawCentredString(PAGE_W/2, PAGE_H - 22*mm, title)

    # Mini brass linka pod logem
    line_w = 12 * mm
    c.setStrokeColor(BRASS)
    c.setLineWidth(0.6)
    c.line(PAGE_W/2 - line_w/2, PAGE_H - 25*mm, PAGE_W/2 + line_w/2, PAGE_H - 25*mm)

    # ── Eyebrow ──
    c.setFillColor(BRASS)
    c.setFont('Inter-Medium', 7)
    c.drawCentredString(PAGE_W/2, PAGE_H - 33*mm, "C E R T I F I K Á T   O R I G I N A L I T Y")

    # ── Hlavní titul (serif italic) ──
    c.setFillColor(INK)
    c.setFont('Serif-Italic', 26)
    c.drawCentredString(PAGE_W/2, PAGE_H - 48*mm, "Originální umělecké dílo")

    c.setFont('Serif', 13)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W/2, PAGE_H - 56*mm, "Jeden v jednom · bez edice · bez reprodukce")

    # ── Číslo díla (velký brass) ──
    c.setFillColor(BRASS)
    c.setFont('Serif', 18)
    c.drawCentredString(PAGE_W/2, PAGE_H - 72*mm, data['cislo'])

    # ── Tělo: dvousloupcová tabulka detailů ──
    y = PAGE_H - 88 * mm
    row_h = 7 * mm
    label_x = 20 * mm
    value_x = 70 * mm

    rows = [
        ("Název díla", data['nazev']),
        ("Autor", data['autor']),
        ("Datum dokončení", data['datum_vyroby']),
        ("Materiály", data['materialy']),
        ("Povrchová úprava", data['povrch']),
        ("Rozměry (v × š × h)", data['rozmery']),
        ("Hmotnost", data['hmotnost']),
    ]
    if data.get('kupujici'):
        rows.append(("Sběratel", data['kupujici']))

    for label, value in rows:
        c.setFillColor(MUTED)
        c.setFont('Inter', 7.5)
        c.drawString(label_x, y, label.upper())

        c.setFillColor(INK)
        c.setFont('Inter-Medium', 9.5)
        # Wrap dlouhý text — respektuj závorky (drž spolu "(...)")
        max_w = PAGE_W - value_x - MARGIN - 6*mm
        from reportlab.pdfbase.pdfmetrics import stringWidth
        if stringWidth(value, 'Inter-Medium', 9.5) > max_w:
            # Najdi nejvhodnější mezeru pro zalomení (mimo závorky)
            words = value.split(' ')
            line1, line2 = '', ''
            paren_depth = 0
            split_idx = -1
            # Postupuj a hledej poslední mezeru kdy paren_depth==0 a line1 ještě se vejde
            cur = ''
            for i, w in enumerate(words):
                test = (cur + ' ' + w).strip()
                if stringWidth(test, 'Inter-Medium', 9.5) <= max_w:
                    cur = test
                    # spočítej závorky v cur (pro reálné rozhodnutí kde lámat)
                    if '(' in w: paren_depth += w.count('(')
                    if ')' in w: paren_depth -= w.count(')')
                    if paren_depth == 0:
                        split_idx = i
                else:
                    break
            if split_idx >= 0:
                line1 = ' '.join(words[:split_idx+1])
                line2 = ' '.join(words[split_idx+1:])
            else:
                # fallback
                line1 = cur
                line2 = ' '.join(words[len(cur.split()):])
            c.drawString(value_x, y, line1)
            c.setFont('Inter', 8.5)
            c.drawString(value_x, y - 3.5*mm, line2)
            y -= row_h + 3*mm
        else:
            c.drawString(value_x, y, value)
            y -= row_h

    # ── Tenká linka před prohlášením ──
    y -= 3*mm
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.3)
    c.line(MARGIN + 6*mm, y, PAGE_W - MARGIN - 6*mm, y)
    y -= 6*mm

    # ── Prohlášení ──
    c.setFillColor(INK)
    c.setFont('Serif-Italic', 10)
    statement = [
        "Tímto stvrzuji, že výše uvedené dílo je",
        "originál, vytvořený ručně v ateliéru KYMERA.",
        "Žádná část díla není reprodukcí ani edicí."
    ]
    for line in statement:
        c.drawCentredString(PAGE_W/2, y, line)
        y -= 4.5*mm

    # ── Podpis ──
    y -= 6*mm
    sig_w = 40 * mm
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.line(PAGE_W/2 - sig_w/2, y, PAGE_W/2 + sig_w/2, y)
    c.setFillColor(MUTED)
    c.setFont('Inter', 7)
    c.drawCentredString(PAGE_W/2, y - 4*mm, "JAKUB NOWICKI · AUTOR")

    # ── Footer ──
    c.setFillColor(MUTED)
    c.setFont('Inter', 6.5)
    c.drawString(MARGIN, MARGIN - 1*mm, "kymera.art")
    c.drawRightString(PAGE_W - MARGIN, MARGIN - 1*mm, "Frýdecká 851, 739 61 Třinec, ČR")


def main():
    out = os.path.join(os.path.dirname(__file__), 'kymera-certifikat.pdf')
    c = canvas.Canvas(out, pagesize=A5)

    # Vzorová data (nahradíš per dílo)
    sample = {
        'cislo': 'KYM — 2026 — 001',
        'nazev': 'Tichá síla I.',
        'autor': 'Jakub Nowicki',
        'datum_vyroby': '5. května 2026',
        'materialy': 'Dřevo (lípa), mechanické díly (převody, písty)',
        'povrch': 'Patinovaná mosaz, ruční nátěr',
        'rozmery': '62 × 24 × 22 cm',
        'hmotnost': '8,4 kg',
        'kupujici': '',  # prázdné = "připraveno pro vyplnění perem"
    }
    draw_certificate(c, sample)

    c.showPage()
    c.save()
    print(f"\n✓ {out}")


if __name__ == '__main__':
    main()
