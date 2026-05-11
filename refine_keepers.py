"""
Vylepšení 3 nejlepších fotek — kontrast, světlo, detail.
Sochy: 5104 (bust), 5106 (vertikální), 5107 (celá figura).
Beru pre-extracted img-transparent PNG a aplikuji vylepšenou galerie pipeline.
"""
import sys, os
sys.path.insert(0, '/home/user/workspace/kymera')
import process_luxury_photos as plp
from PIL import Image, ImageEnhance, ImageFilter

KEEPERS = ['IMG_5104.png', 'IMG_5106.png', 'IMG_5107.png']

# Galerie: dotažený kontrast + ostrost
plp.OUT_DIR = '/home/user/workspace/kymera/assets/galerie'
os.makedirs(plp.OUT_DIR, exist_ok=True)

for f in KEEPERS:
    out_name = f.replace('.png', '.jpg')
    plp.process(
        transparent_name=f,
        out_name=out_name,
        target_size=(900, 1200),
        subject_scale=0.88,  # větší v rámu — víc detailu
        h_align=0.5,
    )
    # Post-zpracování: vyšší kontrast + lokální ostření
    p = os.path.join(plp.OUT_DIR, out_name)
    img = Image.open(p)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Sharpness(img).enhance(1.25)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=2))
    img.save(p, 'JPEG', quality=90, optimize=True)
    print(f"✓ {out_name}: {os.path.getsize(p)//1024} KB")

# Smaž ty které vyhazujeme
for old in ['IMG_5101.jpg', 'IMG_5102.jpg', 'IMG_5108.jpg', 'IMG_5114.jpg', 'IMG_5115.jpg']:
    p = os.path.join(plp.OUT_DIR, old)
    if os.path.exists(p):
        os.remove(p)
        print(f"✗ removed {old}")

print("\nDone.")
