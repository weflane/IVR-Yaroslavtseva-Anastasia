# BookMatch

Подбор книги под настроение: адаптивный тест, рекомендации по прочитанному, каталог с тегами,
личный кабинет, экспорт в .txt и .png. Формат — PWA (React + Vite), бэкенд — FastAPI, база — MongoDB.

## Запуск в Docker

```bash
cp .env.example .env            # один раз; поменяйте пароли и SECRET_KEY
docker compose up -d --build
docker compose exec backend python seed_books.py            # базовый набор книг
docker compose exec backend python seed_books.py --demo 1000   # (по желанию) довести до 1000 книг для проверки нагрузки
```

Сайт: http://localhost:8080 · документация API: http://localhost:8000/docs

PWA устанавливается («Установить приложение» в Chrome/Edge, «На экран Домой» в Safari);
service worker работает по HTTPS или на localhost.

## Локальная разработка

```bash
# база: docker compose up -d mongo   (в .env для локального запуска хост mongo замените на localhost)
cd backend && pip install -r requirements.txt && python seed_books.py && uvicorn main:app --reload
cd frontend && npm install && npm run dev        # http://localhost:5173
```

## Резервные копии

Сервис `backup` каждые 24 часа (`BACKUP_INTERVAL_HOURS`) делает `mongodump` в папку `backups/`
и хранит 14 дней (`BACKUP_KEEP_DAYS`).

```bash
./scripts/backup.sh                                   # копия прямо сейчас
./scripts/restore.sh backups/bookmatch-ГГГГММДД-ЧЧММСС.archive.gz   # восстановление
```

## Книги

`seed_books.py` ничего не удаляет (только добавляет/обновляет). Ключи: `--reset` (стереть всё),
`--json books.json` (свои книги), `--demo N` (синтетические книги «Демо-автор»), `--clear-demo`.

## Тесты, проверка кода и нагрузка

```bash
cd backend && python -m pytest tests     # подбор, адаптивный тест, эмоциональная карта, PNG-карточки
cd frontend && npm run lint              # ESLint
python scripts/load_test.py --users 100 --report loadtest_report.md   # 100 пользователей одновременно, замер скорости подбора
python backend/cleanup_loadtest.py       # удалить тестовых пользователей после нагрузочной проверки
```

Те же тесты, проверка стиля и сборка запускаются автоматически в GitHub Actions
(`.github/workflows/tests.yml`). Сценарий `docker.yml` собирает образы сервера и сайта, публикует их в реестр GitHub и
запускает развёртывание, если в настройках репозитория задан секрет `DEPLOY_HOOK_URL`.

## Администратор

Добавлять и менять книги через API (`POST/PUT/DELETE /books`) может только администратор.
Назначить его: `docker compose exec backend python make_admin.py почта@пример.рф` (сначала зарегистрируйся на сайте).

## Отличия от заявки

Что изменилось по сравнению с заявкой и сценариями и почему, описано в `docs/otlichiya_ot_zayavki.md`.

## Соответствие требованиям

| Требование | Где |
|---|---|
| PWA | `frontend/public/manifest.webmanifest`, `sw.js`, иконки |
| API книг (поиск по тегам, добавление, получение) | `GET/POST/PUT/DELETE /books`, `?tag_ids=&q=` |
| API пользователей (регистрация, история, «прочитано») | `/auth`, `/quiz/history`, `/library` |
| Тест → 3–5 книг | `POST /quiz`, `app/quiz_logic.py` (прочитанные исключаются) |
| Подбор по истории прочитанного | `GET /recommendations` |
| Каталог по тегам | `/catalog`, `GET /books?tag_ids=` |
| Карточка книги, эмоциональная карта | `/books/:id`, `app/emotions.py` |
| «Найти похожую» | кнопка на карточке, `GET /books/{id}/similar` |
| Дневник настроений | вкладка «История настроений» |
| «Прочитано» / «Хочу прочитать» | карточка книги и личный кабинет |
| Экспорт .txt / .png | подборка, библиотека, карточка книги; `GET /books/{id}/card.png` |
| Личные комментарии | `/comments` — отдаются только автору |
| Docker, резервные копии | `docker-compose.yml`, `scripts/` |
| Адаптивный тест | `GET /quiz/options`, `available_options` в `app/quiz_logic.py`: варианты ответов подстраиваются под выбранные |
| Экспорт подборки .png | окно «Экспорт» на странице результата, `GET /quiz/results/{id}/card.png`, `render_selection_card` |
| Помощь | страница `/help` |
| Подбор ≤ 3 с, 100 пользователей | `scripts/load_test.py` и отчёт `loadtest_report.md` |
