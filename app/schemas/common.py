from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Пагинированный ответ со списком элементов и общим количеством."""

    items: list[T]
    total: int
    skip: int
    limit: int
