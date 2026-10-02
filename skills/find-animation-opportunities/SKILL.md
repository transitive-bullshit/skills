---
name: find-animation-opportunities
description: "Suggest evidence-backed opportunities for motion. Use when asked where animation would help; return recommendations without implementation."
---

# Find useful motion opportunities

Use for an explicit request for recommendations about where motion would help. For a request to add or improve motion directly, implement the requested change using [shared motion guidance](../better-ui/motion.md).

Inspect the requested flow and its design system. Suggest motion only when it clarifies feedback, state, continuity, or an intentional expressive moment. Prefer no motion where it adds repeated attention cost without helping the task.

For each recommendation, cite the actual surface and evidence, explain the benefit, and name the relevant project tokens or clearly labeled starting values. Include reduced-motion behavior and any meaningful performance tradeoff. Keep optional aesthetic changes separate from defects.

A recommendations-only task is complete with a prioritized, supported set of suggestions and its inspection limits. Do not require a fixed number of rejected candidates. If the user asks to apply a suggestion, implement it and verify the result within that scope.
