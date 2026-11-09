"""Probe provider requests using synthetic messages; never execute resident tools."""

import os

for prefix in ("LANGCHAIN", "LANGSMITH"):
    for suffix in ("TRACING", "TRACING_V2"):
        os.environ[f"{prefix}_{suffix}"] = "false"

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402
from openai import APIError  # noqa: E402

from src.agent_core.context import compact_messages  # noqa: E402
from src.container import AppContainer  # noqa: E402


def main():
    app = AppContainer()
    connection = app.settings.resolve_llm()
    if not connection:
        raise RuntimeError("No provider configured")
    print("provider:", connection.provider, "model:", connection.model)
    client = app._model().with_config({"callbacks": []})
    tools = app.packs.get("moveinmate").tools_for("diagnostic-only")
    bound = client.bind_tools(tools, parallel_tool_calls=False)
    plain = [HumanMessage(content="Reply with OK. Do not call any tools.")]
    direct = [
        HumanMessage(content="Summarize the following synthetic progress result. Do not call more tools."),
        AIMessage(content="", tool_calls=[{"id": "direct-diagnostic", "name": "get_onboarding_progress", "args": {}}]),
        ToolMessage(content='{"percent":0,"items":[]}', tool_call_id="direct-diagnostic"),
    ]
    history = []
    for index in range(6):
        history.extend([
            HumanMessage(content="Check synthetic progress"),
            AIMessage(content="", tool_calls=[{"id": f"direct-history-{index}", "name": "get_onboarding_progress", "args": {}}]),
            ToolMessage(content='{"percent":0}', tool_call_id=f"direct-history-{index}"),
            AIMessage(content="Synthetic progress is zero."),
        ])
    history.extend(direct)
    compacted, _ = compact_messages(history)
    try:
        for label, model, messages in (("plain", client, plain), ("tools", bound, plain), ("direct", bound, direct),
                                       ("compacted_history", bound, compacted)):
            try:
                model.invoke(messages)
                print(label, "OK")
            except APIError as exc:
                # This request contains only synthetic text; redact the key as
                # an additional precaution. Never inspect live conversation bodies.
                detail = str(exc).replace(connection.api_key, "[REDACTED]")
                print(label, "ERROR", detail[:2500])
    finally:
        app.store.engine.dispose()


if __name__ == "__main__":
    main()
