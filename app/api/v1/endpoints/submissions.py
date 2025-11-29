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
from app.schemas.common import PaginatedResponse
from app.crud.submission_comment import submission_comment_crud
from app.schemas.submission import SubmissionCreate, SubmissionRead, SubmissionUpdate
from app.schemas.submission_comment import SubmissionCommentCreate, SubmissionCommentRead

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
            detail="Курс не найден",
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

    assignment = await assignment_crud.get_by_id(db, assignment_id)
    if not assignment or assignment.lesson_id != lesson_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено",
        )

    return course, lesson, assignment


@router.get("/", response_model=PaginatedResponse[SubmissionRead])
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
        items = await submission_crud.get_by_assignment(db, assignment_id, skip, limit)
        total = await submission_crud.count_by_assignment(db, assignment_id)
    else:
        submission = await submission_crud.get_by_assignment_and_student(
            db, assignment_id, current_user.id
        )
        items = [submission] if submission else []
        total = 1 if submission else 0
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


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
            detail="Ответ не найден",
        )

    is_owner = submission.student_id == current_user.id
    is_course_teacher = (
        current_user.role == UserRole.TEACHER and course.teacher_id == current_user.id
    )

    if not is_owner and not is_course_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён",
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
            detail="Только студенты могут сдавать работы",
        )

    existing = await submission_crud.get_by_assignment_and_student(
        db, assignment_id, current_user.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас уже есть ответ на это задание. Используйте PUT для обновления.",
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
            detail="Ответ не найден",
        )

    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете обновлять только свои ответы",
        )

    if submission.status == SubmissionStatus.GRADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя обновить оценённый ответ",
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
            detail="Ответ не найден",
        )

    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете удалять только свои ответы",
        )

    if submission.status == SubmissionStatus.GRADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить оценённый ответ",
        )

    await submission_crud.delete(db, submission)


@router.post("/{submission_id}/return", response_model=SubmissionRead)
async def return_submission(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Вернуть работу на доработку.
    Только преподаватель курса может вернуть работу.
    """
    course, lesson, assignment = await get_assignment_with_access(
        course_id, lesson_id, assignment_id, db, current_user
    )

    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только преподаватель курса может вернуть работу на доработку",
        )

    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ответ не найден",
        )

    if submission.status == SubmissionStatus.RETURNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Работа уже возвращена на доработку",
        )

    if submission.status == SubmissionStatus.GRADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя вернуть уже оценённую работу. Сначала удалите оценку.",
        )

    return await submission_crud.return_for_revision(db, submission)


# ===== Комментарии к работе (чат) =====


@router.get("/{submission_id}/comments", response_model=list[SubmissionCommentRead])
async def get_submission_comments(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Получить все комментарии к работе.
    Доступно студенту-автору и преподавателю курса.
    """
    course, lesson, assignment = await get_assignment_with_access(
        course_id, lesson_id, assignment_id, db, current_user
    )

    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ответ не найден",
        )

    is_owner = submission.student_id == current_user.id
    is_course_teacher = current_user.role == UserRole.TEACHER and course.teacher_id == current_user.id

    if not is_owner and not is_course_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён",
        )

    comments = await submission_comment_crud.get_by_submission(db, submission_id)

    # Добавляем информацию об авторе
    result = []
    for comment in comments:
        await db.refresh(comment, ["user"])
        result.append(SubmissionCommentRead(
            id=comment.id,
            submission_id=comment.submission_id,
            user_id=comment.user_id,
            content=comment.content,
            created_at=comment.created_at,
            author_name=f"{comment.user.first_name} {comment.user.last_name}",
            author_role=comment.user.role.value,
        ))
    return result


@router.post("/{submission_id}/comments", response_model=SubmissionCommentRead, status_code=status.HTTP_201_CREATED)
async def create_submission_comment(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    comment_in: SubmissionCommentCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Добавить комментарий к работе.
    Доступно студенту-автору и преподавателю курса.
    """
    course, lesson, assignment = await get_assignment_with_access(
        course_id, lesson_id, assignment_id, db, current_user
    )

    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ответ не найден",
        )

    is_owner = submission.student_id == current_user.id
    is_course_teacher = current_user.role == UserRole.TEACHER and course.teacher_id == current_user.id

    if not is_owner and not is_course_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён",
        )

    comment = await submission_comment_crud.create(db, comment_in, submission_id, current_user.id)

    return SubmissionCommentRead(
        id=comment.id,
        submission_id=comment.submission_id,
        user_id=comment.user_id,
        content=comment.content,
        created_at=comment.created_at,
        author_name=f"{current_user.first_name} {current_user.last_name}",
        author_role=current_user.role.value,
    )
