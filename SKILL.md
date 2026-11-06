---
name: agent-hub
description: Delegate work to Codex or Gemini through their own workspace, with shared project context, resumable sessions and a task record. Use to save Claude limits - for broad code review, second opinions, hard architecture questions, large code investigation, research, or a well-scoped implementation Codex can do on its own branch. Also use when the user names Codex or Gemini, or asks for all agents together.
---

# Agent Hub

The user talks only to Claude and never operates the other agents. Decide on delegation yourself, without asking, and report results in your own words.

Claude writes the code. Hand reading-heavy work to the others to save Claude limits: broad review, code investigation, research, second opinions. Use Codex `--write` only for large mechanical edits, or when the user asks.
Do small jobs yourself: a brief plus review costs more than the job.

| Agent | Give it | Access |
|---|---|---|
| codex | review, hard reasoning, architecture, large mechanical edits | read-only, or `--write` on a new `agent/codex/<task>` branch |
| gemini | large code investigation, research, independent analysis (runs through Antigravity CLI `agy`; Gemini CLI is closed for personal accounts) | read-only always |

All three together only when the user asks. Then run both agents on the same brief and compare.

## Commands

Run with the Bash tool. Use `run_in_background` for anything long; the hub prints a short report at the end.

```
H=~/.claude/skills/agent-hub/hub.py
python "$H" run codex "brief" [--write] [--base <branch-or-commit>] [--effort high] [--timeout 1800]
python "$H" run gemini --brief-file <file>
python "$H" resume <task> "follow-up"     # same session, same workspace, same branch
python "$H" list
python "$H" show <task>                   # full report
```

- Each agent has one workspace, so one task per agent at a time. A second task stops with "busy".
- The workspace holds committed code only. Commit the work first, or pass `--base <branch>`. The default is HEAD; uncommitted changes and other branches are not there unless named.
- Gemini can read only its workspace, the memory folder and `read_dirs` from the config. One read outside those ends its run, so check the paths in the brief. Codex read-only can read the whole disk.
- Do not write a task off as done on a thin report. The hub marks a task `failed` when the agent's shell could not start or its report is unfinished; then fix the cause or do the job yourself.
- Project rules, the memory index and the report format are added automatically. The brief needs only the goal, the paths, and what done means.
- Files: `~/.agent-hub/tasks/<task>/` holds `report.md`, `prompt.md`, `events.jsonl`, `stderr.log`, `diff.patch`.

## After a task

- Treat the report as a lead, not a fact. Check each finding in the code before acting on it.
- `--write` results stay on the `agent/` branch. Read `diff.patch`, then cherry-pick into your own worktree. Never merge blind, and delete the branch once done.
- Status `quota` means that subscription is out for now: use the other agent or do the work yourself.
- Production systems, databases and deploys stay with Claude and the project's normal procedures.
- Models come from `--model`, then `~/.agent-hub/config.json`, then the CLI's own default. Pick a lighter `--effort` for simple tasks.
