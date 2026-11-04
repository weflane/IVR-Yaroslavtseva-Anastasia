from fastapi import APIRouter, Depends, HTTPException

from app import models, schemas
from app.auth_utils import get_current_user
from app.services import load_books_ordered, read_book_ids, serialize_books

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

TOP_N = 5


@router.get("", response_model=list[schemas.BookOut])
def get_recommendations(current_user: models.User = Depends(get_current_user)):
    read_ids = read_book_ids(str(current_user.id))
    if not read_ids:
        raise HTTPException(status_code=400, detail="Пройдите тест или добавьте прочитанные книги")
    weights = {}
    for bt in models.BookTag.objects(book_id__in=read_ids):
        weights[bt.tag_id] = weights.get(bt.tag_id, 0) + 1
    if not weights:
        raise HTTPException(status_code=400, detail="У прочитанных книг нет тегов, подобрать нечего")

    scores = {}
    for bt in models.BookTag.objects(tag_id__in=list(weights), book_id__nin=read_ids):
        scores[bt.book_id] = scores.get(bt.book_id, 0) + weights[bt.tag_id]
    if not scores:
        raise HTTPException(status_code=400, detail="Похожих книг не найдено")

    top_ids = [i for i, _ in sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:TOP_N]]
    return serialize_books(load_books_ordered(top_ids))
