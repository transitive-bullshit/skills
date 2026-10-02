---
name: improve-animations
description: "Audit a codebase’s motion and prepare improvement plans. Use for motion audits, roadmaps, or execution of an existing motion plan."
---

# Motion audit and improvement plans

Use for explicit motion audits, roadmaps, plans, or execution of an existing plan. Direct requests to fix motion should proceed to implementation rather than being diverted into an audit-only workflow.

## Select the mode

- Audit: inspect the requested surface, report supported findings, and leave source unchanged.
- Plan: inspect enough context to write the requested self-contained plans; no extra selection round is needed when scope is already supplied.
- Execute or audit-and-fix: implement the authorized changes and inspect the result. Use an isolated checkout when the task requires one, through the host's native tools.
- Reconcile: compare existing plans with current source and update their status and stale evidence.

## Inspect and report

Identify the relevant motion libraries, existing tokens, interaction purpose, and project conventions. Read [shared motion guidance](../better-ui/motion.md) and only the recipes needed for the affected interaction. [AUDIT.md](AUDIT.md) is a compact evidence checklist.

Inspect runtime behavior when timing, interruption, or perceived motion matters. Source searches produce candidates, not confirmed defects. Preserve intentional exceptions, verify cited locations, consolidate shared causes, and rank by consequence and reach. Distinguish measured performance issues, accessibility failures, and optional aesthetic improvements.

Scale investigation to the request. Use independent read-only subagents only when distinct areas justify parallel review. A small component can be reviewed directly. Do not require a fixed number of findings, missed opportunities, or agents.

Report location, evidence, user impact, and the proposed correction. State what could not be verified. Ask the user to select work only when they requested a selection step or a material scope decision remains.

## Deliver

For plans, use [PLAN-TEMPLATE.md](PLAN-TEMPLATE.md). Prefer project tokens and show the intended behavior, affected owners, and relevant checks. Keep an index when producing several plans.

For execution, adapt ordinary source drift within the approved intent; ask only if the plan conflicts with current product requirements. Complete the edits, run relevant checks, inspect affected motion and reduced-motion behavior, and fix failures caused by the change. Report a concrete blocker if required verification is unavailable.
