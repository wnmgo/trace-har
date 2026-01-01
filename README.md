# trace-har

Rebuild a Playwright HAR file from trace artifacts when the original HAR is missing.

## What this does

- Reads `trace.network` and `resources/` from a Playwright trace folder or `.zip`.
- Hydrates request/response bodies from `_sha1` resource files.
- Writes a standalone HAR (`log.version = 1.2`) suitable for offline replay.

## Quick start

```bash
pdm install
pdm run trace-har archive --output reconstructed.har
```

## CLI usage

```bash
pdm run trace-har TRACE_PATH --output OUTPUT.har [--pretty] [--overwrite]
```

- `TRACE_PATH` can be a trace directory (unpacked) or a `.zip` trace.
- Use `--pretty` to indent the HAR JSON.
- Use `--overwrite` to replace an existing output.

## Project layout

- `src/trace_har/` - conversion logic + CLI.
- `tests/` - unit tests and fixtures.
- `docs/` - architecture, implementation, and user guide.

## Development

```bash
pdm run pytest
```

## Notes

- Response bodies are embedded into the HAR.
- Binary bodies are stored as base64 with `encoding: base64`.
- The converter preserves Playwright-specific fields like `_securityDetails`.
