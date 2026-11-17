---
name: lts4ai-image
description: Use when a user wants to generate, edit, or batch-create images with their LTS4AI API key using GPT-image-2.5/2.6 or Gemini image models, including multi-reference edits, centimeter posters, Image Studio 商品套图 and 服装工作台. Does not manage website accounts or history.
---

# LTS4AI Image

Use the bundled standard-library Python client with the image-model contracts used by `image.ctzlyj.com`. Default to `gpt-image-2.5` and preserve an explicitly selected model. `gpt-image-2.6` must retain its exact ID and use Images API generation/edit endpoints, never a substituted model or Chat Completions. Do not silently fall back when a model is unavailable.

## 更换生图模型 / 如何选择生图模型

- **gpt-image-2.5（默认）**：日常商品图、批量出图和多参考图编辑。
- **gpt-image-2.6**：可选，支持文字生图和参考图编辑，保留原始 ID。
- **官方 Imagen 通道**：`gemini-pro-imagen-official`、`gemini-flash-lite-imagen-official`、`gemini-flash-imagen-official`、`gemini-argon-imagen-official`。
- **Gemini 图片模型**：`gemini-3-pro-image-preview`、`gemini-3.1-flash-image-preview`。
- `GPT-image-2` 仅保留旧调用兼容；不作为第九款现行模型推荐。旧 ID 若由用户明确指定则原样提交，不擅自映射。
- 用户问如何选择时，运行 `python scripts/lts4ai_image.py guide`，用中文解释当前目录（离线说明；价格与可用性以实时服务和账户权限为准）；不要让用户访问英文官方说明或外部链接。建议不是速度、价格或质量保证，实际可用模型以用户 Key 的 `models` 结果为准。

## Workflow

1. Determine the operation:
   - no reference image → `generate`
   - one to twelve reference images → `edit`
   - several outputs or one prompt per line → `batch`
   - 商品套图或服装工作台任务 → 先阅读 `references/image-studio-workflows.md`，再按其中的角色分工、参考图顺序和保真约束组织提示词
2. On the user's own Windows machine, reuse the current-user DPAPI credential at `%LOCALAPPDATA%\JoyCode\credentials\sufy-image2.dpapi` when present. The legacy filename is intentionally retained after renaming; do not move, copy, or export it. It is encrypted for that Windows identity and must never be copied to another account or machine.
3. Otherwise ask once for the LTS4AI API key. Keep transient keys process-local with `LTS4AI_API_KEY` or `--api-key-stdin`; never put a key in command arguments, source, logs, replies, or plaintext files.
4. Infer missing creative details from the request. Default to ratio `1:1`, quality `2K`, and output directory `output/`. Write all titles, selling points, and scene copy directly from the user's product information and explicit instructions; do not call a separate text/chat model for copy. For a specified poster/canvas size, use `--width-cm` and `--height-cm`; read `references/api-contract.md` for exact limits. Distinguish canvas dimensions from product/package dimensions, and resolve conflicting sizes before a paid call.
5. Run the command from this Skill's directory.
6. Read the JSON summary from stdout. Render or display each generated local image when the host supports images; otherwise provide its absolute path.
7. Report provider errors concisely without repeating the API key.

## Commands

```bash
python scripts/lts4ai_image.py generate --prompt "A premium product photograph" --ratio 1:1 --quality 2K
```

Select 2.6 explicitly with `--model gpt-image-2.6`. On the standard LTS4AI endpoint, GPT 1K square requests 1024×1024, 2K square requests 2048×2048, and 4K square requests 2880×2880 (about 8 MP, not 4096×4096). The API reference lists the model-specific size mappings. Explicit pixel and centimeter canvases are preserved.

```bash
python scripts/lts4ai_image.py edit --prompt "Keep the product unchanged and replace the background" --image product.png --ratio Adaptive --quality 2K
```

```bash
python scripts/lts4ai_image.py batch --prompt "A refined studio product photo" --count 4 --concurrency 2 --ratio 1:1 --quality 2K
```

```bash
python scripts/lts4ai_image.py batch --prompts-file prompts.txt --image reference.png --concurrency 2 --ratio Adaptive --quality 4K
```

Add `--api-key-stdin` after the subcommand when using stdin. Never put the key in a command argument.

```bash
python scripts/lts4ai_image.py canvas --width-cm 120 --height-cm 40 --quality 4K
python scripts/lts4ai_image.py generate --prompt "海报设计，保留全部指定标题与卖点" --width-cm 120 --height-cm 40 --quality 4K
```

`canvas` is offline and free; the second command generates a paid image. Width/height set the exact aspect ratio, not native print resolution or DPI. Report requested `size` separately from each output's measured `width`/`height`; inspect actual output rather than claiming a 120 cm print is natively 300 DPI. Local canvas validation is not a guarantee that every model accepts every size; prefer GPT 2.5/2.6 for custom canvases.

## Operating Rules

- Use only JPEG, PNG, GIF, or WebP references.
- Accept at most 12 references and 15 MB total source bytes.
- Use `Adaptive` for edits when the first reference should determine the closest supported ratio.
- Treat 4K as a potentially 30-minute request; 1K/2K default to 10 minutes.
- Batch at most 10 tasks and use conservative concurrency, normally 1–3.
- Preserve all user titles, selling points, edited plans, product identity, and background/style choices. Do not add a “精简清晰” mode, remove text to conceal poor small-text rendering, or unify cross-border platform presets to white backgrounds. This CLI does not manage the website's accounts, COS archives, history, or templates.
- Compose image copy yourself as the Agent. Do not invoke DeepSeek or any other text/chat model to generate titles or selling points; use only verified user-provided facts and do not invent certifications, parameters, or comparisons.
- Generation HTTP 408/409/5xx, interrupted responses, and network timeouts have an unknown outcome: stop and reconcile results/billing before another paid submission. Never automatically replay a whole failed batch; retain already saved images. `--retries` only retries explicit 429 responses and read-only GET 5xx.
- Billing follows actual upstream submissions; failed or timed-out submissions may still be charged, while explicitly unsubmitted requests are not charged. Prices and ledger outcomes come from the current LTS4AI service, not this offline guide. Querying an original result does not authorize another paid POST; this CLI does not implement website operation recovery.
- Do not add legacy `n` or `response_format` fields.
- Do not claim deterministic seed support; no image request sends a seed.
- Do not save keys in `.env`, shell scripts, generated metadata, logs, commits, or final responses.

## References

- Read `references/api-contract.md` when diagnosing request shape, ratios, sizes, or response formats.
- Read `references/agent-workflow.md` for secure invocation patterns and actionable error handling.
- Read `references/image-studio-workflows.md` for Image Studio 商品套图、标准换装、直接动作、主图审核和动作轮次规则。
