# Phase 5 Evaluation — Gmail Draft & End-to-End Orchestration

**Phase:** [Implementation Plan — Phase 5](../implementationplan.md#phase-5--gmail-draft--end-to-end-orchestration)

---

## Objectives Under Test

- Gmail draft created via **Gmail MCP only**
- Full pipeline runs in one agent session: ingest → pulse → Doc → draft
- All problem statement success criteria met

---

## Test Cases

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| T5.1 | MCP draft creation | Agent calls Gmail MCP `create_draft` | Draft appears in Gmail Drafts folder |
| T5.2 | Recipient | Open draft in Gmail UI | To: self or documented alias (per `decision.md`) |
| T5.3 | Subject line | Inspect subject | Clear, dated, product-named e.g. `Weekly Pulse — [Product] — YYYY-MM-DD` |
| T5.4 | Body content | Compare draft body to pulse | Full pulse content included; ≤250 words in body |
| T5.5 | PII in email | Scan draft body | No usernames, emails, or IDs |
| T5.6 | MCP-only Gmail | Code audit for Gmail API/SDK | No direct Gmail API usage in `src/` |
| T5.7 | E2E — happy path | Single agent run from raw exports | Doc created + draft created without manual intermediate steps |
| T5.8 | E2E — ordering | Verify run sequence | Analysis completes before Drive/Gmail calls; Doc before or independent of draft per design |
| T5.9 | Failure isolation | Document behavior if Drive succeeds but Gmail fails | Partial success documented; recovery steps in runbook |
| T5.10 | Runbook | Follow runbook as new operator | Weekly job completable without author present |
| T5.11 | Scheduler worker | `python -m src.worker --pulse-only` | `scheduler-last-run.json` written with `status: success` |
| T5.12 | Windows scheduler | Run `install-weekly-scheduler.ps1` | Task `Groww-Weekly-Pulse` registered for weekly run |
| T5.13 | MCP scheduler | Call `run_weekly_job` on Railway MCP | Fetch + pulse completes; `scheduler_status` returns last run |

---

## End-to-End Success Criteria (from Problem Statement)

- [ ] Reviews from 8–12 weeks imported and themed correctly
- [ ] Weekly pulse: top 3 themes, 3 quotes, 3 action ideas
- [ ] Google Doc created via Drive MCP
- [ ] Gmail draft created via Gmail MCP (to self/alias)
- [ ] No PII in any deliverable
- [ ] Google integrations use MCP only (no parallel API path)

---

## Manual Verification Checklist

- [ ] Draft visible in Gmail (web or app)
- [ ] Doc link included in draft body or run output (optional but recommended)
- [ ] Full E2E demo recorded or walkthrough completed with reviewer
- [ ] Runbook covers: data refresh, MCP auth, expected runtime, failure contacts

---

## Exit Criteria

1. **All** E2E success criteria checked.
2. Gmail draft created exclusively via Gmail MCP (T5.6 passes).
3. One full E2E run documented with date and evidence.
4. Runbook committed under `docs/` or linked from README.
5. Phase 5 checklist **100% passed** — **milestone complete**.

---

## Evidence to Capture

- E2E run timestamp
- Doc URL + draft screenshot (internal)
- Link to all phase eval sign-offs (Phases 1–5)

---

## Milestone Sign-off

| Role | Name | Date | Pass / Fail |
|------|------|------|-------------|
| Implementer | | | |
| Reviewer | | | |
| Stakeholder (optional) | | | |
