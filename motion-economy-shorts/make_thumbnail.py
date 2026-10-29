#!/usr/bin/env python3
"""Shorts thumbnail generator (1080x1920, 9:16).

Style: bright product photo on a soft gray backdrop, 3-line headline on top:
  line 1 = yellow bold, line 2 = white bold, line 3 = small white #hashtag,
  all with a thick black outline and a soft drop shadow.

Usage:
  make_thumbnail.py --line1 "폰도 태블릿도" --line2 "이거 하나로 끝!" \
      --tag "#갤럭시Z폴드8" --photo product.png --out thumb.png
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "Pretendard-Black.otf")
YELLOW, WHITE, BLACK = (255, 230, 0), (255, 255, 255), (0, 0, 0)

# (text color, target width as fraction of W, center y as fraction of H, max font px)
LINES = [(YELLOW, 0.71, 0.075, 190), (WHITE, 0.78, 0.155, 190), (WHITE, 0.41, 0.235, 110)]


def backdrop():
    top, bot = (194, 194, 196), (232, 232, 236)
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        g.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
    return g.resize((W, H))


def place_photo(canvas, path):
    """Product/hand photo: cover-fit the area under the headline (bleeds off the
    sides/bottom), top edge feathered into the backdrop."""
    top = int(H * 0.25)
    bw, bh = W, H - top
    im = Image.open(path).convert("RGBA")
    s = max(bw / im.width, bh / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    l, t = (im.width - bw) // 2, im.height - bh  # anchor to the bottom
    im = im.crop((l, t, l + bw, t + bh))
    fade = int(bh * 0.12)
    mask = Image.new("L", (bw, bh), 255)
    for y in range(fade):
        ImageDraw.Draw(mask).line([(0, y), (bw, y)], fill=int(255 * y / fade))
    im.putalpha(Image.composite(im.getchannel("A"), Image.new("L", (bw, bh), 0), mask))
    canvas.alpha_composite(im, (0, top))


def fit_font(text, frac, max_px):
    size = max_px
    while size > 20:
        f = ImageFont.truetype(FONT, size)
        if f.getlength(text) <= W * frac:
            return f
        size -= 2
    return ImageFont.truetype(FONT, 20)


def draw_line(canvas, text, color, frac, cy_frac, max_px):
    f = fit_font(text, frac, max_px)
    stroke = max(4, int(f.size * 0.09))
    pos = (W / 2, H * cy_frac)
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((pos[0], pos[1] + f.size * 0.05), text, font=f, anchor="mm",
                                fill=(0, 0, 0, 120), stroke_width=stroke, stroke_fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(f.size * 0.04))
    canvas.alpha_composite(shadow)
    ImageDraw.Draw(canvas).text(pos, text, font=f, anchor="mm", fill=color,
                                stroke_width=stroke, stroke_fill=BLACK)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--line1", required=True, help="yellow hook line")
    ap.add_argument("--line2", required=True, help="white payoff line")
    ap.add_argument("--tag", default="", help="small white hashtag line, e.g. #제품명")
    ap.add_argument("--photo", help="product/hand photo (PNG with transparency works best)")
    ap.add_argument("--bg", help="full-bleed background image instead of the gray gradient")
    ap.add_argument("--out", default="thumbnail.png")
    a = ap.parse_args()

    if a.bg:
        bg = Image.open(a.bg).convert("RGB")
        s = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * s), int(bg.height * s)), Image.LANCZOS)
        l, t = (bg.width - W) // 2, (bg.height - H) // 2
        canvas = bg.crop((l, t, l + W, t + H)).convert("RGBA")
    else:
        canvas = backdrop().convert("RGBA")
    if a.photo:
        place_photo(canvas, a.photo)
    for (color, frac, cy, mx), text in zip(LINES, [a.line1, a.line2, a.tag]):
        if text:
            draw_line(canvas, text, color, frac, cy, mx)
    canvas.convert("RGB").save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
