"""
KYMERA — zpracování fotek z Drive do brand-ready assetů.

Krok 2 (oprava): 8 unikátních zdrojů → 8 unikátních pozic. Žádné duplikáty.
- 7 AI vizualizací (Gemini): a02–a08
- 1 reálná fotka v interiéru: a01
"""

import os
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove, new_session

ROOT = Path("/home/user/workspace/kymera/assets")
SRC = ROOT / "source"
WEB = ROOT / "img"
TRANSPARENT = ROOT / "img-transparent"

WEB.mkdir(parents=True, exist_ok=True)
TRANSPARENT.mkdir(parents=True, exist_ok=True)

GRAPHITE = (21, 20, 15)  # #15140f

# rembg session
session = new_session("isnet-general-use")


def remove_watermark(img: Image.Image) -> Image.Image:
    """Odstraní AI watermark (Gemini/ChatGPT diamond) v pravém dolním rohu."""
    img = img.copy()
    w, h = img.size
    box_size = 65
    margin = 8
    x1 = w - box_size - margin
    y1 = h - box_size - margin
    x2 = w - margin
    y2 = h - margin

    patch_h = 25
    patch = img.crop((x1, max(0, y1 - patch_h), x2, y1)).resize((x2 - x1, y2 - y1))
    patch = patch.filter(ImageFilter.GaussianBlur(radius=2))
    img.paste(patch, (x1, y1))
    return img


def grade(img: Image.Image, brightness=1.0, contrast=1.08, color=1.05) -> Image.Image:
    """
    Lehký editorial grading. Brightness 1.0 = neutrální (sochy se neztratí proti tmavému pozadí webu).
    """
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(color)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=3))
    return img


def crop_to_ratio(img: Image.Image, target_ratio: float, vertical_offset: float = 0.35) -> Image.Image:
    """Center-crop na požadovaný poměr w/h. Vertical_offset 0.35 = nechá víc nad sochou než pod."""
    w, h = img.size
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        x1 = (w - new_w) // 2
        return img.crop((x1, 0, x1 + new_w, h))
    else:
        new_h = int(w / target_ratio)
        y1 = int((h - new_h) * vertical_offset)
        return img.crop((0, y1, w, y1 + new_h))


def upscale_if_small(img: Image.Image, min_w: int) -> Image.Image:
    if img.width < min_w:
        scale = min_w / img.width
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return img


def process_one(src: str, out_name: str, ratio: float, min_w: int,
                vertical_offset: float = 0.35, brightness: float = 1.0,
                strip_watermark: bool = True):
    src_path = SRC / src
    print(f"  → {src} → {out_name}.jpg ({ratio:.2f}, min {min_w}px, vy={vertical_offset})")
    img = Image.open(src_path).convert("RGB")
    if strip_watermark:
        img = remove_watermark(img)
    img = grade(img, brightness=brightness)
    img = crop_to_ratio(img, ratio, vertical_offset=vertical_offset)
    img = upscale_if_small(img, min_w)
    out_path = WEB / f"{out_name}.jpg"
    img.save(out_path, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"    ✓ {out_path.stat().st_size // 1024} KB")


def process_transparent(src: str, out_name: str):
    src_path = SRC / src
    print(f"  → transparent: {src} → {out_name}.png")
    with open(src_path, "rb") as f:
        data = f.read()
    output = remove(data, session=session)
    out_path = TRANSPARENT / f"{out_name}.png"
    with open(out_path, "wb") as f:
        f.write(output)
    print(f"    ✓ {out_path.stat().st_size // 1024} KB")


# ===================== MAPPING =====================
# Každý zdroj se použije max jednou. Žádné duplikáty.
# Formát: (zdroj, out_name, target_ratio_w_h, min_width, vertical_offset, brightness, strip_watermark)
MAPPING = [
    # HERO — maska s kabely (a07), široká horizontální, dramatická
    ("a07_nnfre6.png", "hero", 16/9, 2400, 0.4, 1.0, True),

    # KOLEKCE (4:5)
    # figurativní → figura pod lampou (a05)
    ("a05_fybkzq.png", "collection-figurative", 4/5, 1600, 0.25, 1.05, True),
    # busty → busta z profilu (a02)
    ("a02_2gc3w2.png", "collection-busts", 4/5, 1600, 0.2, 1.0, True),
    # industriální → polopostava s ozubenými koly (a04)
    ("a04_65fldd.png", "collection-industrial", 4/5, 1600, 0.15, 1.0, True),

    # VYBRANÁ DÍLA (4:5) — 3 položky
    # work-01: figura v ateliéru (a08)
    ("a08_u8lvhq.png", "work-01", 4/5, 1600, 0.2, 1.05, True),
    # work-02: figura v betonovém prostoru (a06)
    ("a06_gyah5t.png", "work-02", 4/5, 1600, 0.2, 1.05, True),
    # work-03: štíhlá figura, frontální (a03)
    ("a03_8yoe31.png", "work-03", 4/5, 1600, 0.15, 1.05, True),

    # ABOUT — reálná fotka v interiéru (a01) — ne AI, žádný watermark
    ("a01_53e2b91f.jpeg", "about", 4/5, 1400, 0.3, 1.05, False),
]

# Transparent PNG masters (pro budoucí použití — ne pro web)
TRANSPARENT_MAPPING = [
    ("a02_2gc3w2.png", "kymera-bust-01"),
    ("a03_8yoe31.png", "kymera-figure-01"),
    ("a04_65fldd.png", "kymera-bust-02"),
    ("a05_fybkzq.png", "kymera-figure-02"),
    ("a06_gyah5t.png", "kymera-figure-03"),
    ("a07_nnfre6.png", "kymera-mask-01"),
    ("a08_u8lvhq.png", "kymera-figure-04"),
]


def main():
    print("=" * 60)
    print("KYMERA — photo processing v2 (čistá mapa, žádné duplikáty)")
    print("=" * 60)

    # Smaž staré web JPG (jistota)
    for f in WEB.glob("*.jpg"):
        f.unlink()

    print("\n[1/2] Web JPG:")
    for entry in MAPPING:
        process_one(*entry)

    print("\n[2/2] Transparent PNG (masters):")
    for src, out_name in TRANSPARENT_MAPPING:
        process_transparent(src, out_name)

    print("\n✓ Hotovo.")


if __name__ == "__main__":
    main()
