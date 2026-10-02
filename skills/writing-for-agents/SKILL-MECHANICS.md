# Skill mechanics

Use [writing-for-agents](SKILL.md) for document design. This reference covers skill discovery and invocation.

## Invocation policy

A concise description explains the task that should select the skill. Put scope and important exclusions before workflow details. Preserve existing user preferences about automatic selection.

For Codex, configure explicit-only invocation in `agents/openai.yaml`:

```yaml
policy:
  allow_implicit_invocation: false
```

Merge this into existing metadata rather than replacing UI or dependency fields. Explicit `$skill-name` invocation remains available. Other clients may use frontmatter such as `disable-model-invocation: true`; retain it when needed, but do not assume it configures Codex. Verify the actual host catalog and selection behavior instead of promising zero context cost from a frontmatter flag.

## Shared references

Invocation policy controls automatic workflow selection. Reusable reference material can still be read by another skill when it is relevant. If several workflows share rules, put them in one ordinary reference and link it conditionally. Do not make the user invoke a second skill solely to expose a reusable procedure.

## Routers

Keep a root router only when it helps choose among distinct workflows or substantial references. Give each link its task condition. A small self-contained skill needs neither a router nor extra documents. Avoid loading every branch for one task.
