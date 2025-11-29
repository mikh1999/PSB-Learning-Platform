from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_active_user
from app.crud.course import course_crud
from app.crud.enrollment import enrollment_crud
from app.db.session import get_async_session
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.grade import Grade
from app.models.lesson import Lesson
from app.models.submission import Submission, SubmissionStatus
from app.models.user import User, UserRole

router = APIRouter(prefix="/gradebook", tags=["Gradebook"])


class StudentGradeItem(BaseModel):
    assignment_id: int
    assignment_title: str
    max_score: int
    score: int | None
    status: str  # not_submitted, submitted, graded


class StudentGradeSummary(BaseModel):
    student_id: int
    student_email: str
    student_name: str
    total_score: int
    max_possible_score: int
    percentage: int
    grades: list[StudentGradeItem]


class CourseGradebook(BaseModel):
    course_id: int
    course_title: str
    students: list[StudentGradeSummary]


@router.get("/courses/{course_id}", response_model=CourseGradebook)
async def get_course_gradebook(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Get gradebook for a course. Teachers only.
    Shows all students with their grades for all assignments.
    """
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только преподаватель курса может просматривать журнал",
        )

    # Get all assignments for the course
    assignments_result = await db.execute(
        select(Assignment)
        .join(Lesson)
        .where(Lesson.course_id == course_id)
        .order_by(Lesson.order, Assignment.id)
    )
    assignments = list(assignments_result.scalars().all())

    # Get all enrolled students with their submissions and grades
    enrollments_result = await db.execute(
        select(User)
        .join(User.enrollments)
        .where(User.enrollments.any(course_id=course_id))
        .options(selectinload(User.submissions).selectinload(Submission.grade))
    )
    students = list(enrollments_result.scalars().all())

    student_summaries = []

    for student in students:
        # Build grades list for this student
        student_submissions = {s.assignment_id: s for s in student.submissions}
        grades_list = []
        total_score = 0
        max_possible = 0

        for assignment in assignments:
            max_possible += assignment.max_score
            submission = student_submissions.get(assignment.id)

            if submission:
                if submission.grade:
                    grades_list.append(
                        StudentGradeItem(
                            assignment_id=assignment.id,
                            assignment_title=assignment.title,
                            max_score=assignment.max_score,
                            score=submission.grade.score,
                            status="graded",
                        )
                    )
                    total_score += submission.grade.score
                else:
                    grades_list.append(
                        StudentGradeItem(
                            assignment_id=assignment.id,
                            assignment_title=assignment.title,
                            max_score=assignment.max_score,
                            score=None,
                            status="submitted",
                        )
                    )
            else:
                grades_list.append(
                    StudentGradeItem(
                        assignment_id=assignment.id,
                        assignment_title=assignment.title,
                        max_score=assignment.max_score,
                        score=None,
                        status="not_submitted",
                    )
                )

        percentage = int((total_score / max_possible * 100)) if max_possible > 0 else 0

        student_summaries.append(
            StudentGradeSummary(
                student_id=student.id,
                student_email=student.email,
                student_name=f"{student.first_name} {student.last_name}",
                total_score=total_score,
                max_possible_score=max_possible,
                percentage=percentage,
                grades=grades_list,
            )
        )

    return CourseGradebook(
        course_id=course_id,
        course_title=course.title,
        students=student_summaries,
    )


@router.get("/my/courses/{course_id}", response_model=StudentGradeSummary)
async def get_my_grades(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Get current student's grades for a course.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут просматривать свои оценки",
        )

    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    enrollment = await enrollment_crud.get_by_student_and_course(
        db, current_user.id, course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы должны быть записаны на этот курс",
        )

    # Get all assignments for the course
    assignments_result = await db.execute(
        select(Assignment)
        .join(Lesson)
        .where(Lesson.course_id == course_id)
        .order_by(Lesson.order, Assignment.id)
    )
    assignments = list(assignments_result.scalars().all())

    # Get student's submissions with grades
    submissions_result = await db.execute(
        select(Submission)
        .options(selectinload(Submission.grade))
        .where(Submission.student_id == current_user.id)
        .where(Submission.assignment_id.in_([a.id for a in assignments]))
    )
    submissions = {s.assignment_id: s for s in submissions_result.scalars().all()}

    grades_list = []
    total_score = 0
    max_possible = 0

    for assignment in assignments:
        max_possible += assignment.max_score
        submission = submissions.get(assignment.id)

        if submission:
            if submission.grade:
                grades_list.append(
                    StudentGradeItem(
                        assignment_id=assignment.id,
                        assignment_title=assignment.title,
                        max_score=assignment.max_score,
                        score=submission.grade.score,
                        status="graded",
                    )
                )
                total_score += submission.grade.score
            else:
                grades_list.append(
                    StudentGradeItem(
                        assignment_id=assignment.id,
                        assignment_title=assignment.title,
                        max_score=assignment.max_score,
                        score=None,
                        status="submitted",
                    )
                )
        else:
            grades_list.append(
                StudentGradeItem(
                    assignment_id=assignment.id,
                    assignment_title=assignment.title,
                    max_score=assignment.max_score,
                    score=None,
                    status="not_submitted",
                )
            )

    percentage = int((total_score / max_possible * 100)) if max_possible > 0 else 0

    return StudentGradeSummary(
        student_id=current_user.id,
        student_email=current_user.email,
        student_name=f"{current_user.first_name} {current_user.last_name}",
        total_score=total_score,
        max_possible_score=max_possible,
        percentage=percentage,
        grades=grades_list,
    )


# === Pending Submissions for Teacher ===


class PendingSubmissionItem(BaseModel):
    submission_id: int
    student_id: int
    student_name: str
    student_email: str
    assignment_id: int
    assignment_title: str
    max_score: int
    lesson_id: int
    lesson_title: str
    course_id: int
    course_title: str
    content: str | None
    file_url: str | None
    submitted_at: datetime | None
    status: str


class PendingSubmissionsResponse(BaseModel):
    items: list[PendingSubmissionItem]
    total: int


@router.get("/pending", response_model=PendingSubmissionsResponse)
async def get_pending_submissions(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    status_filter: str | None = None,
):
    """
    Get all submissions for teacher's courses.
    Teachers only.

    Args:
        status_filter: Filter by status (submitted, graded, returned, all).
                      Default: submitted (pending review).
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только преподаватели могут просматривать задания на проверку",
        )

    # Build query
    query = (
        select(Submission, Assignment, Lesson, Course, User)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(Lesson, Assignment.lesson_id == Lesson.id)
        .join(Course, Lesson.course_id == Course.id)
        .join(User, Submission.student_id == User.id)
        .where(Course.teacher_id == current_user.id)
    )

    # Apply status filter
    if status_filter == "all":
        # Show all except drafts
        query = query.where(Submission.status != SubmissionStatus.DRAFT)
    elif status_filter == "graded":
        query = query.where(Submission.status == SubmissionStatus.GRADED)
    elif status_filter == "returned":
        query = query.where(Submission.status == SubmissionStatus.RETURNED)
    else:
        # Default: show only submitted (pending review)
        query = query.where(Submission.status == SubmissionStatus.SUBMITTED)

    query = query.order_by(Submission.submitted_at.desc())

    result = await db.execute(query)

    rows = result.all()
    items = []

    for submission, assignment, lesson, course, student in rows:
        items.append(
            PendingSubmissionItem(
                submission_id=submission.id,
                student_id=student.id,
                student_name=f"{student.first_name} {student.last_name}",
                student_email=student.email,
                assignment_id=assignment.id,
                assignment_title=assignment.title,
                max_score=assignment.max_score,
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                course_id=course.id,
                course_title=course.title,
                content=submission.content,
                file_url=submission.file_url,
                submitted_at=submission.submitted_at,
                status=submission.status.value,
            )
        )

    return PendingSubmissionsResponse(items=items, total=len(items))
