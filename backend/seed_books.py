from app.database import init_db
from app.models import Book, Tag, BookTag
TAGS = {
    "Настроение": ["Грустное", "Радостное", "Задумчивое", "Напряжённое"],
    "Жанр": ["Детектив", "Фантастика", "Роман", "Классика"],
}

BOOKS = [
    {
        "title": "Гарри Поттер и философский камень",
        "author": "Дж. К. Роулинг",
        "description": "Мальчик узнает, что он волшебник, и отправляется в школу магии Хогвартс.",
        "cover_url": "https://covers.openlibrary.org/b/id/10521270-L.jpg",
        "page_count": 320, "pace": "medium",
        "tags": ["Радостное", "Фантастика"],
    },
    {
        "title": "Шерлок Холмс: Этюд в багровых тонах",
        "author": "Артур Конан Дойл",
        "description": "Знакомство доктора Ватсона с гениальным сыщиком Шерлоком Холмсом.",
        "cover_url": "https://covers.openlibrary.org/b/id/11208716-L.jpg",
        "page_count": 200, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
    },
    {
        "title": "Три товарища",
        "author": "Эрих Мария Ремарк",
        "description": "История о настоящей дружбе и любви на фоне послевоенной разрухи.",
        "cover_url": "https://covers.openlibrary.org/b/id/12858339-L.jpg",
        "page_count": 480, "pace": "slow",
        "tags": ["Грустное", "Задумчивое", "Роман", "Классика"],
    },
    {
        "title": "Хоббит, или Туда и обратно",
        "author": "Дж. Р. Р. Толкин",
        "description": "Путешествие Бильбо Бэггинса в компании гномов и волшебника Гэндальфа.",
        "cover_url": "https://covers.openlibrary.org/b/id/6979861-L.jpg",
        "page_count": 330, "pace": "medium",
        "tags": ["Радостное", "Фантастика"],
    },
    {
        "title": "Метро 2033",
        "author": "Дмитрий Глуховский",
        "description": "Постапокалиптический роман о выживании людей в московском метро.",
        "cover_url": "https://covers.openlibrary.org/b/id/12871707-L.jpg",
        "page_count": 560, "pace": "fast",
        "tags": ["Напряжённое", "Фантастика"],
    },
    {
        "title": "Гордость и предубеждение",
        "author": "Джейн Остин",
        "description": "Классический роман о любви, социальном статусе и предрассудках.",
        "cover_url": "https://covers.openlibrary.org/b/id/12646651-L.jpg",
        "page_count": 430, "pace": "slow",
        "tags": ["Радостное", "Роман", "Классика"],
    },
    {
        "title": "Дюна",
        "author": "Фрэнк Герберт",
        "description": "Эпическая сага о пустынной планете Арракис и борьбе за специю.",
        "cover_url": "https://covers.openlibrary.org/b/id/11481354-L.jpg",
        "page_count": 700, "pace": "slow",
        "tags": ["Задумчивое", "Фантастика"],
    },
    {
        "title": "Убийство в «Восточном экспрессе»",
        "author": "Агата Кристи",
        "description": "Эркюль Пуаро расследует убийство в застрявшем в снегах поезде.",
        "cover_url": "https://covers.openlibrary.org/b/id/12602882-L.jpg",
        "page_count": 256, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
    },
    {
        "title": "Цветы для Элджернона",
        "author": "Дэниел Киз",
        "description": "История умственно отсталого человека, который становится гением.",
        "cover_url": "https://covers.openlibrary.org/b/id/12519212-L.jpg",
        "page_count": 320, "pace": "medium",
        "tags": ["Грустное", "Задумчивое", "Фантастика"],
    },
    {
        "title": "Властелин колец: Братство Кольца",
        "author": "Дж. Р. Р. Толкин",
        "description": "Начало великого похода за уничтожением Кольца Всевластья.",
        "cover_url": "https://covers.openlibrary.org/b/id/12709662-L.jpg",
        "page_count": 480, "pace": "slow",
        "tags": ["Напряжённое", "Фантастика"],
    },
]
def get_or_create_tags():
    result = {}
    for category, names in TAGS.items():
        for name in names:
            tag = Tag.objects(name=name).first()
            if not tag:
                tag = Tag(name=name, category=category).save()
            result[name] = tag
    return result


def seed_books():
    print("Подключение к базе данных...")
    init_db()

    print("Создание тегов...")
    tags = get_or_create_tags()

    print("Очистка старых книг...")
    Book.objects.delete()
    BookTag.objects.delete()
    print("Добавление книг...")
    for data in BOOKS:
        tag_names = data["tags"]
        fields = {k: v for k, v in data.items() if k != "tags"}
        book = Book(**fields).save()
        for name in tag_names:
            BookTag(book_id=str(book.id), tag_id=str(tags[name].id)).save()
        print(f" [OK] {book.title}")

    print("База данных успешно наполнена")


if __name__ == "__main__":
    seed_books()