from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate


class LessonCRUD:
    async def get_by_id(self, db: AsyncSession, lesson_id: int) -> Lesson | None:
        result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        return result.scalar_one_or_none()

    async def get_by_course(
        self, db: AsyncSession, course_id: int, skip: int = 0, limit: int = 100
    ) -> list[Lesson]:
        result = await db.execute(
            select(Lesson)
            .where(Lesson.course_id == course_id)
            .order_by(Lesson.order)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_course(self, db: AsyncSession, course_id: int) -> int:
        result = await db.execute(
            select(func.count(Lesson.id)).where(Lesson.course_id == course_id)
        )
        return result.scalar() or 0

    async def create(
        self, db: AsyncSession, lesson_in: LessonCreate, course_id: int
    ) -> Lesson:
        lesson = Lesson(
            course_id=course_id,
            title=lesson_in.title,
            content=lesson_in.content,
            order=lesson_in.order,
            type=lesson_in.type,
            file_url=lesson_in.file_url,
        )
        db.add(lesson)
        await db.commit()
        await db.refresh(lesson)
        return lesson

    async def update(
        self, db: AsyncSession, lesson: Lesson, lesson_in: LessonUpdate
    ) -> Lesson:
        update_data = lesson_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lesson, field, value)
        await db.commit()
        await db.refresh(lesson)
        return lesson

    async def delete(self, db: AsyncSession, lesson: Lesson) -> None:
        await db.delete(lesson)
        await db.commit()

    async def reorder(
        self, db: AsyncSession, course_id: int, lesson_ids: list[int]
    ) -> list[Lesson]:
        """Reorder lessons by updating their order field."""
        lessons = []
        for order, lesson_id in enumerate(lesson_ids):
            result = await db.execute(
                select(Lesson).where(
                    Lesson.id == lesson_id, Lesson.course_id == course_id
                )
            )
            lesson = result.scalar_one_or_none()
            if lesson:
                lesson.order = order
                lessons.append(lesson)
        await db.commit()
        return lessons


lesson_crud = LessonCRUD()
