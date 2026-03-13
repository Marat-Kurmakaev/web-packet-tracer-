# Обучающая платформа для создания сетевых карт

## Требования

Для запуска с Docker:

- Docker
- Docker Compose

Для локального запуска:

- Python 3.14
- PostgreSQL

## Запуск backend через Docker

1. Создать `.env` из шаблона:

```bash
cp .env.example .env
```

2. Поднять контейнеры:

```bash
docker compose up -d --build
```

3. Применить миграции:

```bash
docker compose exec backend python manage.py migrate
```

4. Создать суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

После запуска backend будет доступен по адресу: http://localhost:8000

## Локальный запуск (без Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```
