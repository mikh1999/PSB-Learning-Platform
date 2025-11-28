from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


class CourseCRUD:
    async def get_by_id(self, db: AsyncSession, course_id: int) -> Course | None:
        result = await db.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Course]:
        result = await db.execute(select(Course).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_teacher(
        self, db: AsyncSession, teacher_id: int, skip: int = 0, limit: int = 100
    ) -> list[Course]:
        result = await db.execute(
            select(Course)
            .where(Course.teacher_id == teacher_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, course_in: CourseCreate, teacher_id: int
    ) -> Course:
        course = Course(
            title=course_in.title,
            description=course_in.description,
            teacher_id=teacher_id,
        )
        db.add(course)
        await db.commit()
        await db.refresh(course)
        return course

    async def update(
        self, db: AsyncSession, course: Course, course_in: CourseUpdate
    ) -> Course:
        update_data = course_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)
        await db.commit()
        await db.refresh(course)
        return course

    async def delete(self, db: AsyncSession, course: Course) -> None:
        await db.delete(course)
        await db.commit()


course_crud = CourseCRUD()
