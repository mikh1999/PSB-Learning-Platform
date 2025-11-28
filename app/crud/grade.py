from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grade import Grade
from app.models.submission import Submission, SubmissionStatus
from app.schemas.grade import GradeCreate, GradeUpdate


class GradeCRUD:
    async def get_by_id(self, db: AsyncSession, grade_id: int) -> Grade | None:
        result = await db.execute(select(Grade).where(Grade.id == grade_id))
        return result.scalar_one_or_none()

    async def get_by_submission(
        self, db: AsyncSession, submission_id: int
    ) -> Grade | None:
        result = await db.execute(
            select(Grade).where(Grade.submission_id == submission_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        grade_in: GradeCreate,
        submission: Submission,
        grader_id: int,
    ) -> Grade:
        grade = Grade(
            submission_id=submission.id,
            score=grade_in.score,
            comment=grade_in.comment,
            graded_by=grader_id,
            graded_at=datetime.utcnow(),
        )
        db.add(grade)
        submission.status = SubmissionStatus.GRADED
        await db.commit()
        await db.refresh(grade)
        return grade

    async def update(
        self, db: AsyncSession, grade: Grade, grade_in: GradeUpdate
    ) -> Grade:
        update_data = grade_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(grade, field, value)
        grade.graded_at = datetime.utcnow()
        await db.commit()
        await db.refresh(grade)
        return grade

    async def delete(self, db: AsyncSession, grade: Grade, submission: Submission) -> None:
        submission.status = SubmissionStatus.SUBMITTED
        await db.delete(grade)
        await db.commit()


grade_crud = GradeCRUD()
