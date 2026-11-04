from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app import models, schemas
from app.auth_utils import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


def _own_comment(comment_id: str, user: models.User) -> models.Comment:
    comment = models.Comment.objects(id=comment_id, user_id=str(user.id)).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return comment


@router.get("/me", response_model=list[schemas.CommentOut])
def my_comments(current_user: models.User = Depends(get_current_user)):
    return list(models.Comment.objects(user_id=str(current_user.id)).order_by("-created_at"))


@router.get("/book/{book_id}", response_model=list[schemas.CommentOut])
def get_book_comments(book_id: str, current_user: models.User = Depends(get_current_user)):
    comments = models.Comment.objects(
        book_id=book_id, user_id=str(current_user.id)
    ).order_by("-created_at")
    return list(comments)


@router.post("", response_model=schemas.CommentOut, status_code=201)
def create_comment(
    body: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_user),
):
    if not models.Book.objects(id=body.book_id).first():
        raise HTTPException(status_code=404, detail="Книга не найдена")

    comment = models.Comment(
        user_id=str(current_user.id),
        book_id=body.book_id,
        text=body.text.strip(),
    )
    comment.save()
    return comment


@router.put("/{comment_id}", response_model=schemas.CommentOut)
def update_comment(
    comment_id: str,
    body: schemas.CommentUpdate,
    current_user: models.User = Depends(get_current_user),
):
    comment = _own_comment(comment_id, current_user)
    comment.text = body.text.strip()
    comment.updated_at = datetime.utcnow()
    comment.save()
    return comment


@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: str,
    current_user: models.User = Depends(get_current_user),
):
    _own_comment(comment_id, current_user).delete()
    return None
