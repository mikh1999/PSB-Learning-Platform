from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.user import user_crud
from app.db.session import get_async_session
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserRead

router = APIRouter(prefix="/admin", tags=["Admin"])


async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Проверить, что текущий пользователь - администратор."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для администраторов",
        )
    return current_user


@router.get("/users", response_model=PaginatedResponse[UserRead])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    admin: Annotated[User, Depends(get_current_admin)],
    skip: int = 0,
    limit: int = 100,
):
    """Получить список всех пользователей. Только для админов."""
    items = await user_crud.get_all(db, skip, limit)
    total = await user_crud.count_all(db)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/users/pending", response_model=PaginatedResponse[UserRead])
async def get_pending_users(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    admin: Annotated[User, Depends(get_current_admin)],
    skip: int = 0,
    limit: int = 100,
):
    """Получить список пользователей на рассмотрении. Только для админов."""
    items = await user_crud.get_pending(db, skip, limit)
    total = await user_crud.count_pending(db)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/users/{user_id}/activate", response_model=UserRead)
async def activate_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    admin: Annotated[User, Depends(get_current_admin)],
):
    """Активировать пользователя. Только для админов."""
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже активен",
        )
    return await user_crud.activate(db, user)


@router.post("/users/{user_id}/deactivate", response_model=UserRead)
async def deactivate_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    admin: Annotated[User, Depends(get_current_admin)],
):
    """Деактивировать пользователя. Только для админов."""
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя деактивировать самого себя",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже неактивен",
        )
    return await user_crud.deactivate(db, user)
