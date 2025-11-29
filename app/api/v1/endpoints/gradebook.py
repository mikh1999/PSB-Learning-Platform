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
from app.models.grade import Grade
from app.models.lesson import Lesson
from app.models.submission import Submission
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
