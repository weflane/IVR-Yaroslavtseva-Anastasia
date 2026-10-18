import uuid
from datetime import datetime
from mongoengine import (
    Document, StringField, BooleanField, IntField,
    DateTimeField, DictField, ListField, ReferenceField,
    EmbeddedDocument, EmbeddedDocumentField
)


class User(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    email = StringField(unique=True, required=True, max_length=255)
    password_hash = StringField(required=True, max_length=255)
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'users', 'indexes': ['email']}


class Tag(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = StringField(unique=True, required=True, max_length=100)
    category = StringField(required=True, max_length=50)

    meta = {'collection': 'tags'}


class BookTag(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = StringField(required=True)
    tag_id = StringField(required=True)

    meta = {'collection': 'book_tags'}


class Book(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    title = StringField(required=True, max_length=255)
    author = StringField(required=True, max_length=255)
    cover_url = StringField(max_length=500)
    description = StringField()
    page_count = IntField()
    pace = StringField(max_length=20)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'books'}

    @property
    def tags(self):
        """Get all tags for this book"""
        book_tags = BookTag.objects(book_id=str(self.id))
        tag_ids = [bt.tag_id for bt in book_tags]
        return Tag.objects(id__in=tag_ids)


class QuizSession(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True)
    answers = DictField(required=True)
    result_book_ids = ListField(StringField(), default=[])
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'quiz_sessions'}

    @property
    def result_books(self):
        """Книги, подобранные по результатам квиза"""
        books = {str(b.id): b for b in Book.objects(id__in=self.result_book_ids)}
        return [books[i] for i in self.result_book_ids if i in books]


class ReadBook(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True)
    book_id = StringField(required=True)
    comment = StringField()
    added_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'read_books'}


class WishList(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True)
    book_id = StringField(required=True)
    added_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'wish_list'}


class Comment(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True)
    book_id = StringField(required=True)
    text = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'comments'}
