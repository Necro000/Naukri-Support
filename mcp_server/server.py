"""FastMCP HTTP server exposing check_job_application_status at /mcp (Task 14)."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from agent.tools import check_job_application_status as _lookup_status
from config import MCP_HOST, MCP_PATH, MCP_PORT, MCP_URL

mcp = FastMCP("naukri-status")


@mcp.tool
def check_job_application_status(record_id: str) -> dict[str, Any]:
    """Look up a Naukri.com job application's status, expected salary, and escalation score.

    Queries the validated Naukri.com job-application dataset by ``record_id`` (e.g. ``APP-0002``)
    and returns the candidate's current application status, role category, expected annual
    salary in INR, age in days, priority-review flag, computed escalation score in [0, 1],
    and whether priority escalation is recommended.

    Args:
        record_id: Job application identifier formatted as ``APP-XXXX`` (e.g. ``APP-0002``).

    Returns:
        Standardized dictionary containing ``record_id``, ``category``, ``status``,
        ``expected_salary_inr``, ``days_since_created``, ``flagged_priority_review``,
        ``escalation_score``, ``escalation_threshold``, and ``escalate_recommended``.
    """
    print(f"[MCP Server] Executing check_job_application_status(record_id={record_id!r})", flush=True)
    return _lookup_status(record_id)


def main() -> None:
    """Start the FastMCP server over streamable HTTP transport at http://127.0.0.1:8000/mcp."""
    print(f"=== Starting Naukri.com FastMCP Server at {MCP_URL} ===", flush=True)
    mcp.run(transport="http", host=MCP_HOST, port=MCP_PORT, path=MCP_PATH)


if __name__ == "__main__":
    main()
