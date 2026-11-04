import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.card import render_book_card
from app.emotions import build_emotion_map
from app.quiz_logic import book_score, pick_books


def info(i, tags, pace="medium", pages=300):
    return (f"b{i}", f"Книга {i:03d}", tags, pace, pages)


def test_score_weights():
    answers = {"mood": "sad", "genre": "classic", "pace": "slow", "length": "long"}
    assert book_score(answers, ["Грустное", "Классика"], "slow", 600) == 6
    assert book_score(answers, [], "fast", 100) == 0


def test_pick_returns_at_most_five_and_best_first():
    answers = {"mood": "tense", "genre": "mystery"}
    books = [info(i, ["Напряжённое", "Детектив"] if i < 8 else ["Роман"]) for i in range(20)]
    result = pick_books(answers, books)
    assert len(result) == 5
    assert all(int(r[1:]) < 8 for r in result)


def test_pick_excludes_read_books():
    answers = {"mood": "tense", "genre": "mystery"}
    books = [info(i, ["Напряжённое", "Детектив"]) for i in range(10)]
    read = {"b0", "b1", "b2"}
    assert not read & set(pick_books(answers, books, exclude_ids=read))


def test_pick_pads_to_minimum_three():
    answers = {"mood": "sad"}
    books = [info(0, ["Грустное"])] + [info(i, ["Роман"]) for i in range(1, 10)]
    result = pick_books(answers, books)
    assert result[0] == "b0"
    assert len(result) == 3


def test_pick_small_catalog_and_empty():
    assert len(pick_books({"mood": "sad"}, [info(0, [])])) == 1
    assert pick_books({"mood": "sad"}, []) == []


def test_pick_random_tiebreak_varies():
    import random
    books = [info(i, ["Грустное"]) for i in range(50)]
    seen = {tuple(pick_books({"mood": "sad"}, books, rng=random.Random(s))) for s in range(10)}
    assert len(seen) > 1


def test_emotion_map_axes():
    m = build_emotion_map(["Грустное"], "slow", 350)
    assert [x["key"] for x in m] == ["sad", "uplifting", "philosophical", "tense", "pace", "volume"]
    assert m[0]["value"] == 85 and m[1]["value"] == 10
    assert m[4]["value"] == 30 and m[5]["value"] == 50
    manual = build_emotion_map([], "fast", 5000, {"tense": 300, "sad": -5})
    assert manual[3]["value"] == 100 and manual[0]["value"] == 0 and manual[5]["value"] == 100


def test_card_is_valid_png_without_cover():
    png = render_book_card("Тест", "Автор", "Описание " * 50, ["Грустное"], None,
                           build_emotion_map(["Грустное"], "slow", 300), 300, "неспешный")
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", png[16:24])
    assert (width, height) == (800, 1200)
