# Decisions Log

Architectural and logical decisions made **while designing this project**. Only significant choices are recorded here — not restatements of problem-statement constraints unless they drove a non-obvious design fork.

Update when a decision is made, reversed, or superseded.

---

## DEC-001 — Google Workspace access exclusively through MCP

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Gmail and Google Docs could be integrated via official REST APIs/SDKs or via Google’s managed Workspace MCP servers. Milestone 3 is explicitly an MCP agent exercise.

**Decision:** All Google-side operations (Doc creation, draft email) go through **remote Workspace MCP servers**. No parallel Drive, Docs, or Gmail API integration in project logic.

**Rationale:** Keeps a single integration boundary; OAuth and tool contracts live in the MCP client; matches milestone learning objective.

**Consequences:** Feature set limited to what MCP tools expose; debugging shifts to GCP + MCP client config rather than application HTTP logs.

---

## DEC-002 — Google Docs delivered via Drive MCP (no separate Docs server)

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Product language says “Google Docs,” but Google’s MCP setup guide provides a **Drive MCP** endpoint, not a standalone Docs MCP.

**Decision:** Treat **Drive MCP** as the document integration point — create and verify weekly pulse files as Google Docs through Drive MCP tools (`create_file`, `read_file_content`, etc.).

**Rationale:** Aligns with official Google Workspace MCP architecture; avoids unsupported assumptions about a Docs-specific server.

**Consequences:** Formatting control is coarser than native Docs API; visual check in Docs UI required after creation.

---

## DEC-003 — Cursor as the MCP client and agent runtime

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** The agent needs tool discovery, OAuth, LLM reasoning, and local repo access in one environment.

**Decision:** Use **Cursor** as the sole MCP client for development and weekly production runs.

**Rationale:** Built-in MCP support, agent workflows, and direct access to `data/` and `prompts/` without extra glue.

**Consequences:** No headless/CI runner in v1; weekly job is operator-triggered in Cursor.

---

## DEC-004 — Five-phase delivery with eval gates

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** The milestone spans infra (MCP), data, content, and two Google integrations — easy to block late on auth or publish bad content early.

**Decision:** Split delivery into **five phases**, each with a dedicated `eval.md` and hard gate before the next phase. Master `eval.md` tracks milestone acceptance.

**Rationale:** Isolates failure domains; MCP proven before analysis investment; content approved before Google publish.

**Consequences:** More documentation overhead; clearer progress tracking for reviewers.

---

## DEC-005 — Local analysis first, MCP publish second (two-stage workflow)

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** The agent could call Google MCP tools immediately after generating a pulse, or pause for human review.

**Decision:** Split each weekly run into **Phase A (local)** — ingest, sanitize, theme, write `weekly-pulse-YYYY-MM-DD.md` — and **Phase B (MCP)** — Drive Doc + Gmail draft only after operator approval.

**Rationale:** Prevents publishing PII, over-length, or off-topic content; local file becomes content contract for parity checks.

**Consequences:** Extra manual step; requires discipline in runbook so operators do not skip approval.

---

## DEC-006 — LLM-assisted theming with a fixed product vocabulary

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Themes could be discovered fully open-ended (unstable labels week to week) or constrained to product domains (onboarding, KYC, payments, etc.).

**Decision:** Use **LLM-assisted clustering** bounded by a **fixed theme vocabulary** aligned to the Milestone 1 fintech product. Allow ≤5 themes internally; pulse shows top 3.

**Rationale:** Stable labels for leadership; still flexible enough to absorb new issues via nearest theme or controlled “other” merge.

**Consequences:** Occasional misfit reviews need manual vocabulary updates when product surface changes.

---

## DEC-007 — PII sanitization at the data layer, before quote selection

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** PII could be stripped only in the final pulse, or earlier in the pipeline.

**Decision:** Run **mandatory PII sanitization on normalized reviews** before theming and quote selection. Re-scan final pulse before MCP publish.

**Rationale:** Defense in depth; quotes are chosen from already-clean text, reducing leak risk from LLM reproduction.

**Consequences:** Some vivid quotes may be lost to redaction; paraphrase when needed.

---

## DEC-008 — New Google Doc per weekly run (no rolling overwrite)

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Weekly pulses could update a single rolling Doc or create a new file each week.

**Decision:** Create a **new Google Doc each weekly run** with dated title `[Product] Weekly Pulse — YYYY-MM-DD`.

**Rationale:** Historical archive in Drive; avoids accidental overwrite; simpler MCP flow (create-only).

**Consequences:** More files in Drive; operator may want a Drive folder convention later.

---

## DEC-009 — Gmail draft only; human sends manually

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Gmail MCP can create drafts; sending introduces approval, deliverability, and scope concerns.

**Decision:** Stop at **`create_draft`**; operator reviews in Gmail UI and sends manually.

**Rationale:** Matches problem statement (“draft email”); safe default for internal weekly pulse.

**Consequences:** One extra click for operator; no unattended email delivery.

---

## DEC-010 — Public review exports as the only data source

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Reviews could come from scrapers, private APIs, or vendor datasets.

**Decision:** Use **public store exports only** (CSV/JSON), manually refreshed weekly. No authenticated scraping.

**Rationale:** Reproducible, ToS-friendlier pipeline; explicit operator step documents data provenance.

**Consequences:** Freshness tied to export cadence; schema drift handled per platform in ingestion phase.

---

## DEC-011 — Local pulse artifact as source of truth for Google parity

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Doc and email could be generated independently by the LLM, risking mismatch.

**Decision:** **`weekly-pulse-YYYY-MM-DD.md`** is the canonical content; Drive Doc and Gmail body must match it (optional Doc link in email only as supplement).

**Rationale:** Single artifact for eval, diff, and recovery if MCP partially fails.

**Consequences:** Publish steps must read from approved file, not regenerate prose.

---

## DEC-012 — Theme ranking weights volume and low-star severity

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Top 3 themes could be ranked by mention count alone, which favors noisy neutral feedback.

**Decision:** Rank themes using **frequency plus severity skew** — low ratings (1–2 stars) weigh heavier than volume alone.

**Rationale:** Weekly pulse is for “what to fix next,” not just “what is mentioned most.”

**Consequences:** A lower-volume high-pain theme can outrank a high-volume mild annoyance.

---

## Superseded Decisions

_None._

---

## DEC-013 — Dual folder layout: `phases/` work + `docs/phases/` eval

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Phase deliverables include runbooks, evidence, and eval checklists. Mixing operational artifacts with specification docs can clutter `docs/`.

**Decision:** Use **`phases/phase-XX-name/`** at repo root for runbooks, scripts, fixtures, and evidence; keep **`docs/phases/phase-XX-name/eval.md`** as the exit gate only.

**Rationale:** Clear separation between “what to verify” (docs) and “how we did it” (phases); shared `data/` and `prompts/` across phases.

**Consequences:** README in each phase folder links to matching eval in `docs/phases/`.

---

## DEC-014 — Project-scoped `.cursor/mcp.json` with env-based OAuth

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** MCP config can live globally (`~/.cursor/mcp.json`) or per project. OAuth client secrets must not be committed.

**Decision:** Commit **`.cursor/mcp.json`** in the repo with `${env:GOOGLE_OAUTH_CLIENT_ID}` and `${env:GOOGLE_OAUTH_CLIENT_SECRET}`; operators copy `.env.example` → `.env` locally.

**Rationale:** Team shares server URLs and scopes; secrets stay local. Matches Cursor config interpolation.

**Consequences:** Cursor must be restarted after env changes; redirect URI `cursor://anysphere.cursor-mcp/oauth/callback` registered in GCP.

---

### DEC-015 — Zomato as Milestone 1 product; public scraper for review download

**Date:** 2026-06-15  
**Status:** Accepted  

**Context:** Milestone 1 project is `MILESTONE 1 - ZOMATO`. Reviews must come from public exports with an 8–12 week window.

**Decision:** Use **Zomato** (`434613896` / `com.application.zomato`). Download via `phases/phase-02-review-ingestion/scripts/fetch-reviews.py` — App Store RSS + `google-play-scraper` for Play Store, stored under `data/raw/`.

**Rationale:** Aligns with Milestone 1; no login scraping; repeatable script with date window filter.

**Consequences:** Play Store public scraper for high-volume apps may not reach full 10 weeks in one run (Zomato: ~8 weeks / 60k reviews). App Store RSS covers ~10 weeks (~489 reviews). Sufficient for milestone analysis when combined.

---

### DEC-016 — Normalization: English only, >6 words, no emojis

**Date:** 2026-06-16  
**Status:** Accepted  

**Context:** Raw store reviews include Hindi/regional text, emojis, and very short low-signal comments unsuitable for theming and quotes.

**Decision:** During normalization, **drop** reviews that fail any rule; **clean** survivors:
1. **Word count** — keep only if title + text have **more than 6 words** (minimum 7)
2. **Emojis** — strip from text; reviews that become empty or too short after strip are dropped
3. **Language** — **English only** (`langdetect`); non-English reviews removed
4. **PII** — strip emails, @handles, phone-like patterns (existing policy)

**Rationale:** Higher-quality input for pulse themes and anonymized quotes; aligns with English executive summary audience.

**Consequences:** Fewer reviews in processed set vs raw (especially Android India corpus); document drop rates in `normalization-summary.json`.

---

## Deferred (not yet decided)

| Topic | Options | Decide by |
|-------|---------|-----------|
| Exact Milestone 1 product name & export URLs | **Zomato** — see `data/raw/export-summary-*.json` | Resolved 2026-06-15 |
| Gmail recipient (primary vs alias) | — | Phase 5 start |
| Default review window within 8–12 weeks | **10 weeks** (iOS full; Play ~8 weeks via public scraper) | Resolved 2026-06-15 |
