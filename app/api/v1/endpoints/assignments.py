from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.assignment import assignment_crud
from app.crud.course import course_crud
from app.crud.lesson import lesson_crud
from app.db.session import get_async_session
from app.models.user import User, UserRole
from app.schemas.assignment import AssignmentCreate, AssignmentRead, AssignmentUpdate

router = APIRouter(
    prefix="/courses/{course_id}/lessons/{lesson_id}/assignments",
    tags=["Assignments"],
)


async def get_lesson_with_access(
    course_id: int,
    lesson_id: int,
    db: AsyncSession,
    current_user: User,
    require_owner: bool = False,
):
    """Check if course and lesson exist and user has access."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    if require_owner and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только владелец курса может выполнить это действие",
        )

    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён",
        )

    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден",
        )

    return course, lesson


@router.get("/", response_model=list[AssignmentRead])
async def get_assignments(
    course_id: int,
    lesson_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    """Get all assignments for a lesson."""
    await get_lesson_with_access(course_id, lesson_id, db, current_user)
    return await assignment_crud.get_by_lesson(db, lesson_id, skip, limit)


@router.get("/{assignment_id}", response_model=AssignmentRead)
async def get_assignment(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get assignment by ID."""
    await get_lesson_with_access(course_id, lesson_id, db, current_user)
    assignment = await assignment_crud.get_by_id(db, assignment_id)
    if not assignment or assignment.lesson_id != lesson_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено",
        )
    return assignment


@router.post("/", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    course_id: int,
    lesson_id: int,
    assignment_in: AssignmentCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Create a new assignment. Only course owner can create."""
    await get_lesson_with_access(course_id, lesson_id, db, current_user, require_owner=True)
    return await assignment_crud.create(db, assignment_in, lesson_id)


@router.put("/{assignment_id}", response_model=AssignmentRead)
async def update_assignment(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    assignment_in: AssignmentUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Update assignment. Only course owner can update."""
    await get_lesson_with_access(course_id, lesson_id, db, current_user, require_owner=True)
    assignment = await assignment_crud.get_by_id(db, assignment_id)
    if not assignment or assignment.lesson_id != lesson_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено",
        )
    return await assignment_crud.update(db, assignment, assignment_in)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Delete assignment. Only course owner can delete."""
    await get_lesson_with_access(course_id, lesson_id, db, current_user, require_owner=True)
    assignment = await assignment_crud.get_by_id(db, assignment_id)
    if not assignment or assignment.lesson_id != lesson_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено",
        )
    await assignment_crud.delete(db, assignment)
