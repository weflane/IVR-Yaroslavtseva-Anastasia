from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    is_admin: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class TagOut(BaseModel):
    id: str
    name: str
    category: str
    model_config = {"from_attributes": True}


class BookOut(BaseModel):
    id: str
    title: str
    author: str
    cover_url: Optional[str] = None
    description: Optional[str] = None
    page_count: Optional[int] = None
    pace: Optional[str] = None
    tags: list[TagOut] = []
    model_config = {"from_attributes": True}
    @field_validator("tags", mode="before")
    @classmethod
    def _tags_to_list(cls, v):
        return list(v) if v is not None else []


class BookCreate(BaseModel):
    title: str
    author: str
    cover_url: Optional[str] = None
    description: Optional[str] = None
    page_count: Optional[int] = None
    pace: Optional[str] = None
    tag_ids: list[str] = []


class QuizAnswers(BaseModel):
    answers: dict


class QuizSubmit(BaseModel):
    answers: dict


class QuizSessionOut(BaseModel):
    id: str
    answers: Any
    result_books: list[BookOut] = []
    created_at: datetime
    model_config = {"from_attributes": True}

    @field_validator("result_books", mode="before")
    @classmethod
    def _books_to_list(cls, v):
        return list(v) if v is not None else []


class AddToLibrary(BaseModel):
    book_id: str
    comment: Optional[str] = None


class AddToRead(AddToLibrary):
    pass


class AddToWishlist(BaseModel):
    book_id: str


class AddToWishList(AddToWishlist):
    pass


class ReadBookOut(BaseModel):
    id: str
    user_id: str
    book_id: str
    comment: Optional[str] = None
    added_at: datetime
    model_config = {"from_attributes": True}


class WishListOut(BaseModel):
    id: str
    user_id: str
    book_id: str
    added_at: datetime
    model_config = {"from_attributes": True}


class LibraryOut(BaseModel):
    read: list[BookOut] = []
    wishlist: list[BookOut] = []


class CommentCreate(BaseModel):
    book_id: str
    text: str = Field(..., min_length=1, max_length=500)


class CommentUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class CommentOut(BaseModel):
    id: str
    user_id: str
    book_id: str
    text: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
