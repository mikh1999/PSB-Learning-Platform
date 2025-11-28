from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.course import course_crud
from app.db.session import get_async_session
from app.models.user import User, UserRole
from app.schemas.course import CourseCreate, CoursePublic, CourseRead, CourseUpdate

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/featured", response_model=list[CoursePublic])
async def get_featured_courses(
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Получить случайные опубликованные курсы для главной страницы. Без авторизации."""
    return await course_crud.get_random_published(db, limit=3)


@router.get("/", response_model=list[CourseRead])
async def get_courses(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    """Get all courses. Teachers see only their courses."""
    if current_user.role == UserRole.TEACHER:
        return await course_crud.get_by_teacher(db, current_user.id, skip, limit)
    return await course_crud.get_all(db, skip, limit)


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get course by ID."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    # Teachers can only view their own courses
    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    return course


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_in: CourseCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Create a new course. Only teachers can create courses."""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create courses",
        )
    return await course_crud.create(db, course_in, current_user.id)


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Update course. Only course owner can update."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only course owner can update",
        )
    return await course_crud.update(db, course, course_in)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Delete course. Only course owner can delete."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only course owner can delete",
        )
    await course_crud.delete(db, course)
