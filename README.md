# Catalog Microservice

Проект каталога товаров с интеграцией Telegram Mini App.

## Архитектура
- **Backend**: FastAPI (Python 3.11, SQLAlchemy 2.0 async, asyncpg, boto3)
- **Bot**: aiogram 3.x (Python 3.11, aiohttp)
- **Frontend**: Next.js 14 (App Router, TypeScript)
- **Database**: PostgreSQL 15
- **Storage**: MinIO S3

## Инструкция по запуску
1. Откройте `docker-compose.yml` и укажите свои значения для:
   - `BOT_TOKEN`
   - `ADMIN_ID`
   - `WEBAPP_URL`
2. Запустите проект через Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
