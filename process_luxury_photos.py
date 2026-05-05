"""KYMERA — pipeline LUXURY v2.
Přebírá hotové transparentní PNG soch a sází je do atmosférického prostředí
s texturou, dramatickým světlem a stínem.

Cíl: vypadat jako fotky z magazínu Architectural Digest / Sotheby's catalog.
"""
import os
import math
import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageOps

ROOT = os.path.dirname(__file__)
TRANS_DIR = os.path.join(ROOT, "assets", "img-transparent")
OUT_DIR = os.path.join(ROOT, "assets", "img")

# Paleta — graphite + warm
DEEP = (14, 13, 12)         # nejhlubší černá
GRAPHITE = (28, 27, 26)     # base
GRAPHITE_HI = (52, 50, 48)  # světlejší (pro hero)
WARM_HI = (74, 64, 48)      # warm spotlight
GLOW = (180, 150, 100)      # jemný brass glow


def add_noise(img, intensity=6):
    """Přidá subtilní filmový grain — proti banding pruhům v gradientu."""
    w, h = img.size
    arr = np.array(img, dtype=np.int16)
    noise = np.random.randint(-intensity, intensity + 1, (h, w, 1), dtype=np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def make_atmospheric_bg(size, hero=False):
    """Atmosférické pozadí: tmavý gradient + warm spotlight + podlaha + grain."""
    w, h = size

    # 1. vertikální gradient pomocí numpy (rychlé)
    top = np.array(GRAPHITE_HI if hero else (38, 36, 34), dtype=np.float32)
    bot = np.array(DEEP, dtype=np.float32)
    t = np.linspace(0, 1, h, dtype=np.float32).reshape(h, 1, 1)
    grad = top * (1 - t) + bot * t
    arr = np.broadcast_to(grad, (h, w, 3)).copy()

    # 2. warm spotlight
    cx, cy = (w * 0.25, h * 0.30) if not hero else (w * 0.18, h * 0.35)
    radius = max(w, h) * 0.55
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    intensity = np.clip(1 - dist / radius, 0, 1) ** 2.2
    warm = np.array(WARM_HI, dtype=np.float32)
    spot = intensity[..., None] * warm

    # screen blend: 1 - (1-a)(1-b) pro hodnoty 0-255
    arr = 255 - (255 - arr) * (255 - spot) / 255
    arr = np.clip(arr, 0, 255)

    # 3. podlaha (ztmavnění dolí třetiny)
    floor_y = int(h * 0.78)
    floor_t = np.zeros(h, dtype=np.float32)
    floor_t[floor_y:] = np.linspace(0, 0.25, h - floor_y)
    floor_t = floor_t.reshape(h, 1, 1)
    arr = arr * (1 - floor_t)

    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    # 4. blur pro měkkost + grain
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    img = add_noise(img, intensity=5)

    return img


def feather_alpha(rgba, radius=2):
    """Mírně rozmaže alpha kanál — odstraní rembg ostrý lem."""
    r, g, b, a = rgba.split()
    a = a.filter(ImageFilter.GaussianBlur(radius=radius))
    # mírně erodovat aby socha nezesvětlala v okraji
    a = a.point(lambda v: max(0, min(255, int((v - 12) * 1.08))))
    return Image.merge("RGBA", (r, g, b, a))


def cast_shadow_under(transparent, target_size, subject_pos, subject_size,
                      shadow_offset=(0, 22), spread=(1.2, 0.35), opacity=110, blur=18):
    """Vytvoří měkký kontaktní stín pod sochou (eliptický)."""
    tw, th = target_size
    sx, sy = subject_pos
    sw, sh = subject_size

    shadow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)

    # střed stínu = paty subjectu + offset
    cx = sx + sw / 2 + shadow_offset[0]
    cy = sy + sh + shadow_offset[1]
    rx = sw * spread[0] / 2
    ry = sh * spread[1] / 2
    sd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
               fill=(0, 0, 0, opacity))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    return shadow


def color_grade(img, contrast=1.08, saturation=0.92, brightness=1.02,
                warm_r=1.03, warm_b=0.96):
    """Filmové dolazení."""
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(saturation)
    img = ImageEnhance.Brightness(img).enhance(brightness)
    # warm cast
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * warm_r)))
    b = b.point(lambda v: int(v * warm_b))
    img = Image.merge("RGB", (r, g, b))
    # mild sharpen
    img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=80, threshold=2))
    return img


def crop_to_aspect(img, aspect, vertical_align=0.42):
    """Crop na zadaný aspect ratio."""
    w, h = img.size
    if w / h > aspect:
        # moc široký
        nw = int(h * aspect)
        x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    else:
        nh = int(w / aspect)
        y = int((h - nh) * vertical_align)
        return img.crop((0, y, w, y + nh))


def composite_luxury(transparent_path, target_size, subject_scale=0.85,
                     v_offset=0.04, h_align=0.5, hero=False):
    """Hlavní složení."""
    print(f"  → {os.path.basename(transparent_path)}")

    # 1. načti transparentní sochu, feather
    sub = Image.open(transparent_path).convert("RGBA")
    sub = feather_alpha(sub, radius=2)

    bbox = sub.getbbox()
    if bbox:
        sub = sub.crop(bbox)

    sw, sh = sub.size
    tw, th = target_size

    # 2. škála subjectu — nech kolem prostoru
    avail_w = tw * subject_scale
    avail_h = th * subject_scale
    scale = min(avail_w / sw, avail_h / sh)
    new_w, new_h = int(sw * scale), int(sh * scale)
    sub = sub.resize((new_w, new_h), Image.LANCZOS)

    # 3. pozice
    x = int((tw - new_w) * h_align)
    y = int((th - new_h) / 2 + th * v_offset)

    # 4. atmosférické pozadí
    bg = make_atmospheric_bg(target_size, hero=hero)

    # 5. kontaktní stín pod sochou (na podlaze)
    shadow_layer = cast_shadow_under(
        sub, target_size, (x, y), (new_w, new_h),
        shadow_offset=(15, 18), spread=(1.3, 0.32),
        opacity=140, blur=20
    )
    bg_rgba = bg.convert("RGBA")
    bg_rgba = Image.alpha_composite(bg_rgba, shadow_layer)

    # 6. vlož sochu
    canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
    canvas.paste(sub, (x, y), sub)
    composite = Image.alpha_composite(bg_rgba, canvas)

    # 7. lehký rim-light přes sochu (zvýraznit okraj)
    # Jednoduše: přidám decentní vinettu po obvodu plátna
    vignette = Image.new("L", target_size, 0)
    vd = ImageDraw.Draw(vignette)
    margin = int(min(tw, th) * 0.08)
    vd.rectangle([margin, margin, tw - margin, th - margin], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=int(min(tw, th) * 0.12)))
    dark = Image.new("RGB", target_size, (0, 0, 0))
    composite_rgb = composite.convert("RGB")
    composite_rgb = Image.composite(composite_rgb, dark, vignette)

    # 8. color grade
    composite_rgb = color_grade(composite_rgb)

    return composite_rgb


def process(transparent_name, out_name, target_size, aspect=None,
            subject_scale=0.85, v_offset=0.04, h_align=0.5, hero=False,
            vertical_align=0.42):
    src = os.path.join(TRANS_DIR, transparent_name)
    img = composite_luxury(src, target_size, subject_scale=subject_scale,
                           v_offset=v_offset, h_align=h_align, hero=hero)
    if aspect:
        img = crop_to_aspect(img, aspect, vertical_align=vertical_align)
    out = os.path.join(OUT_DIR, out_name)
    img.save(out, "JPEG", quality=92, optimize=True)
    print(f"     ✓ {out_name} ({img.size[0]}×{img.size[1]})")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)

    # HERO — 16:9, dramatický
    process("IMG_5102.png", "hero.jpg", (1920, 1080),
            subject_scale=0.95, v_offset=0.02, h_align=0.78,
            aspect=16/9, hero=True)

    # KOLEKCE — 4:5
    process("IMG_5106.png", "collection-figurative.jpg", (960, 1200),
            subject_scale=0.82, v_offset=0.03)

    process("IMG_5104.png", "collection-busts.jpg", (960, 1200),
            subject_scale=0.78, v_offset=0.02)

    process("IMG_5114.png", "collection-industrial.jpg", (960, 1200),
            subject_scale=0.82, v_offset=0.03)

    # VYBRANÁ DÍLA — 4:5
    process("IMG_5108.png", "work-01.jpg", (960, 1200),
            subject_scale=0.82, v_offset=0.03)

    process("IMG_5102.png", "work-02.jpg", (960, 1200),
            subject_scale=0.85, v_offset=0.02, h_align=0.5)

    process("IMG_5101.png", "work-03.jpg", (960, 1200),
            subject_scale=0.82, v_offset=0.03)

    # ABOUT — 4:5
    process("IMG_5107.png", "about.jpg", (960, 1200),
            subject_scale=0.80, v_offset=0.03)

    print("\n✓ Hotovo")
