# SandStreamBot

Telegram-бот и админ-панель для публикации и поиска **остатков сыпучих строительных материалов** в Санкт-Петербурге и Ленинградской области: песок, щебень, гравий, ПГС, грунты и смежное.

| | |
|---|---|
| **Статус** | MVP / ветка `beta` |
| **Канал UX** | Telegram (aiogram 3, long polling) |
| **Данные** | Django ORM + PostgreSQL |
| **FSM** | Redis |
| **Админка** | Django Admin |

> Подробный план развития: [`docs/SandStreamBot_plan_razvitiya.pdf`](docs/SandStreamBot_plan_razvitiya.pdf)

---

## Возможности

### Уже работает

- **Поиск объявлений** — материал → населённый пункт → тип цены (все / бесплатные / платные)
- **Каталог в боте** — пагинация, сортировка (новые / цена ↑ / цена ↓), карточка с контактом
- **Создание объявления** — пошаговый FSM (материал, описание, объём, цена, город, адрес, геолокация)
- **Справочники** — типы материалов и города СПб/ЛО (seed-команды)
- **Django Admin** — пользователи Telegram, объявления, фото, подписки (модели)
- **Инфраструктура** — PostgreSQL 16 и Redis 7 через Docker Compose

### В модели / UI, но ещё не в продукте

- Роли `user` / `owner` / `admin` в БД — публикация пока только через `ADMIN_IDS` в `.env`
- Фото объявлений (`ListingPhoto`) — загрузка из бота не подключена
- Подписки и уведомления — модели есть, в боте stub
- Geo «рядом со мной» — задел в FSM/клавиатурах, сервис поиска по радиусу не готов

---

## Архитектура

```text
┌──────────────────────┐         Redis (FSM)        ┌─────────────────┐
│  python -m app       │◄──────────────────────────►│  redis:7        │
│  aiogram 3           │                            └─────────────────┘
│  handlers/services   │
└──────────┬───────────┘
           │  django.setup() + ORM (sync_to_async)
           ▼
┌──────────────────────┐                            ┌─────────────────┐
│  web/ (Django 6)     │───────────────────────────►│  PostgreSQL 16  │
│  models + Admin      │                            └─────────────────┘
└──────────────────────┘
```

Это **shared-database** схема: Telegram — основной интерфейс, Django — модели, миграции и админка. Публичного HTTP API и веб-каталога пока нет.

---

## Стек

| Компонент | Версия / выбор |
|---|---|
| Python | 3.12+ (проверено на 3.13) |
| Telegram | aiogram 3.33 |
| Backend / ORM | Django 6 |
| БД | PostgreSQL 16 (рекомендуется) или SQLite |
| FSM storage | Redis 7 |
| Конфиг | pydantic-settings + `.env` |
| Медиа | Pillow, `MEDIA_ROOT` |

---

## Требования

- Python 3.12+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — для Postgres и Redis
- Токен бота от [@BotFather](https://t.me/BotFather)
- Свой числовой Telegram ID (для `ADMIN_IDS`) — удобно взять у [@userinfobot](https://t.me/userinfobot)

---

## Быстрый старт (Windows / PowerShell)

### 1. Клонирование и окружение

```powershell
cd SandStreamBot
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### 2. Настройка `.env`

Обязательно заполните:

| Переменная | Назначение |
|---|---|
| `BOT_TOKEN` | токен Telegram-бота |
| `ADMIN_IDS` | Telegram ID админов через запятую |
| `DJANGO_SECRET_KEY` | длинная случайная строка (без неё Django не стартует) |
| `POSTGRES_*` | доступы к БД (как в compose) |
| `REDIS_URL` | например `redis://localhost:6379/0` |

Шаблон — [`.env.example`](.env.example). Файл `.env` в git не коммитится.

### 3. Инфраструктура

```powershell
docker compose up -d db redis
```

Порты слушаются только на `127.0.0.1` (5432 и 6379).

Проверка:

```powershell
docker compose ps
```

### 4. Миграции и справочники

Команды Django запускаются из корня репозитория (подхватывается корневой `.env`):

```powershell
.\.venv\Scripts\python.exe web\manage.py migrate
.\.venv\Scripts\python.exe web\manage.py seed_catalog
.\.venv\Scripts\python.exe web\manage.py seed_listings   # опционально, демо-данные
.\.venv\Scripts\python.exe web\manage.py createsuperuser
```

| Команда | Что делает |
|---|---|
| `seed_catalog` | материалы + города СПб/ЛО (идемпотентно) |
| `seed_listings` | тестовые объявления; есть флаг `--flush` |

### 5. Запуск

**Терминал 1 — бот:**

```powershell
.\.venv\Scripts\Activate.ps1
python -m app
```

**Терминал 2 — Django Admin:**

```powershell
.\.venv\Scripts\Activate.ps1
python web\manage.py runserver 127.0.0.1:8000
```

Админка: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

В Telegram откройте бота и отправьте `/start`.

---

## Переменные окружения

| Ключ | По умолчанию | Описание |
|---|---|---|
| `BOT_TOKEN` | — | токен BotFather (**обязателен**) |
| `ADMIN_IDS` | пусто | CSV Telegram ID с правом публикации |
| `LOG_LEVEL` | `INFO` | уровень логирования бота |
| `REDIS_URL` | `redis://localhost:6379/0` | хранилище FSM |
| `DJANGO_SECRET_KEY` | — | секрет Django (**обязателен**) |
| `DJANGO_DEBUG` | `false` | режим отладки Django |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | CSV хостов |
| `DB_ENGINE` | `sqlite` в коде / в example — `postgresql` | `postgresql` или `sqlite` |
| `POSTGRES_DB` | `sandstream` | имя БД |
| `POSTGRES_USER` | `sandstream` | пользователь |
| `POSTGRES_PASSWORD` | — | пароль |
| `POSTGRES_HOST` | `localhost` | хост |
| `POSTGRES_PORT` | `5432` | порт |

Для локальной разработки без Docker можно поставить `DB_ENGINE=sqlite` — боту всё равно нужен Redis для FSM.

---

## Структура репозитория

```text
SandStreamBot/
├── app/                      # Telegram-бот
│   ├── __main__.py           # точка входа: Django setup → polling
│   ├── bot.py                # фабрика Bot
│   ├── config.py             # pydantic-settings
│   ├── django_setup.py       # подключение ORM
│   ├── handlers/             # роутеры: start, search, catalog, listings
│   ├── keyboards/            # reply / inline клавиатуры
│   ├── states/               # FSM-состояния
│   ├── services/             # работа с ORM (listings, search)
│   └── filters/
├── web/                      # Django-проект
│   ├── manage.py
│   ├── config/               # settings, urls, asgi/wsgi
│   ├── accounts/             # TelegramUser
│   ├── catalog/              # MaterialType, City, Listing, Photo, …
│   │   └── management/commands/
│   │       ├── seed_catalog.py
│   │       └── seed_listings.py
│   ├── templates/
│   └── media/                # загружаемые файлы (в .gitignore)
├── docs/
│   └── SandStreamBot_plan_razvitiya.pdf
├── docker-compose.yml        # postgres + redis
├── requirements.txt
├── .env.example
├── start.bat                 # локальный хелпер Windows Terminal (опционально)
└── README.md
```

### Слои бота

| Слой | Ответственность |
|---|---|
| `handlers` | сценарии диалога, валидация ввода |
| `keyboards` | разметка кнопок |
| `states` | имена состояний FSM |
| `services` | транзакции ORM, выборки каталога |

Порядок подключения роутеров: `start` → `listings` → `catalog` → `search`.

---

## Роли и доступ

| Источник | Сейчас |
|---|---|
| `ADMIN_IDS` в `.env` | единственный способ получить кнопки «Добавить / Управление» |
| `TelegramUser.role` | поле в БД (`user` / `owner` / `admin`), в боте ещё не используется |
| Django superuser | доступ к `/admin/`, не связан с Telegram-ролями автоматически |

Команды в боте:

| Команда | Действие |
|---|---|
| `/start` | приветствие, главное меню, сброс FSM |
| `/cancel` | отмена текущего сценария |

---

## Docker Compose

Сервисы (приложения в контейнеры не упакованы — только зависимости):

```powershell
docker compose up -d          # db + redis
docker compose up -d db       # только Postgres
docker compose down           # остановить
docker compose down -v        # остановить и удалить тома (данные пропадут)
```

Healthcheck'и настроены для `pg_isready` и `redis-cli ping`.

---

## Разработка

### Типичный цикл

1. Поднять `db` + `redis`
2. `migrate` при новых миграциях
3. Запустить `python -m app` и при необходимости admin
4. Менять handlers/services; справочники править в Admin или seeders

### Полезные замечания

- Справочники в reply-клавиатурах кэшируются (`lru_cache`). После изменения материалов/городов в Admin **перезапустите бота**, иначе кнопки могут быть старыми.
- Объявления в поиске — со статусом `active`.
- Создание из бота сразу ставит `ACTIVE` (модерации пока нет).
- Геоточка при создании опциональна («Пропустить»).
- Тесты и CI пока не подключены (`tests/` — заготовка).

### SQLite (упрощённый режим)

```env
DB_ENGINE=sqlite
```

Файл БД: `web/db.sqlite3` (игнорируется git). Redis всё равно нужен для FSM.

---

## Дорожная карта (кратко)

Ближайший горизонт пилота:

1. Материал при создании — только из справочника (как в поиске)
2. Роли `OWNER` / `ADMIN` из БД вместо одного `ADMIN_IDS`
3. Загрузка фото в wizard
4. Управление своими объявлениями (архив / продано)
5. Обязательный телефон в карточке

Далее: подписки, geo-поиск, тесты/CI, деплой (webhook).

Полный план с приёмкой фаз — в [`docs/SandStreamBot_plan_razvitiya.pdf`](docs/SandStreamBot_plan_razvitiya.pdf).

---

## Устранение неполадок

| Симптом | Что проверить |
|---|---|
| `DJANGO_SECRET_KEY is not set` | заполнен ли `.env` в корне репозитория |
| бот падает на Redis / FSM | `docker compose ps`, `REDIS_URL` |
| ошибки БД / connection refused | запущен ли `db`, верны ли `POSTGRES_*`, `DB_ENGINE=postgresql` |
| пустые кнопки материалов/городов | выполнен ли `seed_catalog`, перезапущен ли бот |
| нет кнопки «Добавить объявление» | ваш ID в `ADMIN_IDS` |
| Admin не открывается | запущен ли `runserver`, создан ли superuser |

---

## Лицензия

Проприетарный проект. Все права защищены, если иное не оговорено отдельно.
