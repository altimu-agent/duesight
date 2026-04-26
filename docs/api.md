# API reference

| Method | Path | Description |
|---|---|---|
| `GET`  | `/`            | Web UI |
| `GET`  | `/health`      | `{"status": "ok", "model": "..."}` |
| `POST` | `/api/analyze` | Server-Sent Events stream of typed events |

## `POST /api/analyze`

Request body:

```json
{
  "company": "Stripe",
  "website": "stripe.com",
  "industry": "payments",
  "country": "USA",
  "contract_value": 250000,
  "competitors": null
}
```

`country`, `contract_value`, and `competitors` are optional. When `competitors` is `null` the orchestrator auto-discovers them as a preflight step.

Response: `text/event-stream`. Each event is a JSON object on a `data:` line.

## SSE event types

| Type | Payload | When |
|---|---|---|
| `competitors_discovered`   | `{competitors: [{name, tagline}, ...]}` | After preflight discovery |
| `dimension_started`        | `{dimension, label}` | A sub-agent begins research |
| `dimension_completed`      | `{dimension, status, summary_preview}` | Sub-agent finished |
| `dimension_timeout`        | `{dimension, elapsed_s}` | Sub-agent exceeded its budget |
| `tool_call`                | `{step, name, args, dimension}` | A tool call was issued |
| `tool_result`              | `{step, name, preview, dimension}` | A tool call returned |
| `reduce_started`           | `{}` | All sub-agents done, synthesis begins |
| `reduce_chunk_started`     | `{chunk, label}` | A reduce chunk begins streaming |
| `reduce_chunk_delta`       | `{chunk, text}` | Token delta from a reduce chunk |
| `reduce_chunk_completed`   | `{chunk, char_count}` | A reduce chunk finished |
| `reduce_chunk_error`       | `{chunk, message}` | A reduce chunk failed |
| `report`                   | `{content, score_info}` | Final reconciled markdown report |
| `info`                     | `{message}` | Non-fatal notice (e.g. score reconciled) |
| `error`                    | `{message}` | Fatal error |
| `done`                     | `{}` | Stream end marker |
