"""Checks for the parts of hub.py that decide task outcomes. Run: python test_hub.py"""
import hub

assert hub.codex_session('noise\n{"type":"thread.started","thread_id":"abc"}\n') == "abc"
assert hub.codex_session('{"type":"turn.completed"}') is None

assert hub.gemini_result('log line\n{"conversation_id":"s","status":"SUCCESS","response":"hi"}') == ("s", "hi", None)
assert hub.gemini_result('{"conversation_id":"s","error":{"message":"bad"}}') == ("s", "", "bad")
assert hub.gemini_result('{"conversation_id":"s","status":"ERROR","error":"bad"}') == ("s", "", "bad")
assert hub.gemini_result('{"conversation_id":"s","status":"WAITING","response":"x"}')[2] == "agy ended with status WAITING"
assert hub.gemini_result("") == (None, "", "no output")
assert hub.gemini_result("not json") == (None, "", "not json")

assert hub.classify(0, "quota text in a normal answer") == "completed"
assert hub.classify(1, "You've hit your usage limit") == "quota"
assert hub.classify(1, "RESOURCE_EXHAUSTED") == "quota"
assert hub.classify(1, "boom") == "failed"

config = {"project_name": "Demo", "limits": ["Never touch prod."], "memory": "MEM"}
first = hub.build_prompt("t", "codex", False, "W", "c", "BRIEF", config, "RULES", "INDEX", False)
assert all(part in first for part in ("BRIEF", "RULES", "INDEX", "read-only", "## Result", "Never touch prod.", "Demo"))
bare = hub.build_prompt("t", "codex", False, "W", "c", "BRIEF", {}, "", "", False)
assert "memory index" not in bare and "Project rules" not in bare and "Do not push" in bare
write = hub.build_prompt("t", "codex", True, "W", "c", "BRIEF", config, "RULES", "INDEX", False)
assert "may edit" in write and "read-only task" not in write
follow = hub.build_prompt("t", "codex", False, "W", "c", "BRIEF", config, "RULES", "INDEX", True)
assert "BRIEF" in follow and "RULES" not in follow

read_task = {"model": "m", "effort": "e", "write": False, "session": "s", "codex_config": ["a=b"]}
codex = hub.command_for("codex", read_task, False, "r")
assert "read-only" in codex and "m" in codex and "model_reasoning_effort=e" in codex and "a=b" in codex
assert "workspace-write" in hub.command_for("codex", {**read_task, "write": True}, False, "r")
assert 'sandbox_mode="read-only"' in hub.command_for("codex", read_task, True, "r")
assert "-m" not in hub.command_for("codex", {"write": False}, False, "r")

hub.agy_path = lambda: "agy"
agy = hub.command_for("gemini", {**read_task, "session": None}, False, "dir/report.md", "MEM")
assert "plan" in agy and hub.GEMINI_READ_ONLY in agy and "--conversation" not in agy and "MEM" in agy
assert agy[agy.index("--model") + 1] == "m"
assert "--conversation" in hub.command_for("gemini", read_task, True, "dir/report.md")
assert "--model" not in hub.command_for("gemini", {"write": False}, False, "dir/report.md")
print("ok")
