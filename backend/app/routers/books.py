from fastapi import APIRouter, Depends, HTTPException, Query, Response
from mongoengine.queryset.visitor import Q

from app import models, schemas
from app.auth_utils import require_admin
from app.card import render_book_card
from app.emotions import PACE_LABEL
from app.services import fetch_cover, load_books_ordered, serialize_books

router = APIRouter(prefix="/books", tags=["books"])

MAX_LIMIT = 1000


@router.get("", response_model=list[schemas.BookOut])
def list_books(
    tag_ids: list[str] = Query(default=[]),
    pace: str | None = None,
    q: str | None = Query(default=None, description="поиск по названию или автору"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=60, ge=1, le=MAX_LIMIT),
):
    query = models.Book.objects()

    if pace:
        query = query.filter(pace=pace)

    if q and q.strip():
        text = q.strip()
        query = query.filter(Q(title__icontains=text) | Q(author__icontains=text))

    if tag_ids:
        book_ids = None
        for tag_id in tag_ids:
            ids = {bt.book_id for bt in models.BookTag.objects(tag_id=tag_id)}
            book_ids = ids if book_ids is None else book_ids & ids
            if not book_ids:
                return []
        query = query.filter(id__in=list(book_ids))

    books = query.order_by("title").skip(skip).limit(limit)
    return serialize_books(books)


@router.get("/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: str):
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return serialize_books([book])[0]


@router.get("/{book_id}/similar", response_model=list[schemas.BookOut])
def similar_books(book_id: str):
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    tag_ids = [bt.tag_id for bt in models.BookTag.objects(book_id=str(book.id))]
    if not tag_ids:
        return []

    shared = {}
    for bt in models.BookTag.objects(tag_id__in=tag_ids, book_id__ne=str(book.id)):
        shared[bt.book_id] = shared.get(bt.book_id, 0) + 1
    if not shared:
        return []

    top_ids = [i for i, _ in sorted(shared.items(), key=lambda x: (-x[1], x[0]))[:30]]
    candidates = load_books_ordered(top_ids)
    ranked = sorted(
        candidates,
        key=lambda b: (-(shared[str(b.id)] + (0.5 if b.pace == book.pace else 0)), b.title),
    )
    return serialize_books(ranked[:5])


@router.get("/{book_id}/card.png")
def book_card_png(book_id: str):
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    data = serialize_books([book])[0]
    png = render_book_card(
        title=data["title"],
        author=data["author"],
        description=data["description"] or "",
        tags=[t["name"] for t in data["tags"]],
        cover_bytes=fetch_cover(data["cover_url"]),
        emotion_map=data["emotion_map"],
        pages=data["page_count"],
        pace_label=PACE_LABEL.get(data["pace"]),
    )
    return Response(
        content=png,
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename="bookmatch-card.png"'},
    )


def _set_book_tags(book, tag_ids):
    ids = list(dict.fromkeys(tag_ids))
    if ids:
        found = {str(t.id) for t in models.Tag.objects(id__in=ids)}
        missing = [i for i in ids if i not in found]
        if missing:
            raise HTTPException(status_code=400, detail="Неизвестные теги: " + ", ".join(missing))
    models.BookTag.objects(book_id=str(book.id)).delete()
    if ids:
        models.BookTag.objects.insert([models.BookTag(book_id=str(book.id), tag_id=i) for i in ids])


@router.post("", response_model=schemas.BookOut, status_code=201)
def create_book(body: schemas.BookCreate, _=Depends(require_admin)):
    book = models.Book(
        title=body.title,
        author=body.author,
        cover_url=body.cover_url,
        description=body.description,
        page_count=body.page_count,
        pace=body.pace,
        emotions=body.emotions,
    )
    book.save()
    _set_book_tags(book, body.tag_ids)
    return serialize_books([book])[0]


@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: str, body: schemas.BookCreate, _=Depends(require_admin)):
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    book.title = body.title
    book.author = body.author
    book.cover_url = body.cover_url
    book.description = body.description
    book.page_count = body.page_count
    book.pace = body.pace
    book.emotions = body.emotions
    book.save()
    _set_book_tags(book, body.tag_ids)
    return serialize_books([book])[0]


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: str, _=Depends(require_admin)):
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    models.BookTag.objects(book_id=str(book.id)).delete()
    book.delete()
    return None
