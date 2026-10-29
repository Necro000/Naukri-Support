"""Separate MCP client process calling the FastMCP status server over HTTP at /mcp (Task 14)."""

from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client

from config import MCP_URL

DEMO_RECORD_IDS: tuple[str, ...] = ("APP-0002", "APP-0006", "APP-0001")


async def run_mcp_client_demo(
    record_ids: tuple[str, ...] = DEMO_RECORD_IDS,
    server_url: str = MCP_URL,
) -> list[Any]:
    """Connect to the FastMCP server at ``server_url`` and invoke the lookup tool for multiple IDs.

    Args:
        record_ids: Tuple of job application record IDs to query (must be >= 2).
        server_url: Full MCP HTTP endpoint URL ending with ``/mcp``.

    Returns:
        List of raw MCP CallToolResult responses.
    """
    print("=== Naukri.com MCP Client Round-Trip Demonstration (Task 14) ===")
    print(f"Connecting to MCP server endpoint: {server_url}\n")

    responses: list[Any] = []
    async with Client(server_url) as client:
        tools = await client.list_tools()
        print(f"Discovered {len(tools)} MCP tool(s):")
        for t in tools:
            schema = getattr(t, "input_schema", getattr(t, "inputSchema", None))
            print(f"  - name       : {t.name}")
            print(f"    description: {(t.description or '').splitlines()[0]}")
            print(f"    input_schema: {schema}\n")

        for idx, rid in enumerate(record_ids, start=1):
            print(f"--- MCP Tool Call #{idx}: record_id={rid!r} ---")
            result = await client.call_tool(
                "check_job_application_status",
                {"record_id": rid},
            )
            responses.append(result)
            print(f"Standardized MCP Response object:\n  {result}")
            if hasattr(result, "data") and result.data is not None:
                print(f"Structured data payload:\n  {result.data}\n")
            elif hasattr(result, "content") and result.content:
                print(f"Content blocks:\n  {result.content}\n")

    print("[OK] MCP client-server round trip completed for all record IDs.")
    return responses


def main() -> None:
    """Entry point for running the standalone MCP client script."""
    asyncio.run(run_mcp_client_demo())


if __name__ == "__main__":
    main()
