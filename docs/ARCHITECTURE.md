# Architecture

## Goals

- Convert Playwright trace artifacts into a complete HAR file.
- Keep the conversion deterministic and easy to audit.
- Support both unpacked trace folders and zipped trace archives.

## High-level flow

1. Open the trace source (directory or zip).
2. Parse `trace.network` as JSON-lines resource snapshots.
3. Hydrate request/response bodies from `resources/` by `_sha1`.
4. Build `log.pages` from the first entry per `pageref`.
5. Emit a standalone HAR file.

## Components

### `TraceSource`

- Location: `src/trace_har/source.py`
- Responsibilities:
  - Abstract away trace input type (folder vs zip).
  - Provide consistent `read_bytes`, `read_text`, and line iteration.

### Converter

- Location: `src/trace_har/converter.py`
- Responsibilities:
  - Load context metadata from `trace.trace`.
  - Iterate resource snapshots into HAR entries.
  - Hydrate `_sha1` request/response bodies.
  - Build `log.pages` in a single pass.

### CLI

- Location: `src/trace_har/cli.py`
- Responsibilities:
  - Parse arguments and write the HAR output.
  - Provide helpful feedback and safety checks.

## Data ownership

- Input trace artifacts remain unchanged.
- Output HAR is written to the chosen path only.
- The converter preserves Playwright-specific fields so the data can still be
  inspected in other tooling.
