---
name: testing-strategy
description: Choose proportionate verification and maintain useful tests when implementing changes, fixing bugs, or reviewing test coverage.
---

# Testing Strategy

Establish confidence proportionate to the consequences of failure, then minimize the total cost of obtaining and maintaining it. Coverage and test counts help identify gaps; they are not targets.

## Choose the verification

Identify the intended behavior and inspect existing coverage. Use repository scripts and configuration as the authority for running checks. Resolve material uncertainty about the contract before encoding an expectation.

Choose the least costly checks that exercise the behavior and the boundaries where it can fail:

- Use types and static checks for guarantees they can enforce.
- Prefer unit tests for focused logic and integration tests for collaborating code.
- Use the real environment for layout, rendering, and platform behavior.
- Exercise the changed user journey when narrower checks cannot establish that it works.

Critical behavior may warrant complementary checks at several layers. Low-risk edits do not automatically need new tests or a build. Runtime input, configuration, protocol, and schema checks remain useful when they enforce a real contract beyond static guarantees.

Keep the relevant failure path real. Prefer real internal collaborators; replace dependencies only when doing so preserves what the check needs to prove. Mocking a boundary does not verify its integration. Wire fixtures through the relevant production path and inputs.

## Write tests that can catch the defect

When TDD is requested or useful, work in vertical slices: one failing behavior test, enough implementation to pass, then refactor while green. Let each cycle inform the next; avoid a batch of tests against an imagined implementation. Otherwise use the sequence appropriate to the change.

Derive expected results from requirements, worked examples, or a known-good reference. For regressions, confirm the check fails for the original bug and passes after the fix, including when the test was written after the fix. Verify that the failing run exercised the faulty path and failed for the expected reason; preserve unrelated work when reproducing it.

Assert observable behavior through stable interfaces. Check exact values when contractual; avoid assertions that copy implementation values, freeze incidental structure, or merely count calls to mocked internals. Use the smallest fixture that exposes the behavior. For normalization or deduplication, check the resulting values, not just collection size.

Control configuration, time, randomness, and other variables irrelevant to the claim. Compare alternatives under equivalent conditions. For stochastic claims, use representative seeds or repeated runs with justified distribution bounds; one lucky sample cannot establish reliability. Keep invariant assertions exact. Do not widen margins merely to obtain a pass.

Iterate with the fastest relevant runner and check its exit status. Inspect the failures for shared causes before editing expectations: the code, the asserted contract, the fixture, or an uncontrolled variable may be wrong.

## Retain useful coverage

Use temporary tests and probes freely. Before finishing, retain or consolidate those whose future regression protection justifies their upkeep, and remove disposable scaffolding. Realistic verification today does not automatically require permanent end-to-end coverage.

Judge the suite and its infrastructure by total confidence and lifetime cost: runtime, flakiness, diagnosis, fixture upkeep, and friction during legitimate refactors.

Apply a higher bar to heavyweight checks. They can earn their place by covering consequential failures, providing useful complementary protection, or replacing several brittle tests. Explain unusual testing cost or scope; routine tests need no written business case.

Keep behavioral tests near the code that owns the contract. Share checks across implementations of the same contract. Expand matrices for distinct risks and use representative cases for equivalent behavior.

Change expectations when the intended contract changes. Otherwise investigate failures and preserve meaningful protection when replacing or removing tests. Never weaken assertions or performance budgets merely to pass a check.

## Finish

Keep checks deterministic and failures actionable. Prefer observable conditions or controlled scheduling to fixed sleeps. Use isolated test data and configuration; prefer offscreen or headless checks when they preserve the evidence. If a real visible interaction is necessary, minimize disruption and report it. Restore state and release resources, including on failure.

Run affected checks against the final code and complete required project checks. A suite's exclusion from routine CI does not waive relevant verification. Broaden or repeat testing only for a new change, failure, or concrete unresolved risk. Otherwise stop.

Report what ran, results, and material verification gaps. State the limits of fixtures, mocks, and environments; passing tests do not establish every live integration or human usability judgment.

## Sources

Derived from Travis Fischer's testing guidance, Matt Pocock's `tdd`, and David Zhang's `write-tests`. When maintaining this skill or updating its sources, read [the derivation record](references/derivation.md); the bundled upstream copies are provenance, not additional runtime instructions.
