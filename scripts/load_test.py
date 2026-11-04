import argparse
import json
import math
import random
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

QUIZ_LIMIT_SECONDS = 3.0
MAX_ERROR_RATE = 0.01

MOODS = ["sad", "uplifting", "philosophical", "tense"]
GENRES = ["mystery", "sci-fi", "romance", "classic"]
PACES = ["slow", "medium", "fast"]
LENGTHS = ["short", "medium", "long"]


def call(base, method, path, token=None, body=None, timeout=30):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(base + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw, status = response.read(), response.status
    except urllib.error.HTTPError as error:
        raw, status = error.read(), error.code
    except Exception:
        return None, None, time.perf_counter() - started
    elapsed = time.perf_counter() - started
    try:
        payload = json.loads(raw) if raw else None
    except ValueError:
        payload = None
    return status, payload, elapsed


class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {}

    def add(self, name, seconds, ok):
        with self.lock:
            self.data.setdefault(name, []).append((seconds, ok))


def percentile(sorted_values, share):
    if not sorted_values:
        return 0.0
    index = max(0, math.ceil(share * len(sorted_values)) - 1)
    return sorted_values[index]


def virtual_user(number, args, run_id, stats, barrier):
    base = args.base_url.rstrip("/")
    email, password = f"loadtest-{run_id}-{number}@example.com", "loadtest123"

    def step(name, method, path, token=None, body=None, expected=(200, 201)):
        status, payload, seconds = call(base, method, path, token, body, args.timeout)
        stats.add(name, seconds, status in expected)
        return status, payload

    status, _ = step("Регистрация (шифрование пароля)", "POST", "/auth/register",
                     body={"email": email, "password": password}, expected=(201,))
    token = None
    if status == 201:
        status, payload = step("Вход", "POST", "/auth/login", body={"email": email, "password": password})
        token = payload.get("access_token") if status == 200 and payload else None

    try:
        barrier.wait(timeout=300)
    except threading.BrokenBarrierError:
        pass
    if not token:
        return

    for _ in range(args.rounds):
        _, books = step("Каталог (60 книг)", "GET", "/books?limit=60")
        step("Список тегов", "GET", "/tags")
        if isinstance(books, list) and books:
            book_id = random.choice(books)["id"]
            step("Страница книги", "GET", f"/books/{book_id}")
            step("Найти похожие", "GET", f"/books/{book_id}/similar")
        mood, genre = random.choice(MOODS), random.choice(GENRES)
        step("Варианты ответов теста", "GET", f"/quiz/options?mood={mood}&genre={genre}", token)
        answers = {"mood": mood, "genre": genre, "pace": random.choice(PACES), "length": random.choice(LENGTHS)}
        step("ПОДБОР КНИГИ (тест)", "POST", "/quiz", token, {"answers": answers})
        step("Рекомендации", "GET", "/recommendations", token, expected=(200, 400))


def summarize(stats):
    rows = []
    for name, items in stats.data.items():
        times = sorted(seconds for seconds, _ in items)
        errors = sum(1 for _, ok in items if not ok)
        rows.append({
            "name": name, "count": len(items), "errors": errors,
            "p50": percentile(times, 0.50), "p95": percentile(times, 0.95), "max": times[-1],
        })
    return rows


def build_report(args, rows, duration, verdicts):
    lines = [
        "# Результаты нагрузочной проверки",
        "",
        f"- Дата: {datetime.now():%d.%m.%Y %H:%M}",
        f"- Адрес: {args.base_url}",
        f"- Одновременных пользователей: {args.users}, повторов на пользователя: {args.rounds}",
        f"- Общая длительность: {duration:.1f} с",
        "",
        "| Действие | Запросов | Ошибок | Медиана, с | 95-й процентиль, с | Максимум, с |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['count']} | {r['errors']} | {r['p50']:.3f} | {r['p95']:.3f} | {r['max']:.3f} |"
        )
    lines += ["", "## Вывод", ""] + [f"- {text}" for text in verdicts]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Нагрузочная проверка")
    parser.add_argument("--base-url", default="http://localhost:8000", help="адрес API")
    parser.add_argument("--users", type=int, default=100, help="сколько пользователей одновременно")
    parser.add_argument("--rounds", type=int, default=3, help="сколько раз каждый повторяет сценарий")
    parser.add_argument("--timeout", type=float, default=30, help="сколько секунд ждать ответ")
    parser.add_argument("--report", help="сохранить результаты в этот файл (Markdown)")
    args = parser.parse_args()

    status, _, _ = call(args.base_url.rstrip("/"), "GET", "/health", timeout=5)
    if status != 200:
        print(f"Сервер не отвечает по адресу {args.base_url}. Запусти проект и повтори.")
        return 2

    run_id = uuid.uuid4().hex[:8]
    stats, barrier = Stats(), threading.Barrier(args.users)
    print(f"Запускаю {args.users} пользователей одновременно, по {args.rounds} повтора(ов) каждый...")
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.users) as pool:
        futures = [pool.submit(virtual_user, i, args, run_id, stats, barrier) for i in range(args.users)]
        for future in futures:
            future.result()
    duration = time.perf_counter() - started

    rows = summarize(stats)
    total = sum(r["count"] for r in rows)
    errors = sum(r["errors"] for r in rows)
    quiz = next((r for r in rows if r["name"].startswith("ПОДБОР")), None)

    verdicts = []
    quiz_ok = bool(quiz) and quiz["p95"] <= QUIZ_LIMIT_SECONDS
    if quiz:
        verdicts.append(
            f"Подбор книги: 95% запросов быстрее {quiz['p95']:.2f} с "
            f"(требование: не дольше {QUIZ_LIMIT_SECONDS:.0f} с), максимум {quiz['max']:.2f} с. "
            f"{'ТРЕБОВАНИЕ ВЫПОЛНЕНО' if quiz_ok else 'ТРЕБОВАНИЕ НЕ ВЫПОЛНЕНО'}."
        )
    else:
        verdicts.append("Подбор книги не удалось измерить: ни один пользователь не вошёл в систему.")
    error_rate = errors / total if total else 1
    errors_ok = error_rate <= MAX_ERROR_RATE
    outcome = f"Устойчивость к {args.users} пользователям подтверждена." if errors_ok else "Слишком много ошибок."
    verdicts.append(f"Ошибок: {errors} из {total} запросов ({error_rate:.1%}). {outcome}")

    report = build_report(args, rows, duration, verdicts)
    print("\n" + report)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as file:
            file.write(report)
        print(f"Результаты сохранены в {args.report}")
    return 0 if quiz_ok and errors_ok else 1


if __name__ == "__main__":
    sys.exit(main())
