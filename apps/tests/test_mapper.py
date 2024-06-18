from api.models import Program, ProgramsResponse
from mq.dto import MessageProgram


def test_programs_response_json_to_object():
    """check api response convertion"""

    with open("tests/resources/programs.json", "r", encoding="utf-8") as f:
        response = ProgramsResponse.model_validate_json(f.read())
        assert response is not None


def test_programs_to_dto():
    """check response to dto conversion"""

    program = Program(title="title", slug="slug", reports_count=123)
    message = MessageProgram.model_validate(program.model_dump())

    assert program.slug == message.slug
    assert program.reports_count == message.reports_count
