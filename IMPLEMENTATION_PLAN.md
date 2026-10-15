# Ali Fathima campaign site: implementation plan

Hand-off for Antigravity. **A working reference build already exists in `index.html`.** The job is to run it locally, confirm it matches this spec, then improve it without changing the behaviour described here. Keep edits minimal and scoped to what is asked.

## 1. What this is

A single-page, scroll-driven portfolio site for **Ali Fathima**, a candidate in the upcoming college elections (CSE department, College of Engineering Trivandrum). No navbar. Everything is triggered by scroll position. Plain HTML + CSS + vanilla JS in one file, no framework, no build step.

## 2. Run it

```
cd ali-fathima-site
python3 -m http.server 8000      # then open http://localhost:8000
```

Needs internet only for Google Fonts (Archivo variable with `wdth` axis, Pinyon Script). Without it the page falls back to Arial and a cursive font and still works, but the look changes.

## 3. Files

| Path | Purpose |
|---|---|
| `index.html` | the whole site (CSS in `<style>`, JS in one IIFE at the bottom) |
| `assets/building.webp` | the user's black-and-white fisheye photo of the department, cut out of its black background (RGBA, 1487x716, flush at the bottom) |
| `assets/building_outline.webp` | small cream sticker outline of the building silhouette, same canvas, sits behind `building.webp` |
| `assets/cut.webp` | Ali cut out of her photo, background removed (RGBA, 692x1277) |
| `assets/outline.webp` | cream sticker outline of the same silhouette, same canvas size, sits behind `cut.webp` |
| `assets/mf-cover.webp` | her photo blended into the book cover (RGBA, soft-edged, background graded crimson); built by `tools/make_cover.py` |
| `source/` | original photos: `candidate.jpg`, `building.png` (`megaphone.png` is no longer used) |
| `tools/make_assets.py` | regenerates everything in `assets/` from `source/` and prints the geometry constants |

If `building.png` changes, rerun `tools/make_assets.py` and copy the printed `AR`, `SX`, `SIGN_BELOW`, `SIGN_ABOVE`, `SIGN_W` into the constants block near the top of the script in `index.html`. Layout depends on them.

## 4. Content to edit (top of the `<script>`, block marked "EDIT THIS BLOCK")

- `CANDIDATE`: display name.
- `ROLES`: exactly 8 objects `{t, w}` = role title, event/club and year.
- `PROJECTS`: array of `{name, kick, tag, note, points:[[heading, body] x4]}`. One scroll page is generated per entry. Currently Code Digest, Initiative Athithi CET, then three placeholders.

All of these are still bracketed placeholders like `[Role title 1]`. Do not invent real roles or achievements. Ask the user for them.

## 5. Design system

**Direction:** crimson / cream / black social-post look. Wide bold sans titles mixed with a calligraphic script that overlaps them. Halftone pop-art stickers.

| Token | Value |
|---|---|
| `--oxblood` | `#760a12` (base background) |
| `--scarlet` | `#b3121e` |
| `--ink` | `#050303` |
| `--paper` | `#f8f3ee` |
| `--cream` | `#fff0c8` (sticker outline, script accents) |
| `--gold` | `#f2b632` (sparkles, bolts, underline) |
| `--arrow` | `#fff3d6` |
| `--wide` | Archivo, `font-stretch:125%`, weight 800, uppercase. For all titles and card headings |
| `--script` | Pinyon Script. Big words only (hero line, "Vote for", role names, notes) |
| `--sans` | Archivo normal width, for body text |

Rules: script words overlap the first line of the bold title (negative margin or absolute position). Cards are rounded (18px) with a thin outlined circle in the corner. Page backgrounds alternate per project: paper, oxblood, ink, paper, oxblood.

## 6. Scroll engine (do not change the maths without a reason)

- Each scene is a `.track` with an inner `.stage` (`position:sticky; top:0; height:100svh`).
- Track heights in `vh`: intro 720, done-head 260, each project 400, outro 320. Set in JS from `data-vh`.
- Per frame, for each visible track: `p = clamp(-rect.top / (trackH - stageH))` and `pre = clamp(1 - rect.top / stageH)`. `pre` drives entrances before a stage sticks.
- Values are smoothed: `ps += (p - ps) * 0.17`, loop runs only while still moving.
- `prefers-reduced-motion`: every scene jumps to its final state (`p = pre = 1`) and tracks shrink to one screen.
- Helpers: `seg(p,a,b)` maps p in [a,b] to 0..1; `ease` (cubic in-out), `easeOut`, `easeBack` (small overshoot).

## 7. Scene timelines (p = scene progress 0..1)

### 7.1 Intro (720vh): homepage, reveal, illustrations, roles

| p | What happens |
|---|---|
| 0 to .10 | Hero holds: pill "elections are around the corner", script "The department" over bold **HAS A VOICE.**, scroll cue. Building sticker (cream outline) sits centred at the bottom, about 38% of screen height, flush with the bottom edge |
| .05 to .20 | Hero text fades and lifts out |
| .10 to .34 | Building zooms from height `h0` to `h1` with its **bottom edge pinned to the bottom of the screen the whole time** (it scales upward, never lifts off). Horizontal anchor blends from image centre to sign centre so it ends centred over the candidate. Red `veil` rises to about .46 opacity. Top `fade` gradient hides the roofline behind the title |
| .32 to .46 | Red sunburst `rays` fade in behind her, rotating with `p * 80deg` |
| .30 to .46 | Candidate rises from below with `easeBack` |
| .34 to .46 | Rotating text ring "VOTE ALI FATHIMA" appears (rotates `p * 220deg`) |
| .44 to .55 | Cream outline wipes upward via `clip-path: inset()` |
| .45 to .50 | Script "Vote for" fades in |
| .47 to .56 | **ALI FATHIMA** letters rise one by one through a mask |
| .40 to .60 | Illustrations pop (scale from 0, `easeBack`): bolt right .49, bolt left .50, ballot box .52, sparkles .52 / .54 / .55 |
| .61 + i x .044 | Role `i` (0 to 7): chip fades in over .03, then its arrow draws (`stroke-dashoffset`) from +.014 to +.044, arrowhead at +.04 to +.05. Order alternates left, right, left, right down the page |
| last | All 8 roles stay visible until the scene ends |


### 7.1b Static building and desktop extras (this REPLACES the zoom in 7.1 at every width)

- **No zoom, no tint, at every width.** `h1 = h0`, `g = 0`, `veil` and `fade` stay 0, rays sit behind the building. The building stays at its homepage size and position (`h0 = min(.42*Hd, 1.3*Wd/AR)`, the same as the closing page) with `veil` and `fade` at 0. On desktop (>= 900px) candidate height is `hc = min(.58*Hd, .96*Wd)`, matching the closing page; below 900px it stays `min(.45*Hd, .96*Wd)`.
- **Pulled-forward timeline (all widths).** `p = praw < .08 ? praw/.08*.3 : .3 + (praw-.08)/.92*.7`, so the candidate starts rising right after the hero text leaves (hero text exits on raw p .03 to .12). Everything else in 7.1 (outline wipe, title, rays, ring, roles) then runs on that remapped p.
- **Gap fill beside the building (desktop only, >= 900px).** The empty columns left and right of the building hold two mirrored clusters that appear on load (CSS `popIn`, staggered by `--d`, then a slow `floaty` loop; disabled under reduced motion) and stay for the whole scene: thin cream ring, gold halftone disc, ballot box on the left / "VOTE!" speech bubble on the right, a lightning bolt and two sparkles. Width available = `min((Wd - buildingWidth)/2 - 18, roleLabelLeftEdge - 10)`; cluster hidden if under 110px. Rings and discs sit at `z-index:-1`; role chips (`z-index:6`) stay above illustrations (`z-index:4`).
- **Role labels** are `min 240px` wide with a 40px gap to the candidate on desktop so they do not cover the clusters. Rows run from 7% of her height down to `Hd - 92`.
- Rays sit behind the building on desktop (`#rays{z-index:-1}`).


### 7.1c Maximalist reveal layers (all widths, drawn by `layoutReveal()` + `revealFx(p)`; p = remapped intro progress)

Visual references: a cut-out figure with a gold spiky halo and red lightning bolts over op-art swirls, retro stripe bands fanning out in perspective, and rainbow ribbon swirls. Adapted to the crimson / cream / gold palette plus hot pink and orange.

| p | Layer |
|---|---|
| .28 to .44 | `#waves` canvas (behind the building): crimson/cream wavy zebra bands, phase driven by p |
| .32 to .50 | `#groove` stripe wings: 7 bands per side (crimson, cream, pink, gold, orange, pink, cream) drawn on from behind her shoulders, staggered |
| .34 to .52 | `#groove` rainbow ribbons (orange / pink / gold triple stroke) looping in from both top corners |
| .36 to .48 | `#halo`: orange back burst + gold 18-point starburst with dark-gold halftone dots, pops with `easeBack`, rotates `p*50deg` |
| .42 to .64 | `#shock`: three expanding ring pulses (cream, gold, pink) from her head |
| .44 to .64 | `#conf` canvas confetti: 22 (mobile) / 42 particles, position is a pure function of p |
| .44 to .47 | `.flash`: brief cream flash (peak opacity .3) as she lands |
| .46 to .56 | `#bolts`: six red-orange lightning bolts drawn off the halo, then flicker |
| .52 to .62 | Name gets stacked retro shadows (pink, gold, orange) via CSS var `--o` |

Notes: layers sit in this DOM order: waves, building, rays (z -1), ring, shock, groove, halo, title, candidate, bolts, confetti, arrows, chips, illustrations, flash. Canvas redraws are throttled. Reduced motion shows the final composition with no confetti or flash.

### 7.2 What have we done (done-head, 260vh)
Words of "WHAT HAVE WE DONE?" rise by `pre` (stagger .1). Gold underline draws p .12 to .45. Subline fades p .35 to .58. Script note "less promise, more proof" p .55 to .78.

### 7.3 Project pages (400vh each, generated from `PROJECTS`)
Left column: script kicker (`kick`), title words rise by `pre` (.3 + i x .1), tagline `pre` .6 to .95, script note p .05 to .2. Right: 4 cards, card `i` enters p from `.06 + i x .2` over .15 (slide up 70px, rotate from about +/-5 deg to about +/-1 deg, scale .9 to 1). Mobile (<760px): single column, cards become rows, note hidden.

### 7.4 Outro (320vh)
Candidate rises p .04 to .26, outline .22 to .34, title words from .26 (stagger .05), script "now it's your turn" .46 to .56, body .55 to .66, rotating "VOTE Ali Fathima" starburst .62 to .76, "Back to the start" button .78 to .9 (smooth-scrolls to top). Rays .1 to .3, sparkles .32 to .42. The building sits centred at the bottom again (about 42% of screen height, outlined) as a bookend.

## 8. Layout geometry (computed in JS on load and resize, all in px from stage size `Wd x Hd`)

```
h0  = min(.38*Hd, 1.3*Wd/AR)                      hero building height
hc  = min(.45*Hd, .96*Wd)                         candidate height;  wc = hc * 692/1277
yHead = Hd - hc                                   candidate sits flush to the bottom
h1  = max(min((hc+8)/SIGN_BELOW, 1.5*Hd, .96*Wd/SIGN_W), h0*1.05)   zoomed building height
signTop = Hd - SIGN_ABOVE*h1,  signBot = Hd - SIGN_BELOW*h1
```
The building's bottom edge is always at `Hd` (`yb = Hd`), so `h1` is chosen so the sign lands just above her head without lifting the building. Transform each frame: `translate(cx - ax*w, Hd - h) scale(h/h0)` with `transform-origin: 0 0`, `h = lerp(h0, h1, g)`, `w = h*AR`, `ax = lerp(.5, SX, g)`. Title sits between 4% of `Hd` and `signTop - 14`. Role chips sit in 4 rows starting at `signBot + 40`; left chips are right-aligned to `cx - wc/2 - 56`, right chips mirror that. Arrows are cubic Beziers from the chip's inner edge to a point on her silhouette (row targets at 13/34/55/74% of her height).

Mobile (<640px): the sign cannot fit above her head while the building stays pinned to the bottom, so the building acts as a backdrop behind the chips; title stacks onto two lines (each word has its own mask), chips are narrower and may overlap her arms, rows start at her head, bolts and ballot box are hidden.

## 9. Asset pipeline notes

- Candidate cutout: `rembg` model `u2net_human_seg`, alpha eroded 2px and blurred to remove green fringe. Outline = alpha blurred (r=11), thresholded, re-blurred, filled cream `#fff0aa`.
- Building: the user's B&W fisheye photo. The black area touching the top edge is flood-filled out (luminance < 14), eroded 2px, then softened. Outline = alpha blurred (r=9), thresholded, re-blurred, cream `#fff0aa`, padded 18px left, right and top (bottom stays flush).
- Book cover photo: `tools/make_cover.py` registers `cut.webp` back onto `source/candidate.jpg`, keeps her in natural colour and grades everything behind her into the cover crimson, with feathered edges.

## 10. Quality bar (keep these true)

- No horizontal scroll. Responsive down to 360px wide.
- Focus ring visible on the "Back to the start" button.
- Reduced-motion users see final states, no animation.
- Everything animates with `transform` and `opacity` only (plus `stroke-dashoffset`, `clip-path`).
- Page weight about 0.9 MB of images. Do not add frameworks.

## 11. Suggested next steps for Antigravity

1. Run locally and check the 5 checkpoints at 1440x900 and 390x844: hero (p=0), mid-reveal (p=.5), roles complete (p=.97), a project page, outro.
2. Replace placeholder text once the user supplies it (section 4).
3. Optional polish, only if asked: add a share/meta image (`og:image`), add favicon, deploy to Netlify or Vercel as static files.

## 12. Prompt to paste into Antigravity

> Open `IMPLEMENTATION_PLAN.md` and `index.html` in this folder. `index.html` is a finished reference build of a scroll-driven campaign site. Serve it locally, verify it against the plan, and tell me anything that deviates. Do not restyle, restructure or add dependencies unless I ask. When I give you the real role and project text, put it into the `ROLES` and `PROJECTS` arrays only.

## Manifesto book (RENOVA)

- Front cover: `assets/mf-front.webp`, the printed cover used as-is (sfi mark, black-and-white portrait, VOTE FOR / ALI FATHIMA / -RENOVA- / ELECTION MANIFESTO). Cover counts as page 1.
- Inner pages follow the printed template: white sheet, hand lettering (Gaegu from Google Fonts), bold centred "OUR MANIFESTO" title on the first page, then numbered points (heading, text, Goal line), 3 per page, page number centred at the bottom starting at 2.
- Pages come from `MFD` (the 15 points) via `MFP`; the last page is "Our Commitment". `NP` must stay even (two per leaf). Currently 6: 5 pages of points + commitment.
- `layoutMf()` shrinks the font of any page whose text would overflow the sheet.
- Background: the red burst (`.pz-rays`) plus the yellow starburst behind the book. No megaphones.

## Latest changes (candidate reveal, manifesto, titles)

- Candidate reveal: the side stickers (bolts, ballot box, rings, discs, speech bubble, sparkles) and the two "VOTE FOR ALI FATHIMA" ribbons are removed from the intro. The conclusion page keeps its own ribbons and sparkles.
- Manifesto page: starburst removed. Background is a yellow and red sunburst (`.pz-rays`, 18deg wedges) that spins in and grows from behind the book as it rises.
- Manifesto text: one size on every page (`--fs` = 4% of the page width, 16 to 22px, always at least the conclusion text size). If a page would overflow, all pages shrink together, never one page alone. One point per page (CS Cup and Farewell share one page), commitment split over two pages: 16 pages.
- RENOVA title and the arched finale title use the same face as the "ALI FATHIMA" reveal name.
- Titles on the other pages use the same soft shadow as the reveal name (CSS `drop-shadow`, so the word masks do not clip it).
