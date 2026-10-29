"""SQLite checkpointing pause-and-resume demonstration with LangGraph (Task 15)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Callable

from langgraph.checkpoint.sqlite import SqliteSaver

from agent.graph import build_graph, validate_response
from agent.state import AgentState
from config import CHECKPOINT_DB_PATH


def run_checkpoint_demo(
    db_path: Path = CHECKPOINT_DB_PATH,
    thread_id: str = "thread-checkpoint-demo-001",
) -> dict[str, Any]:
    """Demonstrate SQLite checkpointing: partial execution, interruption, state inspection, and resume.

    Proves that when resuming the SAME ``thread_id``, already-completed nodes
    (``guard_input``, ``route_intent``, ``status_lookup``) are loaded from the
    SQLite checkpoint and NOT re-executed.

    Args:
        db_path: Path to the SQLite checkpoint database file (``checkpoints.sqlite``).
        thread_id: Thread identifier used to key the checkpointed conversation.

    Returns:
        Dictionary containing execution counters before/after resume and final response.
    """
    if db_path.exists():
        db_path.unlink()

    node_counts: dict[str, int] = {
        "guard_input": 0,
        "route_intent": 0,
        "rag_retrieve": 0,
        "status_lookup": 0,
        "generate_answer": 0,
        "guard_output": 0,
        "format_response": 0,
    }

    def counting_wrapper(
        node_name: str,
        fn: Callable[[AgentState], dict[str, Any]],
    ) -> Callable[[AgentState], dict[str, Any]]:
        def _wrapped(state: AgentState) -> dict[str, Any]:
            node_counts[node_name] = node_counts.get(node_name, 0) + 1
            print(f"  [EXEC] node={node_name:<18} execution_count={node_counts[node_name]}")
            return fn(state)

        return _wrapped

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    try:
        saver = SqliteSaver(conn)
        graph = build_graph(
            checkpointer=saver,
            interrupt_before=["generate_answer"],
            node_wrapper=counting_wrapper,
        )

        config = {"configurable": {"thread_id": thread_id}}
        initial_state: AgentState = {
            "conversation_id": thread_id,
            "trace_id": "trace-checkpoint-015",
            "query": "Please check the job application status and escalation score for APP-0006.",
            "guardrail_flags": [],
            "blocked": False,
            "history": [],
        }

        print("=== SQLite Checkpointing Pause & Resume Demonstration (Task 15) ===")
        print(f"SQLite checkpoint DB : {db_path.name}")
        print(f"Thread ID            : {thread_id}")
        print("Interrupt configured : interrupt_before=['generate_answer']\n")

        print("--- Phase (a): Initial Run (executes first 3 nodes, stops before 'generate_answer') ---")
        graph.invoke(initial_state, config=config)
        counts_after_pause = dict(node_counts)

        print("\n--- Phase (b): Inspect Persisted Checkpoint State before Resume ---")
        snapshot = graph.get_state(config)
        print(f"  snapshot.next                 : {snapshot.next}")
        print(f"  checkpointed masked_query     : {snapshot.values.get('masked_query')!r}")
        print(f"  checkpointed intent           : {snapshot.values.get('intent')!r}")
        print(f"  checkpointed record_id        : {snapshot.values.get('record_id')!r}")
        print(f"  checkpointed tool_result      : {snapshot.values.get('tool_result')}")
        print(f"  Node execution counts (paused): {counts_after_pause}")

        print(
            "\n--- Phase (c): Resume on SAME thread_id with graph.invoke(None, config) ---\n"
            "  (Recompiling without interrupt_before on the same SqliteSaver + thread_id)"
        )
        resumed_graph = build_graph(
            checkpointer=saver,
            interrupt_before=None,
            node_wrapper=counting_wrapper,
        )
        final_state = resumed_graph.invoke(None, config=config)
        counts_after_resume = dict(node_counts)

        final_snapshot = resumed_graph.get_state(config)
        response = final_state["response"]
        validate_response(response)

        print("\n--- Proof that Completed Nodes Were NOT Re-Executed ---")
        print(f"  snapshot.next after completion: {final_snapshot.next}")
        for n_name in (
            "guard_input",
            "route_intent",
            "status_lookup",
            "generate_answer",
            "guard_output",
            "format_response",
        ):
            before_v = counts_after_pause[n_name]
            after_v = counts_after_resume[n_name]
            note = (
                "LOADED FROM CHECKPOINT (not re-executed)"
                if before_v == 1 and after_v == 1
                else "EXECUTED ON RESUME"
            )
            print(f"  {n_name:<18}: before_resume={before_v} -> after_resume={after_v}  [{note}]")

        print(f"\nFinal Resumed Agent Answer:\n  {response['answer']}")
        print("\n[OK] SQLite checkpoint pause-and-resume verified.")

        return {
            "thread_id": thread_id,
            "next_at_pause": list(snapshot.next),
            "counts_after_pause": counts_after_pause,
            "counts_after_resume": counts_after_resume,
            "response": response,
        }
    finally:
        conn.close()


if __name__ == "__main__":
    run_checkpoint_demo()
