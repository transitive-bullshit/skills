# Derivation record

Read this when maintaining `testing-strategy` or refreshing its inputs. The main `SKILL.md` is the consolidated runtime guidance; source copies preserve evidence, not extra instructions to execute.

## Inputs and precedence

1. [Travis Fischer's supplied guidance](../sources/personal-guidance.md) governs proportionality, verification scope, retained coverage, and stopping conditions. [His TDD decision](../sources/personal-decisions.json) keeps TDD optional unless requested.
2. [Matt Pocock's `tdd`](../sources/mattpocock-tdd/49dd158d1076134a641b33efb035946536778336/SKILL.upstream.md), including its `tests.md` and `mocking.md` resources, contributes focused red → green cycles and tests through stable contracts.
3. [David Zhang's `write-tests`](../sources/dzhng-write-tests/d51322866ffa298838346960414d18a221b52588/SKILL.upstream.md) contributes production-faithful fixtures, falsification, controlled comparisons, canonical-value assertions, and isolated test state.

The two upstream skill subtrees are versioned source snapshots at the full commits named in their directories. They retain exact bytes, file modes, and MIT notices. Their `SKILL.md` files are named `SKILL.upstream.md` locally so the installer discovers only `testing-strategy`. Original paths, Git blob IDs, and SHA-256 hashes are recorded in [sources.lock.json](../sources.lock.json).

## Reconciliation

| Source tension | Decision in this skill |
| --- | --- |
| Both upstream workflows prescribe test-first cycles. | Use TDD when useful; require it only when requested. When chosen, keep one behavior slice at a time. This is the user's explicit decision. |
| Matt requires user approval of every test boundary. | Choose established boundaries autonomously; clarify consequential uncertainty about the intended contract. |
| David favors the outermost entry point; Matt favors integration-style checks. | Use the least costly adequate proof: focused units, collaborating-code integration, and real platform or journey checks when needed. |
| Matt excludes refactoring from TDD and requires a separate review skill. | Permit in-scope refactoring while green. No mandatory companion skill or separate approval phase. |
| Both prohibit mocking internal collaborators. | Prefer real collaborators; a substitute is justified only when the relevant failure path remains real and its limits are clear. |
| David says to mock configuration and delete checks of compiler guarantees. | Preserve runtime, configuration, protocol, and schema checks when they enforce actual contracts beyond static guarantees. |
| Matt treats database inspection as an implementation detail. | Assert through the interface that owns the contract; persistence itself can be an observable contract. Do not freeze incidental schema. |
| David prioritizes obsolete tests and loose margins before production defects. | Diagnose from evidence. Never weaken an assertion or performance budget merely to pass. |
| David prescribes a full-suite final gate and links to `audit-tests` for retention. | Run affected and required project checks; broaden for concrete risk. The user's lifetime-cost policy governs retention without another skill dependency. |
| David forbids visible UI tests but also allows necessary real launches. | Prefer isolated offscreen checks when sufficient; real platform evidence may require visible interaction. Minimize disruption and disclose it. |

Repeated guidance on behavioral assertions, independent expectations, regression falsification, real collaborators, and cleanup appears once in the combined skill. Generic architecture prescriptions and unconditional deletion of production code used only by tests were not adopted.

## Refresh procedure

This is a reviewed synthesis, not deterministic generation. Recipe version 1 is this record plus the precedence and decisions above.

1. Fetch each upstream repository into a temporary checkout. Compare its current head with the pinned source; do not overwrite old version directories. Add the complete new skill subtree and license under a new full-commit directory, preserving bytes and modes and renaming only `SKILL.md` to `SKILL.upstream.md`.
2. Review changed guidance against the personal inputs and this reconciliation. Edit the consolidated skill deliberately; a source update does not automatically override a local decision. Keep a change from the user as a versioned personal input.
3. Update the active source paths, commits, original-to-stored path mappings, and file hashes in `sources.lock.json`. Older snapshot directories may remain as history. Never change input hashes just to silence a failed integrity check.
4. Validate the skill on fresh, realistic requests, including a low-risk edit, regression falsification, and explicitly requested TDD. Inspect both unjustified testing cost and missed consequential behavior. These are behavior checks, not prescribed wording.
5. Format authored files, then run `python3 scripts/upstream.py record testing-strategy` to record the reviewed output hashes. This command checks frozen input integrity before recording outputs; it does not fetch or synthesize sources. Format `skills.json` and the lock JSON if needed, run `pnpm test`, apply the shared environment, and finish with `agent-env doctor`.

`python3 scripts/upstream.py check testing-strategy` verifies the pinned source files, personal inputs, and recorded outputs. It proves artifact integrity; it does not prove that a future agent will make the right testing judgment.
