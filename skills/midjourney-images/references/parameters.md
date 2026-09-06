# Current controls and parameters

Use the visible web UI and current official documentation as the source of truth. Midjourney models and feature compatibility change. The facts below were checked on 2026-09-05, when V8.2 was the default.

## Syntax

Parameters belong at the end of the text prompt. Leave a space before each `--parameter`, keep values clean, and put no descriptive prompt text after the first parameter.

Prefer prompt-level parameters because account-wide settings persist across future jobs. Preserve the user’s existing model, Personalization, Moodboard, privacy, and speed settings unless they explicitly ask to change them.

## Core expressive controls

- `--ar W:H`: sets aspect ratio and composition shape, not exact pixels. Match the intended canvas. Route exact pixel requirements to built-in `imagegen` unless Midjourney was explicitly requested.
- `--s N` / `--stylize N`: current range `0–1000`, default `100`. Higher values give the Midjourney aesthetic more freedom and can reduce literal adherence. Current presets are `50`, `100`, `250`, and `750`; `250` is a useful expressive first pass, while `750` grants substantial latitude.
- `--c N` / `--chaos N`: current range `0–100`. Higher values make the four outputs more diverse and less predictable. Raise it modestly for aesthetic exploration; keep it low when comparing details.
- `--w N` / `--weird N`: current range `0–3000`. Adds unconventional choices. Start low and use only when strangeness is part of the brief.
- `--exp N`: current V8.x expressive control, currently `0–100`. Start with a low value and increase deliberately; it can add detail and dynamism while reducing accuracy and competing with Stylize or Personalization.
- `--raw`: reduces Midjourney’s automatic styling. Use for more literal control, photographic realism, or when a carefully authored style description should dominate.
- `--no <items>`: excludes concrete unwanted content. First describe the desired alternative positively. Keep exclusions simple because words in the exclusion can be interpreted independently.
- `--seed N`: holds initial noise stable for a controlled A/B test. It is not a durable style, identity, or composition lock.

Use as few controls as will meaningfully change the search. `--s`, `--c`, `--w`, and `--exp` all trade some fidelity for expression; stacking high values produces drift rather than “more taste.”

## Image-guided controls

- `--iw`: increases an Image Prompt’s influence. Supported ranges vary by model; verify before using.
- `--sref`: applies a Style Reference URL or style code. `--sref random` can discover an unexpected reusable style code.
- `--sw`: controls Style Reference strength, currently `0–1000` with default `100`. It is not compatible with Moodboards.
- `--p`: selects Personalization or a Moodboard. Because the site’s P control may persist, use it only when the user requests that profile or moodboard.
- `--edit`: current V8.x edit path. Prefer the website’s Edit Model interface for uploads and instruction-led edits.

## Current-version traps

- Use the website’s current default model unless the user names a version or reproducibility requires pinning one.
- The current V8.x compatibility chart does not support `::` multi-prompts or `--quality`; do not put either in the default recipe.
- Use visible SD/HD controls for current V8.x resolution. Select a direction before spending resources on HD or upscaling.
- Draft mode currently creates 24 low-resolution images from one V8.1/V8.2 prompt. Use it only when the user explicitly authorizes that batch size.
- `--repeat` / `--r` and `{a, b}` permutation syntax fan one submission into multiple billed jobs. Expand the count before submission and use them only when that total is within the user-authorized job count.
- If the generic parameter list and the version compatibility chart conflict, follow the compatibility chart and the visible site UI.

## Official anchors

- [Parameter List](https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List)
- [Version and compatibility chart](https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version)
- [Aspect Ratio](https://docs.midjourney.com/hc/en-us/articles/31894244298125-Aspect-Ratio)
- [Stylize](https://docs.midjourney.com/hc/en-us/articles/32196176868109-Stylize)
- [Chaos / Variety](https://docs.midjourney.com/hc/en-us/articles/32099348346765-Chaos-Variety)
- [Weird](https://docs.midjourney.com/hc/en-us/articles/32390120435085-Weird)
- [Experimental aesthetics (`--exp`)](https://updates.midjourney.com/v7-update-editor-and-exp/)
- [Raw](https://docs.midjourney.com/hc/en-us/articles/32634113811853-Raw)
- [No](https://docs.midjourney.com/hc/en-us/articles/32173351982093-No)
- [Seeds](https://docs.midjourney.com/hc/en-us/articles/32604356340877-Seeds)
- [Draft and Conversational Modes](https://docs.midjourney.com/hc/en-us/articles/35577175650957-Draft-Conversational-Modes)
- [Repeat](https://docs.midjourney.com/hc/en-us/articles/32757107922061-Repeat)
- [Permutations](https://docs.midjourney.com/hc/en-us/articles/32761322355597-Permutations)
