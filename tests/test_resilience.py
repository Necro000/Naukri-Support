"""Unit tests for Part 4: MCP tool wrapper, SQLite checkpoint resume, retries, and timeouts (Tasks 14-16)."""

from __future__ import annotations

import asyncio
from pathlib import Path

from mcp_server.server import check_job_application_status as mcp_tool_fn
from resilience.checkpoint_demo import run_checkpoint_demo
from resilience.timeout_retry_demo import (
    run_global_timeout_demo,
    run_node_timeout_demo,
    run_retry_demo,
)


def test_mcp_wrapped_tool_callable() -> None:
    """MCP-exposed status tool must have a docstring and return valid application status dicts."""
    fn = getattr(mcp_tool_fn, "fn", mcp_tool_fn)
    assert fn.__doc__ is not None and len(fn.__doc__.strip()) > 20
    res = fn("APP-0002")
    assert res["record_id"] == "APP-0002"
    assert "escalation_score" in res


def test_sqlite_checkpoint_pause_and_resume(tmp_path: Path) -> None:
    """Completed nodes before interruption must not re-execute on resume."""
    db_file = tmp_path / "test_checkpoints.sqlite"
    res = run_checkpoint_demo(db_path=db_file, thread_id="pytest-thread-15")
    assert res["next_at_pause"] == ["generate_answer"]
    # First 3 nodes ran once before pause and remained at 1 after resume
    for node_name in ("guard_input", "route_intent", "status_lookup"):
        assert res["counts_after_pause"][node_name] == 1
        assert res["counts_after_resume"][node_name] == 1
    # Remaining 3 nodes ran only after resume
    for node_name in ("generate_answer", "guard_output", "format_response"):
        assert res["counts_after_pause"][node_name] == 0
        assert res["counts_after_resume"][node_name] == 1


def test_retry_and_timeouts() -> None:
    """RetryPolicy must recover on attempt 3; per-node and global timeouts must fire cleanly."""
    retry_res = run_retry_demo()
    assert retry_res["status"] == "recovered"
    assert retry_res["attempts"] == 3

    node_res = asyncio.run(run_node_timeout_demo(node_timeout_s=0.2, simulated_delay_s=1.0))
    assert node_res["status"] == "node_timeout_fired"
    assert node_res["error_type"] == "NodeTimeoutError"

    global_res = asyncio.run(run_global_timeout_demo(global_timeout_s=0.35, step_delay_s=0.25))
    assert global_res["status"] == "global_timeout_fired"
    assert global_res["error_type"] == "GlobalGraphTimeoutError"
    assert "step_3" not in global_res["executed_nodes"]
