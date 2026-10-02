---
name: tdd
description: Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
---

# Test-driven development

Use when test-first development is requested. Work in small behavior slices: failing test, minimal implementation, then refactor while keeping the behavior green.

## Choose a meaningful seam

Use the public interface established by the request, repository, and existing tests. State the seam when it helps explain the work and proceed without reconfirming settled decisions. Ask only when choosing an interface would decide unresolved product behavior or materially change the scope.

When the interface itself needs design work, consult [codebase-design](../codebase-design/SKILL.md) for relevant concepts, preserving the project's terminology.

## Keep tests useful

Verify externally observable behavior rather than private methods or collaborator wiring. Expected results must come from a spec, a worked example, or independently known values, not a restatement of the implementation. See [tests.md](tests.md) and [mocking.md](mocking.md) when examples or mocking choices matter.

Implement one behavior at a time rather than writing a speculative suite for an imagined design. Observe the test fail for the intended reason, implement the behavior, and observe it pass. Refactor when it improves the changed code without expanding scope.

Complete the requested behavior and run relevant checks. Broaden testing when the change or a failure warrants it; unrelated baseline failures do not automatically require approval to continue. Report remaining evidence gaps and do not equate a passing implementation-shaped test with correctness.
