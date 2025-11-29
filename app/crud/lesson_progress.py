from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson_progress import LessonProgress


class LessonProgressCRUD:
    async def get_by_student_and_lesson(
        self, db: AsyncSession, student_id: int, lesson_id: int
    ) -> LessonProgress | None:
        result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.student_id == student_id,
                LessonProgress.lesson_id == lesson_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_student_and_course(
        self, db: AsyncSession, student_id: int, course_id: int
    ) -> list[LessonProgress]:
        """Get all lesson progress records for a student in a course."""
        from app.models.lesson import Lesson

        result = await db.execute(
            select(LessonProgress)
            .join(Lesson)
            .where(
                LessonProgress.student_id == student_id,
                Lesson.course_id == course_id,
            )
        )
        return list(result.scalars().all())

    async def mark_completed(
        self, db: AsyncSession, student_id: int, lesson_id: int
    ) -> LessonProgress:
        """Mark a lesson as completed for a student."""
        progress = await self.get_by_student_and_lesson(db, student_id, lesson_id)

        if progress:
            if not progress.completed:
                progress.completed = True
                progress.completed_at = datetime.utcnow()
                await db.commit()
                await db.refresh(progress)
        else:
            progress = LessonProgress(
                student_id=student_id,
                lesson_id=lesson_id,
                completed=True,
                completed_at=datetime.utcnow(),
            )
            db.add(progress)
            await db.commit()
            await db.refresh(progress)

        return progress

    async def mark_incomplete(
        self, db: AsyncSession, student_id: int, lesson_id: int
    ) -> LessonProgress | None:
        """Mark a lesson as incomplete for a student."""
        progress = await self.get_by_student_and_lesson(db, student_id, lesson_id)

        if progress:
            progress.completed = False
            progress.completed_at = None
            await db.commit()
            await db.refresh(progress)

        return progress

    async def get_course_progress(
        self, db: AsyncSession, student_id: int, course_id: int
    ) -> dict:
        """Calculate course completion percentage for a student."""
        from app.models.lesson import Lesson

        # Count total lessons in course
        total_result = await db.execute(
            select(func.count(Lesson.id)).where(Lesson.course_id == course_id)
        )
        total_lessons = total_result.scalar() or 0

        if total_lessons == 0:
            return {"total": 0, "completed": 0, "percentage": 0}

        # Count completed lessons
        completed_result = await db.execute(
            select(func.count(LessonProgress.id))
            .join(Lesson)
            .where(
                LessonProgress.student_id == student_id,
                Lesson.course_id == course_id,
                LessonProgress.completed == True,
            )
        )
        completed_lessons = completed_result.scalar() or 0

        percentage = int((completed_lessons / total_lessons) * 100)

        return {
            "total": total_lessons,
            "completed": completed_lessons,
            "percentage": percentage,
        }


lesson_progress_crud = LessonProgressCRUD()
