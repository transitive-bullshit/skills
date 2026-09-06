# Prompt craft

Use this reference for image inputs, multi-direction aesthetic exploration, text in images, and detailed prompt shaping.

## Brief first, prompt second

Use a structured brief internally, but do not paste the labels into Midjourney:

```text
Purpose: <brand inspiration, campaign concept, editorial image, concept art>
Essential content: <subject, action, environment, exact count>
Aesthetic territory: <medium, era/design idiom, emotional register>
Composition: <viewpoint, scale, focal hierarchy, negative space>
Light and color: <light behavior, palette relationship>
Material and texture: <surfaces, grain, finish, atmospheric texture>
Signature move: <one unexpected but coherent use of scale, material, space, or light>
Constraints: <must preserve or exclude>
Canvas: <aspect ratio or placement intent>
```

Turn that into a concise, image-native description. V8-era Midjourney can understand detail, but a single coherent description works better than prose instructions, repeated synonyms, or a long unordered list.

## Calibrate creative latitude

- **Specific brief:** Normalize and sharpen it. Do not invent extra characters, brand claims, slogans, or story beats.
- **Broad aesthetic brief:** Supply tasteful choices for medium, composition, light, palette, material, texture, and atmosphere. Add one signature move rather than a pile of novelty.
- **Exploration request:** Create genuinely different visual theses. Change the governing metaphor, medium, spatial logic, or emotional temperature—not merely adjectives.
- **Precision inside an expressive task:** Keep the essential noun, count, interaction, and framing explicit; allow style and atmosphere to roam.

Fewer details produce more variety. Every added detail should either protect essential content or create a meaningful aesthetic decision.

## Prompt shape

A useful default shape is:

```text
<subject and action>, <environment or visual story>, <medium and design idiom>, <composition or camera>, <lighting>, <palette and materials>, <texture and atmosphere>, <mood> <parameters>
```

Prefer nouns and precise visual adjectives. Describe the image that should exist instead of saying “please make,” “show me,” “copy this,” or explaining how the model should think.

Avoid generic quality incantations such as “award-winning, trending, masterpiece, 8K” unless one is genuinely part of the requested visual language. They dilute more discriminating art direction.

## Reference images by role

Label every input before uploading it:

- **Style Reference:** captures a specific visual vibe—color, medium, texture, or lighting—not the depicted people or objects.
- **Image Prompt:** influences content, composition, colors, and style; it inspires rather than copies exactly.
- **Edit Model reference:** current V8.x route for instruction-led edits, subject consistency, or combining up to four source images.
- **Moodboard:** a broad, project-level aesthetic range rather than one specific look.

With a Style Reference, keep the text prompt focused on the desired final content and remove style words that fight the reference. With an Image Prompt, restate all essential content in text. Crop reference inputs toward the intended final aspect ratio when practical.

Use Omni Reference only when intentionally working in V7. Character Reference is legacy behavior; do not make either part of the current default path.

## Text in images

Midjourney is best used for the visual concept while final typography is added downstream. If the user explicitly wants text in Midjourney:

- keep it to a short word or phrase
- wrap exact text in double quotation marks
- say where and how it appears
- prefer Latin-script text when possible
- lower Stylize or use Raw when accuracy matters
- state that exact spelling is not guaranteed

Use the built-in `imagegen` skill instead when verbatim copy or a controlled layout is central, unless the user explicitly chose Midjourney.

## Iteration

Evaluate concept, composition, style, palette/material, and light/mood separately. Preserve the parts that work and alter one weak dimension at a time.

- **Strong Variation:** explore around a promising visual thesis.
- **Subtle Variation:** polish a nearly successful candidate.
- **Remix:** change wording or parameters while retaining lineage.
- **Fixed seed:** use only for controlled A/B tests; change one phrase or parameter. A seed is not a durable style or character bookmark.
- **Style Reference, style code, or Moodboard:** preserve a direction once it has landed.
- **HD/upscale:** defer until a direction is selected.

## Examples

### Brand world

```text
A future-facing botanical skincare world, monolithic translucent vessels nestled in damp volcanic stone, editorial still life, biomorphic modernism, misty side light, milky jade and oxidized copper, tactile mineral condensation, serene and uncanny --ar 4:5 --s 250 --c 12
```

### Conceptual editorial illustration

```text
A tiny archivist tending a luminous garden grown from tangled memories, vast interior dreamscape, painterly editorial illustration, wide cinematic composition, dim indigo with ember-orange accents, soft atmospheric depth, tender and strange --ar 16:9 --s 750 --c 18
```

### Spatial atmosphere

```text
A neighborhood tea house conceived as a quiet observatory, circular openings framing rain and distant rooftops, restrained Japanese modernism with weathered brass and charcoal timber, eye-level architectural photograph, diffuse blue-hour light, contemplative and intimate --ar 3:2 --s 250
```

## Official anchors

- [Prompt Basics](https://docs.midjourney.com/hc/en-us/articles/32023408776205-Prompt-Basics)
- [Art of Prompting](https://docs.midjourney.com/hc/en-us/articles/32835253061645-Art-of-Prompting)
- [Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference)
- [Image Prompts](https://docs.midjourney.com/hc/en-us/articles/32040250122381-Image-Prompts)
- [Moodboards](https://docs.midjourney.com/hc/en-us/articles/39193335040013-Moodboards)
- [Edit Model](https://docs.midjourney.com/hc/en-us/articles/48495453462797-Edit-Model)
- [Text Generation](https://docs.midjourney.com/hc/en-us/articles/32502277092109-Text-Generation)
