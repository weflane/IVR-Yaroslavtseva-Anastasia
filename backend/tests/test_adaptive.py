import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.quiz_logic import available_options

BOOKS = [
    ("1", "Дюна", ["Фантастика", "Задумчивое"], "slow", 700),
    ("2", "Марсианин", ["Фантастика", "Радостное"], "fast", 400),
    ("3", "Маленький принц", ["Классика", "Грустное", "Задумчивое"], "slow", 100),
    ("4", "Гордость и предубеждение", ["Роман", "Классика", "Радостное"], "medium", 430),
    ("5", "Убийство в Восточном экспрессе", ["Детектив", "Напряжённое"], "fast", 256),
]


def test_without_answers_everything_that_exists_is_offered():
    options = available_options({}, BOOKS)
    assert set(options["mood"]) == {"sad", "uplifting", "philosophical", "tense"}
    assert set(options["genre"]) == {"mystery", "sci-fi", "romance", "classic"}
    assert options["pace"] == ["slow", "medium", "fast"]
    assert options["count"] == 5


def test_genres_are_narrowed_by_mood():
    options = available_options({"mood": "sad"}, BOOKS)
    assert options["genre"] == ["classic"]
    assert options["count"] == 1


def test_paces_are_narrowed_by_mood_and_genre():
    options = available_options({"mood": "uplifting", "genre": "sci-fi"}, BOOKS)
    assert options["pace"] == ["fast"]


def test_lengths_depend_on_chosen_pace():
    options = available_options({"mood": "philosophical", "pace": "slow"}, BOOKS)
    assert options["length"] == ["short", "long"]


def test_read_books_do_not_count():
    options = available_options({"mood": "sad"}, BOOKS, exclude_ids=["3"])
    assert options["count"] == 0
    assert options["genre"] == []


def test_dead_end_gives_empty_lists():
    options = available_options({"mood": "tense", "genre": "romance"}, BOOKS)
    assert options["count"] == 0
    assert options["pace"] == [] and options["length"] == []


def test_unknown_answer_is_ignored():
    assert available_options({"mood": "???"}, BOOKS)["count"] == 5
