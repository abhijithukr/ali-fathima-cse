"""Rebuilds every image in ../assets from the originals in ../source.
   pip install "rembg[cpu]" pillow numpy scipy
   python tools/make_assets.py            (writes ../assets)
   OUT=/tmp/x python tools/make_assets.py (writes elsewhere, for testing)
Prints the sign-geometry constants that index.html hard-codes (AR, SX, SIGN_BELOW, SIGN_ABOVE, SIGN_W)."""
import os, json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
from rembg import remove, new_session

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source')
OUT = os.environ.get('OUT', os.path.join(ROOT, 'assets'))
os.makedirs(OUT, exist_ok=True)

# ---------- 1. candidate cutout + cream sticker outline ----------
im = Image.open(f'{SRC}/candidate.jpg').convert('RGB')
cut = remove(im, session=new_session('u2net_human_seg')).convert('RGBA')
l, t, r, b = cut.getbbox(); m = 6
cut = cut.crop((l-m, t-m, r+m, cut.height))                       # keep flush to the bottom edge
al = cut.split()[3].filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.1))  # kills green fringe
cut.putalpha(al)
tw = 640; cut = cut.resize((tw, round(cut.height*tw/cut.width)), Image.LANCZOS)
pad = 26
cv = Image.new('RGBA', (cut.width+2*pad, cut.height+pad), (0,0,0,0)); cv.paste(cut, (pad, pad), cut)
d = cv.split()[3].filter(ImageFilter.GaussianBlur(11)).point(lambda v: 255 if v > 6 else 0).filter(ImageFilter.GaussianBlur(1.2))
outline = Image.new('RGBA', cv.size, (255,240,170,0)); outline.putalpha(d)
cv.save(f'{OUT}/cut.webp', quality=90, method=6)
outline.save(f'{OUT}/outline.webp', quality=90, method=6)
print('candidate canvas', cv.size, '(CAR = w/h =', round(cv.width/cv.height, 4), ')')

# ---------- 2. building: cut out of its black background + small cream outline ----------
# source/building.png is the user's black-and-white fisheye photo of the department.
src = Image.open(f'{SRC}/building.png').convert('RGB')
arr = np.asarray(src); lum = arr.astype(int).mean(axis=2); H, W = lum.shape
lab, n = ndi.label(lum < 14)
bg = np.isin(lab, list(set(np.unique(lab[0, :])) - {0}))           # black area touching the top edge
bg = ndi.binary_dilation(bg, iterations=2)                          # eat the dark fringe along the roofline
alpha = np.clip((ndi.gaussian_filter((~bg).astype(np.float32), 1.0) - .35)/.4, 0, 1)
im = Image.fromarray(np.dstack([arr, (alpha*255).astype('uint8')]), 'RGBA')
ys = np.where((alpha > .5).any(axis=1))[0]; top = max(0, ys.min()-2)
im = im.crop((0, top, W, H))                                        # flush at the bottom
pad = 18
bc = Image.new('RGBA', (im.width+2*pad, im.height+pad), (0,0,0,0)); bc.paste(im, (pad, pad), im)
d = bc.split()[3].filter(ImageFilter.GaussianBlur(9)).point(lambda v: 255 if v > 6 else 0).filter(ImageFilter.GaussianBlur(1.2))
bo = Image.new('RGBA', bc.size, (255,240,170,0)); bo.putalpha(d)
bc.save(f'{OUT}/building.webp', quality=86, method=6); bo.save(f'{OUT}/building_outline.webp', quality=90, method=6)
CW, CH = bc.size
# sign board in the source photo: x 435..1103, y 348..402
L_, R_, T_, B_ = 435+pad, 1103+pad, 348-top+pad, 402-top+pad
print('building consts', json.dumps({'AR': round(CW/CH, 4), 'SX': round((L_+R_)/2/CW, 4),
      'SIGN_BELOW': round((CH-B_)/CH, 4), 'SIGN_ABOVE': round((CH-T_)/CH, 4), 'SIGN_W': round((R_-L_)/CH, 4)}))
