"""
Aktualizace všech web fotek z 3 nejlepších soch (5104, 5106, 5107).
"""
import sys, os
sys.path.insert(0, '/home/user/workspace/kymera')
import process_luxury_photos as plp
from PIL import Image, ImageEnhance, ImageFilter

def enhance(path):
    img = Image.open(path)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=100, threshold=2))
    img.save(path, 'JPEG', quality=90, optimize=True)

plp.OUT_DIR = '/home/user/workspace/kymera/assets/img'

# HERO — 5104 bust, 16:9 wide
plp.process(transparent_name='IMG_5104.png', out_name='hero.jpg',
            target_size=(1920, 1080), subject_scale=0.85, h_align=0.7, hero=True)
enhance(os.path.join(plp.OUT_DIR, 'hero.jpg'))

# KOLEKCE — 3 různé sochy, čtvercové
plp.process(transparent_name='IMG_5107.png', out_name='collection-figurative.jpg',
            target_size=(800, 800), subject_scale=0.85, h_align=0.5)
plp.process(transparent_name='IMG_5104.png', out_name='collection-busts.jpg',
            target_size=(800, 800), subject_scale=0.85, h_align=0.5)
plp.process(transparent_name='IMG_5106.png', out_name='collection-industrial.jpg',
            target_size=(800, 800), subject_scale=0.85, h_align=0.5)

# VYBRANÁ DÍLA — 3 sochy, 4:5 portrait
plp.process(transparent_name='IMG_5104.png', out_name='work-01.jpg',
            target_size=(900, 1125), subject_scale=0.88, h_align=0.5)
plp.process(transparent_name='IMG_5106.png', out_name='work-02.jpg',
            target_size=(900, 1125), subject_scale=0.88, h_align=0.5)
plp.process(transparent_name='IMG_5107.png', out_name='work-03.jpg',
            target_size=(900, 1125), subject_scale=0.88, h_align=0.5)

# ABOUT — 5107 figurativní celá
plp.process(transparent_name='IMG_5107.png', out_name='about.jpg',
            target_size=(900, 1125), subject_scale=0.82, h_align=0.5)

# Enhance všechny
for f in ['hero.jpg','collection-figurative.jpg','collection-busts.jpg','collection-industrial.jpg',
          'work-01.jpg','work-02.jpg','work-03.jpg','about.jpg']:
    enhance(os.path.join(plp.OUT_DIR, f))
    print(f"✓ {f}: {os.path.getsize(os.path.join(plp.OUT_DIR,f))//1024} KB")
