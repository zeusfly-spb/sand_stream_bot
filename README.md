# SandStreamBot

Telegram-бот для публикации и поиска остатков сыпучих строительных материалов.

## Требования
- Python 3.11+
- Docker Desktop (для PostgreSQL, опционально на первом запуске)

## Быстрый старт в Windows PowerShell

```powershell
cd SandStreamBot
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Откройте `.env` и укажите `BOT_TOKEN`, полученный у BotFather, и свой Telegram ID в `ADMIN_IDS`.

Запуск:

```powershell
python -m app
```

## PostgreSQL
Для запуска базы данных через Docker:

```powershell
docker compose up -d db
```

Пока бот использует минимальный каркас и не подключается к БД: подключение и модели добавим следующим этапом.

## Структура

```text
app/
  __init__.py
  __main__.py
  config.py
  bot.py
  handlers/
    __init__.py
    start.py
  keyboards/
    __init__.py
    main_menu.py
  filters/
    __init__.py
  services/
    __init__.py
```
