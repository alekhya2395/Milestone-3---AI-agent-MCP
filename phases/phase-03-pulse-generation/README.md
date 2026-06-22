# Phase 3 — Theme Analysis & Pulse Generation

**Status:** Implemented  
**Eval:** [docs/phases/phase-03-pulse-generation/eval.md](../../docs/phases/phase-03-pulse-generation/eval.md)  
**Plan:** [Implementation Plan — Phase 3](../../docs/implementationplan.md#phase-3--theme-analysis--pulse-generation)

## Objective

Generate the weekly pulse (top 3 themes, 3 quotes, 3 actions, ≤250 words) as a **local markdown artifact** for operator approval before Google publish.

## Run locally

```powershell
# Prerequisites: Phase 2 complete + GROQ_API_KEY in .env
python phases/phase-03-pulse-generation/scripts/run-phase3.py
```

Outputs in `data/processed/`:

| File | Description |
|------|-------------|
| `llm-input-bundle.json` | Stats on 1,000 + ~120 Groq sample |
| `theme-summary.json` | Theme rankings and quote candidates |
| `weekly-pulse-YYYY-MM-DD.md` | Weekly pulse (canonical artifact) |
| `groq-usage-log.json` | Token usage (2 Groq calls per run) |

## Run via Railway MCP

MCP server: [https://milestone-3-ai-agent-mcp-production.up.railway.app/mcp](https://milestone-3-ai-agent-mcp-production.up.railway.app/mcp)

Configure in `.cursor/mcp.json` as `weekly-pulse`, then in Cursor **Settings → Tools & MCP**:

| Tool | Purpose |
|------|---------|
| `build_llm_bundle` | Phase 3 step 1 |
| `generate_pulse` | 2 Groq calls → pulse markdown |
| `run_phase3_pipeline` | Full Phase 3 with validation |
| `theme_summary` | Read theme rankings JSON |
| `latest_pulse` | Read latest pulse markdown |

**Railway env:** set `GROQ_API_KEY` in Railway Variables for server-side pulse generation.

## Groq design (2 calls only)

| Call | Input | Output |
|------|-------|--------|
| 1 — Theme tag | ~120 stratified reviews | JSON theme assignments |
| 2 — Pulse write | Top 3 themes + stats + 9 quote candidates | `weekly-pulse-*.md` |

Local Python ranks themes on 1,000 reviews (DEC-011 severity weighting).

## Prompts

- [prompts/theming.md](../../prompts/theming.md) — Groq call 1
- [prompts/pulse-format.md](../../prompts/pulse-format.md) — Groq call 2
- [prompts/system.md](../../prompts/system.md) — Agent role

## Previous / next

- **Previous:** [Phase 2](../phase-02-review-ingestion/README.md)
- **Next:** [Phase 4](../phase-04-google-docs-mcp/README.md)
