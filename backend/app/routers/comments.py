from fastapi import APIRouter, Depends, HTTPException
from app import models, schemas
from app.auth_utils import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/book/{book_id}", response_model=list[schemas.CommentOut])
def get_book_comments(book_id: str):
    """Get all comments for a book"""
    comments = models.Comment.objects(book_id=book_id).order_by('-created_at')
    return list(comments)


@router.post("", response_model=schemas.CommentOut, status_code=201)
def create_comment(
    body: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_user)
):
    """Add new comment to a book"""
    book = models.Book.objects(id=body.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    comment = models.Comment(
        user_id=str(current_user.id),
        book_id=body.book_id,
        text=body.text
    )
    comment.save()
    return comment


@router.put("/{comment_id}", response_model=schemas.CommentOut)
def update_comment(
    comment_id: str,
    body: schemas.CommentUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """Edit comment (owner only)"""
    comment = models.Comment.objects(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    if comment.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")

    comment.text = body.text
    comment.updated_at = __import__('datetime').datetime.utcnow()
    comment.save()
    return comment


@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: str,
    current_user: models.User = Depends(get_current_user)
):
    """Delete comment (owner only)"""
    comment = models.Comment.objects(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    if comment.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")

    comment.delete()
    return None
