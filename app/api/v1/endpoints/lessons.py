from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.course import course_crud
from app.crud.lesson import lesson_crud
from app.db.session import get_async_session
from app.models.user import User, UserRole
from app.schemas.lesson import LessonCreate, LessonRead, LessonUpdate

router = APIRouter(prefix="/courses/{course_id}/lessons", tags=["Lessons"])


async def get_course_with_access(
    course_id: int,
    db: AsyncSession,
    current_user: User,
    require_owner: bool = False,
) -> None:
    """Check if course exists and user has access."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    if require_owner and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only course owner can perform this action",
        )
    # Teachers can only access their own courses
    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    return course


@router.get("/", response_model=list[LessonRead])
async def get_lessons(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    """Get all lessons for a course."""
    await get_course_with_access(course_id, db, current_user)
    return await lesson_crud.get_by_course(db, course_id, skip, limit)


@router.get("/{lesson_id}", response_model=LessonRead)
async def get_lesson(
    course_id: int,
    lesson_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get lesson by ID."""
    await get_course_with_access(course_id, db, current_user)
    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    return lesson


@router.post("/", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: int,
    lesson_in: LessonCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Create a new lesson. Only course owner can create lessons."""
    await get_course_with_access(course_id, db, current_user, require_owner=True)
    return await lesson_crud.create(db, lesson_in, course_id)


@router.put("/{lesson_id}", response_model=LessonRead)
async def update_lesson(
    course_id: int,
    lesson_id: int,
    lesson_in: LessonUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Update lesson. Only course owner can update."""
    await get_course_with_access(course_id, db, current_user, require_owner=True)
    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    return await lesson_crud.update(db, lesson, lesson_in)


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    course_id: int,
    lesson_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Delete lesson. Only course owner can delete."""
    await get_course_with_access(course_id, db, current_user, require_owner=True)
    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    await lesson_crud.delete(db, lesson)


@router.post("/reorder", response_model=list[LessonRead])
async def reorder_lessons(
    course_id: int,
    lesson_ids: list[int],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Reorder lessons. Only course owner can reorder."""
    await get_course_with_access(course_id, db, current_user, require_owner=True)
    return await lesson_crud.reorder(db, course_id, lesson_ids)
