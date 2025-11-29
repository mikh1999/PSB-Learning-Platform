from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserCRUD:
    async def get_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, user_in: UserCreate) -> User:
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            role=user_in.role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update(self, db: AsyncSession, user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate(
        self, db: AsyncSession, email: str, password: str
    ) -> User | None:
        user = await self.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        result = await db.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Получить пользователей на рассмотрении (is_active=False)."""
        result = await db.execute(
            select(User)
            .where(User.is_active == False)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_all(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def count_pending(self, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.count(User.id)).where(User.is_active == False)
        )
        return result.scalar() or 0

    async def activate(self, db: AsyncSession, user: User) -> User:
        """Активировать пользователя."""
        user.is_active = True
        await db.commit()
        await db.refresh(user)
        return user

    async def deactivate(self, db: AsyncSession, user: User) -> User:
        """Деактивировать пользователя."""
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        return user


user_crud = UserCRUD()