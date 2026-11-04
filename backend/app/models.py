import uuid
from datetime import datetime
from mongoengine import (
    Document, StringField, BooleanField, IntField,
    DateTimeField, DictField, ListField,
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

    meta = {
        'collection': 'book_tags',
        'indexes': ['book_id', 'tag_id', {'fields': ['book_id', 'tag_id'], 'unique': True}],
    }


class Book(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    title = StringField(required=True, max_length=255)
    author = StringField(required=True, max_length=255)
    cover_url = StringField(max_length=500)
    description = StringField()
    page_count = IntField()
    pace = StringField(max_length=20)
    emotions = DictField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'books', 'indexes': ['pace', 'title']}

    @property
    def tags(self):
        book_tags = BookTag.objects(book_id=str(self.id))
        tag_ids = [bt.tag_id for bt in book_tags]
        return Tag.objects(id__in=tag_ids)


class QuizSession(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True)
    answers = DictField(required=True)
    result_book_ids = ListField(StringField(), default=[])
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'quiz_sessions', 'indexes': [('user_id', '-created_at')]}

    @property
    def result_books(self):
        books = {str(b.id): b for b in Book.objects(id__in=self.result_book_ids)}
        return [books[i] for i in self.result_book_ids if i in books]


class ReadBook(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True)
    book_id = StringField(required=True)
    comment = StringField()
    added_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'read_books',
        'indexes': [{'fields': ['user_id', 'book_id'], 'unique': True}],
    }


class WishList(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True)
    book_id = StringField(required=True)
    added_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'wish_list',
        'indexes': [{'fields': ['user_id', 'book_id'], 'unique': True}],
    }


class Comment(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True)
    book_id = StringField(required=True)
    text = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'comments', 'indexes': [('user_id', 'book_id')]}
