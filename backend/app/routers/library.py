from fastapi import APIRouter, Depends, HTTPException
from mongoengine import NotUniqueError

from app import models, schemas
from app.auth_utils import get_current_user
from app.services import load_books_ordered, serialize_books

router = APIRouter(prefix="/library", tags=["library"])


def _ensure_book(book_id: str):
    if not models.Book.objects(id=book_id).first():
        raise HTTPException(status_code=404, detail="Книга не найдена")


@router.get("", response_model=schemas.LibraryOut)
def get_library(current_user: models.User = Depends(get_current_user)):
    uid = str(current_user.id)
    read_ids = [r.book_id for r in models.ReadBook.objects(user_id=uid).order_by("-added_at")]
    wish_ids = [w.book_id for w in models.WishList.objects(user_id=uid).order_by("-added_at")]
    return {
        "read": serialize_books(load_books_ordered(read_ids)),
        "wishlist": serialize_books(load_books_ordered(wish_ids)),
    }


@router.get("/ids", response_model=schemas.LibraryIds)
def get_library_ids(current_user: models.User = Depends(get_current_user)):
    uid = str(current_user.id)
    return {
        "read_ids": [r.book_id for r in models.ReadBook.objects(user_id=uid)],
        "wishlist_ids": [w.book_id for w in models.WishList.objects(user_id=uid)],
    }


@router.get("/read", response_model=list[schemas.ReadBookOut])
def get_read_books(current_user: models.User = Depends(get_current_user)):
    return list(models.ReadBook.objects(user_id=str(current_user.id)))


@router.get("/wishlist", response_model=list[schemas.WishListOut])
def get_wishlist(current_user: models.User = Depends(get_current_user)):
    return list(models.WishList.objects(user_id=str(current_user.id)))


@router.post("/read", response_model=schemas.ReadBookOut, status_code=201)
def add_to_read(body: schemas.AddToRead, current_user: models.User = Depends(get_current_user)):
    uid = str(current_user.id)
    _ensure_book(body.book_id)
    if models.ReadBook.objects(user_id=uid, book_id=body.book_id).first():
        raise HTTPException(status_code=400, detail="Книга уже в списке прочитанных")
    try:
        read_book = models.ReadBook(user_id=uid, book_id=body.book_id, comment=body.comment or None)
        read_book.save()
    except NotUniqueError:
        raise HTTPException(status_code=400, detail="Книга уже в списке прочитанных")
    models.WishList.objects(user_id=uid, book_id=body.book_id).delete()
    return read_book


@router.post("/wishlist", response_model=schemas.WishListOut, status_code=201)
def add_to_wishlist(body: schemas.AddToWishList, current_user: models.User = Depends(get_current_user)):
    uid = str(current_user.id)
    _ensure_book(body.book_id)
    if models.ReadBook.objects(user_id=uid, book_id=body.book_id).first():
        raise HTTPException(status_code=400, detail="Эта книга уже прочитана")
    if models.WishList.objects(user_id=uid, book_id=body.book_id).first():
        raise HTTPException(status_code=400, detail="Книга уже в списке желаемых")
    try:
        wish = models.WishList(user_id=uid, book_id=body.book_id)
        wish.save()
    except NotUniqueError:
        raise HTTPException(status_code=400, detail="Книга уже в списке желаемых")
    return wish


@router.delete("/read/book/{book_id}", status_code=204)
def remove_read_by_book(book_id: str, current_user: models.User = Depends(get_current_user)):
    models.ReadBook.objects(user_id=str(current_user.id), book_id=book_id).delete()
    return None


@router.delete("/wishlist/book/{book_id}", status_code=204)
def remove_wish_by_book(book_id: str, current_user: models.User = Depends(get_current_user)):
    models.WishList.objects(user_id=str(current_user.id), book_id=book_id).delete()
    return None


@router.delete("/read/{read_id}", status_code=204)
def remove_from_read(read_id: str, current_user: models.User = Depends(get_current_user)):
    read_book = models.ReadBook.objects(id=read_id, user_id=str(current_user.id)).first()
    if not read_book:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    read_book.delete()
    return None


@router.delete("/wishlist/{wish_id}", status_code=204)
def remove_from_wishlist(wish_id: str, current_user: models.User = Depends(get_current_user)):
    wish = models.WishList.objects(id=wish_id, user_id=str(current_user.id)).first()
    if not wish:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    wish.delete()
    return None
