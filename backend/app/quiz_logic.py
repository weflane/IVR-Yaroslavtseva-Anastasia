MOOD_TAGS = {
    "sad": "Грустное",
    "uplifting": "Радостное",
    "philosophical": "Задумчивое",
    "tense": "Напряжённое",
}
GENRE_TAGS = {
    "mystery": "Детектив",
    "sci-fi": "Фантастика",
    "romance": "Роман",
    "classic": "Классика",
}

LENGTH_RANGES = {
    "short": (0, 300),
    "medium": (300, 500),
    "long": (500, None),
}

TOP_N = 5


def book_score(answers, tag_names, pace, page_count):
    """Сколько баллов набирает книга: тег настроения +2, тег жанра +2, темп +1, длина +1."""
    score = 0
    names = {n.lower() for n in tag_names}

    for wanted in (MOOD_TAGS.get(answers.get("mood")), GENRE_TAGS.get(answers.get("genre"))):
        if wanted and wanted.lower() in names:
            score += 2

    if answers.get("pace") and pace == answers["pace"]:
        score += 1

    length = LENGTH_RANGES.get(answers.get("length"))
    if length and page_count is not None:
        low, high = length
        if page_count >= low and (high is None or page_count < high):
            score += 1

    return score


def pick_books(answers, books_info, top_n=TOP_N):
    """books_info: список (book_id, title, tag_names, pace, page_count).
    Возвращает id лучших книг: сначала с большим числом баллов, при равенстве по алфавиту."""
    scored = []
    for book_id, title, tag_names, pace, page_count in books_info:
        score = book_score(answers, tag_names, pace, page_count)
        if score > 0:
            scored.append((-score, title, book_id))
    scored.sort()
    return [book_id for _, _, book_id in scored[:top_n]]
