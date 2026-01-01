# Implementation Notes

## Trace parsing

- `trace.network` is newline-delimited JSON. Each `resource-snapshot` entry is
  treated as a HAR entry.
- Non-network records are ignored.

## Body hydration

- Response bodies are referenced by `_sha1` in `response.content`.
- Request bodies are referenced by `_sha1` in `request.postData`.
- The converter reads `resources/<sha1>` and embeds the data into HAR fields.

## Text vs binary detection

- Content is treated as text if the MIME type starts with `text/` or includes
  tokens like `json`, `html`, `xml`, `javascript`, `css`, or `svg`.
- Text payloads are decoded using the MIME `charset` when provided, otherwise
  UTF-8.
- Binary payloads are base64 encoded and marked with `encoding: base64`.

## Page reconstruction

- Each distinct `pageref` becomes a HAR page.
- `startedDateTime` is taken from the first entry for that page.
- `pageTimings` defaults to `-1` for `onLoad` and `onContentLoad` because trace
  events do not provide reliable navigation timing in the network snapshot.

## Playwright metadata

- `trace.trace` is scanned for a `context-options` record.
- `browserName` and `playwrightVersion` are surfaced as `log.browser`.
- If metadata is missing, `log.browser.name` is set to `unknown`.

## JSON output

- The CLI writes ASCII-safe JSON with `ensure_ascii=True`.
- Use `--pretty` for indentation when debugging.
