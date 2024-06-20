from uplink import Consumer, get, Query, returns, headers
from api.models import ProgramsResponse


@headers({"Accept": "application/json"})
class YWHClient(Consumer):
    """A Python Client for the YWH API."""

    @returns.json
    @get("programs")
    def get_programs(
        self, page: Query("page"), results_per_page: Query("resultsPerPage")  # type: ignore
    ) -> ProgramsResponse:
        pass
