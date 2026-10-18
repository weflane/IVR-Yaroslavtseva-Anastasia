from fastapi import APIRouter, Depends, HTTPException
from app import models, schemas
from app.auth_utils import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[schemas.BookOut])
def get_recommendations(current_user: models.User = Depends(get_current_user)):
    """Get personalized book recommendations based on user's reading history"""
    read_books = models.ReadBook.objects(user_id=str(current_user.id))
    read_book_ids = [rb.book_id for rb in read_books]

    if not read_book_ids:
        raise HTTPException(
            status_code=400,
            detail="Пройди тест или добавь прочитанные книги"
        )
    books = models.Book.objects(id__in=read_book_ids)
    tag_frequencies = {}
    for book in books:
        book_tags = models.BookTag.objects(book_id=str(book.id))
        for bt in book_tags:
            tag_frequencies[bt.tag_id] = tag_frequencies.get(bt.tag_id, 0) + 1

    if not tag_frequencies:
        raise HTTPException(
            status_code=400,
            detail="Похожих книг не найдено"
        )
    all_books = models.Book.objects()
    scored_books = []

    for book in all_books:
        if str(book.id) in read_book_ids:
            continue
        book_tags = models.BookTag.objects(book_id=str(book.id))
        score = sum(
            tag_frequencies.get(bt.tag_id, 0)
            for bt in book_tags
        )

        if score > 0:
            scored_books.append((book, score))

    if not scored_books:
        raise HTTPException(
            status_code=400,
            detail="Похожих книг не найдено"
        )

    sorted_books = sorted(scored_books, key=lambda x: x[1], reverse=True)[:5]
    return [book for book, _ in sorted_books]
