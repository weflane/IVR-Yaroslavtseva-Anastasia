from app import models
from app.database import init_db


def main():
    init_db()
    users = list(models.User.objects(email__startswith="loadtest-", email__endswith="@example.com"))
    ids = [str(u.id) for u in users]
    if ids:
        models.QuizSession.objects(user_id__in=ids).delete()
        models.ReadBook.objects(user_id__in=ids).delete()
        models.WishList.objects(user_id__in=ids).delete()
        models.Comment.objects(user_id__in=ids).delete()
        models.User.objects(id__in=ids).delete()
    print(f"Удалено тестовых пользователей: {len(ids)}")


if __name__ == "__main__":
    main()
