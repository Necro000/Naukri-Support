"""Resilience demonstrations: exponential-backoff retry policy, per-node timeout, and global timeout (Task 16)."""

from __future__ import annotations

import asyncio
import sys
import time
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from agent.tools import check_job_application_status
from config import (
    GLOBAL_TIMEOUT_SECONDS,
    NODE_TIMEOUT_SECONDS,
    RETRY_BACKOFF_FACTOR,
    RETRY_INITIAL_INTERVAL,
    RETRY_JITTER,
    RETRY_MAX_ATTEMPTS,
    RETRY_MAX_INTERVAL,
)


class TransientLookupError(RuntimeError):
    """Simulated transient network/database failure for retry demonstration."""


class NodeTimeoutError(TimeoutError):
    """Raised when an individual LangGraph node exceeds its configured per-node timeout."""


class GlobalGraphTimeoutError(TimeoutError):
    """Raised when the entire LangGraph run exceeds the configured global timeout."""


class ResilienceState(TypedDict, total=False):
    """State for the Task 16 resilience demonstrations."""

    record_id: str
    attempt_count: int
    tool_result: dict[str, Any]
    answer: str
    status: str


def run_retry_demo() -> dict[str, Any]:
    """(a) Demonstrate LangGraph RetryPolicy recovering from 2 transient failures on attempt 3."""
    print("=== Task 16 (a): Exponential-Backoff RetryPolicy Recovery Demonstration ===")
    print(
        f"Configured RetryPolicy:\n"
        f"  max_attempts     = {RETRY_MAX_ATTEMPTS}\n"
        f"  initial_interval = {RETRY_INITIAL_INTERVAL}s\n"
        f"  backoff_factor   = {RETRY_BACKOFF_FACTOR}\n"
        f"  max_interval     = {RETRY_MAX_INTERVAL}s\n"
        f"  jitter           = {RETRY_JITTER}\n"
    )

    call_log: list[dict[str, Any]] = []
    start_ts = time.perf_counter()

    def flaky_lookup_node(state: ResilienceState) -> dict[str, Any]:
        attempt = len(call_log) + 1
        elapsed = round(time.perf_counter() - start_ts, 3)
        if attempt <= 2:
            call_log.append({"attempt": attempt, "elapsed_s": elapsed, "outcome": "TransientLookupError"})
            print(
                f"  [Attempt {attempt}/{RETRY_MAX_ATTEMPTS} at t={elapsed:.3f}s] "
                f"flaky_lookup_node -> SIMULATED FAILURE (TransientLookupError)"
            )
            raise TransientLookupError(f"Simulated transient database timeout on attempt {attempt}")

        res = check_job_application_status(state["record_id"])
        call_log.append({"attempt": attempt, "elapsed_s": elapsed, "outcome": "SUCCESS"})
        print(
            f"  [Attempt {attempt}/{RETRY_MAX_ATTEMPTS} at t={elapsed:.3f}s] "
            f"flaky_lookup_node -> RECOVERED SUCCESSFULLY"
        )
        return {
            "attempt_count": attempt,
            "tool_result": res,
        }

    def format_node(state: ResilienceState) -> dict[str, Any]:
        tr = state["tool_result"]
        return {
            "status": "recovered",
            "answer": (
                f"Recovered on attempt {state['attempt_count']}: Application {tr['record_id']} "
                f"status is '{tr['status']}' (escalation_score={tr['escalation_score']:.4f})."
            ),
        }

    retry_policy = RetryPolicy(
        max_attempts=RETRY_MAX_ATTEMPTS,
        initial_interval=RETRY_INITIAL_INTERVAL,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        max_interval=RETRY_MAX_INTERVAL,
        jitter=RETRY_JITTER,
        retry_on=TransientLookupError,
    )

    builder = StateGraph(ResilienceState)
    builder.add_node("flaky_lookup_node", flaky_lookup_node, retry_policy=retry_policy)
    builder.add_node("format_node", format_node)
    builder.add_edge(START, "flaky_lookup_node")
    builder.add_edge("flaky_lookup_node", "format_node")
    builder.add_edge("format_node", END)

    graph = builder.compile()
    final_state = graph.invoke({"record_id": "APP-0006"})

    print(f"\nFinal Result : {final_state['answer']}")
    print(f"Attempt Log  : {call_log}")
    print("[OK] RetryPolicy recovered cleanly on attempt 3 within max_attempts=4.")
    return {
        "status": final_state["status"],
        "attempts": len(call_log),
        "call_log": call_log,
        "answer": final_state["answer"],
    }


async def run_node_timeout_demo(
    node_timeout_s: float = NODE_TIMEOUT_SECONDS,
    simulated_delay_s: float = 2.5,
) -> dict[str, Any]:
    """(b) Demonstrate per-node timeout catching a stalled node and raising a clean NodeTimeoutError."""
    print("=== Task 16 (b): Per-Node Timeout Demonstration ===")
    print(f"Configured per-node timeout : {node_timeout_s:.2f}s")
    print(f"Simulated slow node delay   : {simulated_delay_s:.2f}s\n")

    async def slow_rag_node(state: ResilienceState) -> dict[str, Any]:
        print(
            f"  [Node 'slow_rag_node'] Starting work (simulated sleep={simulated_delay_s:.2f}s, "
            f"timeout={node_timeout_s:.2f}s)..."
        )
        t0 = time.perf_counter()
        try:
            await asyncio.wait_for(asyncio.sleep(simulated_delay_s), timeout=node_timeout_s)
        except asyncio.TimeoutError as exc:
            elapsed = time.perf_counter() - t0
            msg = (
                f"Node 'slow_rag_node' exceeded per-node timeout of {node_timeout_s:.2f}s "
                f"(aborted cleanly after {elapsed:.3f}s)."
            )
            print(f"  [NodeTimeoutError] {msg}")
            raise NodeTimeoutError(msg) from exc
        return {"status": "completed"}

    builder = StateGraph(ResilienceState)
    builder.add_node("slow_rag_node", slow_rag_node)
    builder.add_edge(START, "slow_rag_node")
    builder.add_edge("slow_rag_node", END)
    graph = builder.compile()

    t_start = time.perf_counter()
    try:
        await graph.ainvoke({"record_id": "APP-0002"})
        raise AssertionError("Expected NodeTimeoutError was not raised")
    except NodeTimeoutError as err:
        elapsed_total = round(time.perf_counter() - t_start, 3)
        print(f"\nCaught clean per-node exception after {elapsed_total:.3f}s: {err}")
        print("[OK] Per-node timeout fired cleanly without hanging.")
        return {
            "status": "node_timeout_fired",
            "error_type": type(err).__name__,
            "error_message": str(err),
            "elapsed_s": elapsed_total,
        }


async def run_global_timeout_demo(
    global_timeout_s: float = GLOBAL_TIMEOUT_SECONDS,
    step_delay_s: float = 1.3,
) -> dict[str, Any]:
    """(c) Demonstrate global graph timeout cancelling a multi-node run exceeding total budget."""
    print("=== Task 16 (c): Global Graph Timeout Demonstration ===")
    print(f"Configured global graph timeout : {global_timeout_s:.2f}s")
    print(f"Simulated 3-node delay          : 3 x {step_delay_s:.2f}s = {3 * step_delay_s:.2f}s total\n")

    executed_nodes: list[str] = []

    async def step_1(state: ResilienceState) -> dict[str, Any]:
        executed_nodes.append("step_1")
        print(f"  [Global Run] Executing step_1 (sleeping {step_delay_s:.2f}s)...")
        await asyncio.sleep(step_delay_s)
        print("  [Global Run] step_1 completed.")
        return {"status": "step_1_done"}

    async def step_2(state: ResilienceState) -> dict[str, Any]:
        executed_nodes.append("step_2")
        print(f"  [Global Run] Executing step_2 (sleeping {step_delay_s:.2f}s)...")
        await asyncio.sleep(step_delay_s)
        print("  [Global Run] step_2 completed.")
        return {"status": "step_2_done"}

    async def step_3(state: ResilienceState) -> dict[str, Any]:
        executed_nodes.append("step_3")
        print(f"  [Global Run] Executing step_3 (sleeping {step_delay_s:.2f}s)...")
        await asyncio.sleep(step_delay_s)
        return {"status": "step_3_done"}

    builder = StateGraph(ResilienceState)
    builder.add_node("step_1", step_1)
    builder.add_node("step_2", step_2)
    builder.add_node("step_3", step_3)
    builder.add_edge(START, "step_1")
    builder.add_edge("step_1", "step_2")
    builder.add_edge("step_2", "step_3")
    builder.add_edge("step_3", END)
    graph = builder.compile()

    t_start = time.perf_counter()
    try:
        await asyncio.wait_for(
            graph.ainvoke({"record_id": "APP-0001"}),
            timeout=global_timeout_s,
        )
        raise AssertionError("Expected global timeout did not fire")
    except asyncio.TimeoutError as exc:
        elapsed_total = round(time.perf_counter() - t_start, 3)
        msg = (
            f"Global graph execution cancelled cleanly after {elapsed_total:.3f}s "
            f"(budget={global_timeout_s:.2f}s; nodes started before cancellation={executed_nodes})."
        )
        err = GlobalGraphTimeoutError(msg)
        print(f"\n[GlobalGraphTimeoutError] {err}")
        print("[OK] Global timeout cancelled the multi-node run cleanly.")
        return {
            "status": "global_timeout_fired",
            "error_type": type(err).__name__,
            "error_message": str(err),
            "executed_nodes": executed_nodes,
            "elapsed_s": elapsed_total,
        }


def main() -> None:
    """CLI entry point for running retry, node_timeout, or global_timeout demos."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "retry":
        run_retry_demo()
    elif mode == "node_timeout":
        asyncio.run(run_node_timeout_demo())
    elif mode == "global_timeout":
        asyncio.run(run_global_timeout_demo())
    elif mode == "all":
        run_retry_demo()
        print()
        asyncio.run(run_node_timeout_demo())
        print()
        asyncio.run(run_global_timeout_demo())
    else:
        raise SystemExit(f"Unknown mode: {mode}")


if __name__ == "__main__":
    main()
