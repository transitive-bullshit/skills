# Midjourney web workflow

Use this reference only when the user asked to create images, not when they asked only for prompt text. Operate the site through the available browser/computer-use capability, using semantic labels and a fresh UI snapshot after each state change. Never rely on hard-coded coordinates or stale element indexes.

## Open the Create page

1. Use the browser or tab the user explicitly named. Otherwise prefer an existing authenticated Midjourney tab.
2. Open `https://www.midjourney.com/imagine` in a visible tab when no suitable Create tab exists.
3. If an existing Imagine bar contains draft text or attached references, preserve it by opening a fresh Create tab instead of clearing the user’s work.
4. Check for a folder destination indicator. If a folder is active and the user did not request it, do not submit there. Use a neutral Create context; if leaving the folder would change persistent user state, ask first.
5. Verify authentication by finding the Create interface and an editable Imagine prompt input. Current semantic labels include `Create`, `Add Images`, and the prompt entry `desktop_input_bar`, but re-inspect rather than assuming labels remain unchanged.

Distinguish the blocking state:

- **Log In or Sign Up:** leave the tab ready for handoff and use the login notice from `SKILL.md`.
- **Authenticated but no subscription:** say that an active plan is required and leave account or purchase decisions to the user.
- **Still loading or transient site error:** wait for a fresh state and reload once if safe. If the Imagine bar is still unavailable, report the site or browser-control error rather than calling it an authentication problem.

The user must complete authentication, CAPTCHA, two-factor, and plan selection. Do not enter credentials, create an account, purchase a plan, or bypass a site barrier.

## Prepare without changing global state

- Finalize the text and prompt-level parameters before placing them in the Imagine bar.
- Preserve account-wide model, aspect ratio, Stylize, Variety, Weirdness, Raw, speed, Stealth, Personalization, and Moodboard defaults. Do not toggle them merely to reproduce a prompt; persistent changes affect later user jobs.
- Require still-image, normal direct-prompt mode. Conversational mode rewrites the entered text, and V8.1/V8.2 Draft mode currently creates 24 images. If either is active and was not requested, pause before submission and ask whether to disable it or use it; restore any setting the user authorizes changing.
- If the user wants exact reproducibility, note any active Personalization or Moodboard influence visible in the UI or completed job.

## Add user-designated references

Uploading sends the file to Midjourney. The user must have explicitly designated the file for this Midjourney task and be authorized to use it; otherwise ask immediately before upload. Uploaded references can remain in Midjourney’s uploads library and linked prompt history.

For private or unreleased material, proceed only when Stealth is visibly active or after the user explicitly accepts that the upload and resulting creation may be visible or retained by Midjourney. Do not enable Stealth or change public/private settings without the user’s request.

1. Read the browser tool’s file-upload instructions before using its upload control.
2. Activate `Add Images`, upload or choose the intended image, and assign the correct role: Style Reference, Image Prompt, or current Edit Model reference.
3. Verify the attachment appears in the intended section before submitting. Do not attach an image merely because it is present in the conversation.
4. Midjourney’s documented maximum upload size is currently 10 MB. If an input exceeds it, report the limit instead of silently changing the source.

## Submit exactly once

1. Check the prompt for `--repeat` / `--r`, permutation braces, or any other fan-out. Calculate the total jobs and images. For an ordinary request the total must remain one standard four-image batch; otherwise obtain an explicit user count before submission.
2. Capture the pre-submit feed boundary, including the newest visible job IDs or job-specific URLs.
3. Place the complete prompt into the Imagine bar in one operation.
4. Read back the editable field and verify the exact text, parameter order, reference attachments, and effective mode.
5. Submit once with Enter or the visible send control.
6. Identify the new job relative to the captured feed boundary, capture its Job ID or job-specific URL, and use that identifier for all waiting and reporting.

If the submission’s effect is uncertain, inspect the Create or Organize feed against the captured boundary before retrying. Never press Enter repeatedly: duplicate submissions consume additional GPU time. If browser control is lost after any submission attempt, report the job state as uncertain and do not retry until the feed can be checked.

## Wait and inspect

Wait until the identified job visibly completes at 100%, yields its expected image set, or shows a concrete error. Recheck the page periodically with fresh semantic state; do not infer completion from elapsed time alone.

Inspect the completed set visually against the brief in `SKILL.md`. For ordinary creative exploration, leave the full set available and report the strongest candidate rather than spending more GPU time automatically.

Current completed-batch actions may include `Run batch as HD`, `Rerun`, `Use`, and `More`. Opening a candidate may expose `Download Image`, Vary `Subtle`/`Strong`, Upscale `Subtle`/`Creative`, `Quick Edit`, and `Open Editor`. Re-inspect the current page before acting.

## Iterate only within the user’s budget

- **Rerun:** a new image set from the same prompt.
- **Vary Strong:** broader exploration around a selected candidate.
- **Vary Subtle:** smaller refinements.
- **Remix:** change prompt text or parameters while keeping image lineage.
- **Quick Edit / Editor / Edit Model:** local or instruction-led correction.
- **Run as HD / Upscale:** resolution step after selection.

Each action can consume additional Midjourney resources. Use only the iterations, variants, or finishing actions the user requested. Change one dimension at a time and verify that a matching new job appears.

## Download and hand off

Download only when the user asked for a local file or the stated workflow requires one:

1. Open the chosen candidate.
2. Use the visible `Download Image` control.
3. Verify the download completed and resolve its real local path.
4. For project work, copy the chosen file into the workspace without overwriting an existing asset unless replacement was requested.

Keep the live result tab available as a deliverable. Report the exact prompt, reference roles, parameters, number of submitted jobs, completed/error state, result page, selected candidate, and verified download path if any.

If browser control is unavailable before any submission attempt, return the final prompt and `https://www.midjourney.com/imagine`, explain that no job was submitted, and do not claim an image was created. If control becomes unavailable after a submission attempt, say the job state is uncertain and require a feed check before any retry.

## Official anchors

- [Creating on Web](https://docs.midjourney.com/hc/en-us/articles/33390732264589-Creating-on-Web)
- [Getting Started](https://docs.midjourney.com/hc/en-us/articles/33329261836941-Getting-Started-Guide)
- [Logging In and Connecting Accounts](https://docs.midjourney.com/hc/en-us/articles/33390994570509-Logging-In-Connecting-Accounts)
- [Modifying Your Creations](https://docs.midjourney.com/hc/en-us/articles/33329329805581-Modifying-Your-Creations)
- [Image Prompts](https://docs.midjourney.com/hc/en-us/articles/32040250122381-Image-Prompts)
- [Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference)
- [Edit Model](https://docs.midjourney.com/hc/en-us/articles/48495453462797-Edit-Model)
- [Draft and Conversational Modes](https://docs.midjourney.com/hc/en-us/articles/35577175650957-Draft-Conversational-Modes)
- [Using Folders](https://docs.midjourney.com/hc/en-us/articles/34580542725645-Using-Folders)
- [Repeat](https://docs.midjourney.com/hc/en-us/articles/32757107922061-Repeat)
- [Permutations](https://docs.midjourney.com/hc/en-us/articles/32761322355597-Permutations)
- [Stealth Mode](https://docs.midjourney.com/hc/en-us/articles/32019750070669-Stealth-Mode)
- [Managing Image Uploads](https://docs.midjourney.com/hc/en-us/articles/33329380893325-Managing-Image-Uploads)
