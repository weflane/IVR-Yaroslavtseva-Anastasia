import urllib.request
from concurrent.futures import ThreadPoolExecutor

from app import models
from app.emotions import build_emotion_map


def serialize_books(books):
    books = list(books)
    if not books:
        return []

    tags_by_id = {str(t.id): t for t in models.Tag.objects()}
    ids = [str(b.id) for b in books]
    tags_by_book = {}
    for bt in models.BookTag.objects(book_id__in=ids):
        tag = tags_by_id.get(bt.tag_id)
        if tag:
            tags_by_book.setdefault(bt.book_id, []).append(tag)

    result = []
    for b in books:
        tags = sorted(tags_by_book.get(str(b.id), []), key=lambda t: (t.category, t.name))
        result.append({
            "id": str(b.id),
            "title": b.title,
            "author": b.author,
            "cover_url": b.cover_url,
            "description": b.description,
            "page_count": b.page_count,
            "pace": b.pace,
            "tags": [{"id": str(t.id), "name": t.name, "category": t.category} for t in tags],
            "emotion_map": build_emotion_map(
                [t.name for t in tags], b.pace, b.page_count, dict(b.emotions or {})
            ),
        })
    return result


def load_books_ordered(book_ids):
    books = {str(b.id): b for b in models.Book.objects(id__in=book_ids)}
    return [books[i] for i in book_ids if i in books]


def read_book_ids(user_id):
    return [r.book_id for r in models.ReadBook.objects(user_id=user_id)]


def fetch_cover(url, limit=3_000_000):
    if not url or not url.lower().startswith(("http://", "https://")):
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BookMatch/1.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = resp.read(limit + 1)
        return data if len(data) <= limit else None
    except Exception:
        return None


def fetch_covers(urls):
    urls = list(urls)
    if not urls:
        return []
    with ThreadPoolExecutor(max_workers=min(5, len(urls))) as pool:
        return list(pool.map(fetch_cover, urls))
