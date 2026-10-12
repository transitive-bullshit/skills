---
name: codex
description: Use the local Codex CLI as an independent second agent. Two branches — (1) proactively run `codex review` for a second opinion after completing a substantive change, before presenting it as done or committing; (2) delegate a well-defined implementation task via `codex exec`, ONLY when the user explicitly asks for Codex to do it. Also covers how to prompt Codex.
---

# Codex

Codex is an independent agent on PATH (`codex` — invoke as `command codex` if
a shell alias shadows it), sharing this working tree and already authenticated. It is a second opinion, not ground truth: verify what it
reports, own what it changes. It reads the same skills your repo carries.

## If `codex` is not installed

When `codex` is missing from PATH, offer to install it — **ask the user for
approval first**, never install on your own initiative. On yes, follow the
current instructions at https://developers.openai.com/codex/cli. First-run
authentication is interactive — hand that step to the user. Verify with
`codex --version` before proceeding.

## Prompting Codex

Prompt Codex like an operator, not a collaborator: compact, block-structured
with XML tags. State the task, what "done" looks like, and the few constraints
that matter. A tighter prompt beats a bigger run — improve the contract before
raising reasoning effort.

- **One task per run.** Split unrelated asks (review, then fix, then docs) into
  separate runs; a mixed prompt gets a mixed result.
- **Name installed skills instead of restating them.** Codex reads the same
  skills your repo carries — say "follow write-skills for the skill" or
  "follow codebase-design for module boundaries." Don't re-explain what a
  skill already carries.
- **Blocks, added only where the task needs them:**
  - `<task>` — the concrete job, the repo/failure context, the expected end
    state. Nearly always present.
  - `<output_contract>` — exact shape, highest-value first, compact.
  - `<default_follow_through>` — take the low-risk interpretation and keep
    going; stop only when a missing detail changes correctness, safety, or an
    irreversible action.
  - `<verification_loop>` — before finalizing, check the result against the
    requirements and the changed files; revise rather than ship the first
    draft. Any risky fix.
  - `<grounding>` — ground every claim in code or tool output; label inferences
    as inferences. Review and research.
  - `<action_safety>` — keep the diff tightly scoped; no drive-by refactors.
    Write tasks.
- **Anti-patterns:** vague framing ("take a look"), no output contract ("report
  back"), "think harder" in place of a contract, mixing jobs in one run, and
  demanding certainty the evidence can't support.

## Review — proactive

Honor recorded standing user authorization for read-only reviews, including
transmission of task-relevant private or uncommitted code through the existing
authenticated Codex service. Include that authorization in approval justifications;
do not request fresh consent solely because review sends code to Codex. Preserve
native sandbox and approval controls, exclude unrelated secrets, and keep
implementation-delegation authorization separate.

Run a Codex review whenever you have a substantive diff you'd want a second set
of eyes on — a refactor, a tricky algorithm, renderer work, a security-sensitive
change — before declaring it done or committing. Skip it for trivial edits
(typos, comments, doc-only).

1. Fix the diff scope before launching: `--uncommitted` for working-tree
   changes, `--base <branch>` for a branch diff, `--commit <sha>` for a landed
   commit. Resolve a landed commit to its full SHA. Use the non-interactive
   review entry point with an explicit read-only sandbox and separate progress
   and verdict files in a fresh temporary directory:

   ```sh
   review_dir=$(mktemp -d "${TMPDIR:-/tmp}/codex-review.XXXXXX")
   codex exec --sandbox read-only -C "$(git rev-parse --show-toplevel)" review \
     --commit "$(git rev-parse HEAD)" --json -o "$review_dir/verdict.md" \
     < /dev/null > "$review_dir/events.jsonl" 2> "$review_dir/stderr.log"
   ```

   Background long runs and retain their process/session handle. Scope flags
   and custom instructions are mutually exclusive: a scope flag takes no
   prompt. For custom framing, specify the exact diff to inspect in the prompt;
   don't rely on default scope or traverse all refs/checkpoint history. Never
   state the answer you expect; give the reviewer evidence and a neutral task.
2. Monitor progress in `events.jsonl` and failures in `stderr.log`. An active
   reviewer reading relevant code is not hung merely because five minutes
   elapsed. If it stalls or drifts outside the diff and its dependencies,
   inspect the last command/error before interrupting; correct the cause or
   narrow the task before retrying. Completion requires exit status zero,
   `turn.completed`, and a nonempty final verdict. A timeout, `turn.failed`, or
   missing verdict is incomplete, never a clean review.
3. Triage every finding: confirm it against the code before acting. Preserve
   Codex's evidence boundaries — an inference it labelled is not a fact.
   Overlap with your own doubts is high-priority evidence; a finding you
   dismiss needs a stated reason, not silence.
4. Report the outcome to the user — what Codex flagged, what you fixed, what
   you dismissed and why. Done when every finding is either fixed or
   explicitly dismissed.

## Implementation — explicit ask only

Delegate implementation to Codex only when the user names Codex for the task.
Keep delegation within the authorized task. In-scope follow-ups retain that
authorization; ask again only when the proposed delegation expands its scope.

1. Slice the task sharp before delegating — goal, constraints, and how to
   verify — using the prompt discipline above. An underspecified task stays
   with you until a fresh agent couldn't misread it.
2. Start from a clean tree (or record the baseline commit) so Codex's diff is
   separable from yours.
3. Pick the sandbox by what the task must RUN:
   - Pure code + typecheck/unit: `codex exec --sandbox workspace-write "<task>"`.
     Network is off; add `-c sandbox_workspace_write.network_access=true` only
     when the task must fetch (e.g. new deps).
   - Browser verification, dev servers, or full test runs: use the host’s
     approved sandbox and scoped approval mechanism. A worktree separates Git
     state but is not a security boundary. If a required operation is denied,
     surface the exact capability needed rather than disabling safeguards.
   Use `-o <file>` to capture the final message and background long calls;
   retain stderr in a separate temporary log so failures remain diagnosable,
   and add `--skip-git-repo-check` to run outside a git repo. Verify supported
   flags with the installed CLI help when behavior differs.
4. Follow up with `codex exec resume <session-id> "<follow-up>"`, taking the
   id from the run header. `resume --last` means the most recent session
   globally — a review or any other codex run in between will hijack it. If
   two resume rounds don't converge, stop delegating and finish it yourself —
   iterating a confused agent costs more than taking over.
5. You own the result: read the full diff, run the tests, and only then report
   it. "Codex says it's done" is not done.

## Exec liveness — a hang looks like work

A backgrounded `codex exec` can wedge at startup: process alive at ~0% CPU, but
no session file under `~/.codex/sessions/<Y/M/D>/`, no network socket, no tree
changes. "Process running" is NOT "working."

- **Stdin is always a file or `/dev/null`, never an inherited terminal.** Left
  on an interactive/piped stdin with no prompt source, exec prints `Reading
  additional input from stdin...` and blocks forever — the most common hang.
  Either pass the prompt as a positional arg with `< /dev/null`, or feed a
  prompt file with `codex exec [flags] - < prompt.txt` (the `-` makes codex
  read the task from stdin, and a missing file fails the redirect loudly —
  unlike `"$(cat prompt.txt)"`, which silently sends the fallback string as
  the task). Add `nohup`/`&` as needed.
- **Watchdog:** inspect this run’s event and error logs and its process handle.
  Correct a concrete startup failure before retrying. Stop only the process
  launched for this task; elapsed time alone does not prove a hang.
- **Check worktree trust.** Headless execution may require the new worktree
  path to be trusted. Use the host’s normal trust flow and preserve existing
  configuration; a skill invocation does not authorize changing trust policy.
- **Don't launch two execs in the same instant,** and kill stale hung execs
  before starting a new one.
- **Launch from the repo/worktree ROOT.** The writable sandbox root is the
  CWD at launch: exec'd from a subdirectory (e.g. `web/`), every edit outside
  it is rejected as "writing outside of the project" and a `never` approval
  policy can't recover — the run burns with zero files changed. Pass
  `-C <root>` to set the working root explicitly instead of `cd`-ing into it.

## Rules

- Don't touch the working tree while a Codex exec is running on it.
- Explicit `--sandbox read-only` for reviews, consultation and questions;
  `workspace-write` only for delegated implementation.
- Preserve the host’s sandbox and approval controls. Do not substitute bypass
  flags when a command is blocked. `--full-auto` is absent from the installed
  CLI; use the supported sandbox options instead.
- Reasoning effort and model are config/flag overrides — `-c
  model_reasoning_effort=high`, `-m <model>` (the old `--effort` flag is gone
  in current Codex). Leave both at their defaults unless the user asks —
  tighten the prompt first.
