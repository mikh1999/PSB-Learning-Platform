from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.crud.assignment import assignment_crud
from app.crud.course import course_crud
from app.crud.lesson import lesson_crud
from app.crud.submission import submission_crud
from app.db.session import get_async_session
from app.models.submission import SubmissionStatus
from app.models.user import User, UserRole
from app.schemas.submission import SubmissionCreate, SubmissionRead, SubmissionUpdate

router = APIRouter(
    prefix="/courses/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}/submissions",
    tags=["Submissions"],
)


async def get_assignment_with_access(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    db: AsyncSession,
    current_user: User,
):
    """Check if course, lesson, and assignment exist and user has access."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
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

    return course, lesson, assignment


@router.get("/", response_model=list[SubmissionRead])
async def get_submissions(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    """Get all submissions for an assignment. Teachers see all, students see only their own."""
    course, lesson, assignment = await get_assignment_with_access(
        course_id, lesson_id, assignment_id, db, current_user
    )

    if current_user.role == UserRole.TEACHER and course.teacher_id == current_user.id:
        return await submission_crud.get_by_assignment(db, assignment_id, skip, limit)
    else:
        submission = await submission_crud.get_by_assignment_and_student(
            db, assignment_id, current_user.id
        )
        return [submission] if submission else []


@router.get("/my", response_model=SubmissionRead | None)
async def get_my_submission(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get current student's submission for an assignment."""
    await get_assignment_with_access(course_id, lesson_id, assignment_id, db, current_user)
    return await submission_crud.get_by_assignment_and_student(
        db, assignment_id, current_user.id
    )


@router.get("/{submission_id}", response_model=SubmissionRead)
async def get_submission(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get submission by ID. Teachers can see any, students can see only their own."""
    course, lesson, assignment = await get_assignment_with_access(
        course_id, lesson_id, assignment_id, db, current_user
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

    return submission


@router.post("/", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
async def create_submission(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_in: SubmissionCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Submit work for an assignment. Students only."""
    await get_assignment_with_access(course_id, lesson_id, assignment_id, db, current_user)

    if current_user.role == UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit work",
        )

    existing = await submission_crud.get_by_assignment_and_student(
        db, assignment_id, current_user.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a submission for this assignment. Use PUT to update.",
        )

    return await submission_crud.create(db, submission_in, assignment_id, current_user.id)


@router.put("/{submission_id}", response_model=SubmissionRead)
async def update_submission(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    submission_in: SubmissionUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Update submission. Only the student who submitted can update, and only if not graded."""
    await get_assignment_with_access(course_id, lesson_id, assignment_id, db, current_user)

    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own submission",
        )

    if submission.status == SubmissionStatus.GRADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a graded submission",
        )

    return await submission_crud.update(db, submission, submission_in)


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Delete submission. Only the student who submitted can delete, and only if not graded."""
    await get_assignment_with_access(course_id, lesson_id, assignment_id, db, current_user)

    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own submission",
        )

    if submission.status == SubmissionStatus.GRADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a graded submission",
        )

    await submission_crud.delete(db, submission)
