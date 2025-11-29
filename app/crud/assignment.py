from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate


class AssignmentCRUD:
    async def get_by_id(self, db: AsyncSession, assignment_id: int) -> Assignment | None:
        result = await db.execute(
            select(Assignment).where(Assignment.id == assignment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_lesson(
        self, db: AsyncSession, lesson_id: int, skip: int = 0, limit: int = 100
    ) -> list[Assignment]:
        result = await db.execute(
            select(Assignment)
            .where(Assignment.lesson_id == lesson_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_lesson(self, db: AsyncSession, lesson_id: int) -> int:
        result = await db.execute(
            select(func.count(Assignment.id)).where(Assignment.lesson_id == lesson_id)
        )
        return result.scalar() or 0

    async def create(
        self, db: AsyncSession, assignment_in: AssignmentCreate, lesson_id: int
    ) -> Assignment:
        assignment = Assignment(
            lesson_id=lesson_id,
            title=assignment_in.title,
            description=assignment_in.description,
            deadline=assignment_in.deadline,
            max_score=assignment_in.max_score,
        )
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)
        return assignment

    async def update(
        self, db: AsyncSession, assignment: Assignment, assignment_in: AssignmentUpdate
    ) -> Assignment:
        update_data = assignment_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assignment, field, value)
        await db.commit()
        await db.refresh(assignment)
        return assignment

    async def delete(self, db: AsyncSession, assignment: Assignment) -> None:
        await db.delete(assignment)
        await db.commit()


assignment_crud = AssignmentCRUD()
