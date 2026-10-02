---
name: better-ui
description: "Implement or review focused UI polish using the project’s design system. Use for alignment, surfaces, icons, or interaction detail."
---

# UI polish

Apply the user's requested changes in the project's existing component and styling system. Preserve established tokens, density, icon language, and intentional design choices. Treat the examples in this skill as defaults, not mandatory exact values.

## Focused principles

- Use optical alignment where geometric centering visibly fails. Coordinate nested radii with padding and the existing shape system.
- Use borders for structure or state and shadows for elevation when that matches the project. Image outlines are optional, theme-aware treatments rather than a universal requirement.
- Match icon weight and state treatment to the existing set. Reuse assets and `currentColor` where appropriate; distinct icons can express genuinely different states.
- Give actions clear, timely feedback without adding distracting motion. Preserve state cues when animation is disabled.

For motion, use [motion.md](motion.md) as the shared source for authoring and review. Read a recipe only for the interaction being changed; it does not override project conventions.

## Domain ownership

Consult only the owners relevant to the task:

- [Typography](../better-typography/SKILL.md): wrapping, type scale, font rendering, numeric alignment.
- [Accessibility](../better-accessibility/SKILL.md): names, keyboard/focus, hit areas, semantic behavior.
- [Layout](../better-layout/SKILL.md): grouping, spatial relationships, responsive layout.
- [Colors](../better-colors/SKILL.md): tokens and contrast.
- [Writing](../better-writing/SKILL.md): product copy.

Do not load every owner for a focused polish change.

## Complete the requested work

For implementation, edit the relevant surface, inspect affected states when available, run appropriate checks, and fix failures caused by the change. For review, remain read-only and report supported problems by impact with source evidence and the smallest correction. Optional style preferences are suggestions, not blockers. State actual coverage and unverified checks; no findings is a valid result.
