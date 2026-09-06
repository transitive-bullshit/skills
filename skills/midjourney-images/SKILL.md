---
name: midjourney-images
description: Craft expressive Midjourney prompts and create images in the midjourney.com web app. Use for explicit Midjourney requests or open-ended aesthetic exploration.
---

# Midjourney Images

Use Midjourney as an art-direction studio: discover expressive, taste-led visual worlds when the content can tolerate interpretation. The built-in `imagegen` skill remains the production default for concrete assets, exact dimensions, text or layout constraints, transparent output, precise edits, and tight instruction following.

## Route deliberately

- Use this skill when Midjourney is explicitly requested for the current stage of work.
- Invoke it implicitly only when exploring the aesthetic direction is itself the task: brand worlds, visual language, campaign mood, concept art, material or spatial studies, and high-level look and feel.
- Words such as “beautiful,” “cinematic,” or “polished” alone do not make a request a Midjourney task.
- An explicit provider choice wins. If the user chooses Midjourney for precision-heavy work, briefly flag the likely fidelity tradeoff and continue with Midjourney.
- For mixed exploration and production, use Midjourney to discover the direction. Move to `imagegen` or native design tools for the final controlled asset only when the user requested that production stage or approves it.

## Choose the mode

**Prompt only:** When the user asks to write, improve, or translate a prompt, return copyable prompt text without opening or submitting it in Midjourney.

**Create on web:** When the user asks to create, generate, make, or show the image with Midjourney, craft the prompt and operate the web app. One ordinary create request authorizes one standard four-image batch per distinct requested prompt. Draft mode, Repeat, permutations, Rerun, Vary, Remix, Edit, and additional submissions can create more images or jobs; use them only when the user explicitly requests the resulting fan-out or gives an iteration count or stopping rule.

Uploading an image sends it to Midjourney. Upload only images the user explicitly designated for this Midjourney task. Do not assume that an account, upload, or creation is private.

## Craft the prompt

1. Distill the request into an internal creative brief: intended use, essential subject/content, desired emotional effect, aesthetic territory, framing/aspect ratio, references, and hard constraints.
2. Preserve a detailed user brief. When the request is broad, add selective art direction—medium, composition, light, palette, materials, texture, atmosphere—and one coherent signature move that gives the direction character.
3. Compress the brief into one concise but complete description of the final image. Prefer concrete visual language over conversational instructions or keyword soup.
4. Use a coherent order: subject/action → environment or story → medium/design idiom → composition/view → lighting → palette/material/texture → mood.
5. Keep only three to six visually decisive style signals. Remove repetition and accidental conflicts. Describe desired content positively; reserve `--no` for concrete exclusions.
6. Append only useful, current parameters at the end. Prefer the site’s current default model and prompt-level parameters over changing persistent settings. Read [references/parameters.md](references/parameters.md) before using version-sensitive or unfamiliar controls.

For image references, multi-direction exploration, text-in-image requests, or prompt examples, read [references/prompting.md](references/prompting.md).

## Create in the web app

Read and follow [references/webapp.md](references/webapp.md). The happy path is an already authenticated browser session at `https://www.midjourney.com/imagine`.

If the site shows Log In or Sign Up, leave the browser on that page and tell the user:

> Midjourney needs you to sign in with Google or Discord before I can continue. Please complete sign-in—including any CAPTCHA or two-factor step—in the open browser tab and return to the Create page, then tell me you’re ready. Don’t send credentials here.

If the user is authenticated but the account lacks an active plan, say that a subscription is required and ask them to handle it in the open tab. Never enter passwords or one-time codes, solve a CAPTCHA, create an account, purchase or change a plan, or silently fall back to another generator. Resume in the same tab after the user confirms they are ready.

## Inspect and iterate

Judge every completed image set against the internal brief, separating:

- concept and subject
- composition and scale
- visual language and medium
- palette, material, and texture
- lighting, atmosphere, and emotional tone
- explicit constraints

For user-authorized iteration, change one variable at a time. Use Strong Variation to search around a promising concept, Subtle Variation to polish it, and Remix when prompt text or parameters should change. Preserve the successful parts of the direction explicitly.

## Completion

A prompt-only task is complete when the user has the final copyable prompt and any requested distinct alternatives.

A web task is complete when the identified job visibly reaches its requested completed batch at 100% or a concrete site error is reported. Keep the Midjourney result tab available. Download a candidate only when requested or needed by the user’s stated workflow, and verify the saved file before reporting it.

Always report the exact prompt delivered or submitted. For web tasks, also report the effective parameters, how many jobs were submitted, whether the result completed or needs user action, the result page, and any verified downloaded path.
