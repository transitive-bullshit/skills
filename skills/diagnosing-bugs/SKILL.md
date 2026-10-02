---
name: diagnosing-bugs
description: "Diagnose difficult or uncertain bugs and performance regressions with a reproducible feedback loop. Use when investigation is needed beyond an evident local fix."
---

# Diagnose bugs and performance regressions

Start with the user's symptom, relevant source, and available evidence. For an evident local defect, make the scoped fix and verify it directly. Use a deeper investigation loop when the cause is uncertain, reproduction is intermittent, or earlier fixes failed.

## Establish useful evidence

Inspect relevant code, configuration, logs, and recent changes to form a bounded hypothesis and choose a reproduction. Consult the project's glossary or ADRs only when they affect this area.

Prefer the smallest reliable signal that reaches the actual failure: an existing test, a targeted regression test, a local request, a UI interaction, a trace replay, or a temporary harness. Confirm the signal distinguishes the reported bug from an unrelated failure. For performance problems, record a baseline and compare equivalent workloads.

Improve reproduction speed and determinism when that will materially help investigation. Minimize enough to distinguish causes; exhaustive minimality and a fixed reproduction percentage are not prerequisites for progress.

If the environment cannot reproduce the issue, continue source and evidence analysis, clearly separating confirmed facts from hypotheses. Ask for the specific missing artifact or access only when it blocks the next meaningful step. Production instrumentation or unrelated live-system changes need their own authorization.

## Investigate and fix

Choose the most plausible falsifiable explanation and test the prediction. Compare alternatives when evidence is ambiguous; no fixed hypothesis count is required. Use targeted instrumentation and avoid changing several causal variables at once.

Add a regression test when a meaningful seam can exercise the real bug and the test will guard against recurrence. Prefer existing public interfaces and independent expected results. A trivial reversible correction does not require an elaborate new harness. If automated coverage is unsuitable, verify the actual behavior and explain the limit.

Apply the fix, rerun the relevant reproduction/checks, and fix failures caused by the change. Preserve unrelated work and record unrelated baseline failures without automatically pausing.

## Completion

The requested behavior works under the available evidence, relevant checks pass or their concrete blocker is disclosed, and temporary instrumentation is removed. Report the cause, change, and verification without claiming evidence you could not obtain.

Keep credentials in environment variables and redact secrets from commands, logs, traces, and shared artifacts. Request only the redacted evidence needed to diagnose the symptom.
