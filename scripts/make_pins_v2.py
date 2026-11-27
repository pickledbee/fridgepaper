"""Render the second-style FridgePaper pins (1000 x 1500 PNG) with headless Chrome.

Run from the repository root:  python3 scripts/make_pins_v2.py
Two layouts:
  photo  the printable's on-fridge photo with a colored headline panel
  list   a numbered tip list for blog posts and calculators
Writes pins/<name>-2.png and prints a pins.json entry for each.
"""
import html
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "google-chrome"

COLORS = {
    "Chore Charts for Kids": ("#e98a3b", "#fff4e8"),
    "Family Routines and Goals": ("#4f7cc2", "#eaf1fb"),
    "Meal Planning Printables": ("#5b9a68", "#ecf5ee"),
    "Family Budget Printables": ("#3a9a9a", "#e6f4f4"),
    "Cleaning Schedules and Home Organization": ("#d9574a", "#fcecea"),
}

FONT_CSS = """
@font-face{font-family:Fredoka;font-weight:500;src:url(file://%(r)s/assets/fonts/fredoka-latin-500-normal.woff2)}
@font-face{font-family:Fredoka;font-weight:600;src:url(file://%(r)s/assets/fonts/fredoka-latin-600-normal.woff2)}
@font-face{font-family:Fredoka;font-weight:700;src:url(file://%(r)s/assets/fonts/fredoka-latin-700-normal.woff2)}
@font-face{font-family:Hand;src:url(file://%(r)s/assets/fonts/patrick-hand-latin-400-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1000px;height:1500px;overflow:hidden}
body{font-family:Fredoka,sans-serif;background:#f6f1e7;color:#2b2a33;position:relative}
""" % {"r": ROOT}


def photo_html(p, color, tint):
    img = f"file://{ROOT}/assets/img/{p['photo']}"
    return f"""<html><head><style>{FONT_CSS}
.ph{{position:absolute;top:0;left:0;width:1000px;height:1080px;background:url({img}) center 38%/cover}}
.badge{{position:absolute;top:44px;right:44px;width:210px;height:210px;border-radius:50%;background:#f4c542;
 color:#2b2a33;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(9deg);
 border:6px solid #fff;font-weight:700;line-height:1}}
.badge b{{font-size:64px}}.badge span{{font-size:30px;margin-top:6px;font-weight:600}}
.panel{{position:absolute;top:1040px;left:0;width:1000px;height:460px;background:{color};color:#fff;
 border-radius:44px 44px 0 0;padding:52px 60px 0;text-align:center}}
.kick{{font-family:Hand;font-size:44px;opacity:.95}}
h1{{font-weight:700;font-size:{p.get('size',78)}px;line-height:1.04;margin-top:6px}}
.foot{{position:absolute;bottom:40px;left:0;width:1000px;text-align:center}}
.pill{{display:inline-block;background:#fff;color:{color};font-weight:600;font-size:34px;padding:14px 38px;border-radius:999px}}
</style></head><body>
<div class="ph"></div>
<div class="badge"><b>FREE</b><span>to print</span></div>
<div class="panel"><div class="kick">{html.escape(p['kicker'])}</div><h1>{p['headline']}</h1></div>
<div class="foot"><span class="pill">fridgepaper.co</span></div>
</body></html>"""


def list_html(p, color, tint):
    rows = "".join(
        f'<div class="row"><div class="n">{i}</div><div class="t">{html.escape(t)}</div></div>'
        for i, t in enumerate(p["items"], 1)
    )
    return f"""<html><head><style>{FONT_CSS}
body{{background:{tint};display:flex;flex-direction:column}}
.top{{background:{color};color:#fff;padding:64px 60px 70px;text-align:center;border-radius:0 0 60px 60px}}
.kick{{font-family:Hand;font-size:46px}}
h1{{font-weight:700;font-size:{p.get('size',84)}px;line-height:1.03;margin-top:8px}}
.list{{flex:1;display:flex;flex-direction:column;justify-content:center;padding:0 60px 150px}}
.row{{display:flex;align-items:center;gap:26px;background:#fff;border-radius:26px;padding:20px 28px;margin-bottom:{p.get('gap',18)}px;
 border:3px solid rgba(0,0,0,.05)}}
.n{{flex:none;width:68px;height:68px;border-radius:50%;background:{color};color:#fff;font-weight:700;font-size:38px;
 display:flex;align-items:center;justify-content:center}}
.t{{font-weight:500;font-size:{p.get('item',38)}px;line-height:1.18}}
.foot{{position:absolute;bottom:0;left:0;width:1000px;height:150px;background:#2b2a33;color:#fff;display:flex;
 align-items:center;justify-content:center;gap:20px;font-size:40px;font-weight:600}}
.foot span{{color:#f4c542}}
</style></head><body>
<div class="top"><div class="kick">{html.escape(p['kicker'])}</div><h1>{p['headline']}</h1></div>
<div class="list">{rows}</div>
<div class="foot">{html.escape(p['footer'])} <span>fridgepaper.co</span></div>
</body></html>"""


def render(page, out_png):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(page)
        path = f.name
    subprocess.run(
        [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", "--allow-file-access-from-files",
         "--virtual-time-budget=3000", "--window-size=1000,1500",
         f"--screenshot={out_png}", f"file://{path}"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    os.unlink(path)


def main():
    with open(os.path.join(ROOT, "scripts", "pins_v2.json"), encoding="utf-8") as f:
        pins = json.load(f)
    only = set(sys.argv[1:])
    for p in pins:
        if only and p["image"] not in only:
            continue
        color, tint = COLORS[p["board"]]
        page = photo_html(p, color, tint) if p["style"] == "photo" else list_html(p, color, tint)
        render(page, os.path.join(ROOT, "pins", p["image"]))
        print("made", p["image"])


if __name__ == "__main__":
    main()
