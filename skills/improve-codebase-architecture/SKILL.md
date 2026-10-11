---
name: improve-codebase-architecture
description: "Find opportunities for deeper modules and explore the user’s selected candidate. Use when explicitly invoked for architecture exploration."
disable-model-invocation: true
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

This command is _informed_ by the project's domain model and built on a shared design vocabulary:

- Read [codebase-design](../codebase-design/SKILL.md) for deep-module concepts and principles. Preserve the project’s domain vocabulary and explain architecture in the terms that make the candidate clearest.
- The project’s glossary (`GLOSSARY.md`, `CONTEXT.md`, or its documented equivalent) gives names to useful seams. Existing ADRs record decisions this workflow should not re-litigate.

For exploration, present candidates and let the user select a direction. If the user already selected a candidate or requested implementation, proceed within that scope; the exploration workflow does not add another approval round. Keep an audit read-only unless changes were requested.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction (a module, a subsystem, a pain point), take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots, the files and areas that keep coming up, and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Read the project’s existing domain glossary and relevant ADRs before proposing changes.

Inspect the selected scope directly, or delegate independent areas when parallel review helps and the host supports it. Look for concrete friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow**, with an interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file. Open it for the user (`xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows) and tell them the absolute path.

The report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Mix Mermaid with hand-crafted CSS/SVG visuals: use Mermaid when relationships are graph-shaped (call graphs, dependencies, sequences), and hand-built divs/SVG when you want something more editorial (mass diagrams, cross-sections, collapse animations). Each candidate gets a **before/after visualisation**. Be visual.

For each candidate, render a card with:

- **Files**: which files/modules are involved
- **Problem**: why the current architecture is causing friction
- **Solution**: plain English description of what would change
- **Benefits**: explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram**: side-by-side, custom-drawn, illustrating the shallowness and the deepening
- **Recommendation strength**: one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

Use the project’s established domain names and the concepts from `codebase-design`. Translate the architecture terminology to existing component, service, or API names where clearer.

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (e.g. a warning callout: _"contradicts ADR-0007, but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

See [HTML-REPORT.md](HTML-REPORT.md) for the full HTML scaffold, diagram patterns, and styling guidance.

When the request is to choose among candidates, stop at the report and ask which direction to explore. When a candidate is already selected, continue to its interface design or authorized implementation.

### 3. Grilling loop

When an interview is requested or unresolved product decisions require one, use [grilling](../grilling/SKILL.md) to discuss constraints, dependencies, interface shape, and behavior coverage. Reuse settled decisions and continue authorized implementation without repeating an interview.

When documenting the domain is within the requested scope, use [domain-modeling](../domain-modeling/SKILL.md) to record resolved decisions in the existing glossary:

- **Naming a deepened module after a concept not in the project glossary?** Add the term to the project glossary. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update the project glossary right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing; skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Want to explore alternative interfaces for the deepened module?** Read [Design It Twice](../codebase-design/DESIGN-IT-TWICE.md) and compare meaningfully different interfaces.
