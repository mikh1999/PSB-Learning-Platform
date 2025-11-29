from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission_comment import SubmissionComment
from app.schemas.submission_comment import SubmissionCommentCreate


class SubmissionCommentCRUD:
    async def get_by_id(self, db: AsyncSession, comment_id: int) -> SubmissionComment | None:
        result = await db.execute(
            select(SubmissionComment).where(SubmissionComment.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_submission(
        self, db: AsyncSession, submission_id: int, skip: int = 0, limit: int = 100
    ) -> list[SubmissionComment]:
        result = await db.execute(
            select(SubmissionComment)
            .where(SubmissionComment.submission_id == submission_id)
            .order_by(SubmissionComment.created_at)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_submission(self, db: AsyncSession, submission_id: int) -> int:
        result = await db.execute(
            select(func.count(SubmissionComment.id))
            .where(SubmissionComment.submission_id == submission_id)
        )
        return result.scalar() or 0

    async def create(
        self,
        db: AsyncSession,
        comment_in: SubmissionCommentCreate,
        submission_id: int,
        user_id: int,
    ) -> SubmissionComment:
        comment = SubmissionComment(
            submission_id=submission_id,
            user_id=user_id,
            content=comment_in.content,
            created_at=datetime.utcnow(),
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    async def delete(self, db: AsyncSession, comment: SubmissionComment) -> None:
        await db.delete(comment)
        await db.commit()


submission_comment_crud = SubmissionCommentCRUD()
