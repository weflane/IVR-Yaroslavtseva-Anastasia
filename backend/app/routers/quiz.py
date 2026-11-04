from fastapi import APIRouter, Depends, HTTPException, Response

from app import models, quiz_logic, schemas
from app.auth_utils import get_current_user
from app.card import render_selection_card
from app.services import fetch_covers, read_book_ids, serialize_books

router = APIRouter(prefix="/quiz", tags=["quiz"])


def _sessions_out(sessions):
    sessions = list(sessions)
    all_ids = {i for s in sessions for i in s.result_book_ids}
    books = {}
    if all_ids:
        books = {b["id"]: b for b in serialize_books(models.Book.objects(id__in=list(all_ids)))}
    return [
        {
            "id": str(s.id),
            "answers": s.answers,
            "result_books": [books[i] for i in s.result_book_ids if i in books],
            "created_at": s.created_at,
        }
        for s in sessions
    ]


def _books_info():
    tag_name_by_id = {str(t.id): t.name for t in models.Tag.objects()}

    tag_names_by_book = {}
    for bt in models.BookTag.objects():
        name = tag_name_by_id.get(bt.tag_id)
        if name:
            tag_names_by_book.setdefault(bt.book_id, []).append(name)

    return [
        (str(b.id), b.title, tag_names_by_book.get(str(b.id), []), b.pace, b.page_count)
        for b in models.Book.objects.only("title", "pace", "page_count")
    ]


@router.post("", response_model=schemas.QuizSessionOut, status_code=201)
def submit_quiz(body: schemas.QuizSubmit, current_user: models.User = Depends(get_current_user)):
    user_id = str(current_user.id)
    books_info = _books_info()
    result_ids = quiz_logic.pick_books(
        body.answers,
        books_info,
        exclude_ids=read_book_ids(user_id),
        rng=quiz_logic.new_rng(),
    )

    session = models.QuizSession(user_id=user_id, answers=body.answers, result_book_ids=result_ids)
    session.save()
    return _sessions_out([session])[0]


@router.get("/history", response_model=list[schemas.QuizSessionOut])
def quiz_history(current_user: models.User = Depends(get_current_user)):
    sessions = models.QuizSession.objects(user_id=str(current_user.id)).order_by("-created_at")
    return _sessions_out(sessions)


@router.get("/results/{session_id}", response_model=list[schemas.BookOut])
def get_quiz_results(session_id: str, current_user: models.User = Depends(get_current_user)):
    session = models.QuizSession.objects(id=session_id, user_id=str(current_user.id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return _sessions_out([session])[0]["result_books"]


@router.get("/options")
def quiz_options(
    mood: str | None = None,
    genre: str | None = None,
    pace: str | None = None,
    current_user: models.User = Depends(get_current_user),
):
    answers = {key: value for key, value in (("mood", mood), ("genre", genre), ("pace", pace)) if value}
    return quiz_logic.available_options(answers, _books_info(), exclude_ids=read_book_ids(str(current_user.id)))


@router.get("/results/{session_id}/card.png")
def quiz_card_png(session_id: str, current_user: models.User = Depends(get_current_user)):
    session = models.QuizSession.objects(id=session_id, user_id=str(current_user.id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    books = _sessions_out([session])[0]["result_books"]
    if not books:
        raise HTTPException(status_code=404, detail="В подборке нет книг")

    covers = fetch_covers([b.get("cover_url") for b in books])
    items = [
        {"title": b["title"], "author": b["author"], "cover_bytes": cover}
        for b, cover in zip(books, covers)
    ]
    png = render_selection_card(items, "Моя подборка", f"{session.created_at:%d.%m.%Y}")
    return Response(
        content=png,
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename="bookmatch-podborka.png"'},
    )
