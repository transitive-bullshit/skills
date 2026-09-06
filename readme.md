# Repaint

![repaint](docs/brand-assets/repaint-wordmark.svg)

**The web is a rental. Paint anyway.**

Repaint's finalized **Default dissent** identity, reusable assets, voice, and product explanations live in the [brand guide](docs/brand-identity.md). The complete [brand exploration](docs/brand-exploration/README.md) is preserved as decision history.

**Current progress:** [Done, next steps, and review items](docs/status.md).

Repaint is a Chrome extension that applies expressive themes to supported websites, bringing your taste to familiar places while keeping their content and controls. The current local proof of concept starts with X and includes Cyberpunk, Lo-fi, and Petal themes, adjustable artistic controls, and independent Focus mode and Copy Markdown features. Next.js Studio provides the authoring workspace; the extension applies the same runtime to an existing tab.

The implementation is ready for local review. Browser evidence is recorded by surface and scenario; fixture results alone do not establish authenticated-X compatibility. See the [verification record](docs/verification.md) for completed checks and remaining work, the [MVP agreement](docs/repaint-mvp.md) for scope, and the [implementation plan](docs/implementation-plan.md) for contracts and milestones.

## Start locally

Use Node.js **22.18 or newer**, **pnpm 12.3.4**, and current desktop Chrome.

```sh
pnpm install
pnpm dev
```

This starts Studio at [http://127.0.0.1:3000](http://127.0.0.1:3000) and the Vite/CRXJS extension development server on port 5173. Keep both processes running while reviewing the development extension. To run either independently, use `pnpm dev:studio` or `pnpm dev:extension`.

Studio initially uses **Local fixture**: interactive sample content with home, post, and profile routes, a composer, native controls, and dynamically inserted posts. This mode works without an extension or X account. Its preview values stay local to Studio until an explicit source save.

## Load the development extension

1. Start `pnpm dev` and wait for the extension output to appear.
2. In Chrome, open `chrome://extensions`, enable **Developer mode**, and choose **Load unpacked**.
3. Select **`apps/extension/dist`** from this checkout. Copy the extension's 32-character ID.
4. Open an authenticated [X tab](https://x.com/home), then reload it after loading the extension.
5. Click the Repaint toolbar action to open its side panel. Choose a theme or enable a feature.

For a repeatable extension target without an account, open [the extension fixture](http://127.0.0.1:3000/extension-fixture). This separate page gives the extension ownership of the preview; Studio's built-in local fixture manages its own runtime.

To pair Studio with the extension, open Studio in the **same Chrome profile**, select **Live X tab**, paste the extension ID, click **Connect**, and choose a connected target. Keep that target beside Studio to see updates. The target list distinguishes the local extension fixture from X.

The Studio bridge accepts only `http://127.0.0.1:3000` and `http://localhost:3000`, and exists only in the development extension. If a target is disconnected, reload the extension and target tab, then refresh Studio's targets. Background-worker or manifest edits can require that same reconnection.

After restarting the extension development server or installing changed dependencies, reload the extension once in Chrome's extension manager, then reload its target tabs. CRXJS assigns a new development connection token on restart; an older worker can still answer Studio commands while silently missing source updates. Ordinary theme, shader, artwork and authored-default edits update in place after that connection is established. Repaint pins a small [CRXJS correction](patches/README.md) for this source-update path.

## Theme and feature behavior

- Themes and features start off. A site may use the global default theme, select its own theme, or explicitly turn themes off.
- Personal options are saved once per theme in Chrome's local extension storage. They follow that theme across supported sites. Reset replaces those values with the theme's authored defaults.
- Switching or clearing a theme preserves enabled features. Focus mode hides identified recommendations and promotions without removing their layout space or changing feed width. Copy Markdown exposes hover/focus actions for available post and profile content.
- **Restore this site** writes a persistent theme-off override and disables that site's features. It retains personal theme options and leaves other site preferences intact. **Restore preview** affects only Studio's local fixture.
- Theme rendering uses WebGPU through vGPU. Static styling remains when GPU visuals are unavailable. Theme activation failures release owned changes while features remain independently usable.

## Author a theme

Theme source lives in `themes/cyberpunk/src`, `themes/lofi/src`, and `themes/petal/src`. Each theme defines its manifest, options, rendering behavior, and authored `defaults.json`; shared rendering support lives in `packages/theme-renderer`.

Studio has three workspaces. **Art direction** develops the scene brief and reference choices for artwork; **Live preview** tunes the executable theme on sample content or a connected browser tab; **Confidence** shows dated review evidence and remaining release gates for each theme/site pair.

In [Art direction](http://127.0.0.1:3000/art-direction), choose an existing theme source, select up to four style references, and adjust the scene brief, style weight and model version. **Copy prompt** and **Open Midjourney** prepare the image exploration. **Save direction** writes `themes/<id>/art-direction.json`, including build notes that stay out of the prompt. The default model is V8.2; V7 additionally offers style interpretation 6 or legacy 4. Studio emits `--sv` only for V7 with selected references. See the [art-direction guide](docs/art-direction.md) for the reference library, parameter behavior and artwork approval workflow.

Art direction edits the three registered sources. Creating another executable theme requires an agent to implement and register a package from approved artwork and the saved brief.

Tune the shared controls in **Live preview**. Cyberpunk exposes neon ink, rain density/drift, atmosphere, surface opacity and film grain. Lo-fi exposes lavender ink, window rain/drift, lamplight, paper opacity and paper texture. Petal supplies its own floral artistic controls. **Save as theme defaults** validates the selected values and deliberately writes that theme's `src/defaults.json`. Review the resulting Git diff before committing. Ordinary controls never write source: live-tab edits save personal extension preferences, while local-fixture edits remain in the preview. Both kinds of source save are available only with development Studio.

Workspace package exports point directly to TypeScript source. Next and Vite consume that source and run separate hot-reload graphs; no per-package tsdown watcher is needed. Package builds generate ESM/declarations and compiled publication mappings. The content host owns ordered teardown and recreation during HMR; the verification record distinguishes watcher checks from installed-extension and authenticated-X behavior.

Cyberpunk's neon-Tokyo concept remains provisional pending approval. Lo-fi uses the approved rainy apartment artwork. Petal uses approved floral artwork; its wider transparent foreground remains unfinished. Source assets are build inputs; generation is outside the build.

## Internal stress theme

Open [Kitchen Sink in Studio](http://127.0.0.1:3000/?theme=kitchen-sink) to exercise two WebGPU passes, three warp patterns, orbiting shapes, a composer halo and all four control kinds. Freeze motion and scrub the frame to compare output; renderer diagnostics show submitted frames and owned layers. It is included in Studio and the development extension, and excluded from the production extension and default standalone builds. See the [stress-theme guide](docs/kitchen-sink.md) for limits, fallback behavior and tests.

## Build and check

```sh
pnpm test
pnpm build
pnpm build:themes
```

`pnpm test` runs formatting, lint, workspace typechecks, and unit/integration tests. Use `pnpm fix:format` and `pnpm fix:lint` for automatic fixes.

`pnpm check:publish` builds the project, runs repository checks, browser regressions and the isolated production-extension smoke tests, then creates a release candidate. Install the test browser once with `pnpm test:browser:install`. The extension smoke uses a fresh browser profile and locally supplied X-shaped pages; it does not log into X or establish live-site visual approval.

`pnpm build` produces library builds, Studio's production build, and the production extension in `apps/extension/dist-production`. To run the built Studio, use `pnpm --filter @repaint/studio start`. Production Studio does not save source defaults or art direction, and the production extension omits the localhost authoring bridge and fixture access.

Development uses `apps/extension/dist`; production uses `apps/extension/dist-production`. A production build preserves the loaded development extension. Reload the production extension and its target tabs after rebuilding it.

`pnpm build:themes` produces standalone artifacts in `build/themes/cyberpunk`, `build/themes/lofi`, and `build/themes/petal`. Each contains `theme.js`, manifest/options/defaults metadata, a bundle inventory, and required assets, with executable dependencies bundled. Build one theme with `pnpm build:themes cyberpunk`, `pnpm build:themes lofi`, or `pnpm build:themes petal`.

## Review the production extension locally

Build the production extension (its output is separate from development):

```sh
pnpm --filter @repaint/extension build
```

In a separate Chrome profile, open `chrome://extensions`, enable **Developer mode**, choose **Load unpacked**, and select `apps/extension/dist-production`. Open an authenticated X tab and reload it if it was already open. Click Repaint's toolbar action, then choose a theme in the side panel. Studio and the development server are not required for this build; the production extension supports X/Twitter and has no localhost fixture or Studio bridge.

After rebuilding, click **Reload** on that extension in Chrome's extension manager and reload the X tab. Save native drafts before these reloads. To stop applying customizations, use **Restore this site** in the side panel, or disable/remove the extension in Chrome's extension manager. A local production build is not a Chrome Web Store release. See [MVP launch readiness](docs/mvp-launch-readiness.md) for the remaining product and distribution gates.

## Package a release candidate

Run `pnpm release:package` to build and validate an isolated production candidate under `work/releases/`. Each candidate includes an unpacked extension, a ZIP, checksums, and a receipt identifying the source revision, dirty state and exact artifact files. Packaging does not publish or approve a release. See [release review and update instructions](docs/release.md), [data and permissions](docs/data-and-permissions.md), and the [bug-report template](https://github.com/transitive-bullshit/repaint/issues/new?template=bug_report.yml).

## Repository map

| Location | Responsibility |
| --- | --- |
| `apps/studio` | Desktop authoring UI, fixtures, deliberate source saves |
| `apps/extension` | Chrome worker, side panel, preferences, content host, Studio bridge |
| `packages/core` | Serializable schemas and preference/option policy |
| `packages/runtime` | Generic adapter, theme, feature, and resource lifecycles |
| `adapters/x` | X selectors, route interpretation, semantic snapshots and resources |
| `packages/features` | Focus mode and Copy Markdown through adapter semantics |
| `packages/theme-controls` | Shared DialKit controls |
| `packages/theme-renderer` | Shared static styling and GPU rendering support |
| `packages/authoring` | Source validation/writes, art-direction metadata and prompts, artifact builds, browser-safe protocol |
| `themes/*` | Authored theme metadata, rendering configuration, art direction, defaults and assets |
| `docs/brand-identity.md` | Final Default dissent identity, copy, visual rules and reusable assets |

The supported target is desktop Chrome on X home (For You/Following), post detail/replies, and profile Posts. X's undocumented DOM can change, and local fixtures do not establish live-site compatibility. Mobile polish, other browsers/sites, a full accessibility/motion-policy pass, audio, distribution, and Chrome Web Store submission are outside this PoC.
