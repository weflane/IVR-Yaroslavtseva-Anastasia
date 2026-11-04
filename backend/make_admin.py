import sys

from app import models
from app.database import init_db


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    email = args[0]
    make_admin = "--remove" not in sys.argv

    init_db()
    user = models.User.objects(email=email).first()
    if not user:
        print(f"Пользователь {email} не найден. Сначала зарегистрируйся на сайте.")
        sys.exit(1)
    user.is_admin = make_admin
    user.save()
    print(f"Готово: {email} {'теперь администратор' if make_admin else 'больше не администратор'}")


if __name__ == "__main__":
    main()
