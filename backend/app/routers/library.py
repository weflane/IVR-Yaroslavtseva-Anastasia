from fastapi import APIRouter, Depends, HTTPException
from app import models, schemas
from app.auth_utils import get_current_user

router = APIRouter(prefix="/library", tags=["library"])


def _load_books(book_ids):
    """Книги по списку id, в том же порядке"""
    books = {str(b.id): b for b in models.Book.objects(id__in=book_ids)}
    return [books[i] for i in book_ids if i in books]


@router.get("", response_model=schemas.LibraryOut)
def get_library(current_user: models.User = Depends(get_current_user)):
    """Вся библиотека пользователя: прочитанное и вишлист"""
    user_id = str(current_user.id)
    read_ids = [r.book_id for r in models.ReadBook.objects(user_id=user_id)]
    wish_ids = [w.book_id for w in models.WishList.objects(user_id=user_id)]
    return {"read": _load_books(read_ids), "wishlist": _load_books(wish_ids)}


@router.get("/read", response_model=list[schemas.ReadBookOut])
def get_read_books(current_user: models.User = Depends(get_current_user)):
    """Get all books marked as read by current user"""
    read_books = models.ReadBook.objects(user_id=str(current_user.id))
    return list(read_books)


@router.get("/wishlist", response_model=list[schemas.WishListOut])
def get_wishlist(current_user: models.User = Depends(get_current_user)):
    """Get user's wishlist"""
    wishlist = models.WishList.objects(user_id=str(current_user.id))
    return list(wishlist)


@router.post("/read", response_model=schemas.ReadBookOut, status_code=201)
def add_to_read(
    body: schemas.AddToRead,
    current_user: models.User = Depends(get_current_user)
):
    """Mark book as read"""
    existing = models.ReadBook.objects(
        user_id=str(current_user.id),
        book_id=body.book_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Книга уже в списке прочитанных")

    read_book = models.ReadBook(
        user_id=str(current_user.id),
        book_id=body.book_id,
        comment=body.comment
    )
    read_book.save()
    return read_book


@router.post("/wishlist", response_model=schemas.WishListOut, status_code=201)
def add_to_wishlist(
    body: schemas.AddToWishList,
    current_user: models.User = Depends(get_current_user)
):
    """Add book to wishlist"""
    # Check if already added
    existing = models.WishList.objects(
        user_id=str(current_user.id),
        book_id=body.book_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Книга уже в списке желаемых")

    wish = models.WishList(
        user_id=str(current_user.id),
        book_id=body.book_id
    )
    wish.save()
    return wish


@router.delete("/read/{read_id}", status_code=204)
def remove_from_read(
    read_id: str,
    current_user: models.User = Depends(get_current_user)
):
    """Remove book from read list"""
    read_book = models.ReadBook.objects(id=read_id).first()
    if not read_book:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if read_book.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")

    read_book.delete()
    return None


@router.delete("/wishlist/{wish_id}", status_code=204)
def remove_from_wishlist(
    wish_id: str,
    current_user: models.User = Depends(get_current_user)
):
    """Remove book from wishlist"""
    wish = models.WishList.objects(id=wish_id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if wish.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")

    wish.delete()
    return None
