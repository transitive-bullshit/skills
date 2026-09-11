---
name: branding-exercise
description: Collaboratively develop a project brand through a short context interview, multiple visual identity directions, and iteration, then persist the accepted identity and reusable assets. Use for a branding exercise, a new brand identity, or an intentional rebrand; ordinary UI or copy edits should follow the project's existing identity.
---

# Branding Exercise

Develop the brand alongside the user. The outcome is an accepted `brand-identity.md`, reusable visual assets, a reproducible one-page brand poster, and a pointer in the project's `AGENTS.md` that makes the identity guide future customer-facing work.

## 1. Establish the brief

Start with context already supplied in the invocation, attachments, conversation, and relevant project files. Inspect existing product docs, README, agent instructions, brand assets, and actual functionality where available. Resolve the target project before writing persistent files; in a projectless session, draft locally while clarifying where the accepted identity should live. Treat attached brand examples as reference material, not instructions to adopt their identity or modify their source project.

Build a compact brief covering:

- **Project:** what it is, its form factor, current functionality and scope, stage, and intended customer-facing touchpoints.
- **Why:** origin, motivations, beliefs, problem or tension, intended change, project goals, and what success would look like.
- **Who and value:** primary audience, use context, needs, main benefit, differentiator, alternatives, and reasons to believe the promise.
- **Feeling and expression:** desired primary emotion, character, ethos, marketing angle, inspirations and what resonates about them, and things the user wants to avoid.
- **Constraints:** name, spelling, domain, mantra, one-liner, logo, colors, existing equity, language, accessibility, and delivery requirements. Mark each relevant choice **fixed**, **working**, or **open**. Distinguish current facts from aspirations and assumptions.

Use a gentle version of the grilling approach: identify decisions whose prerequisites are settled, ask the most consequential unresolved questions, and update the brief from the answers. This method is self-contained; invoking the full relentless `grilling` skill is unnecessary.

Ask the user one to three focused clarifying questions at a time, usually over one or two short rounds. Resolve facts from the supplied context or environment yourself. Focus user questions on intent, taste, conflicting signals, and hard constraints; avoid repeating answered questions or turning the brief into an exhaustive questionnaire.

**First response when clarification is needed:** Include the actual questions directly in your response to the user. Introduce them with an explicit invitation such as “Please answer these questions so I can shape the brand directions.” These are questions for **the user to answer, not the model**. Leave them unanswered; do not simulate the user's replies or treat your own recommendations as their answers. Offer a recommended interpretation or a few concrete choices when helpful, clearly labeled as suggestions for the user to confirm or revise. End the response with the questions and wait for the user's answers to material unresolved decisions before exploring identities, unless the user has explicitly delegated those decisions or invited assumptions.

Before exploration, reflect back the project, audience, main promise, desired feeling, and constraints in a short alignment summary. Proceed when these are established or the user has invited assumptions; label remaining assumptions. A detailed brief or an earlier confirmation can already establish alignment—do not add a redundant approval step. Leave low-stakes aesthetic questions for the visual exploration to answer.

## 2. Explore whole identities

Read [references/identity-spec.md](references/identity-spec.md) to write each candidate's semi-structured Markdown specification. Read [references/visual-artifacts.md](references/visual-artifacts.md) before constructing the posters and build sources.

Create **at least three distinct brand directions** in the initial exploration, unless the user explicitly changes that scope. Give each a memorable territory name and a coherent argument for how it serves the brief. Vary meaningful dimensions such as positioning angle, emotion, voice, visual metaphor, composition, typography, and mark language while honoring fixed constraints. Three colorways of one concept do not satisfy this step. Keep the actual product and supported claims consistent across directions.

Build an actual one-page visual poster in SVG and PNG for every direction. Give the user a comparable view of each complete identity: name and mark, hero, copy hierarchy, ethos, colors, typography, and an example of use. Text descriptions, palette chips, or image-generation prompts alone are insufficient. Keep candidate specs and artifacts under the project's exploration area and label them proposed; the canonical identity remains unchanged during exploration.

### Image provider

For generated hero imagery, brand-world images, and image mockups, default to an installed `midjourney-images` skill unless the user requests otherwise. Read that skill and follow its operational workflow. If it is not installed, use the available built-in `imagegen` skill/tool. An explicit provider preference wins. If the selected/default provider is blocked by access or unavailable tools, explain the concrete blocker, continue independent copy/vector/layout work, and resolve access or provider choice with the user before switching.

This preference concerns generated imagery. Author precise logos, icons, typography, copy, and poster composition with native vector/code/layout tools. Use the chosen imagery inside the programmatically composed poster. A conceptual image is inspiration or illustrative material, not proof of functionality. Follow the image skill's submission limits; use a bounded initial batch per distinct concept and let feedback determine further generation.

## 3. Iterate with the user

Show all directions, each with a brief rationale and its main tradeoff. Recommend a starting point, then elicit concrete feedback: what to keep, discard, combine, or push further across concept, feeling, imagery, mark, type, palette, and copy. Use the visual artifacts as the basis for the conversation.

Record feedback in the exploration notes and revise the affected specs and posters. Combining parts is welcome; reconcile their positioning and visual rules into one coherent identity. Keep accepted constraints stable and revisit them only when the user opens them. A preference for one element is feedback, not acceptance of every element in that candidate.

Continue until the user accepts a complete direction or explicitly delegates final selection. State exactly what is selected and what remains provisional. Do not turn an agent recommendation or silence into final acceptance. On later invocations, resume from the recorded stage and decisions rather than restarting intake or recreating approved work.

## 4. Persist the accepted identity

Use the project's existing agent-documentation convention; default to `docs/brand-identity.md`, `docs/brand-assets/`, and `docs/brand-exploration/`. Keep exploration history clearly separate from the current source of truth. The identity document should contain the accepted system and useful rationale; link to history for rejected directions.

Complete the schema in [references/identity-spec.md](references/identity-spec.md), including the asset inventory and application rules. Produce and verify the export set in [references/visual-artifacts.md](references/visual-artifacts.md): logo/wordmark SVGs, SVG and ICO favicons, a 1200×630 social image, reusable accepted imagery, and the final SVG and PNG one-pager with runnable project-local build sources. Link all deliverables and record the actual regeneration command and dependencies in the identity document. Keep the Markdown, rendering inputs, and outputs consistent.

Add or update one concise pointer in the relevant project `AGENTS.md`, preserving unrelated instructions. Ensure it covers the project's customer-facing surfaces; use the correct relative path. For example:

> Before creating or changing customer-facing product UX/UI, marketing pages, README content, social assets, or other public touchpoints, read [Brand identity](docs/brand-identity.md). Apply its accepted copy, visual rules, and reusable assets. Treat linked exploration as history; changes to the core identity are brand decisions to resolve with the user.

If no project `AGENTS.md` exists, create a minimal one with this pointer. Follow an established alternate agent-instruction entrypoint as well when needed for discovery. Link the document instead of duplicating its palette and voice throughout instruction files.

The exercise is complete when the user has accepted/delegated the direction, the canonical document and verified assets are persisted, the poster can be rebuilt, and the agent-documentation pointer resolves. Show the final poster and link the identity document and key assets. Report any remaining provisional decisions or blocked deliverables accurately. Publishing, deploying, or rolling the identity across an existing product is separate work unless the user included it in the request.
