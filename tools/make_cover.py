"""Builds assets/mf-cover.webp: the candidate photo blended into the book cover (no cutout look).
   python tools/make_cover.py     (needs opencv-python, pillow, numpy; reads source/candidate.jpg + assets/cut.webp)
   The cutout's alpha is registered back onto the original photo, then used only as a soft matte:
   she keeps her natural colours, everything behind her is graded into the cover's crimson, and the edges fade out."""
import os, cv2, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(ROOT, 'source'), os.path.join(ROOT, 'assets')

jpg = cv2.cvtColor(cv2.imread(f'{SRC}/candidate.jpg'), cv2.COLOR_BGR2RGB); H, W = jpg.shape[:2]
cut = np.array(Image.open(f'{OUT}/cut.webp'))                       # RGBA, 26 px pad left/top/right
tpl = cut[26:, 26:666]; gray = cv2.cvtColor(tpl[:, :, :3], cv2.COLOR_RGB2GRAY); a = tpl[:, :, 3]
J = cv2.cvtColor(jpg, cv2.COLOR_RGB2GRAY)
best = None
for s in np.arange(.70, 1.0, .005):                                 # coarse scale + position search
    k = .25/s; t = cv2.resize(gray, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    m = cv2.resize((a > 200).astype(np.uint8)*255, None, fx=k, fy=k, interpolation=cv2.INTER_NEAREST)
    Js = cv2.resize(J, None, fx=.25, fy=.25, interpolation=cv2.INTER_AREA)
    if t.shape[0] > Js.shape[0] or t.shape[1] > Js.shape[1]: continue
    mn, _, loc, _ = cv2.minMaxLoc(cv2.matchTemplate(Js, t, cv2.TM_SQDIFF, mask=m))
    sc = mn/(m > 0).sum()
    if best is None or sc < best[0]: best = (sc, s, loc)
_, s0, loc0 = best; best = None
for s in np.arange(s0-.012, s0+.012, .001):                         # fine search at full size
    k = 1/s; t = cv2.resize(gray, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    m = cv2.resize((a > 230).astype(np.uint8)*255, None, fx=k, fy=k, interpolation=cv2.INTER_NEAREST)
    x0, y0 = max(0, loc0[0]*4-20), max(0, loc0[1]*4-20)
    reg = J[y0:y0+t.shape[0]+40, x0:x0+t.shape[1]+40]
    if reg.shape[0] < t.shape[0] or reg.shape[1] < t.shape[1]: continue
    mn, _, loc, _ = cv2.minMaxLoc(cv2.matchTemplate(reg, t, cv2.TM_SQDIFF, mask=m))
    sc = mn/(m > 0).sum()
    if best is None or sc < best[0]: best = (sc, s, (loc[0]+x0, loc[1]+y0), t.shape)
_, s1, (px, py), (th, tw) = best
matte = np.zeros((H, W), np.float32)
al = cv2.resize(a, (tw, th), interpolation=cv2.INTER_LINEAR).astype(np.float32)/255
matte[py:py+th, px:px+tw] = al[:H-py, :W-px]
matte = cv2.GaussianBlur(matte, (0, 0), 7)                          # soft transition between her and the graded background

# crop: head and shoulders, centred on her
cx0, cy0, cw, ch = 405, 925, 1040, 870
img = jpg[cy0:cy0+ch, cx0:cx0+cw].astype(np.float32)/255; mt = matte[cy0:cy0+ch, cx0:cx0+cw][..., None]
lum = (img @ np.array([.299, .587, .114], np.float32))[..., None]
dark, mid, lite = np.array([.13, .01, .03]), np.array([.62, .07, .11]), np.array([.86, .20, .20])
g = np.clip((lum-.05)/.9, 0, 1)
duo = np.where(g < .55, dark+(mid-dark)*(g/.55), mid+(lite-mid)*((g-.55)/.45))   # crimson duotone, same hue family as the cover
subj = np.clip((img-.5)*1.06+.5, 0, 1)*np.array([1.03, 1.0, .96])               # a touch of warmth so she sits in the red light
out = np.clip(subj*mt + duo*(1-mt), 0, 1)

# soft edges: fade left/right/top/bottom into the cover instead of ending in a hard rectangle
h, w = out.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); xx /= w; yy /= h
sm = lambda v: v*v*(3-2*v)
A = sm(np.clip(xx/.16, 0, 1))*sm(np.clip((1-xx)/.16, 0, 1))*sm(np.clip(yy/.20, 0, 1))*sm(np.clip((1-yy)/.30, 0, 1))
rgba = np.dstack([out, A])
im = Image.fromarray((rgba*255).astype('uint8'), 'RGBA'); im = im.resize((1000, round(1000*h/w)), Image.LANCZOS)
im.save(f'{OUT}/mf-cover.webp', quality=88, method=6)
print('cover', im.size, 'registered scale', round(s1, 3), 'at', (px, py))
