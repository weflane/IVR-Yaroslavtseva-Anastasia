from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import UUID
from app import models, schemas
from app.auth_utils import require_admin

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[schemas.BookOut])
def list_books(
    tag_ids: list[str] = Query(default=[]),
    pace: str | None = None
):
    """List all books with optional filtering by tags and pace"""
    q = models.Book.objects()

    if pace:
        q = q.filter(pace=pace)

    if tag_ids:
        book_ids = set()
        for tag_id in tag_ids:
            book_tags = models.BookTag.objects(tag_id=tag_id)
            tag_book_ids = {bt.book_id for bt in book_tags}
            if not book_ids:
                book_ids = tag_book_ids
            else:
                book_ids = book_ids.intersection(tag_book_ids)

        q = q.filter(id__in=list(book_ids)) if book_ids else []

    return list(q)


@router.get("/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: str):
    """Get single book by ID"""
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book


@router.get("/{book_id}/similar", response_model=list[schemas.BookOut])
def similar_books(book_id: str):
    """Get books similar to the given book (by tags)"""
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    book_tags = models.BookTag.objects(book_id=str(book.id))
    tag_ids = [bt.tag_id for bt in book_tags]

    if not tag_ids:
        return []
    related_book_ids = set()
    for tag_id in tag_ids:
        related_tags = models.BookTag.objects(tag_id=tag_id)
        for bt in related_tags:
            if bt.book_id != str(book.id):
                related_book_ids.add(bt.book_id)
    similar = models.Book.objects(id__in=list(related_book_ids))[:5]
    return list(similar)


@router.post("", response_model=schemas.BookOut, status_code=201)
def create_book(
    body: schemas.BookCreate,
    _=Depends(require_admin)
):
    """Create new book (admin only)"""
    book = models.Book(
        title=body.title,
        author=body.author,
        cover_url=body.cover_url,
        description=body.description,
        page_count=body.page_count,
        pace=body.pace,
    )
    book.save()
    return book


@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(
    book_id: str,
    body: schemas.BookCreate,
    _=Depends(require_admin)
):
    """Update book (admin only)"""
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    book.title = body.title
    book.author = body.author
    book.cover_url = body.cover_url
    book.description = body.description
    book.page_count = body.page_count
    book.pace = body.pace
    book.save()
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: str, _=Depends(require_admin)):
    """Delete book (admin only)"""
    book = models.Book.objects(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    book.delete()
    return None
