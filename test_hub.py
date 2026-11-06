"""Checks for the parts of hub.py that decide task outcomes. Run: python test_hub.py"""
import hub

assert hub.codex_session('noise\n{"type":"thread.started","thread_id":"abc"}\n') == "abc"
assert hub.codex_session('{"type":"turn.completed"}') is None

assert hub.gemini_result('log line\n{"conversation_id":"s","status":"SUCCESS","response":"hi"}') == ("s", "hi", None)
assert hub.gemini_result('{"conversation_id":"s","error":{"message":"bad"}}') == ("s", "", "bad")
assert hub.gemini_result('{"conversation_id":"s","status":"ERROR","error":"bad"}') == ("s", "", "bad")
assert hub.gemini_result('{"conversation_id":"s","status":"WAITING","response":"x"}')[2] == "agy ended with status WAITING"
empty = '{"conversation_id":"s","status":"SUCCESS","response":"","denied_actions":[{"action":"read_file"}]}'
assert hub.gemini_result(empty)[2] == "agy returned no report; denied: read_file"
assert hub.SHELL_BLOCKED.search("Failed to create unified exec process: CreateProcessAsUserW failed: 5")
assert not hub.SHELL_BLOCKED.search("ordinary log line")
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
assert "--mode" not in agy and "--conversation" not in agy and "MEM" in agy
assert agy[agy.index("--settings") + 1].endswith("agy-settings.json")
names = ["src/app.py", "web/db.php", "bot/.env", "bot/.env.local", "keys/server.pem", "docs/SA_PASSWORD.txt",
         "ssh/id_rsa", "bot/.venv/lib/token.py", "node_modules/x/secret.json", "a/secret_quests.py", "web/app.key"]
found = hub.secret_files("C:/p", names)
assert found == ["C:/p/web/db.php", "C:/p/bot/.env", "C:/p/bot/.env.local", "C:/p/keys/server.pem",
                 "C:/p/docs/SA_PASSWORD.txt", "C:/p/ssh/id_rsa", "C:/p/web/app.key"], found
rules = hub.gemini_settings(["MEM", None], found[:1], ["read_file(X/)"])["permissions"]
assert rules["allow"] == ["read_file(MEM/)"]
assert rules["deny"] == ["write_file(*)", "command(*)", "read_file(C:/p/web/db.php)", "read_file(X/)"]
assert agy[agy.index("--model") + 1] == "m"
assert "EXTRA" in hub.command_for("gemini", {"write": False}, False, "dir/report.md", None, ["EXTRA"])
assert "--conversation" in hub.command_for("gemini", read_task, True, "dir/report.md")
assert "--model" not in hub.command_for("gemini", {"write": False}, False, "dir/report.md")
print("ok")
