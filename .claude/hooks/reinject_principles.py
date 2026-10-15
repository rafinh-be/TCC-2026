import json, sys, tempfile
from pathlib import Path

TOKEN_INTERVAL = 50_000

hook_input = json.load(sys.stdin)
project_dir = Path(__file__).resolve().parents[2]


def claude_context_tokens(entry):
    if entry.get("type") != "assistant" or entry.get("isSidechain"):
        return 0
    usage = entry.get("message", {}).get("usage") or {}
    return (
        usage.get("input_tokens", 0)
        + usage.get("cache_creation_input_tokens", 0)
        + usage.get("cache_read_input_tokens", 0)
    )


def codex_context_tokens(entry):
    payload = entry.get("payload") or {}
    if entry.get("type") != "event_msg" or payload.get("type") != "token_count":
        return 0
    return ((payload.get("info") or {}).get("last_token_usage") or {}).get("input_tokens", 0)


def current_context_tokens(transcript_path):
    if not transcript_path or not Path(transcript_path).exists():
        return 0
    context_tokens = 0
    with open(transcript_path, encoding="utf-8") as transcript:
        for line in transcript:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            context_tokens = claude_context_tokens(entry) or codex_context_tokens(entry) or context_tokens
    return context_tokens


def principles_section():
    lines = (project_dir / "AGENTS.md").read_text(encoding="utf-8").splitlines()
    start = lines.index("## Principles")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start:end]).strip()


reached_interval = current_context_tokens(hook_input.get("transcript_path")) // TOKEN_INTERVAL
state_file = Path(tempfile.gettempdir()) / f"claude-principles-{hook_input['session_id']}"
last_interval = int(state_file.read_text()) if state_file.exists() else 0

if reached_interval != last_interval:
    state_file.write_text(str(reached_interval))

if reached_interval > last_interval:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": hook_input["hook_event_name"],
            "additionalContext": "Reminder of the project principles from AGENTS.md:\n\n" + principles_section(),
        }
    }))
