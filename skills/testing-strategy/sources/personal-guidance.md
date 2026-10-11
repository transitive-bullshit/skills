---
name: testing-strategy
description: Choose proportionate verification and maintain useful tests when implementing changes, fixing bugs, or reviewing test coverage.
---

# Testing strategy

Establish confidence proportionate to the consequences of failure, then minimize the total cost of obtaining and maintaining it. Coverage and test counts help identify gaps; they are not targets.

## Verify the change

Identify the intended behavior and inspect existing coverage. Use repository scripts and configuration as the authority for running checks.

Choose the least costly checks that exercise the behavior and the boundaries where it can fail:

- Use types and static checks for guarantees they can enforce.
- Prefer unit tests for focused logic and integration tests for collaborating code.
- Use the real environment for layout, rendering, and platform behavior.
- Exercise the changed user journey when narrower checks cannot establish that it works.

These are starting points. Critical behavior may warrant complementary checks at several layers. Low-risk edits do not automatically need new tests or a build.

Keep the relevant failure path real. Prefer real internal collaborators; replace dependencies only when doing so preserves what the check needs to prove. Mocking a boundary does not verify its integration.

Derive expected results from requirements, worked examples, or a known-good reference. For regressions, confirm the check fails for the original bug and passes after the fix.

Assert observable behavior through stable interfaces. Check exact values when they are contractual; avoid assertions that merely copy implementation values or freeze incidental structure.

## Retain useful coverage

Use temporary tests and probes freely during implementation. Before finishing, retain or consolidate those whose future regression protection justifies their upkeep, and remove disposable scaffolding. Realistic verification today does not automatically require permanent end-to-end coverage.

Judge the maintained suite and its supporting infrastructure by total confidence and lifetime cost: runtime, flakiness, diagnosis, fixture upkeep, and friction during legitimate refactors.

Apply a higher bar to heavyweight checks. They can earn their place by covering consequential failures, providing useful complementary protection, or replacing several brittle tests. Explain unusual testing cost or scope; routine tests need no written business case.

Keep behavioral tests near the code that owns the contract. Share checks across implementations of the same contract. Expand test matrices for distinct risks and use representative cases for equivalent behavior.

Change expectations when the intended contract changes. Otherwise investigate failures and preserve meaningful protection when replacing or removing tests. Never weaken assertions or performance budgets merely to pass a check.

## Finish

Keep checks deterministic and failures actionable. Prefer observable conditions or controlled scheduling to fixed sleeps. Restore test state and release resources, including on failure.

Run affected checks against the final code and complete required project checks. A suite's exclusion from routine CI does not waive relevant verification.

Broaden or repeat testing only for a new change, failure, or concrete unresolved risk. Otherwise stop.

Report what ran, the results, and material verification gaps. State the limits of fixtures, mocks, and environments; passing tests do not establish every live integration or human usability judgment.
