# Instructions for Future Agents

## Scope

This repo reconstructs Playwright HAR files from trace artifacts. The core CLI is
`trace-har` (single-command mode; no `build` subcommand). The main inputs are
trace directories or trace zip files.

## Project setup

```bash
pdm install
```

## Run tests

```bash
pdm run pytest
```

## Run CLI

```bash
pdm run trace-har TRACE_PATH --output reconstructed.har
```

- `TRACE_PATH` can be a directory (unpacked trace) or a `.zip` trace.
- The CLI is single-command mode: do not add `build` unless you update the CLI
  and docs accordingly.

## Repo hygiene

- Local trace inputs (`archive/`, `trace_record.zip`) are ignored in `.gitignore`.
- Generated HAR outputs (e.g., `reconstructed.har`) should not be committed.

## Development workflow

- Use conventional commits with detailed message bodies.
- Commit small, commit often.
- Use `gh` for repo/issue/PR management.
- Do not include literal `\n` in commit/PR/issue bodies; write real newlines or
  use `-m` per paragraph / `--body-file`.

## Release process

- Tag: `git tag -a vX.Y.Z -m "release: vX.Y.Z"` then `git push origin vX.Y.Z`.
- Release: `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file <notes>`.

## Key files

- CLI entrypoint: `src/trace_har/cli.py`
- Converter: `src/trace_har/converter.py`
- Source abstraction: `src/trace_har/source.py`
- Docs: `README.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION.md`,
  `docs/USER_GUIDE.md`
