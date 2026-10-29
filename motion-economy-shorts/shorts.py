#!/usr/bin/env python3
"""모션 이코노미 shorts generator: spec.json -> narrated 9:16 video + thumbnail.

  python3 shorts.py specs/example.json --check   # TTS only; prints per-scene and total length
  python3 shorts.py specs/example.json           # full render (video.mp4 + thumbnail.png in spec["out"])

Rules baked in (see README.md): narration at 1.5x, ~30s, house style (yellow hook line / white payoff line,
black outline, gray gradient, white info cards, big captions, channel footer).
"""
import argparse, json, math, os, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_thumbnail as mt  # noqa: E402

W, H, FPS = 1080, 1920, 30
BLACK_F, XB_F = os.path.join(HERE, "fonts", "Pretendard-Black.otf"), os.path.join(HERE, "fonts", "Pretendard-ExtraBold.otf")
YEL, WHT, BLK = (255, 230, 0), (255, 255, 255), (0, 0, 0)
UP, DOWN, GRY, INK, SUB = (232, 40, 48), (40, 110, 255), (120, 120, 128), (30, 30, 36), (60, 60, 70)  # KR convention: up=red, down=blue
CARD = (90, 500, 990, 1300)
_fonts = {}


def F(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


ease = lambda t: 1 - (1 - max(0.0, min(1.0, t))) ** 3
seg = lambda t, a, b: ease((t - a) / (b - a))


def txt(d, xy, s, font, fill, stroke=0, anchor="mm"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=BLK)


def fit(s, path, frac, mx):
    sz = mx
    while sz > 24 and F(path, sz).getlength(s) > W * frac:
        sz -= 2
    return F(path, sz)


def card(img, box=CARD, r=48):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + 14, box[2], box[3] + 14), r, fill=(0, 0, 0, 70))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    ImageDraw.Draw(img).rounded_rectangle(box, r, fill=(255, 255, 255))


def backdrop():
    g = Image.new("RGB", (1, H))
    for y in range(H):
        k = y / (H - 1)
        g.putpixel((0, y), tuple(int(a + (b - a) * k) for a, b in zip((194, 194, 196), (236, 236, 240))))
    return g.resize((W, H)).convert("RGBA")


def color_of(direction):
    return UP if direction == "up" else DOWN if direction == "down" else GRY


def direction_of(delta):
    return "up" if delta > 0 else "down" if delta < 0 else "flat"


# ------------------------------------------------------------------ graphics
def g_stat_card(img, t, p):
    """{name, logo?, from, to, decimals?, unit?, badge?, note?} price count-up; % computed from from/to."""
    card(img)
    d = ImageDraw.Draw(img)
    y = 575
    if p.get("logo"):
        a = seg(t, .05, .55)
        L = Image.open(os.path.join(HERE, "assets", p["logo"])).convert("RGBA")
        lw = int(560 * (.8 + .2 * a)); lh = int(L.height * lw / L.width)
        L = L.resize((lw, lh), Image.LANCZOS)
        L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(L, (W // 2 - lw // 2, 560))
        d = ImageDraw.Draw(img)
        y = 560 + lh + 35
    txt(d, (W / 2, y), p["name"], F(XB_F, 46), SUB)
    dec, unit = p.get("decimals", 0), p.get("unit", "원")
    frm, to = float(p["from"]), float(p["to"])
    cur = frm + (to - frm) * seg(t, .3, 1.8)
    pct = (cur - frm) / frm * 100
    col = color_of(direction_of(to - frm))
    txt(d, (W / 2, y + 125), f"{cur:,.{dec}f}{unit}", F(BLACK_F, 130), INK)
    arrow = "▲" if to >= frm else "▼"
    txt(d, (W / 2, y + 250), f"{arrow} {abs(pct):.2f}%", F(BLACK_F, 105), col)
    b = seg(t, 1.6, 2.1)
    if p.get("badge") and b > 0:
        bw, bh = int(460 * b), int(110 * b)
        cy = y + 360
        d.rounded_rectangle((W / 2 - bw / 2, cy - bh / 2, W / 2 + bw / 2, cy + bh / 2), 30, fill=col)
        if b > .8:
            txt(d, (W / 2, cy), p["badge"], F(BLACK_F, 84), WHT)
    if p.get("note"):
        txt(d, (W / 2, CARD[3] - 26), p["note"], F(XB_F, 28), GRY)


def g_stat_grid(img, t, p):
    """{title?, tiles:[{label, value, change, dir:'up'|'down'|'flat'}]} up to 5 rows (indices, FX, ...)."""
    card(img)
    d = ImageDraw.Draw(img)
    top = 560
    if p.get("title"):
        txt(d, (W / 2, 585), p["title"], F(XB_F, 46), SUB)
        top = 660
    tiles = p["tiles"][:5]
    rowh = min(150, (CARD[3] - 40 - top) // max(1, len(tiles)))
    for i, tl in enumerate(tiles):
        a = seg(t, .15 + i * .3, .55 + i * .3)
        if a <= 0:
            continue
        y = top + i * rowh + rowh // 2
        off = int((1 - a) * 60)
        col = color_of(tl.get("dir", "flat"))
        d.rounded_rectangle((130 + off, y - rowh // 2 + 8, 950 + off, y + rowh // 2 - 8), 28, fill=(244, 244, 248))
        txt(d, (170 + off, y), tl["label"], F(XB_F, 42), SUB, anchor="lm")
        txt(d, (640 + off, y), tl["value"], F(BLACK_F, 52), INK, anchor="rm")
        txt(d, (925 + off, y), tl["change"], F(BLACK_F, 44), col, anchor="rm")


def g_bars(img, t, p):
    """{title, rows:[{label, value, text, color?:'up'|'down'|'gray'}], note?} horizontal bars scaled to max value."""
    card(img)
    d = ImageDraw.Draw(img)
    txt(d, (W / 2, 590), p["title"], F(XB_F, 48), SUB)
    rows = p["rows"][:4]
    mx = max(r["value"] for r in rows) or 1
    n = len(rows)
    gap = min(250, (1130 - 740) // (n - 1)) if n > 1 else 0
    half = int(min(60, gap * .38)) if n > 1 else 60
    for i, r in enumerate(rows):
        y = 740 + i * gap
        a = seg(t, .2 + i * .5, 1.1 + i * .5)
        w = int(540 * r["value"] / mx * a)
        col = {"up": UP, "down": DOWN}.get(r.get("color", "up"), GRY)
        d.rounded_rectangle((330, y - half, 870, y + half), 24, fill=(232, 232, 236))
        d.rounded_rectangle((330, y - half, 330 + max(w, 8), y + half), 24, fill=col)
        txt(d, (120, y), r["label"], F(XB_F, 38), INK, anchor="lm")
        if a > .9:
            txt(d, (600, y), r["text"], F(BLACK_F, 56), WHT if w > 300 else INK)
    if p.get("note"):
        txt(d, (W / 2, CARD[3] - 40), p["note"], F(XB_F, 38), SUB)


def g_bullets(img, t, p):
    """{title?, items:[str]} up to 4 pill rows revealed one by one."""
    card(img)
    d = ImageDraw.Draw(img)
    top = 560
    if p.get("title"):
        txt(d, (W / 2, 590), p["title"], F(XB_F, 48), SUB)
        top = 660
    items = p["items"][:4]
    rowh = min(150, (CARD[3] - 50 - top) // max(1, len(items)))
    for i, s in enumerate(items):
        a = seg(t, .15 + i * .45, .6 + i * .45)
        if a <= 0:
            continue
        y = top + i * rowh + rowh // 2
        off = int((1 - a) * 80)
        d.rounded_rectangle((120 + off, y - rowh // 2 + 8, 960 + off, y + rowh // 2 - 8), 30, fill=(244, 244, 248))
        d.ellipse((145 + off, y - 34, 213 + off, y + 34), fill=UP)
        txt(d, (179 + off, y), str(i + 1), F(BLACK_F, 44), WHT)
        txt(d, (245 + off, y), s, fit(s, XB_F, .62, 46), INK, anchor="lm")


def g_big_text(img, t, p):
    """{big, sub?, color?:'up'|'down'|'ink'} one huge number/keyword."""
    card(img)
    d = ImageDraw.Draw(img)
    a = seg(t, .1, .7)
    f = fit(p["big"], BLACK_F, .78, 200)
    col = {"up": UP, "down": DOWN}.get(p.get("color", "ink"), INK)
    txt(d, (W / 2, 880 - int((1 - a) * 40)), p["big"], F(BLACK_F, max(24, int(f.size * (.85 + .15 * a)))), col)
    if p.get("sub"):
        txt(d, (W / 2, 1090), p["sub"], fit(p["sub"], XB_F, .78, 52), SUB)


def g_line(img, t, p):
    """{title?, values:[float...] REAL data only, start_label?, end_label?, note?} line chart drawn progressively."""
    card(img)
    d = ImageDraw.Draw(img)
    if p.get("title"):
        txt(d, (W / 2, 590), p["title"], F(XB_F, 48), SUB)
    vals = p["values"]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    x0, x1, y0, y1 = 170, 910, 1130, 720
    pts = [(x0 + (x1 - x0) * i / (len(vals) - 1), y0 - (y0 - y1) * (v - lo) / span) for i, v in enumerate(vals)]
    a = seg(t, .1, 1.4)
    n = max(2, int(len(pts) * a))
    col = color_of(direction_of(vals[-1] - vals[0]))
    d.line(pts[:n], fill=col, width=12, joint="curve")
    if p.get("start_label"):
        txt(d, (x0, 1180), p["start_label"], F(XB_F, 34), GRY, anchor="lm")
    if p.get("end_label") and a > .95:
        txt(d, (x1, 1180), p["end_label"], F(XB_F, 34), col, anchor="rm")
    if p.get("note"):
        txt(d, (W / 2, 1250), p["note"], F(XB_F, 32), SUB)


GRAPHICS = {"stat_card": g_stat_card, "stat_grid": g_stat_grid, "bars": g_bars, "bullets": g_bullets,
            "big_text": g_big_text, "line": g_line}


# ------------------------------------------------------------------ frames
def header(d, t, head):
    a = seg(t, 0, .25)
    off = int((1 - a) * -60)
    f1, f2 = fit(head[0], BLACK_F, .80, 150), fit(head[1], BLACK_F, .84, 130)
    txt(d, (W / 2, 150 + off), head[0], f1, YEL, int(f1.size * .09))
    txt(d, (W / 2, 320 + off), head[1], f2, WHT, int(f2.size * .09))


def captions(d, text, dur_audio, t):
    clauses = [c for c in re.split(r"(?<=[,.!?])\s*", text) if c]
    tot = sum(len(c) for c in clauses); acc = 0; cur = clauses[-1]
    for c in clauses:
        acc += len(c)
        if t <= acc / tot * dur_audio:
            cur = c
            break
    cur = cur.rstrip(",.")
    txt(d, (W / 2, 1500), cur, fit(cur, XB_F, .88, 78), WHT, 9)


def footer(d, spec):
    txt(d, (W / 2, 1790), spec.get("channel", "모션 이코노미"), F(XB_F, 40), SUB)
    txt(d, (W / 2, 1850), spec.get("disclaimer", "※ 투자 판단과 책임은 본인에게 있습니다"), F(XB_F, 28), (110, 110, 120))


def frame(spec, sc, t, dur_audio):
    img = backdrop()
    d = ImageDraw.Draw(img)
    header(d, t, sc["head"])
    GRAPHICS[sc["graphic"]["type"]](img, t, sc["graphic"])
    d = ImageDraw.Draw(img)
    captions(d, sc["narration"], dur_audio, t)
    footer(d, spec)
    return img.convert("RGB")


def render_scene(args):
    spec, i, dur, dur_audio, out = args
    sc = spec["scenes"][i]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", out],
                         stdin=subprocess.PIPE)
    for fr in range(int(round(dur * FPS))):
        p.stdin.write(frame(spec, sc, fr / FPS, dur_audio).tobytes())
    p.stdin.close(); p.wait()
    return i


# ------------------------------------------------------------------ audio
def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())


def tts(spec, work):
    from gtts import gTTS
    raws = []
    for i, sc in enumerate(spec["scenes"]):
        path = os.path.join(work, f"n{i}.mp3")
        for attempt in range(3):
            try:
                gTTS(sc["narration"], lang="ko").save(path)
                break
            except Exception as e:  # network hiccup
                if attempt == 2:
                    raise
                print("tts retry", i, e)
        raws.append(probe(path))
    return raws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--check", action="store_true", help="TTS only: print durations, no render")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    tempo, gap = float(spec.get("tempo", 1.5)), float(spec.get("gap", .3))
    out = spec.get("out", "out/video")
    work = os.path.join(out, "work")
    os.makedirs(work, exist_ok=True)
    raws = tts(spec, work)
    durs = [r / tempo + gap for r in raws]
    for i, (r, dd) in enumerate(zip(raws, durs)):
        print(f"scene {i}: raw {r:.1f}s -> {dd:.1f}s  {spec['scenes'][i]['narration'][:30]}")
    total = sum(durs)
    print(f"TOTAL {total:.1f}s (tempo {tempo}x)" + ("" if 28 <= total <= 32 else "   <-- outside 28-32s, edit narration"))
    if a.check:
        return

    # audio at 1.5x
    ins, filt = [], []
    for i in range(len(raws)):
        ins += ["-i", os.path.join(work, f"n{i}.mp3")]
        filt.append(f"[{i}:a]atempo={tempo},apad=pad_dur={gap}[a{i}]")
    fc = ";".join(filt) + ";" + "".join(f"[a{i}]" for i in range(len(raws))) + f"concat=n={len(raws)}:v=0:a=1,loudnorm=I=-14:TP=-1.5[out]"
    narr = os.path.join(work, "narration.m4a")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[out]", narr])

    # frames (parallel per scene)
    jobs = [(spec, i, durs[i], raws[i] / tempo, os.path.join(work, f"seg{i}.mp4")) for i in range(len(raws))]
    with Pool(min(4, os.cpu_count() or 1)) as pool:
        for i in pool.imap_unordered(render_scene, jobs):
            print("scene", i, "rendered", flush=True)
    lst = os.path.join(work, "list.txt")
    open(lst, "w").write("".join(f"file 'seg{i}.mp4'\n" for i in range(len(raws))))
    silent = os.path.join(work, "silent.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent])
    video = os.path.join(out, "video.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", narr, "-c:v", "copy", "-c:a", "aac",
                           "-b:a", "192k", "-shortest", video])

    # thumbnail: house-style headline + first scene's graphic (final state) as the hero card
    th = spec.get("thumb") or {}
    first = spec["scenes"][0]
    canvas = backdrop()
    hero = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    GRAPHICS[first["graphic"]["type"]](hero, 99.0, first["graphic"])
    hero = hero.crop(CARD).convert("RGBA")
    s = 1.12
    hero = hero.resize((int(hero.width * s), int(hero.height * s)), Image.LANCZOS)
    canvas.alpha_composite(hero, ((W - hero.width) // 2, 640))
    for (color, frac, cy, mx), text in zip(mt.LINES, [th.get("line1", first["head"][0]), th.get("line2", first["head"][1]), th.get("tag", "")]):
        if text:
            mt.draw_line(canvas, text, color, frac, cy, mx)
    canvas.convert("RGB").save(os.path.join(out, "thumbnail.png"))
    print("DONE", video, f"{probe(video):.1f}s")


if __name__ == "__main__":
    main()
