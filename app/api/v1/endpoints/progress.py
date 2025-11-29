from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.course import course_crud
from app.crud.enrollment import enrollment_crud
from app.crud.lesson import lesson_crud
from app.crud.lesson_progress import lesson_progress_crud
from app.db.session import get_async_session
from app.models.user import User, UserRole

router = APIRouter(prefix="/progress", tags=["Progress"])


class ProgressResponse(BaseModel):
    total: int
    completed: int
    percentage: int


class LessonProgressResponse(BaseModel):
    lesson_id: int
    completed: bool


@router.post("/courses/{course_id}/lessons/{lesson_id}/complete")
async def mark_lesson_complete(
    course_id: int,
    lesson_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Mark a lesson as completed. Students only."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут отслеживать прогресс",
        )

    # Check enrollment
    enrollment = await enrollment_crud.get_by_student_and_course(
        db, current_user.id, course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы должны быть записаны на этот курс",
        )

    # Check lesson exists
    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден",
        )

    progress = await lesson_progress_crud.mark_completed(db, current_user.id, lesson_id)

    # Update enrollment progress
    course_progress = await lesson_progress_crud.get_course_progress(
        db, current_user.id, course_id
    )
    await enrollment_crud.update_progress(db, enrollment, course_progress["percentage"])

    return {"message": "Lesson marked as complete", "lesson_id": lesson_id}


@router.delete("/courses/{course_id}/lessons/{lesson_id}/complete")
async def mark_lesson_incomplete(
    course_id: int,
    lesson_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Mark a lesson as incomplete. Students only."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут отслеживать прогресс",
        )

    enrollment = await enrollment_crud.get_by_student_and_course(
        db, current_user.id, course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы должны быть записаны на этот курс",
        )

    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден",
        )

    await lesson_progress_crud.mark_incomplete(db, current_user.id, lesson_id)

    # Update enrollment progress
    course_progress = await lesson_progress_crud.get_course_progress(
        db, current_user.id, course_id
    )
    await enrollment_crud.update_progress(db, enrollment, course_progress["percentage"])

    return {"message": "Lesson marked as incomplete", "lesson_id": lesson_id}


@router.get("/courses/{course_id}", response_model=ProgressResponse)
async def get_course_progress(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get progress for a course. Students see their own, teachers see course stats."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    if current_user.role == UserRole.STUDENT:
        enrollment = await enrollment_crud.get_by_student_and_course(
            db, current_user.id, course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы должны быть записаны на этот курс",
            )

        progress = await lesson_progress_crud.get_course_progress(
            db, current_user.id, course_id
        )
        return ProgressResponse(**progress)
    else:
        # Teachers see their own progress (for testing) or aggregate
        if course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещён",
            )

        # Return total lessons count for teacher
        progress = await lesson_progress_crud.get_course_progress(
            db, current_user.id, course_id
        )
        return ProgressResponse(**progress)


@router.get("/courses/{course_id}/lessons", response_model=list[LessonProgressResponse])
async def get_lessons_progress(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get completion status for all lessons in a course."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут просматривать свой прогресс",
        )

    enrollment = await enrollment_crud.get_by_student_and_course(
        db, current_user.id, course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы должны быть записаны на этот курс",
        )

    # Get all lessons for the course
    lessons = await lesson_crud.get_by_course(db, course_id)

    # Get progress records
    progress_records = await lesson_progress_crud.get_by_student_and_course(
        db, current_user.id, course_id
    )
    completed_lessons = {p.lesson_id for p in progress_records if p.completed}

    return [
        LessonProgressResponse(
            lesson_id=lesson.id,
            completed=lesson.id in completed_lessons,
        )
        for lesson in lessons
    ]
