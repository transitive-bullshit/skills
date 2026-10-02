# Skills

The workflows I use with coding agents: UI and engineering guidance, brand exploration, storytelling, and personal automation. Custom skills and adopted skills share one editable Git checkout.

[Branding](skills/branding-exercise/SKILL.md) · [Midjourney](skills/midjourney-images/SKILL.md) · [Storytelling](skills/storytelling/SKILL.md) · [All skills and profiles](skills.json)

![Midjourney example](skills/midjourney-images/docs/midjourney-example-output-0.jpg)

## Get started

```text
Set up transitive-bullshit/skills for my coding agents. Read AGENTS.md,
inspect existing skills, and use the mac profile. Preserve local edits,
review conflicts before adopting them, and finish with the doctor check.
For a complete machine setup, use the companion dotfiles repo.
```

Requires Python 3.11+:

```sh
python3 scripts/skillset.py apply --profile mac
python3 scripts/skillset.py doctor
```

Edits through installed skills appear here as Git changes. Commit/push normally; pull and apply on other machines. [Setup notes](docs/setup.md) · [Full environment](https://github.com/transitive-bullshit/dotfiles)

Personal skills are [MIT](license). Adopted skills retain their upstream licenses and attribution, recorded in `skills.json`. Storytelling draws on [Edmund Tian](https://www.instagram.com/edmund.tian).
