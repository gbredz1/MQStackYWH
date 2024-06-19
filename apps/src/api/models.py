from typing import List
from pydantic import BaseModel


class Program(BaseModel):
    title: str
    slug: str
    reports_count: int


class Pagination(BaseModel):
    page: int
    nb_pages: int
    results_per_page: int
    nb_results: int


class ProgramsResponse(BaseModel):
    pagination: Pagination
    items: List[Program]
