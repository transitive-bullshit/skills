---
name: diagnosing-bugs
description: "Diagnose difficult or uncertain bugs and performance regressions with a reproducible feedback loop. Use when investigation is needed beyond an evident local fix."
---

# Diagnose bugs and performance regressions

Start with the user’s symptom, relevant source, and available evidence. For an evident local defect, make the scoped fix and verify it directly. Use a deeper investigation loop when the cause is uncertain, reproduction is intermittent, or earlier fixes failed. Consult the project’s glossary (`GLOSSARY.md`, `CONTEXT.md`, or its equivalent) and ADRs when they affect the area.

## Establish useful evidence

Choose the smallest reliable signal that reaches the actual failure. Useful options include an existing or targeted regression test, a local HTTP request, a CLI fixture, a browser interaction, replaying a captured trace, a temporary harness, bounded seeded fuzzing, bisection, or comparing matched versions. Confirm the signal distinguishes the reported symptom from an unrelated failure.

For a reproduction that requires human interaction, adapt [the human-in-the-loop template](scripts/hitl-loop.template.sh). Capture observations only; leave signing in and entering credentials to the user.

Tighten the loop when doing so improves investigation: cache setup, narrow unrelated work, control time and randomness, isolate state, and assert on the actual symptom. For intermittent bugs, increase the reproduction rate with bounded repeats or controlled stress; preserve comparable workloads. A fixed duration or reproduction percentage is not a prerequisite for progress.

If the environment cannot reproduce the issue, continue useful source and evidence analysis, separating facts from hypotheses. Ask for the specific missing artifact or access only when it blocks the next meaningful step. Production instrumentation and unrelated live-system changes need their own authorization.

## Reproduce and isolate

When a reproduction is available, run it and record the exact failure. For performance problems, establish a baseline and compare equivalent workloads. Minimize enough to distinguish causes: change one input, caller, configuration setting, or step at a time and rerun the signal. Exhaustive minimality is unnecessary when the relevant cause is already isolated.

## Test explanations

Choose a falsifiable explanation and state what observation would support or contradict it. Compare competing explanations when evidence is ambiguous; no fixed hypothesis count is required. Share material findings while continuing authorized investigation.

Use a debugger, REPL, or targeted logs at points that distinguish the explanations. Change one causal variable at a time. Give temporary instrumentation a distinctive prefix so it can be removed reliably. For performance regressions, use matched timing, profiling, or query-plan evidence instead of treating log volume as a performance measurement.

## Fix and verify

Add a regression test when a meaningful public interface can exercise the real failure and guard against recurrence. Expected results must come from the contract or independent examples, not a restatement of the implementation. A trivial reversible correction does not require an elaborate new harness. If automated coverage is unsuitable, verify the actual behavior and explain the limit.

When using a regression test:

1. Confirm it fails for the intended defect. If a temporary source or fixture mutation is used to prove detection, inspect the diff to confirm that mutation actually landed.
2. Apply the scoped fix and observe the test pass.
3. Rerun the original scenario as well as the minimized reproduction when they exercise meaningfully different paths.

Run the relevant project checks and fix failures caused by the change. Preserve unrelated work and report unrelated baseline failures without automatically pausing.

## Completion

The requested behavior works under the available evidence, relevant checks pass or their concrete blocker is disclosed, and temporary instrumentation is removed. Preserve a useful diagnostic artifact only when needed and label its purpose. Report the cause, change, verification, and material evidence gaps.

Keep credentials in environment variables. Redact secrets from commands, logs, traces, and shared artifacts; request only the redacted evidence needed to diagnose the symptom.
