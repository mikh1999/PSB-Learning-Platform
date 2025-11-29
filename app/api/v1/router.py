from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    courses,
    lessons,
    assignments,
    submissions,
    grades,
    enrollments,
    files,
    progress,
    gradebook,
)

api_router = APIRouter()
api_router.include_router(admin.router)
api_router.include_router(auth.router)
api_router.include_router(courses.router)
api_router.include_router(lessons.router)
api_router.include_router(assignments.router)
api_router.include_router(submissions.router)
api_router.include_router(grades.router)
api_router.include_router(enrollments.router)
api_router.include_router(files.router)
api_router.include_router(progress.router)
api_router.include_router(gradebook.router)
