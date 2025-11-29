#!/usr/bin/env python3
"""
Скрипт для создания администратора.

Использование:
    python scripts/create_admin.py

Или с параметрами:
    python scripts/create_admin.py --email admin@example.com --password secret123
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import async_session_maker
from app.core.security import get_password_hash

# Импортируем все модели для корректной работы relationships
from app.models.user import User, UserRole
from app.models.course import Course  # noqa: F401
from app.models.lesson import Lesson  # noqa: F401
from app.models.assignment import Assignment  # noqa: F401
from app.models.submission import Submission  # noqa: F401
from app.models.grade import Grade  # noqa: F401
from app.models.enrollment import Enrollment  # noqa: F401
from app.models.lesson_progress import LessonProgress  # noqa: F401


async def create_admin(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> None:
    """Создать администратора в базе данных."""
    async with async_session_maker() as db:
        # Проверяем, существует ли пользователь
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.role == UserRole.ADMIN:
                print(f"Администратор с email {email} уже существует.")
                return
            else:
                # Обновляем существующего пользователя до админа
                existing_user.role = UserRole.ADMIN
                existing_user.is_active = True
                existing_user.hashed_password = get_password_hash(password)
                await db.commit()
                print(f"Пользователь {email} повышен до администратора.")
                return

        # Создаём нового админа
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            is_active=True,  # Админ сразу активен
        )
        db.add(admin)
        await db.commit()
        print(f"Администратор создан: {email}")


def main():
    parser = argparse.ArgumentParser(description="Создание администратора")
    parser.add_argument(
        "--email",
        default="admin@psb.ru",
        help="Email администратора (по умолчанию: admin@psb.ru)",
    )
    parser.add_argument(
        "--password",
        default="admin123",
        help="Пароль администратора (по умолчанию: admin123)",
    )
    parser.add_argument(
        "--first-name",
        default="Админ",
        help="Имя (по умолчанию: Админ)",
    )
    parser.add_argument(
        "--last-name",
        default="Системы",
        help="Фамилия (по умолчанию: Системы)",
    )

    args = parser.parse_args()

    print(f"Создание администратора...")
    print(f"  Email: {args.email}")
    print(f"  Имя: {args.first_name} {args.last_name}")

    asyncio.run(
        create_admin(
            email=args.email,
            password=args.password,
            first_name=args.first_name,
            last_name=args.last_name,
        )
    )


if __name__ == "__main__":
    main()
