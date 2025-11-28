from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EnrollmentRead(BaseModel):
    id: int
    student_id: int
    course_id: int
    progress: int = Field(..., ge=0, le=100)
    enrolled_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnrollmentWithCourse(EnrollmentRead):
    """Enrollment with course title for student's course list."""

    course_title: str


class EnrollmentWithStudent(EnrollmentRead):
    """Enrollment with student info for teacher's student list."""

    student_email: str
    student_first_name: str
    student_last_name: str
