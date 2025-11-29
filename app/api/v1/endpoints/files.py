import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.storage import storage
from app.crud.course import course_crud
from app.crud.lesson import lesson_crud
from app.crud.submission import submission_crud
from app.db.session import get_async_session
from app.models.user import User, UserRole

router = APIRouter(prefix="/files", tags=["Files"])

# Chunk size for video streaming (2 MB)
STREAM_CHUNK_SIZE = 2 * 1024 * 1024


# ============== Lesson Files ==============


@router.post("/lessons/{course_id}/{lesson_id}")
async def upload_lesson_file(
    course_id: int,
    lesson_id: int,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Upload file for a lesson. Only course owner can upload."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только владелец курса может загружать файлы уроков",
        )

    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден",
        )

    # Delete old file if exists
    if lesson.content and lesson.content.startswith("lessons/"):
        await storage.delete(lesson.content)

    # Upload new file
    file_path = await storage.upload(file, "lessons", lesson_id)

    # Update lesson content with file path
    lesson.content = file_path
    lesson.content_type = "file"
    await db.commit()

    return {
        "message": "File uploaded successfully",
        "file_path": file_path,
        "download_url": storage.get_file_url(file_path),
    }


@router.get("/lessons/{course_id}/{lesson_id}")
async def download_lesson_file(
    course_id: int,
    lesson_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Download lesson file. Enrolled students and course owner can download."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден",
        )

    if not lesson.content or not lesson.content.startswith("lessons/"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="К этому уроку не прикреплён файл",
        )

    filename = storage.get_filename(lesson.content)

    return StreamingResponse(
        storage.download(lesson.content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/lessons/{course_id}/{lesson_id}")
async def delete_lesson_file(
    course_id: int,
    lesson_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Delete lesson file. Only course owner can delete."""
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только владелец курса может удалять файлы уроков",
        )

    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден",
        )

    if lesson.content and lesson.content.startswith("lessons/"):
        await storage.delete(lesson.content)
        lesson.content = None
        await db.commit()

    return {"message": "File deleted successfully"}


# ============== Video Streaming ==============


@router.get("/stream/lessons/{course_id}/{lesson_id}")
async def stream_lesson_video(
    course_id: int,
    lesson_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Stream video file with Range Requests support for seeking.

    Supports HTTP Range Requests for video seeking/scrubbing.
    Returns 206 Partial Content for range requests, 200 OK for full file.
    """
    # Check course exists
    course = await course_crud.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    # Check lesson exists
    lesson = await lesson_crud.get_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден",
        )

    # Check file exists
    if not lesson.content or not lesson.content.startswith("lessons/"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="К этому уроку не прикреплён файл",
        )

    # Check it's a video file
    if not storage.is_video_file(lesson.content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот эндпоинт поддерживает только видеофайлы. Используйте /files/lessons/ для других типов файлов.",
        )

    # Get file info
    file_path = lesson.content
    file_size = storage.get_file_size(file_path)
    content_type = storage.get_content_type(file_path)

    # Parse Range header
    range_header = request.headers.get("range")

    if range_header:
        # Parse "bytes=start-end" format
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if not range_match:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="Неверный формат заголовка Range",
            )

        start = int(range_match.group(1))
        end_str = range_match.group(2)

        if end_str:
            end = int(end_str)
        else:
            # If end not specified, return chunk of STREAM_CHUNK_SIZE
            end = min(start + STREAM_CHUNK_SIZE - 1, file_size - 1)

        # Validate range
        if start >= file_size or end >= file_size or start > end:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail=f"Диапазон недоступен. Размер файла: {file_size}",
            )

        # Read the requested range
        content = await storage.read_range(file_path, start, end)
        content_length = end - start + 1

        return Response(
            content=content,
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": content_type,
            },
        )
    else:
        # No Range header - return full file as streaming response
        return StreamingResponse(
            storage.download(file_path),
            media_type=content_type,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
            },
        )


# ============== Submission Files ==============


@router.post("/submissions/{submission_id}")
async def upload_submission_file(
    submission_id: int,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Upload file for a submission. Only submission owner can upload."""
    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ответ не найден",
        )

    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете загружать файлы только к своим ответам",
        )

    # Delete old file if exists
    if submission.file_url and submission.file_url.startswith("submissions/"):
        await storage.delete(submission.file_url)

    # Upload new file
    file_path = await storage.upload(file, "submissions", submission_id)

    # Update submission file_url
    submission.file_url = file_path
    await db.commit()

    return {
        "message": "File uploaded successfully",
        "file_path": file_path,
        "download_url": storage.get_file_url(file_path),
    }


@router.get("/submissions/{submission_id}")
async def download_submission_file(
    submission_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Download submission file. Owner and course teacher can download."""
    submission = await submission_crud.get_by_id(db, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ответ не найден",
        )

    # Check access: owner or teacher of the course
    is_owner = submission.student_id == current_user.id

    # Get assignment -> lesson -> course to check if user is teacher
    from app.crud.assignment import assignment_crud

    assignment = await assignment_crud.get_by_id(db, submission.assignment_id)
    lesson = await lesson_crud.get_by_id(db, assignment.lesson_id)
    course = await course_crud.get_by_id(db, lesson.course_id)
    is_teacher = course.teacher_id == current_user.id

    if not is_owner and not is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён",
        )

    if not submission.file_url or not submission.file_url.startswith("submissions/"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="К этому ответу не прикреплён файл",
        )

    filename = storage.get_filename(submission.file_url)

    return StreamingResponse(
        storage.download(submission.file_url),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
