from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrollment import Enrollment


class EnrollmentCRUD:
    async def get_by_id(self, db: AsyncSession, enrollment_id: int) -> Enrollment | None:
        result = await db.execute(
            select(Enrollment).where(Enrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student_and_course(
        self, db: AsyncSession, student_id: int, course_id: int
    ) -> Enrollment | None:
        result = await db.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_student(
        self, db: AsyncSession, student_id: int, skip: int = 0, limit: int = 100
    ) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment)
            .where(Enrollment.student_id == student_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_course(
        self, db: AsyncSession, course_id: int, skip: int = 0, limit: int = 100
    ) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment)
            .where(Enrollment.course_id == course_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_student(self, db: AsyncSession, student_id: int) -> int:
        result = await db.execute(
            select(func.count(Enrollment.id)).where(Enrollment.student_id == student_id)
        )
        return result.scalar() or 0

    async def count_by_course(self, db: AsyncSession, course_id: int) -> int:
        result = await db.execute(
            select(func.count(Enrollment.id)).where(Enrollment.course_id == course_id)
        )
        return result.scalar() or 0

    async def create(
        self, db: AsyncSession, student_id: int, course_id: int
    ) -> Enrollment:
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
        )
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    async def update_progress(
        self, db: AsyncSession, enrollment: Enrollment, progress: int
    ) -> Enrollment:
        enrollment.progress = progress
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    async def delete(self, db: AsyncSession, enrollment: Enrollment) -> None:
        await db.delete(enrollment)
        await db.commit()


enrollment_crud = EnrollmentCRUD()
