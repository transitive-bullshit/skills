---
name: review-animations
description: "Review motion for supported interaction, accessibility, consistency, and performance problems. Use for an explicitly requested motion review."
disable-model-invocation: true
---

# Review motion

Review the requested diff or surface using [shared motion guidance](../better-ui/motion.md). Resolve the supplied change scope, including uncommitted edits when requested. Consult only references relevant to the affected interactions.

Report supported defects in feedback, continuity, interruption, accessibility, cohesion with the project's system, or measured performance. An opacity-only entrance, a different easing value, or keyboard-triggered motion is not a defect by itself. Preserve intentional project choices and separate optional taste suggestions.

Inspect runtime behavior when it determines the conclusion. Cite source locations and describe the observable consequence and smallest correction. Consolidate shared causes, rank by impact, and state coverage and verification limits. A review with no findings is valid.

A review request is read-only. If the user also asks for fixes, implement the authorized corrections and verify the affected behavior without requiring another invocation. Complete all requested work or identify a concrete blocker.
