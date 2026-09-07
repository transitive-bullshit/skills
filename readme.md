# Personal Skills

Reusable skills for AI coding agents.

## Midjourney Images

[![skills.sh installs](https://skills.sh/b/transitive-bullshit/skills)](https://skills.sh/transitive-bullshit/skills)

[`midjourney-images`](skills/midjourney-images/SKILL.md) writes focused Midjourney prompts and can create images in the Midjourney web app. Use it to explore a visual style, build a brand world, or develop concept art.

<p align="center">
  <img src="skills/midjourney-images/docs/midjourney-example-output-0.jpg" alt="A lone artist beneath a vast, translucent structure" width="49%">
  <img src="skills/midjourney-images/docs/midjourney-example-output-1.jpg" alt="A lone artist facing a vast, cloud-like spiral" width="49%">
</p>

The skill supports two tasks:

- **Prompt only:** Write or improve a prompt without opening Midjourney.
- **Create on web:** Submit one standard image batch and report the result.

Install it with the Skills CLI:

```sh
npx skills add transitive-bullshit/skills --skill midjourney-images
```

## Keep local skills in sync

Run this command from the repository:

```sh
pnpm link:skills
```

It links each repository skill to `~/.agents/skills`. Edits made through either path appear as changes in this repository. The command stops if a regular file or directory already uses a skill name.

## License

[MIT](license) by [Travis Fischer](https://x.com/transitive_bs).
