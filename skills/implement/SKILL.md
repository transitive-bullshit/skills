---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets. Reuse established decisions and public interfaces.

If the user passes a ticket reference, fetch it from the configured tracker and state its title before starting. Resolve genuinely ambiguous references before acting on them.

Use a failing-test-first loop when the user requests test-first work; otherwise choose verification appropriate to the change. Complete the implementation, run relevant checks, inspect the result where needed, and fix failures caused by the change.

Review the diff for defects and missed requirements before delivery. Follow the user’s requested commit/PR workflow; do not create an unrelated commit merely to satisfy this skill.
