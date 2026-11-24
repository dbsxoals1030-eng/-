#!/usr/bin/env python3
"""블로그 포스팅용 카드 이미지 5장 생성기 (1080x1350, 4:5).

사용: python3 blog/make_blog_images.py   →  blog/inflation-sample/01~05.png
스타일: 딥 네이비 + 골드 포인트, Pretendard, 얇은 라인과 큰 타이포(카드뉴스형 프리미엄 톤)
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "inflation-sample")
os.makedirs(OUT, exist_ok=True)

FONT = {
    "black": os.path.join(ROOT, "fonts/Pretendard-Black.otf"),
    "xbold": os.path.join(ROOT, "fonts/Pretendard-ExtraBold.otf"),
    "bold": os.path.join(ROOT, "../mbti-shorts/fonts/Pretendard-Bold.otf"),
    "med": os.path.join(ROOT, "../mbti-shorts/fonts/Pretendard-Medium.otf"),
}

W, H = 1080, 1350
S = 2  # 슈퍼샘플링 배율 (2160x2700에서 그려 축소 → 선명한 가장자리)

NAVY_TOP = (7, 12, 26)
NAVY_BOT = (19, 30, 62)
GOLD = (212, 175, 106)
GOLD_LIGHT = (245, 224, 168)
GOLD_DARK = (150, 112, 52)
WHITE = (246, 247, 250)
MUTED = (143, 154, 182)
LINE = (70, 84, 120)

CHANNEL = "MOTION ECONOMY"
TOTAL = 5


def f(kind, size):
    return ImageFont.truetype(FONT[kind], int(size * S))


def p(v):
    return int(round(v * S))


def background():
    """세로 그라데이션 + 은은한 골드 글로우 + 비네팅 + 필름 그레인."""
    y = np.linspace(0, 1, H * S)[:, None, None]
    top = np.array(NAVY_TOP, dtype=np.float32)[None, None, :]
    bot = np.array(NAVY_BOT, dtype=np.float32)[None, None, :]
    img = top + (bot - top) * y
    img = np.repeat(img, W * S, axis=1)

    yy, xx = np.mgrid[0:H * S, 0:W * S].astype(np.float32)
    # 우상단 골드 글로우
    d = np.sqrt((xx - W * S * 0.85) ** 2 + (yy - H * S * 0.12) ** 2) / (W * S * 0.7)
    glow = np.clip(1 - d, 0, 1) ** 2.2
    img += glow[..., None] * np.array([46, 34, 12], dtype=np.float32)
    # 비네팅
    dv = np.sqrt(((xx - W * S / 2) / (W * S / 2)) ** 2 + ((yy - H * S / 2) / (H * S / 2)) ** 2)
    img *= (1 - 0.28 * np.clip(dv - 0.55, 0, 1) ** 1.5)[..., None]
    # 그레인
    rng = np.random.default_rng(7)
    img += rng.normal(0, 2.2, (H * S, W * S, 1)).astype(np.float32)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def text(d, xy, s, kind, size, fill=WHITE, anchor="la", spacing=None):
    d.text((p(xy[0]), p(xy[1])), s, font=f(kind, size), fill=fill, anchor=anchor)


def multiline(d, x, y, lines, kind, size, fill=WHITE, lead=1.28, anchor="la"):
    for i, ln in enumerate(lines):
        text(d, (x, y + i * size * lead), ln, kind, size, fill, anchor)


def gold_gradient_text(img, xy, s, kind, size, anchor="la"):
    """골드 그라데이션이 입혀진 텍스트."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text((p(xy[0]), p(xy[1])), s, font=f(kind, size), fill=255, anchor=anchor)
    bbox = mask.getbbox()
    if not bbox:
        return
    grad = Image.new("RGBA", img.size)
    gd = ImageDraw.Draw(grad)
    x0, y0, x1, y1 = bbox
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / max(1, (y1 - y0))
        c = tuple(int(GOLD_LIGHT[i] + (GOLD_DARK[i] - GOLD_LIGHT[i]) * t) for i in range(3))
        gd.line([(x0, yy), (x1, yy)], fill=c + (255,))
    img.paste(grad, (0, 0), mask)


def frame(img, n, label):
    """공통 헤더/푸터."""
    d = ImageDraw.Draw(img)
    # 헤더
    d.line([(p(60), p(96)), (p(W - 60), p(96))], fill=LINE, width=p(1.5))
    text(d, (60, 58), CHANNEL, "xbold", 21, GOLD)
    text(d, (W - 60, 58), label, "med", 21, MUTED, "ra")
    # 푸터
    d.line([(p(60), p(H - 98)), (p(W - 60), p(H - 98))], fill=LINE, width=p(1.5))
    text(d, (60, H - 70), "모션 이코노미 · 경제를 쉽게", "med", 21, MUTED)
    text(d, (W - 60, H - 70), f"{n:02d} / {TOTAL:02d}", "xbold", 21, GOLD, "ra")


def glow_layer(img, drawfn, blur, alpha=1.0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    drawfn(ImageDraw.Draw(layer))
    layer = layer.filter(ImageFilter.GaussianBlur(p(blur)))
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer.putalpha(a)
    img.alpha_composite(layer)


def coin(img, cx, cy, r, missing=None, symbol="₩"):
    """골드 코인. missing=(시작각, 끝각)이면 그 부채꼴이 사라진 코인(가치가 깎임)."""
    box = [p(cx - r), p(cy - r), p(cx + r), p(cy + r)]

    # 바닥 글로우
    glow_layer(img, lambda d: d.ellipse([p(cx - r * 1.05), p(cy - r * 1.05), p(cx + r * 1.05), p(cy + r * 1.05)],
                                        fill=(212, 175, 106, 110)), 46)
    # 그림자
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([p(cx - r), p(cy - r + 26), p(cx + r), p(cy + r + 26)], fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(p(22))))

    # 코인 본체 (대각 그라데이션)
    size = (p(2 * r), p(2 * r))
    yy, xx = np.mgrid[0:size[1], 0:size[0]].astype(np.float32)
    t = np.clip((xx / size[0] * 0.55 + yy / size[1] * 0.75), 0, 1)[..., None]
    c0 = np.array(GOLD_LIGHT, dtype=np.float32)
    c1 = np.array((196, 152, 78), dtype=np.float32)
    c2 = np.array(GOLD_DARK, dtype=np.float32)
    col = np.where(t < 0.5, c0 + (c1 - c0) * (t / 0.5), c1 + (c2 - c1) * ((t - 0.5) / 0.5))
    body = Image.fromarray(col.astype(np.uint8), "RGB").convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size[0] - 1, size[1] - 1], fill=255)
    body.putalpha(mask)

    # 안쪽 링 / 엠보싱
    bd = ImageDraw.Draw(body)
    for k, (inset, w, c) in enumerate([(0.07, 3, (255, 240, 200, 200)), (0.15, 5, (130, 92, 36, 200)),
                                        (0.17, 2, (255, 236, 190, 160))]):
        i = p(r * inset * 2 / 1.0) // 2
        bd.ellipse([i, i, size[0] - 1 - i, size[1] - 1 - i], outline=c, width=p(w))
    # 코인 중앙 기호
    fs = r * 1.05
    glyph = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glyph)
    gd.text((size[0] // 2 + p(3), size[1] // 2 + p(5)), symbol, font=f("black", fs), fill=(110, 76, 26, 230), anchor="mm")
    gd.text((size[0] // 2, size[1] // 2), symbol, font=f("black", fs), fill=(255, 241, 205, 255), anchor="mm")
    body.alpha_composite(glyph)

    if missing:
        cut = Image.new("L", size, 255)
        ImageDraw.Draw(cut).pieslice([-p(2), -p(2), size[0] + p(2), size[1] + p(2)], missing[0], missing[1], fill=0)
        a = ImageChops_multiply(body.getchannel("A"), cut)
        body.putalpha(a)

    img.alpha_composite(body, (box[0], box[1]))

    if missing:
        # 잘려나간 자리: 점선 윤곽으로 '사라진 가치' 표시
        d = ImageDraw.Draw(img)
        steps = 46
        for i in range(steps):
            a0 = missing[0] + (missing[1] - missing[0]) * i / steps
            a1 = missing[0] + (missing[1] - missing[0]) * (i + 0.5) / steps
            d.arc(box, a0, a1, fill=GOLD, width=p(3))
        for ang in missing:
            x = p(cx) + int(math.cos(math.radians(ang)) * p(r))
            y = p(cy) + int(math.sin(math.radians(ang)) * p(r))
            d.line([(p(cx), p(cy)), (x, y)], fill=GOLD, width=p(2))


def ImageChops_multiply(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


def pill(d, x, y, s, kind="bold", size=22, fg=GOLD, outline=GOLD):
    w = d.textlength(s, font=f(kind, size)) / S
    d.rounded_rectangle([p(x), p(y), p(x + w + 44), p(y + size + 26)], radius=p(40), outline=outline, width=p(2))
    text(d, (x + 22, y + 12), s, kind, size, fg)
    return x + w + 44



def rrect(img, box, radius, fill=None, outline=None, width=0):
    """반투명 fill을 올바르게 합성하는 둥근 사각형 (RGBA에 직접 그리면 알파가 덮어써짐)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle([p(v) for v in box], radius=p(radius), fill=fill,
                                            outline=outline, width=p(width) if width else 0)
    img.alpha_composite(layer)


def finish(img, name):
    out = img.resize((W, H), Image.LANCZOS).convert("RGB")
    path = os.path.join(OUT, name)
    out.save(path, optimize=True)
    print("saved", path)


# ------------------------------------------------------------------ 01 표지
def card1():
    img = background()
    frame(img, 1, "경제 쉽게 읽기 · 인플레이션")
    d = ImageDraw.Draw(img)

    pill(d, 60, 150, "STORY 01  |  인플레이션", "bold", 22)
    # 코인 (가치가 25.6% 사라진 코인 = 3%·10년)
    coin(img, 540, 585, 270, missing=(-62, 30))
    d = ImageDraw.Draw(img)
    # 사라진 조각 안에 수치
    text(d, (790, 395), "-25.6%", "black", 52, GOLD_LIGHT, "ma")
    text(d, (790, 460), "10년 뒤", "med", 24, MUTED, "ma")

    gold_gradient_text(img, (60, 905), "1만 원의 가치는", "black", 78)
    text(d, (60, 1000), "어디로 사라졌을까?", "black", 78, WHITE)
    d.line([(p(60), p(1118)), (p(W - 60), p(1118))], fill=GOLD, width=p(2.5))
    text(d, (60, 1146), "물가가 오르면 내 돈이 줄어드는 진짜 이유", "bold", 30, WHITE)
    text(d, (60, 1196), "초보도 3분이면 이해되는 인플레이션 이야기", "med", 25, MUTED)
    finish(img, "01_cover.png")


# ------------------------------------------------------------------ 02 개념
def card2():
    img = background()
    frame(img, 2, "개념 한 줄 정리")
    d = ImageDraw.Draw(img)

    text(d, (60, 150), "인플레이션이란?", "xbold", 30, GOLD)
    multiline(d, 60, 205, ["물가가 오른다 =", "돈의 힘이 약해진다"], "black", 70, WHITE, 1.22)

    # 비교 패널 2개
    def panel(y, title, sub, filled, partial, accent):
        rrect(img, [60, y, W - 60, y + 270], 26, (255, 255, 255, 14), LINE, 2)
        text(d, (96, y + 34), title, "xbold", 34, accent)
        text(d, (96, y + 84), sub, "med", 24, MUTED)
        # 물건 아이콘 10칸
        for i in range(10):
            cx = 96 + 24 + i * 90
            cy = y + 190
            box = [p(cx - 32), p(cy - 32), p(cx + 32), p(cy + 32)]
            d.ellipse(box, outline=LINE, width=p(2))
            if i < filled:
                d.ellipse(box, fill=accent + (255,))
            elif i == filled and partial > 0:
                d.pieslice(box, -90, -90 + 360 * partial, fill=accent + (255,))
                d.ellipse(box, outline=accent, width=p(2))

    panel(480, "지금  |  1만 원", "1,000원짜리 물건을 10개 살 수 있어요", 10, 0, GOLD)
    panel(780, "10년 뒤  |  같은 1만 원", "물가가 매년 3%씩 오르면 약 7.4개", 7, 0.44, (120, 168, 255))

    # 화살표 + 결론
    text(d, (W / 2, 1112), "▼", "bold", 34, GOLD, "ma")
    d.rounded_rectangle([p(60), p(1150), p(W - 60), p(1240)], radius=p(18), fill=GOLD + (255,))
    text(d, (W / 2, 1172), "통장 속 숫자는 그대로, 살 수 있는 양은 줄어듭니다", "xbold", 30, (24, 20, 10), "ma")
    finish(img, "02_concept.png")


# ------------------------------------------------------------------ 03 차트
def card3():
    img = background()
    frame(img, 3, "숫자로 확인하기")
    d = ImageDraw.Draw(img)
    text(d, (60, 150), "물가 연 3%라면", "xbold", 30, GOLD)
    multiline(d, 60, 205, ["1만 원의 구매력은", "이렇게 줄어듭니다"], "black", 66, WHITE, 1.22)

    # 차트 영역
    cx0, cy0, cx1, cy1 = 160, 520, 1000, 1100
    ymax, ymin = 10000, 3000
    X = lambda t: cx0 + (cx1 - cx0) * t / 30
    Y = lambda v: cy1 - (cy1 - cy0) * (v - ymin) / (ymax - ymin)
    for v in (10000, 8000, 6000, 4000):
        d.line([(p(cx0), p(Y(v))), (p(cx1), p(Y(v)))], fill=(60, 74, 110), width=p(1.2))
        text(d, (cx0 - 22, Y(v)), f"{v:,}", "med", 20, MUTED, "rm")
    for t in (0, 10, 20, 30):
        text(d, (X(t), cy1 + 24), "지금" if t == 0 else f"{t}년 뒤", "med", 22, MUTED, "ma")

    pts = [(X(t / 4), Y(10000 / 1.03 ** (t / 4))) for t in range(0, 121)]
    # 영역 채우기
    fill = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(fill)
    fd.polygon([(p(x), p(y)) for x, y in pts] + [(p(cx1), p(cy1)), (p(cx0), p(cy1))], fill=(212, 175, 106, 46))
    img.alpha_composite(fill)
    glow_layer(img, lambda g: g.line([(p(x), p(y)) for x, y in pts], fill=(245, 224, 168, 255), width=p(12)), 12, 0.7)
    d = ImageDraw.Draw(img)
    d.line([(p(x), p(y)) for x, y in pts], fill=GOLD_LIGHT, width=p(6), joint="curve")

    marks = [(0, 10000, "10,000원", "la"), (10, 7441, "7,441원", "ma"), (20, 5537, "5,537원", "ma"), (30, 4120, "4,120원", "ra")]
    for t, v, lab, anc in marks:
        x, y = X(t), Y(v)
        d.line([(p(x), p(y)), (p(x), p(cy1))], fill=(130, 112, 70), width=p(2))
        d.ellipse([p(x - 15), p(y - 15), p(x + 15), p(y + 15)], fill=(12, 18, 36), outline=GOLD_LIGHT, width=p(5))
        if t == 0:
            text(d, (x + 24, y - 66), lab, "black", 34, WHITE, "la")
        else:  # 곡선 아래-왼쪽(영역 안쪽)에 배치해 선과 겹치지 않게
            text(d, (x - 20, y + 26), lab, "black", 34, WHITE, "ra")

    rrect(img, [60, 1180, W - 60, 1244], 16, (255, 255, 255, 16))
    text(d, (W / 2, 1197), "10년 뒤 약 25% · 20년 뒤 약 45% · 30년 뒤 약 59% 감소", "bold", 25, GOLD_LIGHT, "ma")
    finish(img, "03_chart.png")


# ------------------------------------------------------------------ 04 72의 법칙
def card4():
    img = background()
    frame(img, 4, "암산 공식 · 72의 법칙")
    d = ImageDraw.Draw(img)
    text(d, (60, 150), "돈이 반토막 나는 시간은?", "xbold", 30, GOLD)

    # 공식 박스
    rrect(img, [60, 215, W - 60, 445], 26, (255, 255, 255, 14), GOLD, 2.5)
    gold_gradient_text(img, (W / 2, 262), "72 ÷ 물가상승률(%)", "black", 68, "ma")
    d = ImageDraw.Draw(img)
    text(d, (W / 2, 372), "= 내 돈의 가치가 절반이 되는 데 걸리는 햇수", "bold", 29, WHITE, "ma")

    rows = [(2, 36), (3, 24), (4, 18), (6, 12)]
    y = 505
    text(d, (60, y - 4), "물가상승률", "med", 22, MUTED)
    text(d, (W - 60, y - 4), "반토막까지", "med", 22, MUTED, "ra")
    y += 50
    for i, (rate, yrs) in enumerate(rows):
        top = y + i * 150
        rrect(img, [60, top, W - 60, top + 124], 22, (255, 255, 255, 12), LINE, 1.5)
        text(d, (96, top + 62), f"연 {rate}%", "black", 44, WHITE, "lm")
        # 막대 (길수록 오래 버팀)
        bx0, bx1 = 330, 790
        d.rounded_rectangle([p(bx0), p(top + 50), p(bx1), p(top + 74)], radius=p(12), fill=(40, 52, 88))
        w = (bx1 - bx0) * yrs / 36
        hot = rate >= 4
        c = (120, 168, 255) if not hot else GOLD
        d.rounded_rectangle([p(bx0), p(top + 50), p(bx0 + w), p(top + 74)], radius=p(12), fill=c)
        text(d, (W - 96, top + 62), f"{yrs}년", "black", 48, GOLD_LIGHT if hot else WHITE, "rm")
    text(d, (W / 2, 1160), "물가가 천천히 올라도, 시간이 길면 무시할 수 없어요", "bold", 27, WHITE, "ma")
    text(d, (W / 2, 1202), "※ 복리 기준 근사값 · 실제 계산과 소폭 차이가 있을 수 있어요", "med", 20, MUTED, "ma")
    finish(img, "04_rule72.png")


# ------------------------------------------------------------------ 05 정리
def card5():
    img = background()
    frame(img, 5, "오늘의 정리")
    d = ImageDraw.Draw(img)
    text(d, (60, 150), "그래서, 어떻게 해야 할까?", "xbold", 30, GOLD)
    multiline(d, 60, 205, ["내 돈을 지키는", "3가지 습관"], "black", 72, WHITE, 1.2)

    items = [
        ("01", "물가를 알고 시작하기", "내 월급 인상률과 물가상승률을 비교해 보세요."),
        ("02", "'굴리는 돈'과 '쓰는 돈' 나누기", "당장 안 쓸 돈은 물가를 이길 방법을 고민해요."),
        ("03", "한 번에 말고 꾸준히", "분산해서 천천히, 오래 가져가는 습관이 핵심!"),
    ]
    y = 480
    for i, (n, t, s) in enumerate(items):
        top = y + i * 200
        rrect(img, [60, top, W - 60, top + 168], 24, (255, 255, 255, 14), LINE, 2)
        gold_gradient_text(img, (104, top + 84), n, "black", 62, "lm")
        d = ImageDraw.Draw(img)
        d.line([(p(212), p(top + 34)), (p(212), p(top + 134))], fill=GOLD, width=p(2.5))
        text(d, (246, top + 38), t, "xbold", 34, WHITE)
        text(d, (246, top + 98), s, "med", 24, MUTED)

    d.rounded_rectangle([p(60), p(1076), p(W - 60), p(1176)], radius=p(18), fill=GOLD + (255,))
    text(d, (W / 2, 1092), "다음 편 예고  |  금리가 오르면 내 대출이자는?", "black", 30, (24, 20, 10), "ma")
    text(d, (W / 2, 1136), "구독 · 좋아요 · 이웃추가로 다음 이야기도 받아보세요", "bold", 21, (60, 46, 20), "ma")
    text(d, (W / 2, 1202), "※ 본 콘텐츠는 정보 제공 목적이며, 투자 판단과 책임은 본인에게 있습니다.", "med", 19, MUTED, "ma")
    finish(img, "05_summary.png")


if __name__ == "__main__":
    card1()
    card2()
    card3()
    card4()
    card5()
