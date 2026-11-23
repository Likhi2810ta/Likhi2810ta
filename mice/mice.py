"""Generates assets/mice.svg: a cute mouse that nibbles cheese wherever you made contributions."""
import os, re, sys, urllib.request, pathlib

USER = os.environ.get("GH_USER", "Likhi2810ta")
OUT = pathlib.Path(__file__).parent.parent / "assets" / "mice.svg"

html = urllib.request.urlopen(
    urllib.request.Request(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "profile-mice"})
).read().decode()

cells = {}  # (row, col) -> level
for m in re.finditer(r'<td[^>]*?data-date="[^"]+"[^>]*?id="contribution-day-component-(\d+)-(\d+)"[^>]*?data-level="(\d)"', html):
    cells[(int(m.group(1)), int(m.group(2)))] = int(m.group(3))
if not cells:
    sys.exit("could not read contribution graph")
total = sum(int(n) if n.isdigit() else 1 for n in re.findall(r'>(\d+|No) contributions? on', html) if n != "No")

cols = max(c for _, c in cells) + 1
S, PAD, TOP = 15, 24, 58              # cell pitch, padding, header height
W = cols * S
H = 7 * S
width, height = W + PAD * 2, H + TOP + PAD + 6
DUR = 48.0
STEP = S * 2                          # vertical hop between rows (mouse eats every other row path, covers 2 rows)

# mouse runs along "lanes": lane k sits between rows 2k and 2k+1 and eats both
lanes = [(0, 1), (2, 3), (4, 5), (6,)]
lane_y = [TOP + (l[0] + l[-1]) / 2 * S + S / 2 for l in lanes]
x_left, x_right = PAD + 12, PAD + W + 2
run = x_right - x_left
hop = lane_y[1] - lane_y[0]
total_len = len(lanes) * run + (len(lanes) - 1) * hop

def t_at(lane, x):               # fraction of the loop when mouse is at x on lane
    along = (x - x_left) if lane % 2 == 0 else (x_right - x)
    return (lane * (run + hop) + along) / total_len

# path + flips
pts, d = [], []
for i, y in enumerate(lane_y):
    a, b = (x_left, x_right) if i % 2 == 0 else (x_right, x_left)
    d.append(("M" if i == 0 else "L") + f"{a:.1f},{y:.1f} L{b:.1f},{y:.1f}")
path = " ".join(d)
flip_t = [0.0] + [(i * (run + hop)) / total_len for i in range(1, len(lanes))]
flip_vals = ";".join("1 1" if i % 2 == 0 else "-1 1" for i in range(len(lanes)))
flip_keys = ";".join(f"{t:.5f}" for t in flip_t)

PALETTE = ["#efe2cc", "#e6c9a0", "#d4a373", "#a9744f", "#6f4e37"]  # level 0..4, cream -> brown
out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Georgia, serif">')
out.append(f'<rect width="{width}" height="{height}" rx="18" fill="#f7efe1"/>')
out.append(f'<rect x="1.5" y="1.5" width="{width-3}" height="{height-3}" rx="17" fill="none" stroke="#c9a77c" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round"/>')
out.append(f'<text x="{PAD}" y="30" font-size="17" fill="#5a3d2b" font-weight="bold">nom nom nom</text>')
out.append(f'<text x="{PAD}" y="47" font-size="12" fill="#8b6b4e">every crumb = a day i showed up · {total} contributions this year</text>')

for (r, c), lvl in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    x, y = PAD + c * S, TOP + r * S
    out.append(f'<rect x="{x}" y="{y}" width="{S-3}" height="{S-3}" rx="4" fill="#efe2cc"/>')
    if lvl == 0:
        continue
    lane = r // 2
    cx = x + (S - 3) / 2
    t = t_at(lane, cx)
    t0, t1 = max(t - 0.004, 0), min(t + 0.004, 0.97)
    size = 3.2 + lvl * 0.9
    cy = y + (S - 3) / 2
    out.append(
        f'<g><path d="M{cx-size:.1f},{cy+size*0.8:.1f} L{cx+size:.1f},{cy+size*0.8:.1f} L{cx+size:.1f},{cy-size*0.2:.1f} Q{cx:.1f},{cy-size*1.3:.1f} {cx-size:.1f},{cy-size*0.2:.1f} Z" fill="#f2b84b" stroke="#c98a1b" stroke-width="1"/>'
        f'<circle cx="{cx-size*0.3:.1f}" cy="{cy+size*0.3:.1f}" r="{size*0.25:.1f}" fill="#c98a1b"/>'
        f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{t0:.5f};{t1:.5f};0.985;1" values="1;1;0;0;1"/></g>'
    )

mouse = """
<g>
  <path d="M-15,3 Q-30,-2 -26,12 Q-24,18 -32,16" fill="none" stroke="#e7a9a0" stroke-width="2.6" stroke-linecap="round"/>
  <ellipse cx="-2" cy="2" rx="15" ry="10.5" fill="#d9c7b0" stroke="#6f4e37" stroke-width="1.6"/>
  <ellipse cx="0" cy="5" rx="9" ry="5.5" fill="#f7efe1"/>
  <circle cx="11" cy="-1" r="9" fill="#d9c7b0" stroke="#6f4e37" stroke-width="1.6"/>
  <circle cx="6" cy="-10" r="5.6" fill="#d9c7b0" stroke="#6f4e37" stroke-width="1.6"/>
  <circle cx="6" cy="-10" r="3" fill="#f3b7b0"/>
  <circle cx="14" cy="-9" r="5" fill="#d9c7b0" stroke="#6f4e37" stroke-width="1.6"/>
  <circle cx="14" cy="-9" r="2.6" fill="#f3b7b0"/>
  <circle cx="14" cy="-2" r="1.7" fill="#3b2a1e"/>
  <circle cx="14.5" cy="-2.5" r=".5" fill="#fff"/>
  <ellipse cx="19.5" cy="1.5" rx="2.2" ry="1.7" fill="#e58f8f"/>
  <circle cx="10" cy="2.5" r="2.3" fill="#f3b7b0" opacity=".8"/>
  <path d="M20,3 q3,-1 6,-3 M20,4.5 q3,0 6,1" stroke="#6f4e37" stroke-width=".8" fill="none"/>
  <ellipse cx="-6" cy="12" rx="3.2" ry="2" fill="#f3b7b0" stroke="#6f4e37" stroke-width="1"><animate attributeName="cy" values="12;10;12" dur=".35s" repeatCount="indefinite"/></ellipse>
  <ellipse cx="6" cy="12" rx="3.2" ry="2" fill="#f3b7b0" stroke="#6f4e37" stroke-width="1"><animate attributeName="cy" values="10;12;10" dur=".35s" repeatCount="indefinite"/></ellipse>
</g>"""
out.append('<g><g>')
out.append(f'<animateTransform attributeName="transform" type="scale" calcMode="discrete" keyTimes="{flip_keys}" values="{flip_vals}" dur="{DUR}s" repeatCount="indefinite"/>')
out.append(f'<g transform="translate(0,-4)">{mouse}<animateTransform attributeName="transform" type="translate" values="0,-4;0,-6;0,-4" dur=".35s" repeatCount="indefinite"/></g></g>')
out.append(f'<animateMotion dur="{DUR}s" repeatCount="indefinite" path="{path}" calcMode="linear"/></g>')
out.append('</svg>')
OUT.parent.mkdir(exist_ok=True)
OUT.write_text("\n".join(out), encoding="utf-8")
print("wrote", OUT, "cells:", len(cells), "cheese:", sum(1 for v in cells.values() if v), "total:", total)
