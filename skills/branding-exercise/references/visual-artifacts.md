# Visual artifacts

Read when building exploration posters and when exporting the accepted identity. Author the project's composition and build script to suit its brand; a fixed bundled layout would constrain the visual exploration.

## One-page posters

Include the following in every direction's poster:

- Brand name and proposed mark/wordmark.
- Main one-liner, literal product descriptor, and mantra.
- Hero or representative brand imagery, including a vector illustration when that suits the direction.
- A concise statement of character, belief, or desired feeling.
- Palette with named roles and exact values.
- Typography samples and a small example of the identity in use.

Show comparable content at comparable viewing sizes while allowing composition, typography, imagery, and density to express each direction. A 1600×2040 portrait canvas is one workable starting point, not a required aesthetic or aspect ratio. Give the poster a strong hierarchy that communicates the identity at a glance; keep longer rationale in the Markdown.

Use application mockups when they clarify the project's actual form factor. Label speculative interfaces or product scenes as concepts. Present full-resolution posters with an overview/contact sheet or local comparison view when useful; preserve access to each full poster.

## Reproducible build

Author a project-local script using an available runtime and graphics libraries. Save it, rendering inputs, and source assets near the project's brand documentation. Use the project's existing toolchain when suitable; document any added runtime, dependency, or font requirements. Record a command actually run successfully from a stated directory.

Produce an editable SVG poster and a PNG rendering. Keep vector elements and typography editable in the poster SVG; embed raster imagery as data URLs so image paths cannot break when the SVG is moved. Use stable font inputs or document required fonts and fallbacks. Preserve native geometry in separate logo masters; outline approved logo lettering where needed for portability.

The semi-structured Markdown is the source of brand decisions and approved copy. Either parse its relevant fields or maintain an explicit render projection such as JSON. For a projection, map its fields to the Markdown and validate copy, palette, asset paths, and selected direction against that document before export. State which file supplies each part of the rendering. A script reading JSON must not be described as parsing Markdown.

Lay out text with reliable measurement, wrapping, or intentional line breaks. Preserve approved wording when fixing overflow. Keep the rendering code focused on the current project's design, with asset paths relative to its own location or an explicit project root. Retain build sources and inputs alongside finished images.

## Accepted export set

Persist these files after acceptance or delegated selection; use the project's existing naming convention:

| Deliverable | Requirements |
| --- | --- |
| Logo mark and wordmark | Separate native SVG masters; full-color and monochrome/light/dark variants as appropriate. |
| `favicon.svg` | Square viewBox, recognizable at small sizes; document simplification if needed. |
| `favicon.ico` | Genuine ICO with 16×16, 32×32, and 48×48 embedded images, not a renamed PNG. |
| Social preview | Exactly **1200×630 pixels**, normally PNG or JPEG; compose specifically for this crop using the accepted mark, copy, and visual language. |
| Hero and supporting assets | Save the accepted reusable imagery at useful quality, with alt text and provenance/prompt references. |
| `brand-identity-onepager.svg` and `.png` | The final identity poster, synchronized with the accepted Markdown. |
| Build source and inputs | Runnable poster/asset build script, local assets, and any render data; document regeneration. |

Construct logo vectors from editable geometry; a bitmap inside an SVG wrapper does not satisfy the native logo requirement. Use transparent icon backgrounds where the intended surface requires them. Keep important social-preview content comfortably within the image and inspect it at reduced size.

## Export verification

Run the build and visually inspect the actual poster, social image, logo, and icons. Check clipping, wrapping, contrast, crops, font substitution, exact copy, and consistency with the accepted identity. Inspect favicons at their real display sizes. Verify image dimensions and file formats, including the ICO's embedded sizes.

Check that the SVG embeds its image dependencies, then render a copy from a separate directory to catch broken paths without moving or removing source files. Rebuild after corrections. Confirm the documented command reproduces the delivered artifacts, all links resolve, and only the accepted direction is labeled canonical. A failed or unrun export remains unfinished; describe the specific blocker instead of claiming the full package is complete.
