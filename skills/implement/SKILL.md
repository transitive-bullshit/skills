---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets. Reuse established decisions and public interfaces.

Use [TDD](../tdd/SKILL.md) when test-first work was requested. Otherwise choose verification appropriate to the change. Complete the implementation, run relevant checks, inspect the result where needed, and fix failures caused by the change.

Review the diff for defects and missed requirements before delivery. Follow the user's requested commit/PR workflow; do not create an unrelated commit merely to satisfy this skill.
