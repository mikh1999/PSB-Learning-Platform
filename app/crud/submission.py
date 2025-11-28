from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission import Submission, SubmissionStatus
from app.schemas.submission import SubmissionCreate, SubmissionUpdate


class SubmissionCRUD:
    async def get_by_id(self, db: AsyncSession, submission_id: int) -> Submission | None:
        result = await db.execute(
            select(Submission).where(Submission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_assignment(
        self, db: AsyncSession, assignment_id: int, skip: int = 0, limit: int = 100
    ) -> list[Submission]:
        result = await db.execute(
            select(Submission)
            .where(Submission.assignment_id == assignment_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_student(
        self, db: AsyncSession, student_id: int, skip: int = 0, limit: int = 100
    ) -> list[Submission]:
        result = await db.execute(
            select(Submission)
            .where(Submission.student_id == student_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_assignment_and_student(
        self, db: AsyncSession, assignment_id: int, student_id: int
    ) -> Submission | None:
        result = await db.execute(
            select(Submission).where(
                Submission.assignment_id == assignment_id,
                Submission.student_id == student_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        submission_in: SubmissionCreate,
        assignment_id: int,
        student_id: int,
    ) -> Submission:
        submission = Submission(
            assignment_id=assignment_id,
            student_id=student_id,
            content=submission_in.content,
            file_url=submission_in.file_url,
            status=SubmissionStatus.SUBMITTED,
            submitted_at=datetime.utcnow(),
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        return submission

    async def update(
        self, db: AsyncSession, submission: Submission, submission_in: SubmissionUpdate
    ) -> Submission:
        update_data = submission_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(submission, field, value)
        submission.submitted_at = datetime.utcnow()
        await db.commit()
        await db.refresh(submission)
        return submission

    async def delete(self, db: AsyncSession, submission: Submission) -> None:
        await db.delete(submission)
        await db.commit()

    async def update_status(
        self, db: AsyncSession, submission: Submission, status: SubmissionStatus
    ) -> Submission:
        submission.status = status
        await db.commit()
        await db.refresh(submission)
        return submission


submission_crud = SubmissionCRUD()
