---
name: improve-ui
description: "Audit an interface for design inconsistencies and prepare implementation plans. Use for explicit UI audits, design-system drift reviews, or planning requests."
---

# UI design audit

Use this workflow for an explicit design audit or implementation-plan request. A direct request to fix, refine, or improve an interface authorizes implementation; perform that work using the relevant design references instead of stopping at a plan. When an audit is followed by a request to apply findings, continue with the authorized scope.

## Audit

Select the surface named by the user, or one coherent primary flow when the request is broad. Trace its routes, components, variants, tokens, and styles. Consult current design documentation governing that surface; drafts and unrelated applications do not establish a contract.

Inspect the rendered interface when visual or interaction evidence is needed and local inspection is available. Source can establish a token or copy inconsistency; it cannot by itself establish perceived hierarchy, clipping, or animation feel. Mark unavailable checks as unverified.

Report problems supported by a binding project decision, an internal contradiction, or observed harm to the requested user flow. Preserve deliberate design choices. Cite the responsible source and explain the consequence and smallest supported correction. Consolidate findings with the same cause, rank by user impact, and separate defects from optional design suggestions. A review with no supported findings is valid.

Keep an audit read-only unless implementation was requested. Run only relevant, safe checks. Broaden into accessibility, performance, or functional diagnosis when the request calls for it; disclose significant adjacent blockers without claiming a comprehensive audit of those domains.

## Plans and implementation

If plans were requested, produce them for the requested scope without an extra selection gate. Use [the plan template](references/plan-template.md), reusing existing tokens and component owners. Ask only when unresolved product intent changes the correction or the user explicitly wants to choose among alternatives.

If implementation was requested, apply the supported changes and verify the affected surface. Do not turn an approved fix into another planning round.

Complete the requested audit, plans, or implementation and report the scope, evidence, verification, and any concrete remaining blocker. Future optional work is not a reason to stop the authorized task early.
