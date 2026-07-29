# PS-TestAuthoring — Architecture Flow & File Guide

*A QA-architect's analysis: how the agent turns a requirement into review-ready test cases, and what every file in the project does.*

Date: 2026-07-23 · Reflects: EXCEL_SPECIFICATION v2.5 (merged layout; no Review Summary; 6-column Master Summary), single built skill = TestCaseAuthoring.

---

## 1. What this agent is (in one paragraph)

PS-TestAuthoring is a **document-driven AI assistant**, not a compiled application. An AI
runtime reads a set of governing Markdown documents (the `Knowledge/` folder — the single
source of truth) and follows an execution workflow (the `Skills/` folder) to convert a
requirement source (Jira story, Confluence page, Word/PDF/text) into a **review-ready Excel
workbook of manual test cases**. The only executable code is small Python tooling under
`Skills/` that *enforces* the output contract and the documentation's consistency. Nothing
is delivered unless it passes that enforcement.

Three layers:

| Layer | Folder | Role |
|-------|--------|------|
| **Knowledge** | `Knowledge/` | The "what/why" — domain truth. Each concept has exactly one owning document. |
| **Skills** | `Skills/` | The "how it runs" — the workflow (state machine) + machine validators. |
| **Enforcement** | `Skills/*/validate_workbook.py`, `Skills/lint_docs.py` | Deterministic gates. The LLM proposes; these dispose. |

---

## 2. End-to-end flow (input → test cases)

The run is a **finite state machine**. Generic states are inherited from
`Skills/_base/workflow.base.md`; the three **domain** states (ANALYZE → PLAN → DESIGN) are
owned by `Skills/TestCaseAuthoring/workflow.md`. Each state names the Knowledge document
that governs it, and there are three quality gates plus two human checkpoints.

```
( user request )
      │
      ▼
[1 INIT]  ─ initialise run; detect if this story already produced a workbook (→ _vN regeneration)
      │
      ▼
[2 INTENT] ─ classify the ask (generate / regression / smoke / negative / edge …)
      │        governed by USER_REQUEST_PATTERNS.md   · CP-1 human checkpoint if ambiguous
      ▼
[3 ACQUIRE] ─ fetch ALL source: Jira issue (*all fields incl. Acceptance-Criteria custom
      │        field), linked Confluence pages, uploaded docs; record provenance
      │        governed by _base "Source acquisition rules" + DATA_HANDLING.md (PII/secrets)
      ▼
[4 REQ_VALIDATE] (gate) ─ is the source real & sufficient? "absent AC" vs "not fetched"
      │        is distinguished here.        · CP-2 human checkpoint if insufficient/contradictory
      ▼
[5 ANALYZE]  ─ decompose requirements; extract ACs, business rules, actors, workflows;
      │        assign R01…, AC-1…            governed by QA_METHODOLOGY.md
      ▼
[6 PLAN]     ─ plan coverage: scenario types per AC (positive/negative/edge), boundary
      │        values, scenario-diversity, coverage plan   governed by QA_METHODOLOGY.md
      ▼
[7 DESIGN]   ─ author test cases: atomic steps, measurable expected results, priority,
      │        environment-independent placeholders / (value TBC)
      │        governed by TEST_CASE_GENERATION.md (+ QA_METHODOLOGY §8.5 test-data rule)
      ▼
[8 SELF_REVIEW] (cheap gate) ─ model self-challenges the draft and fixes obvious defects
      │        before the expensive gate
      ▼
[9 VALIDATE] (gate) ─ run every applicable rule in VALIDATION_ENGINE.md:
      │        extraction-fidelity → coverage → scenario balance → risk-based depth →
      │        expected-result structure → duplicates → traceability. Fail ⇒ self-correct & re-run.
      ▼
[10 ASSEMBLE] (I/O) ─ build the workbook to EXCEL_SPECIFICATION.md; apply the standard
      │        merged-cell presentation (apply_merged_layout.py); THEN run
      │        validate_workbook.py — a workbook that fails is never returned.
      ▼
[11 SUMMARY] ─ write the Master Summary sheet (per-feature counts, coverage %, open-point
      │        counts); if regeneration, state the diff vs the prior version
      ▼
[12 RETURN]  ─ deliver the .xlsx (proposal, pending human QA review)

  Any unrecoverable problem → [HALT] (safe stop with guidance). Recovery is always one of:
  bounded retry (N=2) · human checkpoint · HALT. No path dead-ends.
```

### The three gates (why output is trustworthy)

1. **SELF_REVIEW** — cheap, LLM-side: catches obvious gaps before the blocking gate.
2. **VALIDATE (VALIDATION_ENGINE.md)** — the QA rulebook: 100% AC coverage, scenario
   balance (Neg+Edge ≥ 40%), risk-based depth, no orphans, measurable results, extraction
   fidelity (ACs must trace to the source, not be invented).
3. **ASSEMBLE → validate_workbook.py** — *deterministic code*, not the model's opinion:
   checks sheet order, exact 8-column schema, merged-cell layout, global ID format,
   blank/enum rules, the embedded schema stamp, cross-workbook ID uniqueness (NS-01/02), and
   PII/secret checks (DP-01/02). Coverage is machine-verified via the Master Summary (CV-06/07)
   and the source-anchored coverage ledger sidecar (CV-08/09/10; a missing ledger blocks —
   CV-11). The Review Summary/RTM sheet is not emitted (removed v2.4); traceability is
   design-time only.
   Exit non-zero ⇒ not delivered.

### Human checkpoints

- **CP-1** (after INTENT): the ask is ambiguous → confirm rather than guess.
- **CP-2** (after REQ_VALIDATE): the source is missing/contradictory → raise it, don't invent.

### What the output looks like

One `.xlsx` per run, named `TC-{ProjectKey}-{Story}_{YYYYMMDD}.xlsx` (regeneration → `_vN`):

- **Master Summary** — 6 columns: Feature/Source, Source Reference, Requirements, Acceptance Criteria, Test Cases, AC Coverage %.
- **Feature worksheet(s)** — the test cases in 8 columns (`Test Case ID | Requirement
  Title | Test Case Title | Pre-Conditions | Step# | Test Step | Expected Result |
  Priority`), with TC-level fields **merged vertically** so each test case shows one ID,
  requirement, title, pre-conditions, and priority spanning its step rows.

As of v2.4 the workbook contains only the Master Summary and feature worksheet(s). The
Review Summary sheet — the confidence assessment, assumptions, open points, conflicts, and
the Requirement Traceability Matrix — is no longer emitted; assumptions/open points and
requirement traceability are handled as design-time concerns, not workbook sheets.

---

## 3. What each file does

### Root

| File | Role |
|------|------|
| `README.md` | Top-level project overview: what the agent is, the two gates, repo layout, runtime, honest status. |
| `PROJECT_INSTRUCTIONS.md` | Project configuration/routing. Mandates using the `Skills/TestCaseAuthoring/` documents for test-case work — never a registered/installed skill. |
| `archive/ARCHITECTURE_REVIEW_2026-07-23.md` | Archived snapshot — the original brutally-honest architecture review (baseline 5.2/10). Superseded. |
| `archive/ENTERPRISE_ARCHITECTURE_REVIEW_2026-07-25.md` | Archived snapshot — the AM board review (5.0/10). Superseded. |
| `archive/REMEDIATION_SCORECARD.md` | Archived snapshot — before/after scores (7.5/10, since re-assessed). Superseded. |
| `PS-TestAuthoring_Flow_and_Files.md` | This document. |
| `STATE_OF_THE_SYSTEM_2026-07-25.md` | Current living review — the up-to-date state-of-the-system assessment (supersedes the two historical reviews above for current status). |
| `TC-Epic04-ApprovalProcess_20260723_v4.xlsx` | Sample output — Epic 04 Approval Process (20 stories, full merged layout). |
| `TC-SAMP-110_20260723_v6.xlsx` | Sample output — "Mark Quote as Presented" (13 test cases, merged layout). |
| `TC-SAMP-166_20260723_v6.xlsx` | Sample output — "Approval Notification – PM" (15 test cases, with 59/60/61 boundary coverage). |

### Knowledge/ — the single source of truth (each concept, one owner)

| File | Owns / governs |
|------|----------------|
| `MASTER_CONTEXT.md` | **Orchestrator.** Document map, the single-source-of-truth ownership matrix, the full precedence order, and the consultation sequence. Read first for context or to resolve a conflict. |
| `SYSTEM_INSTRUCTIONS.md` | Assistant identity, guiding principles, and **guardrails** (never invent, never reproduce PII/secrets, human review mandatory). Defers workflow/validation/schema detail to their owners. |
| `USER_REQUEST_PATTERNS.md` | **Intent detection → capability routing** (which request maps to which capability). Owns INT-01 = TestCaseAuthoring. |
| `QA_METHODOLOGY.md` | **Test-design methodology** (governs ANALYZE + PLAN): decomposition, business-rule types, coverage strategy, boundary analysis, priority rubric, and the §8.5 environment-independent test-data / `(value TBC)` convention. |
| `TEST_CASE_GENERATION.md` | **Authoring standard** (governs DESIGN): fields, title conventions/prefixes, atomic steps, measurable expected results, and the global TC-ID format. |
| `VALIDATION_ENGINE.md` | **All validation rules + the self-correction loop** (governs VALIDATE): extraction fidelity, coverage, scenario-balance thresholds, risk-based coverage, expected-result structure, traceability, QA-readiness. |
| `EXCEL_SPECIFICATION.md` | **The output contract** (governs ASSEMBLE): sheet composition (Master Summary + feature sheets; no Review Summary/RTM as of v2.4), the exact 8 columns, merged-cell layout, global ID format, file naming, formatting, and the mandatory `schema:2.5` stamp. |
| `AI_CAPABILITIES.md` | Capability catalog + the maturity model (Planned/Pilot/Production). TestCaseAuthoring = Production; others Planned. |
| `DATA_HANDLING.md` | Data classification, PII/secret minimisation, retention, and the accurate cloud-LLM data-flow statement (governs ACQUIRE). |
| `EXAMPLES.md` | Teach-by-example corpus of conformant test cases and good-vs-poor contrasts. |
| `ARCHITECTURE.md` | Architectural context. Note: its software/CLI/ExcelJS content is an *illustrative reference design*, not the deployed system (which is document-driven). |
| `README.md` | Knowledge-base orientation — a map of which document owns what. |

### Skills/ — the execution + enforcement layer

| File | Role |
|------|------|
| `README.md` | Execution-layer guide: folder layout, how to run the two gates, and how to add a new skill. |
| `SKILLS_REGISTRY.md` | Manifest of skills (TestCaseAuthoring = Production), the "how to add a skill" checklist, and the record of **deprioritized** ideas (RequirementReview, with the reason it was dropped). |
| `lint_docs.py` | **Documentation linter** — fails CI on encoding corruption, retired vocabulary, stale schema stamps, bare (non-global) TC IDs, broken cross-references, and duplicated ownership. Guards the invariants established during remediation. |
| `_base/workflow.base.md` | **Shared workflow substrate** inherited by every skill: the generic states (INIT/INTENT/ACQUIRE/REQ_VALIDATE/SELF_REVIEW/VALIDATE/ASSEMBLE/SUMMARY/RETURN/HALT), the context object, retry strategy, error recovery, human checkpoints, source-acquisition rules, and regeneration/versioning. |
| `_template/skill.md`, `_template/workflow.md` | Skeleton to scaffold a new skill by inheritance (add only its domain states) without touching the base. |
| `TestCaseAuthoring/skill.md` | The skill contract: responsibility, supported inputs, deliverables, boundaries. |
| `TestCaseAuthoring/workflow.md` | The skill's **domain states** (`ANALYZE → PLAN → DESIGN`), inserted into the inherited base workflow. |
| `TestCaseAuthoring/examples.md` | Execution examples for the skill (how a run behaves end-to-end). |
| `TestCaseAuthoring/validate_workbook.py` | **The deterministic workbook validator** — the machine authority for the output contract and the single source of truth for validation rule codes/severities (the `RULES` catalog + `--rules`). Enforces structure, IDs, coverage-completeness (CV-06/07), the coverage ledger (CV-08..11), and cross-workbook ID uniqueness (NS-01/02). This is the ASSEMBLE gate; also `--register`s delivered workbooks into the ID ledger. |
| `TestCaseAuthoring/apply_merged_layout.py` | The **standard presentation** step: merges TC-level cells per test case and right-sizes row heights. Run in ASSEMBLE. |
| `TestCaseAuthoring/project_registry.json` | Known project keys / business units for namespacing (validator NS-02). |
| `TestCaseAuthoring/id_ledger.json` | Persistent record of every issued Test Case ID; enforces global uniqueness across workbooks (validator NS-01). |
| `TestCaseAuthoring/build_coverage_ledger.py` | Coverage-ledger generator — emits the per-workbook `<wb>.coverage.json` sidecar the validator checks (CV-08..11). Run in ASSEMBLE. |
| `TestCaseAuthoring/<workbook>.coverage.json` | Per-workbook coverage sidecar (one per delivered `.xlsx`): the verifiable AC-to-TC coverage record the validator reads instead of a worksheet (CV-08..11). |

---

## 4. Worked trace (SAMP-110)

1. **INTENT** — "generate test cases for SAMP-110" → INT-01 (TestCaseAuthoring).
2. **ACQUIRE** — fetch SAMP-110 with all fields: description + the **Acceptance Criteria
   custom field** (5 ACs) + linked Confluence QPN-001; record provenance.
3. **REQ_VALIDATE** — ACs are present (not a fetch miss); proceed.
4. **ANALYZE / PLAN** — R01 + AC-1…AC-5; identify business rules; note AC-4 (edit rules)
   and the trigger are undefined.
5. **DESIGN** — 13 test cases, positive/negative/edge; undefined behaviour written with
   placeholders and `(TBC)`, **not invented**.
6. **VALIDATE** — coverage 100% of the *stated* ACs; assumptions/open points recorded;
   confidence = Low (honest, because the source is thin).
7. **ASSEMBLE** — build workbook, merge TC-level cells, run `validate_workbook.py` → PASS.
8. **RETURN** — `TC-SAMP-110_20260723_v6.xlsx`, pending human QA review.

The contrast with SAMP-166 (well-specified, concrete 60-line threshold) is instructive:
same pipeline, but Medium confidence and real boundary tests — **output quality tracks
input quality**, which is why requirement quality is best handled upstream by the SAs.

---

## 5. Architect's summary

- **Separation of concerns is clean:** domain truth (Knowledge) is separate from execution
  (Skills) which is separate from enforcement (validators). One owner per concept.
- **Trust comes from the deterministic gate**, not from the model asserting quality: a
  workbook is only "review-ready" if `validate_workbook.py` passes it.
- **Honesty is built in:** the pipeline records assumptions/open points and reports Low
  confidence rather than inventing behaviour when a requirement is thin.
- **Extensible by inheritance:** a new skill = base workflow + its domain states + one
  Knowledge doc + a registry entry, with no change to the base (demonstrated by the
  add-and-remove of RequirementReview).
- **Known limits:** one skill ships today; nothing has been run at volume; merged output
  needs a flat export before Zephyr/CSV import.
