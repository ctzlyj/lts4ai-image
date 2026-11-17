# LTS4AI Image Model API Contract

## Defaults

- Base URL: `https://api.lts4ai.com/v1`
- Default model: `gpt-image-2.5`
- Current catalog: `gpt-image-2.5`, `gpt-image-2.6`, `gemini-pro-imagen-official`, `gemini-flash-lite-imagen-official`, `gemini-flash-imagen-official`, `gemini-argon-imagen-official`, `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`; preserve exact user selection, never silently fall back
- Legacy IDs such as `GPT-image-2` may still be supplied explicitly and are sent unchanged. Model visibility and availability come from the user's authenticated `GET /v1/models`, not the offline catalog.
- Authentication: `Authorization: Bearer <API key>`
- Output format: PNG

## Text to Image

`POST /v1/images/generations` with `Content-Type: application/json`:

```json
{
  "model": "gpt-image-2.5",
  "prompt": "A premium studio product photograph",
  "size": "1024x1024",
  "output_format": "png"
}
```

All catalog models share this contract. Do not send `n`, `seed`, or `response_format`.

GPT-image-2.6 uses the exact `gpt-image-2.6` ID on both Images API endpoints. Do not substitute 2.5 or route it through Chat Completions.

## Multi-reference Editing

`POST /v1/images/edits` with `multipart/form-data`:

| Field | Value |
|---|---|
| `model` | Selected exact model ID, default `gpt-image-2.5` |
| `prompt` | User prompt |
| `size` | Resolved provider size |
| `output_format` | `png` |
| `image` | Repeated file parts in reference order |

Let the HTTP client generate the multipart boundary. Supported references are JPEG, PNG, GIF, and WebP. The Skill enforces the current site's limit of 12 files and 15 MB total bytes.

## Resolution Mapping

The legacy 1K mapping below also remains the 2K mapping for the official Imagen models and unrecognized/custom endpoint contracts:

| Ratio | Provider size |
|---|---|
| Adaptive, 1:1 | `1024x1024` |
| 16:9, 4:3, 3:2 | `1536x1024` |
| 9:16, 3:4, 2:3, 4:5 | `1024x1536` |
| 21:9, 5:4, 2:1 | `auto` |

For 2K on `https://api.lts4ai.com/v1` or the equivalent `origin.lts4ai.com` endpoint, GPT 2.5/2.6, explicit legacy GPT aliases and the two Gemini preview image models request:

| Ratio | Provider size |
|---|---|
| Adaptive, 1:1 | `2048x2048` |
| 16:9 | `2560x1440` |
| 21:9 | `2688x1152` |
| 4:3 | `2048x1536` |
| 3:2 | `2304x1536` |
| 5:4 | `1920x1536` |
| 2:1 | `2560x1280` |
| 3:4 | `1536x2048` |
| 2:3 | `1536x2304` |
| 4:5 | `1536x1920` |
| 9:16 | `1440x2560` |

This endpoint-specific mapping does not rewrite an explicit `--resolution` or centimeter canvas. Different endpoints retain the previous mapping unless the user supplies a supported explicit resolution.

For 4K:

| Ratio | Provider size |
|---|---|
| Adaptive | `3840x2160` |
| 1:1 | `2880x2880` |
| 16:9 | `3840x2160` |
| 21:9 | `3840x1648` |
| 4:3 | `3264x2448` |
| 3:2 | `3504x2336` |
| 5:4 | `3200x2560` |
| 2:1 | `3840x1920` |
| 3:4 | `2448x3264` |
| 2:3 | `2336x3504` |
| 4:5 | `2560x3200` |
| 9:16 | `2160x3840` |

For edits, Adaptive first infers the nearest listed ratio from the first reference image.

The 4K tier is an approximately 8 MP pixel envelope, not a promise of 4096×4096 output. In particular, a GPT square requests 2880×2880. Inspect measured output dimensions before delivery.

## Custom canvas

`--width-cm` / `--height-cm` compute an exact reduced aspect ratio and choose integer multiples of 16 pixels on both axes. These are client-side validation limits; acceptance by a specific model is subject to its current API. Prefer GPT 2.5/2.6 for custom canvases and do not claim all models support every size. Apply:

- Aspect ratio from 1:3 to 3:1 inclusive.
- Longest side <=3840; area from 655360 to 8294400 pixels inclusive.
- Positive centimeters, up to 9 integer digits and 6 decimal places. No rounding to another ratio; reject an unrepresentable exact ratio.
- Pixel targets: 1K=1048576, 2K=3145728, 4K=8294400, clamped to legal exact multiples. Existing fixed-ratio mappings above remain unchanged.
- No combination with `--ratio` or `--resolution`. Direct `--resolution WIDTHxHEIGHT` uses the same pixel envelope; `auto` remains available. `canvas` computes offline before spending credits.
- 120×40cm → 1728×576 (1K), 3072×1024 (2K), 3840×1280 (4K); 29.7×21cm → 3168×2240 (4K). These are examples, not an exhaustive supported list.
- Append canvas instructions to the complete original prompt, preserving every user title, selling point, and background choice. The centimeters are not product dimensions or text to draw.
- Top-level `size` is the requested provider size; `outputs[].width/height` report readable actual image dimensions. Centimeters do not set DPI, and no output is resized, cropped, or padded by this client.

## Responses

Canonical response:

```json
{
  "data": [
    { "b64_json": "..." }
  ]
}
```

The client also accepts nested `b64Json`, data URLs, SSE `data:` JSON frames, direct image responses, and HTTP(S) image URLs. Remote image downloads never receive the LTS4AI Authorization header.

## Reliability

- Default timeout: 10 minutes for 1K/2K and 30 minutes for 4K.
- Default retry budget: two retries after the first attempt, with 1-second and 3-second waits.
- Retry explicit HTTP 429, and 5xx only for read-only GET requests such as `/models`.
- Image POST HTTP 408/409/5xx, network failures, and interrupted bodies have an unknown outcome. Do not automatically resubmit; reconcile results and charges first. Missing/invalid image data also does not trigger an automatic new generation.
- In a failed batch, already completed output files remain on disk. Inspect them before selecting any retry; do not replay successful tasks or silently change models.
- A seed is not included in any generation or edit request.
- Billing is based on actual upstream submissions, including submitted requests that fail or time out; explicitly unsubmitted requests are not charged. Current prices and outcomes come from LTS4AI's public catalog and ledger. Never derive a refund from HTTP status alone. Querying an original result does not authorize a replacement POST; website operation recovery is outside this CLI.
