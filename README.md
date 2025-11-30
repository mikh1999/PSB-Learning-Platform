# PSB Learning Platform

Образовательная платформа для хакатона **ПСБ Hack&Change 2025**.

**Трек:** ПРЕПОДАВАТЕЛЬ

## Команда

**Название:** Картофельные глазки

| Участник | Роль | Контакт |
|----------|------|---------|
| Нуритдинова Аделина | Frontend-разработчик, UI/UX дизайнер | [@ledaina](https://t.me/ledaina) |
| Дубинин Михаил | Backend-разработчик, DevOps | [@mikh1999](https://t.me/mikh1999) |
| Ганеев Артур | Backend-разработчик, Data Engineer | [@ArturGD](https://t.me/ArturGD) |

## Описание проекта

Платформа для онлайн-обучения с фокусом на сценарии преподавателя:

- Создание и редактирование курсов
- Добавление учебных материалов (видео, PDF, текст)
- Проверка работ студентов с комментариями
- Выставление оценок
- Журнал успеваемости группы
- Система комментариев к ответам (чат преподаватель-студент)

## Стек технологий

### Backend
- **Python 3.11**
- **FastAPI 0.115.5** — REST API фреймворк
- **SQLAlchemy 2.0.36** — ORM (async)
- **PostgreSQL 16** — база данных
- **Alembic 1.14.0** — миграции
- **Pydantic 2.10.2** — валидация данных
- **python-jose 3.3.0** — JWT аутентификация
- **Passlib + bcrypt** — хеширование паролей

### Инфраструктура
- **Docker + docker-compose**
- **Nginx** — reverse proxy
- **Uvicorn** — ASGI сервер

## Структура проекта

```
PSB/
├── app/
│   ├── api/
│   │   ├── deps/              # Dependencies (авторизация)
│   │   │   └── __init__.py
│   │   └── v1/
│   │       ├── endpoints/     # API эндпоинты
│   │       │   ├── auth.py        # Аутентификация
│   │       │   ├── users.py       # Пользователи
│   │       │   ├── courses.py     # Курсы
│   │       │   ├── lessons.py     # Уроки
│   │       │   ├── assignments.py # Задания
│   │       │   ├── submissions.py # Ответы студентов
│   │       │   ├── grades.py      # Оценки
│   │       │   ├── gradebook.py   # Журнал успеваемости
│   │       │   ├── files.py       # Файлы и видео-стриминг
│   │       │   └── lesson_progress.py # Прогресс уроков
│   │       └── router.py
│   ├── core/
│   │   ├── config.py          # Настройки из .env
│   │   ├── security.py        # JWT, хеширование паролей
│   │   └── storage.py         # Файловое хранилище
│   ├── crud/                  # CRUD операции
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── lesson.py
│   │   ├── assignment.py
│   │   ├── submission.py
│   │   ├── grade.py
│   │   └── lesson_progress.py
│   ├── db/
│   │   ├── base.py            # SQLAlchemy Base
│   │   └── session.py         # Async session
│   ├── models/                # SQLAlchemy модели
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── lesson.py
│   │   ├── assignment.py
│   │   ├── submission.py
│   │   ├── grade.py
│   │   ├── enrollment.py
│   │   └── lesson_progress.py
│   ├── schemas/               # Pydantic схемы
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── lesson.py
│   │   ├── assignment.py
│   │   ├── submission.py
│   │   ├── grade.py
│   │   └── lesson_progress.py
│   └── main.py                # FastAPI приложение
├── alembic/                   # Миграции БД
│   ├── versions/
│   └── env.py
├── uploads/                   # Загруженные файлы
│   ├── lessons/               # Файлы уроков
│   └── submissions/           # Файлы ответов
├── nginx/                     # Конфигурация Nginx
│   └── conf/
├── scripts/                   # Вспомогательные скрипты
│   ├── seed_database.py       # Наполнение БД тестовыми данными
│   └── create_sample_files.sh # Создание sample файлов
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── run.py                     # Локальный запуск
└── .env                       # Переменные окружения
```

## Установка и запуск

### Требования

- Python 3.11+
- PostgreSQL 16+
- Docker и Docker Compose (для контейнеризации)

### Вариант 1: Docker (рекомендуется)

1. **Клонировать репозиторий:**
```bash
git clone <repository-url>
cd PSB
```

2. **Создать файл `.env`:**
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=psb_db
DB_USER=postgres
DB_PASSWORD=postgres

APP_HOST=0.0.0.0
APP_PORT=8080

SECRET_KEY=your-secret-key-change-in-production
DEBUG=false
```

3. **Запустить контейнеры:**
```bash
docker-compose up --build
```

4. **API доступен по адресу:** http://localhost:80

### Вариант 2: Локальный запуск

1. **Установить зависимости:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

2. **Создать файл `.env`:**
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=psb_db
DB_USER=postgres
DB_PASSWORD=postgres

APP_HOST=127.0.0.1
APP_PORT=8080

SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
```

3. **Создать базу данных PostgreSQL:**
```bash
createdb psb_db
```

4. **Применить миграции:**
```bash
alembic upgrade head
```

5. **Запустить сервер:**
```bash
python run.py
```

6. **API доступен по адресу:** http://localhost:8080

## API документация

После запуска доступна интерактивная документация:

- **Swagger UI:** http://localhost:8080/api/v1/docs
- **ReDoc:** http://localhost:8080/api/v1/redoc

### Основные эндпоинты

| Группа | Путь | Описание |
|--------|------|----------|
| Auth | `/api/v1/auth/register` | Регистрация пользователя |
| Auth | `/api/v1/auth/login` | Авторизация (получение токена) |
| Auth | `/api/v1/auth/me` | Текущий пользователь |
| Courses | `/api/v1/courses` | CRUD курсов |
| Lessons | `/api/v1/lessons` | CRUD уроков |
| Assignments | `/api/v1/assignments` | CRUD заданий |
| Submissions | `/api/v1/submissions` | Ответы студентов |
| Grades | `/api/v1/grades` | Оценки |
| Gradebook | `/api/v1/gradebook` | Журнал успеваемости |
| Files | `/api/v1/files` | Загрузка/скачивание файлов |

## Роли пользователей

- **student** — просмотр материалов, отправка ответов, просмотр оценок
- **teacher** — создание курсов, проверка работ, выставление оценок, комментирование

## Миграции базы данных

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "описание изменений"

# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Посмотреть текущую версию
alembic current
```

## Библиотеки и версии

```
# FastAPI
fastapi==0.115.5
uvicorn[standard]==0.32.1
python-multipart==0.0.17

# Database
sqlalchemy==2.0.36
asyncpg==0.30.0
alembic==1.14.0
greenlet==3.2.4

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1

# Validation
pydantic==2.10.2
pydantic-settings==2.6.1
email-validator==2.2.0

# Utils
python-dotenv==1.0.1
aiofiles==24.1.0
```

## Тестовые данные

Для наполнения базы тестовыми данными:

```bash
python scripts/seed_database.py
```

Создаёт:
- 5 преподавателей, 50 студентов
- 35 курсов с 5-15 уроками каждый
- ~540 заданий
- ~2600 ответов студентов
- ~1300 оценок
- ~3200 комментариев

**Тестовые аккаунты:**
- Преподаватель: `teacher1@test.edu` / `password123`
- Студент: `student1@test.edu` / `password123`

## Лицензия

MIT License
