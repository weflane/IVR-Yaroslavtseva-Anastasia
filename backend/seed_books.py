"""Наполнение базы книгами.

  python seed_books.py                 добавить/обновить базовый набор (ничего не удаляет)
  python seed_books.py --reset         сначала удалить ВСЕ книги и связи книга-тег
  python seed_books.py --demo 1000     дозаполнить базу демо-книгами до 1000 штук (для проверки нагрузки)
  python seed_books.py --clear-demo    удалить демо-книги
  python seed_books.py --json books.json   импортировать свои книги из JSON (формат ниже)

Формат JSON: [{"title": "...", "author": "...", "description": "...", "cover_url": "...",
               "page_count": 320, "pace": "slow|medium|fast",
               "tags": ["Грустное", "Детектив"], "emotions": {"sad": 80, "tense": 20}}]
"""
import argparse
import json
import random

from app.database import init_db
from app.models import Book, BookTag, Tag

TAGS = {
    "Настроение": ["Грустное", "Радостное", "Задумчивое", "Напряжённое"],
    "Жанр": ["Детектив", "Фантастика", "Роман", "Классика"],
}

DEMO_AUTHOR = "Демо-автор"

BOOKS = [
    {
        "title": "Гарри Поттер и философский камень",
        "author": "Дж. К. Роулинг",
        "description": "Мальчик узнает, что он волшебник, и отправляется в школу магии Хогвартс.",
        "cover_url": "https://covers.openlibrary.org/b/id/10521270-L.jpg",
        "page_count": 320, "pace": "medium",
        "tags": ["Радостное", "Фантастика"],
        "emotions": {"sad": 10, "uplifting": 85, "philosophical": 15, "tense": 45},
    },
    {
        "title": "Шерлок Холмс: Этюд в багровых тонах",
        "author": "Артур Конан Дойл",
        "description": "Знакомство доктора Ватсона с гениальным сыщиком Шерлоком Холмсом.",
        "cover_url": "https://covers.openlibrary.org/b/id/11208716-L.jpg",
        "page_count": 200, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 10, "uplifting": 25, "philosophical": 30, "tense": 85},
    },
    {
        "title": "Три товарища",
        "author": "Эрих Мария Ремарк",
        "description": "История о настоящей дружбе и любви на фоне послевоенной разрухи.",
        "cover_url": "https://covers.openlibrary.org/b/id/12858339-L.jpg",
        "page_count": 480, "pace": "slow",
        "tags": ["Грустное", "Задумчивое", "Роман", "Классика"],
        "emotions": {"sad": 90, "uplifting": 25, "philosophical": 70, "tense": 25},
    },
    {
        "title": "Хоббит, или Туда и обратно",
        "author": "Дж. Р. Р. Толкин",
        "description": "Путешествие Бильбо Бэггинса в компании гномов и волшебника Гэндальфа.",
        "cover_url": "https://covers.openlibrary.org/b/id/6979861-L.jpg",
        "page_count": 330, "pace": "medium",
        "tags": ["Радостное", "Фантастика"],
        "emotions": {"sad": 10, "uplifting": 90, "philosophical": 20, "tense": 45},
    },
    {
        "title": "Метро 2033",
        "author": "Дмитрий Глуховский",
        "description": "Постапокалиптический роман о выживании людей в московском метро.",
        "cover_url": "https://covers.openlibrary.org/b/id/12871707-L.jpg",
        "page_count": 560, "pace": "fast",
        "tags": ["Напряжённое", "Фантастика"],
        "emotions": {"sad": 55, "uplifting": 5, "philosophical": 35, "tense": 90},
    },
    {
        "title": "Гордость и предубеждение",
        "author": "Джейн Остин",
        "description": "Классический роман о любви, социальном статусе и предрассудках.",
        "cover_url": "https://covers.openlibrary.org/b/id/12646651-L.jpg",
        "page_count": 430, "pace": "slow",
        "tags": ["Радостное", "Роман", "Классика"],
        "emotions": {"sad": 15, "uplifting": 80, "philosophical": 40, "tense": 20},
    },
    {
        "title": "Дюна",
        "author": "Фрэнк Герберт",
        "description": "Эпическая сага о пустынной планете Арракис и борьбе за специю.",
        "cover_url": "https://covers.openlibrary.org/b/id/11481354-L.jpg",
        "page_count": 700, "pace": "slow",
        "tags": ["Задумчивое", "Фантастика"],
        "emotions": {"sad": 30, "uplifting": 15, "philosophical": 85, "tense": 60},
    },
    {
        "title": "Убийство в «Восточном экспрессе»",
        "author": "Агата Кристи",
        "description": "Эркюль Пуаро расследует убийство в застрявшем в снегах поезде.",
        "cover_url": "https://covers.openlibrary.org/b/id/12602882-L.jpg",
        "page_count": 256, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 15, "uplifting": 10, "philosophical": 35, "tense": 90},
    },
    {
        "title": "Цветы для Элджернона",
        "author": "Дэниел Киз",
        "description": "История умственно отсталого человека, который становится гением.",
        "cover_url": "https://covers.openlibrary.org/b/id/12519212-L.jpg",
        "page_count": 320, "pace": "medium",
        "tags": ["Грустное", "Задумчивое", "Фантастика"],
        "emotions": {"sad": 90, "uplifting": 15, "philosophical": 85, "tense": 30},
    },
    {
        "title": "Властелин колец: Братство Кольца",
        "author": "Дж. Р. Р. Толкин",
        "description": "Начало великого похода за уничтожением Кольца Всевластья.",
        "cover_url": "https://covers.openlibrary.org/b/id/12709662-L.jpg",
        "page_count": 480, "pace": "slow",
        "tags": ["Напряжённое", "Фантастика"],
        "emotions": {"sad": 35, "uplifting": 30, "philosophical": 45, "tense": 85},
    },
    {
        "title": "Гарри Поттер и философский камень",
        "author": "Дж. К. Роулинг",
        "description": "Мальчик узнает, что он волшебник, и отправляется в школу магии Хогвартс.",
        "page_count": 320, "pace": "medium",
        "tags": ["Радостное", "Фантастика"],
        "emotions": {"sad": 10, "uplifting": 85, "philosophical": 15, "tense": 45},
    },
    {
        "title": "Шерлок Холмс: Этюд в багровых тонах",
        "author": "Артур Конан Дойл",
        "description": "Знакомство доктора Ватсона с гениальным сыщиком Шерлоком Холмсом.",
        "page_count": 200, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 10, "uplifting": 25, "philosophical": 30, "tense": 85},
    },
    {
        "title": "Три товарища",
        "author": "Эрих Мария Ремарк",
        "description": "История о настоящей дружбе и любви на фоне послевоенной разрухи.",
        "page_count": 480, "pace": "slow",
        "tags": ["Грустное", "Задумчивое", "Роман", "Классика"],
        "emotions": {"sad": 90, "uplifting": 25, "philosophical": 70, "tense": 25},
    },
    {
        "title": "Хоббит, или Туда и обратно",
        "author": "Дж. Р. Р. Толкин",
        "description": "Путешествие Бильбо Бэггинса в компании гномов и волшебника Гэндальфа.",
        "page_count": 330, "pace": "medium",
        "tags": ["Радостное", "Фантастика"],
        "emotions": {"sad": 10, "uplifting": 90, "philosophical": 20, "tense": 45},
    },
    {
        "title": "Метро 2033",
        "author": "Дмитрий Глуховский",
        "description": "Постапокалиптический роман о выживании людей в московском метро.",
        "page_count": 560, "pace": "fast",
        "tags": ["Напряжённое", "Фантастика"],
        "emotions": {"sad": 55, "uplifting": 5, "philosophical": 35, "tense": 90},
    },
    {
        "title": "Гордость и предубеждение",
        "author": "Джейн Остин",
        "description": "Классический роман о любви, социальном статусе и предрассудках.",
        "page_count": 430, "pace": "slow",
        "tags": ["Радостное", "Роман", "Классика"],
        "emotions": {"sad": 15, "uplifting": 80, "philosophical": 40, "tense": 20},
    },
    {
        "title": "Дюна",
        "author": "Фрэнк Герберт",
        "description": "Эпическая сага о пустынной планете Арракис и борьбе за специю.",
        "page_count": 700, "pace": "slow",
        "tags": ["Задумчивое", "Фантастика"],
        "emotions": {"sad": 30, "uplifting": 15, "philosophical": 85, "tense": 60},
    },
    {
        "title": "Убийство в «Восточном экспрессе»",
        "author": "Агата Кристи",
        "description": "Эркюль Пуаро расследует убийство в застрявшем в снегах поезде.",
        "page_count": 256, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 15, "uplifting": 10, "philosophical": 35, "tense": 90},
    },
    {
        "title": "Цветы для Элджернона",
        "author": "Дэниел Киз",
        "description": "История умственно отсталого человека, который становится гением.",
        "page_count": 320, "pace": "medium",
        "tags": ["Грустное", "Задумчивое", "Фантастика"],
        "emotions": {"sad": 90, "uplifting": 15, "philosophical": 85, "tense": 30},
    },
    {
        "title": "Властелин колец: Братство Кольца",
        "author": "Дж. Р. Р. Толкин",
        "description": "Начало великого похода за уничтожением Кольца Всевластья.",
        "page_count": 480, "pace": "slow",
        "tags": ["Напряжённое", "Фантастика"],
        "emotions": {"sad": 35, "uplifting": 30, "philosophical": 45, "tense": 85},
    },
    {
        "title": "Мастер и Маргарита", 
        "author": "Михаил Булгаков", 
        "description": "Визит дьявола в Москву 1930-х и история любви Мастера и Маргариты.",
        "page_count": 480, "pace": "slow",
        "tags": ["Задумчивое", "Роман", "Классика"],
        "emotions": {"sad": 40, "uplifting": 20, "philosophical": 90, "tense": 50},
    },
    {
        "title": "Преступление и наказание", 
        "author": "Фёдор Достоевский", 
        "description": "Бедный студент Раскольников совершает убийство и пытается его оправдать.",
        "page_count": 550, "pace": "slow",
        "tags": ["Грустное", "Задумчивое", "Классика"],
        "emotions": {"sad": 85, "uplifting": 5, "philosophical": 95, "tense": 80},
    },
    {
        "title": "1984", 
        "author": "Джордж Оруэлл", 
        "description": "Антиутопия о тоталитарном государстве, где следят за каждым.",
        "page_count": 320, "pace": "medium",
        "tags": ["Напряжённое", "Задумчивое", "Фантастика", "Классика"],
        "emotions": {"sad": 70, "uplifting": 5, "philosophical": 85, "tense": 95},
    },
    {
        "title": "451 градус по Фаренгейту", 
        "author": "Рэй Брэдбери", 
        "description": "Мир, в котором пожарные сжигают книги, и один из них начинает сомневаться.",
        "page_count": 256, "pace": "fast",
        "tags": ["Напряжённое", "Задумчивое", "Фантастика", "Классика"],
        "emotions": {"sad": 60, "uplifting": 10, "philosophical": 80, "tense": 85},
    },
    {
        "title": "Маленький принц", 
        "author": "Антуан де Сент-Экзюпери", 
        "description": "Философская сказка о дружбе, любви и том, что действительно важно.",
        "page_count": 96, "pace": "slow",
        "tags": ["Грустное", "Задумчивое", "Классика"],
        "emotions": {"sad": 60, "uplifting": 40, "philosophical": 95, "tense": 10},
    },
    {
        "title": "Собака Баскервилей", 
        "author": "Артур Конан Дойл", 
        "description": "Холмс и Ватсон расследуют легенду о призрачной собаке на болотах Девоншира.",
        "page_count": 256, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 20, "uplifting": 15, "philosophical": 30, "tense": 85},
    },
    {
        "title": "Десять негритят", 
        "author": "Агата Кристи", 
        "description": "Десять незнакомцев на уединённом острове и кто-то, кто убивает их одного за другим.",
        "page_count": 272, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 25, "uplifting": 5, "philosophical": 40, "tense": 95},
    },
    {
        "title": "Пикник на обочине", 
        "author": "Аркадий и Борис Стругацкие", 
        "description": "Сталкеры идут в Зону, оставшуюся после визита пришельцев, за артефактами.",
        "page_count": 224, "pace": "medium",
        "tags": ["Напряжённое", "Задумчивое", "Фантастика", "Классика"],
        "emotions": {"sad": 50, "uplifting": 10, "philosophical": 85, "tense": 80},
    },
    {
        "title": "Солярис", 
        "author": "Станислав Лем", 
        "description": "Учёные у океана-разума на далёкой планете сталкиваются со своими воспоминаниями.",
        "page_count": 220, "pace": "slow",
        "tags": ["Задумчивое", "Фантастика", "Классика"],
        "emotions": {"sad": 40, "uplifting": 10, "philosophical": 95, "tense": 40},
    },
    {
        "title": "Анна Каренина", 
        "author": "Лев Толстой", 
        "description": "Любовь замужней женщины и судьба её семьи на фоне русского общества XIX века.",
        "page_count": 860, "pace": "slow",
        "tags": ["Грустное", "Роман", "Классика"],
        "emotions": {"sad": 90, "uplifting": 20, "philosophical": 70, "tense": 40},
    },
    {
        "title": "Великий Гэтсби", 
        "author": "Фрэнсис Скотт Фицджеральд", 
        "description": "Таинственный миллионер и его одержимость прошлым в эпоху джаза.",
        "page_count": 220, "pace": "medium",
        "tags": ["Грустное", "Роман", "Классика"],
        "emotions": {"sad": 80, "uplifting": 30, "philosophical": 60, "tense": 30},
    },
    {
        "title": "Над пропастью во ржи", 
        "author": "Джером Сэлинджер", 
        "description": "Несколько дней из жизни подростка Холдена Колфилда, сбежавшего из школы.",
        "page_count": 270, "pace": "medium",
        "tags": ["Грустное", "Задумчивое", "Классика"],
        "emotions": {"sad": 75, "uplifting": 20, "philosophical": 70, "tense": 30},
    },
    {
        "title": "Двенадцать стульев", 
        "author": "Илья Ильф, Евгений Петров", 
        "description": "Погоня за спрятанными в стуле бриллиантами - сатира на советскую жизнь 1920-х.",
        "page_count": 400, "pace": "fast",
        "tags": ["Радостное", "Классика"],
        "emotions": {"sad": 10, "uplifting": 90, "philosophical": 30, "tense": 20},
    },
    {
        "title": "Три мушкетёра", 
        "author": "Александр Дюма", 
        "description": "Д'Артаньян приезжает в Париж и становится другом мушкетёров.",
        "page_count": 720, "pace": "fast",
        "tags": ["Радостное", "Напряжённое", "Классика"],
        "emotions": {"sad": 15, "uplifting": 85, "philosophical": 20, "tense": 70},
    },
    {
        "title": "Девушка с татуировкой дракона", 
        "author": "Стиг Ларссон", 
        "description": "Журналист и хакер расследуют исчезновение девушки сорокалетней давности.",
        "page_count": 560, "pace": "medium",
        "tags": ["Напряжённое", "Детектив"],
        "emotions": {"sad": 40, "uplifting": 5, "philosophical": 30, "tense": 90},
    },
    {
        "title": "Невыносимая лёгкость бытия", 
        "author": "Милан Кундера", 
        "description": "Любовь, измена и выбор между лёгкостью и тяжестью на фоне Пражской весны.",
        "page_count": 320, "pace": "slow",
        "tags": ["Грустное", "Задумчивое", "Роман"],
        "emotions": {"sad": 70, "uplifting": 20, "philosophical": 90, "tense": 30},
    },
        {
        "title": "Понедельник начинается в субботу",
        "author": "Аркадий и Борис Стругацкие",
        "description": "Сказка о научных сотрудниках, магии и буднях института чародейства.",
        "page_count": 280, "pace": "fast",
        "tags": ["Радостное", "Фантастика"],
        "emotions": {"sad": 5, "uplifting": 95, "philosophical": 40, "tense": 20},
    },
    {
        "title": "Идиот",
        "author": "Фёдор Достоевский",
        "description": "История князя Мышкина, идеального человека, столкнувшегося с жестоким миром.",
        "page_count": 640, "pace": "slow",
        "tags": ["Грустное", "Задумчивое", "Роман", "Классика"],
        "emotions": {"sad": 95, "uplifting": 15, "philosophical": 90, "tense": 50},
    },
    {
        "title": "Молчание ягнят",
        "author": "Томас Харрис",
        "description": "Стажёр ФБР Кларис Старлинг обращается за помощью к маньяку Ганнибалу Лектеру.",
        "page_count": 360, "pace": "fast",
        "tags": ["Напряжённое", "Детектив"],
        "emotions": {"sad": 30, "uplifting": 5, "philosophical": 40, "tense": 99},
    },
    {
        "title": "Портрет Дориана Грея",
        "author": "Оскар Уайльд",
        "description": "Красивый юноша остается молодым, в то время как его портрет стареет и уродуется.",
        "page_count": 320, "pace": "medium",
        "tags": ["Задумчивое", "Напряжённое", "Классика"],
        "emotions": {"sad": 60, "uplifting": 20, "philosophical": 85, "tense": 70},
    },
    {
        "title": "Конец детства",
        "author": "Артур Кларк",
        "description": "Пришельцы приносят на Землю утопию, но ценой потери человеческой сущности.",
        "page_count": 240, "pace": "slow",
        "tags": ["Задумчивое", "Фантастика", "Классика"],
        "emotions": {"sad": 50, "uplifting": 30, "philosophical": 95, "tense": 40},
    },
    {
        "title": "Отцы и дети",
        "author": "Иван Тургенев",
        "description": "Конфликт поколений и нигилизм в русской провинции XIX века.",
        "page_count": 288, "pace": "medium",
        "tags": ["Грустное", "Задумчивое", "Роман", "Классика"],
        "emotions": {"sad": 75, "uplifting": 10, "philosophical": 80, "tense": 30},
    },
    {
        "title": "Основание",
        "author": "Айзек Азимов",
        "description": "Математик предсказывает падение Галактической Империи и создает организацию для сохранения знаний.",
        "page_count": 320, "pace": "medium",
        "tags": ["Напряжённое", "Задумчивое", "Фантастика", "Классика"],
        "emotions": {"sad": 30, "uplifting": 40, "philosophical": 85, "tense": 65},
    },
    {
        "title": "Тайна желтой комнаты",
        "author": "Гастон Леру",
        "description": "Классический детектив о загадочном преступлении в комнате без окон.",
        "page_count": 250, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 15, "uplifting": 5, "philosophical": 20, "tense": 95},
    },
    {
        "title": "Норвежский лес",
        "author": "Харуки Мураками",
        "description": "История взросления, первой любви и потерь в Токио 1960-х.",
        "page_count": 380, "pace": "slow",
        "tags": ["Грустное", "Задумчивое", "Роман"],
        "emotions": {"sad": 85, "uplifting": 10, "philosophical": 70, "tense": 20},
    },
    {
        "title": "Убийство Роджера Экройда",
        "author": "Агата Кристи",
        "description": "Эркюль Пуаро расследует убийство в английской деревне.",
        "page_count": 270, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 20, "uplifting": 10, "philosophical": 30, "tense": 90},
    },
    {
        "title": "Гиперион",
        "author": "Дэн Симмонс",
        "description": "Семь паломников рассказывают свои истории по пути к загадочному монстру.",
        "page_count": 550, "pace": "slow",
        "tags": ["Задумчивое", "Напряжённое", "Фантастика"],
        "emotions": {"sad": 60, "uplifting": 10, "philosophical": 95, "tense": 75},
    },
    {
        "title": "Грозовой перевал",
        "author": "Эмили Бронте",
        "description": "История разрушительной страсти и мести на фоне мрачных вересковых пустошей.",
        "page_count": 380, "pace": "slow",
        "tags": ["Грустное", "Роман", "Классика"],
        "emotions": {"sad": 95, "uplifting": 5, "philosophical": 60, "tense": 70},
    },
    {
        "title": "Марсианские хроники",
        "author": "Рэй Брэдбери",
        "description": "История колонизации Марса, написанная в виде отдельных новелл.",
        "page_count": 280, "pace": "medium",
        "tags": ["Задумчивое", "Фантастика", "Классика"],
        "emotions": {"sad": 70, "uplifting": 20, "philosophical": 85, "tense": 40},
    },
    {
        "title": "Записки о Шерлоке Холмсе",
        "author": "Артур Конан Дойл",
        "description": "Сборник коротких рассказов о приключениях великого сыщика.",
        "page_count": 320, "pace": "fast",
        "tags": ["Напряжённое", "Детектив", "Классика"],
        "emotions": {"sad": 10, "uplifting": 30, "philosophical": 20, "tense": 85},
    },
    {
        "title": "Атлант расправил плечи",
        "author": "Айн Рэнд",
        "description": "Философский роман о роли разума, капитализма и свободы личности.",
        "page_count": 1200, "pace": "slow",
        "tags": ["Задумчивое", "Роман", "Классика"],
        "emotions": {"sad": 40, "uplifting": 50, "philosophical": 99, "tense": 60},
    },
    {
        "title": "О дивный новый мир",
        "author": "Олдос Хаксли",
        "description": "Антиутопия о мире, где люди генетически модифицированы и лишены эмоций.",
        "page_count": 256, "pace": "medium",
        "tags": ["Задумчивое", "Напряжённое", "Фантастика", "Классика"],
        "emotions": {"sad": 65, "uplifting": 10, "philosophical": 90, "tense": 75},
    },
    {
        "title": "Мизери",
        "author": "Стивен Кинг",
        "description": "Писатель попадает в плен к безумной фанатке, которая требует вернуть любимого героя.",
        "page_count": 400, "pace": "fast",
        "tags": ["Напряжённое"],
        "emotions": {"sad": 30, "uplifting": 5, "philosophical": 10, "tense": 99},
    },
    {
        "title": "Пиковая дама",
        "author": "Александр Пушкин",
        "description": "Мистическая повесть о тайне трех карт и погубленной душе.",
        "page_count": 60, "pace": "fast",
        "tags": ["Напряжённое", "Задумчивое", "Классика"],
        "emotions": {"sad": 50, "uplifting": 5, "philosophical": 60, "tense": 90},
    },
    {
        "title": "Цветы для Элджернона (пьеса)",
        "author": "Дэниел Киз",
        "description": "Театральная адаптация известной истории о гениальности и одиночестве.",
        "page_count": 150, "pace": "fast",
        "tags": ["Грустное", "Задумчивое", "Фантастика"],
        "emotions": {"sad": 95, "uplifting": 10, "philosophical": 80, "tense": 30},
    },
]

DEMO_WORDS = ["Тень", "Север", "Письмо", "Океан", "Город", "Сад", "Звезда", "Ключ", "Мост", "Берег",
              "Лес", "Зима", "Огонь", "Дорога", "Остров", "Башня", "Эхо", "Сон", "Дом", "Ветер"]


def get_or_create_tags():
    result = {}
    for category, names in TAGS.items():
        for name in names:
            tag = Tag.objects(name=name).first()
            if not tag:
                tag = Tag(name=name, category=category).save()
            result[name] = tag
    return result


def _tag_names_to_ids(names, tags):
    ids = []
    for name in names:
        if name not in tags:
            tags[name] = Tag.objects(name=name).first() or Tag(name=name, category="Другое").save()
        ids.append(str(tags[name].id))
    return ids


def upsert_book(data, tags):
    fields = {k: v for k, v in data.items() if k not in ("tags",)}
    book = Book.objects(title=data["title"], author=data["author"]).first()
    created = book is None
    if created:
        book = Book(**fields)
    else:
        for k, v in fields.items():
            setattr(book, k, v)
    book.save()

    wanted = set(_tag_names_to_ids(data.get("tags", []), tags))
    have = {bt.tag_id for bt in BookTag.objects(book_id=str(book.id))}
    for tag_id in wanted - have:
        BookTag(book_id=str(book.id), tag_id=tag_id).save()
    for tag_id in have - wanted:
        BookTag.objects(book_id=str(book.id), tag_id=tag_id).delete()
    return created


def make_demo_books(count, tags, rng):
    moods, genres = TAGS["Настроение"], TAGS["Жанр"]
    books, links = [], []
    for i in range(count):
        mood = rng.choice(moods)
        genre = rng.sample(genres, k=rng.choice([1, 1, 2]))
        pages = rng.choice([120, 200, 280, 340, 420, 520, 640, 760])
        book = Book(
            title=f"{rng.choice(DEMO_WORDS)} {rng.choice(DEMO_WORDS).lower()} №{i + 1}",
            author=DEMO_AUTHOR,
            description="Демонстрационная книга для проверки производительности каталога.",
            page_count=pages,
            pace=rng.choice(["slow", "medium", "fast"]),
        )
        books.append(book)
        links.append((book, [mood] + genre))
    Book.objects.insert(books)
    BookTag.objects.insert([
        BookTag(book_id=str(book.id), tag_id=str(tags[name].id))
        for book, names in links for name in names
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reset", action="store_true", help="удалить все книги перед заполнением")
    parser.add_argument("--demo", type=int, metavar="N", help="довести общее число книг до N демо-книгами")
    parser.add_argument("--clear-demo", action="store_true", help="удалить демо-книги")
    parser.add_argument("--json", metavar="FILE", help="импортировать книги из JSON-файла")
    args = parser.parse_args()

    print("Подключение к базе данных...")
    init_db()
    tags = get_or_create_tags()

    if args.clear_demo:
        ids = [str(b.id) for b in Book.objects(author=DEMO_AUTHOR)]
        BookTag.objects(book_id__in=ids).delete()
        Book.objects(author=DEMO_AUTHOR).delete()
        print(f"Удалено демо-книг: {len(ids)}")
        return

    if args.reset:
        Book.objects.delete()
        BookTag.objects.delete()
        print("Старые книги удалены")

    data = BOOKS
    if args.json:
        with open(args.json, encoding="utf-8") as f:
            data = json.load(f)

    added = sum(upsert_book(item, tags) for item in data)
    print(f"Книг в наборе: {len(data)}, из них новых: {added}")

    if args.demo:
        missing = args.demo - Book.objects.count()
        if missing > 0:
            make_demo_books(missing, tags, random.Random(2026))
            print(f"Добавлено демо-книг: {missing}")

    print(f"Готово. Всего книг в базе: {Book.objects.count()}")


if __name__ == "__main__":
    main()
