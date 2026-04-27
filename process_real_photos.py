"""
KYMERA — zpracování reálných fotek soch
1. EXIF rotace
2. rembg odstranění pozadí (autosalon)
3. studiové grafitové pozadí + lehký gradient
4. tónové sjednocení (KYMERA paleta: graphite + warm ivory + brass)
5. crop do potřebných formátů (16:9 hero, 4:5 kolekce, 4:5 vybraná díla)
"""

import os
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw
from rembg import remove, new_session

SRC = "/home/user/workspace/kymera/assets/source-real"
TRANSPARENT_DIR = "/home/user/workspace/kymera/assets/img-transparent"
OUT_DIR = "/home/user/workspace/kymera/assets/img"

# KYMERA paleta — tmavé grafitové pozadí (z CSS: --bg-deep, --graphite)
BG_TOP = (28, 30, 33)      # tmavší nahoře
BG_BOTTOM = (18, 19, 21)   # ještě tmavší dole
ACCENT_GLOW = (38, 42, 46) # mírně světlejší centrální záře

# Pro hero zvláště — světlejší pozadí, aby socha byla výraznější
HERO_BG_TOP = (74, 76, 80)
HERO_BG_BOTTOM = (34, 36, 40)

session = new_session("isnet-general-use")


def load_with_exif(path):
    """Otevře a aplikuje EXIF rotaci."""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGBA")


def remove_bg(im_rgba, alpha_threshold=None, kill_saturation=False):
    """Odstraní pozadí přes rembg.
    - alpha_threshold: vyšší = agresivnější ořez
    - kill_saturation: odstraní vysoce saturované piksely (typicky barevná auta v pozadí)
    """
    out = remove(im_rgba, session=session)
    if alpha_threshold is not None:
        r, g, b, a = out.split()
        a = a.point(lambda v: 255 if v >= alpha_threshold else 0)
        out = Image.merge("RGBA", (r, g, b, a))
    if kill_saturation:
        # detekce vysoce saturovaných pikselů (auta) → alpha = 0
        from PIL import ImageColor
        import numpy as np
        arr = np.array(out)
        rgb = arr[..., :3].astype(int)
        max_c = rgb.max(axis=-1)
        min_c = rgb.min(axis=-1)
        sat = (max_c - min_c)
        # vysoce barevné piksely (sat > 60) a ne tmavé (max > 80) = pravděpodobně auto
        mask = (sat > 60) & (max_c > 80)
        arr[mask, 3] = 0
        out = Image.fromarray(arr, mode="RGBA")
    return out


def studio_background(size, vignette=True, hero=False):
    """Vytvoří tmavě grafitové studiové pozadí s jemným gradientem."""
    w, h = size
    top = HERO_BG_TOP if hero else BG_TOP
    bottom = HERO_BG_BOTTOM if hero else BG_BOTTOM
    bg = Image.new("RGB", (w, h), bottom)
    # vertikální gradient
    grad = Image.new("RGB", (1, h), bottom)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        grad.putpixel((0, y), (r, g, b))
    grad = grad.resize((w, h))
    bg.paste(grad)
    
    # jemná centrální záře (warm spotlight)
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(glow)
    cx, cy = w // 2, int(h * 0.45)
    radius = int(min(w, h) * 0.55)
    for r in range(radius, 0, -2):
        alpha = int(40 * (1 - r / radius))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(alpha, alpha, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    bg = Image.blend(bg, Image.eval(glow, lambda v: min(255, v + BG_TOP[0])), 0.25)
    return bg


def composite_on_bg(transparent_rgba, target_size, subject_scale=0.92, vertical_offset=0.05, hero=False, h_align=0.5):
    """Vsadí transparentní subject na studiové pozadí v daném formátu.
    h_align: 0.0 = vlevo, 0.5 = střed, 1.0 = vpravo."""
    tw, th = target_size
    bg = studio_background(target_size, hero=hero)
    
    # zjisti bounding box subjectu
    bbox = transparent_rgba.getbbox()
    if bbox:
        subject = transparent_rgba.crop(bbox)
    else:
        subject = transparent_rgba
    
    sw, sh = subject.size
    # spočítej škálu: nech místo nahoře a dole
    avail_w = tw * subject_scale
    avail_h = th * subject_scale
    scale = min(avail_w / sw, avail_h / sh)
    new_w = int(sw * scale)
    new_h = int(sh * scale)
    subject = subject.resize((new_w, new_h), Image.LANCZOS)
    
    # pozice: vodorovně dle h_align (0=vlevo, 1=vpravo), svisle s offsetem
    x = int((tw - new_w) * h_align)
    y = int((th - new_h) / 2 + th * vertical_offset)
    
    # jemný stín pod subjectem
    shadow = Image.new("RGBA", target_size, (0, 0, 0, 0))
    if subject.mode == "RGBA":
        alpha = subject.split()[-1]
        shadow_layer = Image.new("L", subject.size, 0)
        shadow_layer.paste(alpha, (0, 0))
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(35))
        shadow_rgba = Image.new("RGBA", target_size, (0, 0, 0, 0))
        shadow_rgba.paste((0, 0, 0, 140), (x + 8, y + 18), shadow_layer)
        shadow = shadow_rgba
    
    bg_rgba = bg.convert("RGBA")
    bg_rgba = Image.alpha_composite(bg_rgba, shadow)
    bg_rgba.paste(subject, (x, y), subject)
    
    return bg_rgba.convert("RGB")


def tone_grade(img):
    """Sjednocení tónu — lehce desaturated, teplý nádech, kontrast."""
    img = ImageEnhance.Color(img).enhance(0.92)
    img = ImageEnhance.Contrast(img).enhance(1.06)
    img = ImageEnhance.Brightness(img).enhance(1.0)
    # warm cast
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * 1.02)))
    b = b.point(lambda v: int(v * 0.97))
    img = Image.merge("RGB", (r, g, b))
    img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70))
    return img


def crop_to_aspect(img, aspect_ratio, vertical_align=0.5):
    """Cropne obrázek na cílový poměr stran."""
    w, h = img.size
    current = w / h
    if current > aspect_ratio:
        # obrázek je širší — ořež po stranách
        new_w = int(h * aspect_ratio)
        x = (w - new_w) // 2
        return img.crop((x, 0, x + new_w, h))
    else:
        # obrázek je vyšší — ořež nahoře/dole
        new_h = int(w / aspect_ratio)
        y = int((h - new_h) * vertical_align)
        return img.crop((0, y, w, y + new_h))


def process_one(src_name, out_name, target_size, subject_scale=0.92, v_offset=0.05, aspect=None, save_transparent=True, alpha_threshold=None, kill_saturation=True, hero=False, h_align=0.5):
    """Pipeline: load → exif → rembg → composite → tone → crop → save."""
    src_path = os.path.join(SRC, src_name)
    print(f"  → {src_name}")
    
    im = load_with_exif(src_path)
    
    no_bg = remove_bg(im, alpha_threshold=alpha_threshold, kill_saturation=kill_saturation)
    if save_transparent:
        no_bg.save(os.path.join(TRANSPARENT_DIR, src_name.replace(".jpg", ".png")))
    
    composed = composite_on_bg(no_bg, target_size, subject_scale=subject_scale, vertical_offset=v_offset, hero=hero, h_align=h_align)
    composed = tone_grade(composed)
    
    if aspect:
        composed = crop_to_aspect(composed, aspect)
    
    out_path = os.path.join(OUT_DIR, out_name)
    composed.save(out_path, "JPEG", quality=88, optimize=True)
    print(f"     ✓ {out_name} ({composed.size[0]}×{composed.size[1]})")


# ========================
# MAPOVÁNÍ FOTEK NA POZICE
# ========================

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(TRANSPARENT_DIR, exist_ok=True)
    
    print("KYMERA — zpracování reálných fotek\n")
    
    # HERO (16:9 ratio, široká): IMG_5102 — dramatický detail hlavy s gear halo
    # subject_scale=0.98 = velká socha, světlejší pozadí pro lepší kontrast
    process_one("IMG_5102.jpg", "hero.jpg", (1920, 1080),
                subject_scale=0.98, v_offset=0.02, aspect=16/9, alpha_threshold=200, hero=True, h_align=0.78)
    
    # KOLEKCE (4:5 vertical):
    # figural — IMG_5106 (celá ženská figura)
    process_one("IMG_5106.jpg", "collection-figurative.jpg", (960, 1200),
                subject_scale=0.9, v_offset=0.05, aspect=4/5,
                alpha_threshold=200)  # agárnější ořez aut na pozadí
    # busty — IMG_5104 (čelní bust detail)
    process_one("IMG_5104.jpg", "collection-busts.jpg", (960, 1200),
                subject_scale=0.88, v_offset=0.0, aspect=4/5,
                alpha_threshold=200)
    # industrial — IMG_5114 (mechanický detail) — nahrazuje IMG_5107 (měla orange auto za sochou)
    process_one("IMG_5114.jpg", "collection-industrial.jpg", (960, 1200),
                subject_scale=0.92, v_offset=0.0, aspect=4/5,
                alpha_threshold=200)
    
    # VYBRANÁ DÍLA (4:5):
    # work-01 — IMG_5108 (back view celá)
    process_one("IMG_5108.jpg", "work-01.jpg", (960, 1200),
                subject_scale=0.88, v_offset=0.05, aspect=4/5,
                alpha_threshold=200)
    # work-02 — IMG_5102 (dramatický hlava-detail) — nahrazuje IMG_5114 (teď v collection)
    process_one("IMG_5102.jpg", "work-02.jpg", (960, 1200),
                subject_scale=0.92, v_offset=0.0, aspect=4/5,
                alpha_threshold=200)
    # work-03 — IMG_5101 (head profile celá figura)
    process_one("IMG_5101.jpg", "work-03.jpg", (960, 1200),
                subject_scale=0.9, v_offset=0.05, aspect=4/5,
                alpha_threshold=200)
    
    # O ZNAČCE (4:5 portrait): IMG_5107 (velká figura) — alpha threshold odstraní auto za dírami
    process_one("IMG_5107.jpg", "about.jpg", (960, 1200),
                subject_scale=0.9, v_offset=0.05, aspect=4/5,
                alpha_threshold=220)  # ještě agresivnější
    
    print("\nHotovo.")
