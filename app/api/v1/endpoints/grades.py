from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.assignment import assignment_crud
from app.crud.course import course_crud
from app.crud.grade import grade_crud
from app.crud.lesson import lesson_crud
from app.crud.submission import submission_crud
from app.db.session import get_async_session
from app.models.user import User, UserRole
from app.schemas.grade import GradeCreate, GradeRead, GradeUpdate

router = APIRouter(
    prefix="/courses/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}/submissions/{submission_id}/grade",
    tags=["Grades"],
)


async def get_submission_with_teacher_access(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    db: AsyncSession,
    current_user: User,
):
    """Check if course, lesson, assignment, submission exist and user is teacher."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only course teacher can grade submissions",
        )

    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    assignment = await assignment_crud.get_by_id(db, assignment_id)
    if not assignment or assignment.lesson_id != lesson_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    return course, lesson, assignment, submission


@router.get("/", response_model=GradeRead | None)
async def get_grade(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get grade for a submission. Teacher can see any, student can see own."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    assignment = await assignment_crud.get_by_id(db, assignment_id)
    if not assignment or assignment.lesson_id != lesson_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    is_owner = submission.student_id == current_user.id
    is_course_teacher = (
        current_user.role == UserRole.TEACHER and course.teacher_id == current_user.id
    )

    if not is_owner and not is_course_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return await grade_crud.get_by_submission(db, submission_id)


@router.post("/", response_model=GradeRead, status_code=status.HTTP_201_CREATED)
async def create_grade(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    grade_in: GradeCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Grade a submission. Only course teacher can grade."""
    course, lesson, assignment, submission = await get_submission_with_teacher_access(
        course_id, lesson_id, assignment_id, submission_id, db, current_user
    )

    existing = await grade_crud.get_by_submission(db, submission_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission already graded. Use PUT to update.",
        )

    if grade_in.score > assignment.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Score cannot exceed max score ({assignment.max_score})",
        )

    return await grade_crud.create(db, grade_in, submission, current_user.id)


@router.put("/", response_model=GradeRead)
async def update_grade(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    grade_in: GradeUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Update grade. Only course teacher can update."""
    course, lesson, assignment, submission = await get_submission_with_teacher_access(
        course_id, lesson_id, assignment_id, submission_id, db, current_user
    )

    grade = await grade_crud.get_by_submission(db, submission_id)
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found. Use POST to create.",
        )

    if grade_in.score is not None and grade_in.score > assignment.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Score cannot exceed max score ({assignment.max_score})",
        )

    return await grade_crud.update(db, grade, grade_in)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grade(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Delete grade. Only course teacher can delete."""
    course, lesson, assignment, submission = await get_submission_with_teacher_access(
        course_id, lesson_id, assignment_id, submission_id, db, current_user
    )

    grade = await grade_crud.get_by_submission(db, submission_id)
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found",
        )

    await grade_crud.delete(db, grade, submission)
