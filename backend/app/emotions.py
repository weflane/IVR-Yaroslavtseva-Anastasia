MOOD_AXES = [
    ("sad", "Грусть", "Грустное"),
    ("uplifting", "Радость", "Радостное"),
    ("philosophical", "Задумчивость", "Задумчивое"),
    ("tense", "Напряжение", "Напряжённое"),
]

PACE_VALUE = {"slow": 30, "medium": 60, "fast": 90}
PACE_LABEL = {"slow": "неспешный", "medium": "средний", "fast": "быстрый"}
MAX_PAGES = 700


def _clamp(value):
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


def build_emotion_map(tag_names, pace=None, page_count=None, emotions=None):
    names = {n.lower() for n in (tag_names or [])}
    emotions = emotions or {}
    result = []

    for key, label, tag in MOOD_AXES:
        if key in emotions:
            value = _clamp(emotions[key])
        else:
            value = 85 if tag.lower() in names else 10
        result.append({"key": key, "label": label, "value": value})

    result.append({"key": "pace", "label": "Темп", "value": PACE_VALUE.get(pace, 50)})
    pages = page_count or 0
    result.append({"key": "volume", "label": "Объём", "value": _clamp(pages / MAX_PAGES * 100)})
    return result
