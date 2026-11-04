"""Рендер визуальной карточки книги в PNG (Pillow)."""
import io
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 800, 1200
PINK = (232, 99, 150)
PINK_DEEP = (176, 52, 104)
PINK_SOFT = (253, 232, 241)
PINK_LINE = (244, 196, 218)
TEXT = (51, 35, 44)
TEXT_SOFT = (120, 96, 108)

_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
    "/usr/share/fonts/TTF",
    "/Library/Fonts",
    "C:/Windows/Fonts",
]
_REGULAR = ["DejaVuSans.ttf", "Arial.ttf", "arial.ttf", "LiberationSans-Regular.ttf"]
_BOLD = ["DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf", "LiberationSans-Bold.ttf"]


def _font(size, bold=False):
    env = os.getenv("CARD_FONT_BOLD" if bold else "CARD_FONT")
    candidates = [env] if env else []
    for d in _FONT_DIRS:
        for name in (_BOLD if bold else _REGULAR):
            candidates.append(os.path.join(d, name))
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, TypeError):
            continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width, max_lines):
    words = (text or "").split()
    lines, line = [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            line = trial
            continue
        if line:
            lines.append(line)
        line = word
        if len(lines) == max_lines:
            break
    if line and len(lines) < max_lines:
        lines.append(line)
    consumed = " ".join(lines).split()
    if len(consumed) < len(words) and lines:
        last = lines[-1]
        while last and draw.textlength(last + "…", font=font) > max_width:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines


def _cover_image(cover_bytes, size, title):
    cw, ch = size
    if cover_bytes:
        try:
            img = Image.open(io.BytesIO(cover_bytes)).convert("RGB")
            scale = max(cw / img.width, ch / img.height)
            img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))))
            left, top = (img.width - cw) // 2, (img.height - ch) // 2
            return img.crop((left, top, left + cw, top + ch))
        except Exception:
            pass
    ph = Image.new("RGB", size, PINK_SOFT)
    d = ImageDraw.Draw(ph)
    letter = (title or "?").strip()[:1].upper() or "?"
    f = _font(160, bold=True)
    tw = d.textlength(letter, font=f)
    d.text(((cw - tw) / 2, ch / 2 - 110), letter, font=f, fill=PINK)
    return ph


def render_book_card(title, author, description="", tags=(), cover_bytes=None,
                     emotion_map=(), pages=None, pace_label=None):
    """Возвращает PNG (bytes) с обложкой, названием, тегами, аннотацией и эмоциональной картой."""
    img = Image.new("RGB", (W, H), (255, 247, 251))
    d = ImageDraw.Draw(img)

    d.rectangle((0, 0, W, 14), fill=PINK)

    cw, ch = 300, 450
    cx, cy = (W - cw) // 2, 50
    d.rounded_rectangle((cx - 6, cy - 6, cx + cw + 6, cy + ch + 6), radius=18, fill=PINK_LINE)
    cover = _cover_image(cover_bytes, (cw, ch), title)
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw, ch), radius=14, fill=255)
    img.paste(cover, (cx, cy), mask)

    y = cy + ch + 40
    margin = 60
    max_w = W - 2 * margin

    f_title = _font(40, bold=True)
    for line in _wrap(d, title, f_title, max_w, 2):
        d.text((W / 2, y), line, font=f_title, fill=TEXT, anchor="ma")
        y += 50
    y += 4
    f_author = _font(26)
    d.text((W / 2, y), author or "", font=f_author, fill=TEXT_SOFT, anchor="ma")
    y += 44

    meta = []
    if pages:
        meta.append(f"{pages} стр.")
    if pace_label:
        meta.append(f"темп: {pace_label}")
    if meta:
        d.text((W / 2, y), " · ".join(meta), font=_font(20), fill=TEXT_SOFT, anchor="ma")
        y += 38
    f_tag = _font(20)
    pills, total = [], 0
    for t in list(tags)[:5]:
        w = int(d.textlength(t, font=f_tag)) + 28
        if total + w > max_w:
            break
        pills.append((t, w))
        total += w + 10
    x = (W - (total - 10)) / 2 if pills else 0
    for t, w in pills:
        d.rounded_rectangle((x, y, x + w, y + 36), radius=18, fill=PINK_SOFT)
        d.text((x + w / 2, y + 18), t, font=f_tag, fill=PINK_DEEP, anchor="mm")
        x += w + 10
    y += 56 if pills else 10

    f_desc = _font(22)
    for line in _wrap(d, description, f_desc, max_w, 4):
        d.text((margin, y), line, font=f_desc, fill=TEXT)
        y += 32
    y += 16
    items = list(emotion_map)
    if items:
        d.text((margin, y), "Эмоциональная карта", font=_font(22, bold=True), fill=PINK_DEEP)
        y += 38
        f_lbl = _font(19)
        bar_x, bar_w = margin + 170, max_w - 170
        for item in items[:6]:
            d.text((margin, y), item["label"], font=f_lbl, fill=TEXT_SOFT)
            d.rounded_rectangle((bar_x, y + 4, bar_x + bar_w, y + 20), radius=8, fill=PINK_SOFT)
            fill_w = max(8, int(bar_w * item["value"] / 100))
            d.rounded_rectangle((bar_x, y + 4, bar_x + fill_w, y + 20), radius=8, fill=PINK)
            y += 30

    d.text((W / 2, H - 38), "BookMatch", font=_font(22, bold=True), fill=PINK, anchor="mm")

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


def render_selection_card(items, title="Моя подборка", subtitle=""):
    items = list(items)[:5]
    cw, ch, gap, margin = 260, 390, 25, 50
    width, height = 1500, 820
    img = Image.new("RGB", (width, height), (255, 247, 251))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, width, 14), fill=PINK)

    d.text((width / 2, 56), title, font=_font(46, bold=True), fill=PINK_DEEP, anchor="ma")
    if subtitle:
        d.text((width / 2, 118), subtitle, font=_font(24), fill=TEXT_SOFT, anchor="ma")

    total = len(items) * cw + max(0, len(items) - 1) * gap
    x0 = (width - total) // 2
    f_title, f_author = _font(24, bold=True), _font(20)
    for i, item in enumerate(items):
        x, y = x0 + i * (cw + gap), 170
        d.rounded_rectangle((x - 5, y - 5, x + cw + 5, y + ch + 5), radius=16, fill=PINK_LINE)
        cover = _cover_image(item.get("cover_bytes"), (cw, ch), item.get("title"))
        mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw, ch), radius=12, fill=255)
        img.paste(cover, (x, y), mask)

        ty = y + ch + 24
        for line in _wrap(d, item.get("title"), f_title, cw, 3):
            d.text((x + cw / 2, ty), line, font=f_title, fill=TEXT, anchor="ma")
            ty += 30
        for line in _wrap(d, item.get("author"), f_author, cw, 1):
            d.text((x + cw / 2, ty + 4), line, font=f_author, fill=TEXT_SOFT, anchor="ma")

    d.text((width / 2, height - 34), "BookMatch", font=_font(22, bold=True), fill=PINK, anchor="mm")
    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()
