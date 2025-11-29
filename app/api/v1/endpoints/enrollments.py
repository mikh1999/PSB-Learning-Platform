from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.api.deps import get_current_active_user
from app.crud.course import course_crud
from app.crud.enrollment import enrollment_crud
from app.db.session import get_async_session
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.schemas.enrollment import EnrollmentRead, EnrollmentWithCourse, EnrollmentWithStudent

router = APIRouter(tags=["Enrollments"])


@router.post(
    "/courses/{course_id}/enroll",
    response_model=EnrollmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def enroll_in_course(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Enroll current user (student) in a course."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут записываться на курсы",
        )

    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    existing = await enrollment_crud.get_by_student_and_course(
        db, current_user.id, course_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже записаны на этот курс",
        )

    return await enrollment_crud.create(db, current_user.id, course_id)


@router.delete("/courses/{course_id}/enroll", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_from_course(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Unenroll current user (student) from a course."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут отписываться от курсов",
        )

    enrollment = await enrollment_crud.get_by_student_and_course(
        db, current_user.id, course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы не записаны на этот курс",
        )

    await enrollment_crud.delete(db, enrollment)


@router.get("/courses/{course_id}/students", response_model=list[EnrollmentWithStudent])
async def get_course_students(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    """Get list of students enrolled in a course. Only course teacher can access."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только преподаватель курса может просматривать записанных студентов",
        )

    result = await db.execute(
        select(Enrollment)
        .options(selectinload(Enrollment.student))
        .where(Enrollment.course_id == course_id)
        .offset(skip)
        .limit(limit)
    )
    enrollments = result.scalars().all()

    return [
        EnrollmentWithStudent(
            id=e.id,
            student_id=e.student_id,
            course_id=e.course_id,
            progress=e.progress,
            enrolled_at=e.enrolled_at,
            student_email=e.student.email,
            student_first_name=e.student.first_name,
            student_last_name=e.student.last_name,
        )
        for e in enrollments
    ]


@router.get("/my/courses", response_model=list[EnrollmentWithCourse])
async def get_my_courses(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    """Get list of courses the current student is enrolled in."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут быть записаны на курсы",
        )

    result = await db.execute(
        select(Enrollment)
        .options(selectinload(Enrollment.course))
        .where(Enrollment.student_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    enrollments = result.scalars().all()

    return [
        EnrollmentWithCourse(
            id=e.id,
            student_id=e.student_id,
            course_id=e.course_id,
            progress=e.progress,
            enrolled_at=e.enrolled_at,
            course_title=e.course.title,
        )
        for e in enrollments
    ]


@router.get("/courses/{course_id}/enrollment", response_model=EnrollmentRead | None)
async def get_my_enrollment(
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Check if current user is enrolled in a course."""
    return await enrollment_crud.get_by_student_and_course(
        db, current_user.id, course_id
    )
