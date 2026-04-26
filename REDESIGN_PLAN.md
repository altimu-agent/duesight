# DueSight UI/UX Redesign Plan

## Research summary

Most relevant product types from the UI/UX Pro Max database (`nextlevelbuilder/ui-ux-pro-max-skill`): DueSight is a hybrid of **B2B Service** (trust signals, ROI clarity), **Analytics Dashboard** (data-density, color-coded priority), and **AI/Chatbot Platform** (streaming, conversational, minimal chrome).

Hard rules from `ux-guidelines.csv` to honor across the redesign:

- Streaming feedback (#93) — agent output should feel live
- Step indicators "Step N of M" (#81) — replace the running log with structured progress
- Reserve space for async content (#19) — no layout jump as cards appear
- Visible labels, not placeholder-only (#54)
- Clear error/success feedback (#33-34)
- Respect `prefers-reduced-motion` (#9, #99)
- Visible focus rings (#28)
- ≥16px body text (#67)
- Feedback loop on AI output (#98) — eventually thumbs / regenerate

## Risk Score: improvements (deferred to Phase 4)

Current implementation in [src/prompts.py:173-205](src/prompts.py#L173-L205) is strict and arithmetic, which is good. Suggested upgrades:

1. **Cap lawsuit penalty.** "+15 each" uncapped means three nuisance trademark suits dominate. Suggest `+15 per substantive matter, max +30`.
2. **Add jurisdiction / sanctions axis** (+25). OFAC-sanctioned country = hard procurement block; today the prompt has no place for it.
3. **Add financial-stress axis** (+10). Recent layoffs, down rounds, missed payroll.
4. **Add cyber / breach axis** (+10). Public breach in last 24 months.
5. **Tighten "questionable leadership" → specifics.** "Founder with regulatory ban, prior fraud conviction, or ≥3 failed companies" is auditable.
6. **Calibrate verdict to contract value deterministically.** Map score 55–65 → CONDITIONAL at <$250K, REJECTED at >$1M, instead of leaving the threshold to the model's tone.

## Phases

### Phase 1 — UI restructure (frontend only)

- **F1 Progressive form.** company / website / industry required; country, contract value, competitors collapsed under "Show more details".
- **F4 Summary-first report.** Executive summary + key findings card up top; full markdown collapsed under "View full report".
- **F5 Download dropdown.** Primary "Download PDF" via `html2pdf.js`, chevron dropdown for Markdown / JSON.
- **F6 Interactive loading.** Replace the scrolling log with a structured live panel: step counter, elapsed time, current-task line.
- **File split.** Extract CSS to [static/styles.css](static/styles.css), JS to [static/app.js](static/app.js); [static/index.html](static/index.html) becomes markup-only.

### Phase 2 — Data Integrity Score

Compute deterministically in Python after the report is generated (no LLM math, same approach as `reconcile_score`):

- **Source count** (0–30 pts) — unique domains from `sources[]` + `fetch_page` call history
- **Coverage** (0–30 pts) — non-empty signals across the 5 due-diligence sections
- **Diversity** (0–20 pts) — ≥4 source categories (homepage, review/G2, news, financial DB, social)
- **Authority** (0–20 pts) — hits in known authoritative domains (crunchbase, sec.gov, court records, G2, …)

Verdicts: `<40` INSUFFICIENT, `40–70` PARTIAL, `70+` STRONG. UI card sits next to Risk Score; click reveals source list + section coverage matrix.

### Phase 3 — Conversational follow-up

New `POST /api/chat` SSE endpoint. Stateless: client sends `[report_markdown, prior_messages, new_user_message]` each turn. Render as chat bubbles below the report. Pre-seed with a system message scoping the model to the report context + the same tools.

### Phase 4 — Risk Score v2 (optional)

Implement the 6 improvements listed above. Touches [src/prompts.py](src/prompts.py) and the `reconcile_score` function in [src/agent.py](src/agent.py). Big enough to deserve its own pass.

## File split target

```
static/
├── index.html      # markup only
├── styles.css      # all CSS
└── app.js          # all JS
```

No bundler. [server.py:26](server.py#L26) already mounts `/static`, so this is free.
