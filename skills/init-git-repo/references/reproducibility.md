# Reproducibility recipes

Use whichever sections match the ecosystems in the repo. Always commit the lockfile, and verify installs from it in a clean environment.

## Python: uv

- **Files:** `pyproject.toml`, `uv.lock`, `.python-version`.
- **Script repos** (a working directory, not a library): set `[tool.uv] package = false`, which avoids flat-layout build errors.
- **Groups:** core dependencies go in `[project].dependencies`. Heavy or optional stacks go in `[dependency-groups]`. A `dev` group (pytest) is installed by default.

```toml
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.12,<3.13"
dependencies = ["requests>=2.32", "numpy>=2.0"]

[dependency-groups]
dev = ["pytest>=8"]
ml = ["torch>=2.5", "mlx-whisper>=0.4; sys_platform == 'darwin' and platform_machine == 'arm64'"]
experiments = [{ include-group = "ml" }, "librosa>=0.11"]

[tool.uv]
package = false

[tool.uv.sources]
some-git-dep = { git = "https://github.com/org/repo", rev = "<commit sha>" }
```

- **Finding dependencies:** list third-party imports by parsing the tracked `.py` files with `ast`. Take the installed versions from `uv pip freeze --python .venv/bin/python`.
- **Locking and checking:** run `uv lock`, then verify with `UV_PROJECT_ENVIRONMENT=/tmp/check uv sync --frozen [--group …]` and a smoke import or run.
- **Environment variables:** `uv run --env-file .env python script.py`.
- **pip users:** `uv export --no-hashes --no-emit-project > requirements.txt`.
- **CI:** `astral-sh/setup-uv` with `enable-cache: true`, then `uv sync --frozen`, then `uv run --frozen pytest -q`.

## TypeScript and JavaScript

Follow the user's conventions in `references/typescript.md`: pnpm, `@fisch0920/config`, oxlint, oxfmt, the standard scripts, and the canonical files in `templates/typescript/`.

## Rust

- **Files:** commit `Cargo.lock` for binaries and apps, and pin the toolchain in `rust-toolchain.toml`.
- **CI:** `dtolnay/rust-toolchain`, then `cargo build --locked`, then `cargo test --locked`.

## Go

- **Files:** `go.mod` and `go.sum`, with the `go` directive set.
- **CI:** `actions/setup-go` with `go-version-file: go.mod`, then `go vet ./...`, then `go test ./...`.

## Beyond the package manager

- **System tools** (ffmpeg, rubberband, and so on): document them in `contributing.md`, or add a `Brewfile` if there are several. In CI, `apt-get install` them only if the tests truly need them.
- **Inputs that aren't in git** (a media file, a dataset, model weights): name the exact path the code expects, and say where to get it.
- **Machine-specific configs:** make paths relative to the file or the repo root. Fontconfig, for example, supports `<dir prefix="relative">.</dir>`.
- **Separate environments:** a third-party tool with conflicting dependencies gets its own requirements file and venv, documented as optional.

## CI template (Python / uv)

This follows the same conventions as the TypeScript `test.yml`. After writing it, run `npx actions-up -y` to pin every action to its latest release's commit SHA.

```yaml
name: Test

on: [push]

permissions:
  contents: read

jobs:
  test:
    # Offline and cheap: no secrets, no external APIs.
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true
      - run: uv sync --frozen
      - run: git ls-files -z '*.py' | xargs -0 uv run --frozen python -m py_compile
      - run: uv run --frozen pytest -q
```
