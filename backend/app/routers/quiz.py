from fastapi import APIRouter, Depends, HTTPException
from app import models, schemas, quiz_logic
from app.auth_utils import get_current_user

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("", response_model=schemas.QuizSessionOut, status_code=201)
def submit_quiz(
    body: schemas.QuizSubmit,
    current_user: models.User = Depends(get_current_user)
):
    """Принять ответы квиза, подобрать книги и сохранить результат"""
    tag_name_by_id = {str(t.id): t.name for t in models.Tag.objects()}

    tag_names_by_book = {}
    for bt in models.BookTag.objects():
        name = tag_name_by_id.get(bt.tag_id)
        if name:
            tag_names_by_book.setdefault(bt.book_id, []).append(name)

    books_info = [
        (str(b.id), b.title, tag_names_by_book.get(str(b.id), []), b.pace, b.page_count)
        for b in models.Book.objects()
    ]
    result_ids = quiz_logic.pick_books(body.answers, books_info)

    session = models.QuizSession(
        user_id=str(current_user.id),
        answers=body.answers,
        result_book_ids=result_ids,
    )
    session.save()
    return session


@router.get("/history", response_model=list[schemas.QuizSessionOut])
def quiz_history(current_user: models.User = Depends(get_current_user)):
    """История квизов текущего пользователя, новые сверху"""
    sessions = models.QuizSession.objects(user_id=str(current_user.id)).order_by("-created_at")
    return list(sessions)


@router.get("/results/{session_id}", response_model=list[schemas.BookOut])
def get_quiz_results(session_id: str, current_user: models.User = Depends(get_current_user)):
    """Книги из конкретной сессии квиза"""
    session = models.QuizSession.objects(id=session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    if session.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")

    return session.result_books
