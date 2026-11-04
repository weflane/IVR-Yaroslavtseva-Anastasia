import random

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
MIN_N = 3 


def book_score(answers, tag_names, pace, page_count):
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


def pick_books(answers, books_info, top_n=TOP_N, exclude_ids=(), min_n=MIN_N, rng=None):
    excluded = set(exclude_ids)
    scored = []
    for book_id, title, tag_names, pace, page_count in books_info:
        if book_id in excluded:
            continue
        score = book_score(answers, tag_names, pace, page_count)
        tie = rng.random() if rng is not None else title
        scored.append((-score, tie, book_id))
    scored.sort()

    matched = [item for item in scored if item[0] < 0][:top_n]
    if len(matched) < min_n:
        rest = [item for item in scored if item[0] >= 0]
        matched += rest[: min_n - len(matched)]
    return [book_id for _, _, book_id in matched]


def new_rng():
    return random.Random()


PACE_ORDER = ["slow", "medium", "fast"]


def _in_length(page_count, bounds):
    low, high = bounds
    return page_count is not None and page_count >= low and (high is None or page_count < high)


def available_options(answers, books_info, exclude_ids=()):
    excluded = set(exclude_ids)
    mood_tag = MOOD_TAGS.get(answers.get("mood"))
    genre_tag = GENRE_TAGS.get(answers.get("genre"))
    pool = []
    for book_id, _title, tag_names, pace, page_count in books_info:
        if book_id in excluded:
            continue
        names = {n.lower() for n in tag_names}
        if mood_tag and mood_tag.lower() not in names:
            continue
        if genre_tag and genre_tag.lower() not in names:
            continue
        if answers.get("pace") and pace != answers["pace"]:
            continue
        pool.append((names, pace, page_count))

    def tags_present(mapping):
        return [value for value, tag in mapping.items() if any(tag.lower() in names for names, _, _ in pool)]

    paces = {pace for _, pace, _ in pool}
    return {
        "mood": tags_present(MOOD_TAGS),
        "genre": tags_present(GENRE_TAGS),
        "pace": [p for p in PACE_ORDER if p in paces],
        "length": [v for v, bounds in LENGTH_RANGES.items() if any(_in_length(pc, bounds) for _, _, pc in pool)],
        "count": len(pool),
    }
