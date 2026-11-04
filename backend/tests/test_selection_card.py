import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from app.card import render_selection_card

RED = (200, 50, 100)


def _cover(color=RED):
    buf = io.BytesIO()
    Image.new("RGB", (300, 450), color).save(buf, "PNG")
    return buf.getvalue()


def _open(png):
    img = Image.open(io.BytesIO(png))
    img.load()
    return img


def _item(i=1, cover=None):
    return {"title": f"Книга {i}", "author": "Автор Авторов", "cover_bytes": cover}


def test_card_is_a_valid_png():
    png = render_selection_card([_item(i, _cover()) for i in range(3)], "Моя подборка", "03.11.2026")
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert _open(png).size == (1500, 820)


def test_cover_is_really_drawn():
    img = _open(render_selection_card([_item(1, _cover())]))
    assert img.getpixel((750, 365))[:3] == RED


def test_missing_covers_get_placeholders():
    img = _open(render_selection_card([_item(i) for i in range(5)]))
    assert img.size == (1500, 820)


def test_only_five_books_are_shown():
    assert _open(render_selection_card([_item(i) for i in range(8)])).size == (1500, 820)


def test_broken_cover_and_long_text_do_not_crash():
    item = {"title": "Очень длинное название книги " * 8, "author": "Автор " * 20, "cover_bytes": b"not an image"}
    assert render_selection_card([item]).startswith(b"\x89PNG")
