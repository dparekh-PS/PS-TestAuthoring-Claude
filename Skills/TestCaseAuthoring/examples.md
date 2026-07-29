---
name: TestCaseAuthoring Execution Guide
type: Skill Execution Guide (teach-by-scenario)
component: TestCaseAuthoring Skill
version: 2.5
date: 2026-07-25
status: Approved
classification: Internal — Professional Services QA
governs: Knowledge/ (single source of truth)
companion: skill.md, workflow.md
---

# TestCaseAuthoring — Skill Execution Guide

## How to Read This Guide

This guide teaches how the TestCaseAuthoring skill *executes* real user requests.
It is an execution guide, not a QA guide. It does not define how test cases are
designed, how coverage is measured, how validation rules work, or how the workbook
is formatted — those remain owned exclusively by the `Knowledge/` folder and are
referenced here by name, never restated.

Each scenario below follows one fixed template so behavior is predictable across
requests:

- **User Request** — a representative phrasing of what the user asks.
- **Inputs** — the concrete sources the skill receives.
- **AI Reasoning Summary** — a high-level statement of how the request is
  interpreted. This is a summary only; internal chain-of-thought is never exposed.
- **Workflow Execution** — the state path traversed, using the state machine defined
  in `workflow.md`.
- **Knowledge Files Referenced** — the governing documents consulted, by name.
- **Validation Checks Performed** — the validation categories invoked, owned by
  `VALIDATION_ENGINE.md`.
- **Deliverables Produced** — the artifacts returned.

### Workflow State Reference

The Workflow Execution field uses the state identifiers defined in `workflow.md`:
`INIT` → `INTENT` → `ACQUIRE` → `REQ_VALIDATE` → `ANALYZE` → `PLAN` → `DESIGN` →
`SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`, with `HALT` as the
safe-stop terminal and human checkpoints `CP-1` (intent), `CP-2` (requirement), and
`CP-3` (generation escalation).

### Standard Deliverable Set

Unless a scenario notes otherwise, a successful run returns two files plus a
response-level summary. The Excel workbook (six-column Master Summary + one
eight-column feature worksheet per feature) conforms to `EXCEL_SPECIFICATION.md`, and
the REQUIRED `<name>.coverage.json` coverage ledger travels with it. Coverage,
validation, assumptions, and open questions are reported as sections of the run's
response — not as separate files or workbook sheets (no Review Summary/RTM sheet as
of v2.4):

✓ Excel Workbook  ✓ `<name>.coverage.json` Coverage Ledger  ✓ Generation Summary
(response-level: coverage, validation, assumptions, open questions)

---

## Scenario 1 — Generate Manual Test Cases from a Jira Story

**User Request:** "Generate manual test cases for `<JIRA-KEY>`."

**Inputs:** A single Jira issue key.

**AI Reasoning Summary:** The request maps to the manual-test-case-generation
capability against a single primary source. Intent confidence is high; no
clarification is required. Linked Confluence pages, if any, are resolved
automatically.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` (Jira via Atlassian MCP;
resolve any linked pages) → `REQ_VALIDATE` → `ANALYZE` → `PLAN` → `DESIGN` →
`SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** `MASTER_CONTEXT.md`, `SYSTEM_INSTRUCTIONS.md`,
`USER_REQUEST_PATTERNS.md`, `AI_CAPABILITIES.md`, `QA_METHODOLOGY.md`,
`TEST_CASE_GENERATION.md`, `VALIDATION_ENGINE.md`, `EXCEL_SPECIFICATION.md`.

**Validation Checks Performed:** Requirement Coverage, Acceptance Criteria, Business
Rule, Test Case Quality, Preconditions, Expected Result, Coverage Completeness (CV-06/07) + Coverage Ledger (CV-08/09/10),
Workbook, QA Readiness.

**Deliverables Produced:** ✓ Excel Workbook ✓ `<name>.coverage.json` Coverage Ledger
✓ Generation Summary (response-level: coverage, validation, assumptions, open
questions).

---

## Scenario 2 — Generate from Jira Story + Linked Confluence Pages

**User Request:** "Create test cases for `<JIRA-KEY>` and include everything in the
linked spec pages."

**Inputs:** One Jira issue key with one or more linked Confluence pages.

**AI Reasoning Summary:** Interpreted as a single feature described across correlated
sources. The skill consolidates the Jira story and its linked Confluence content into
one requirement set with per-source provenance before design begins.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` (Jira + linked Confluence via
Atlassian MCP) → source consolidation within `ACQUIRE` → `REQ_VALIDATE` → `ANALYZE`
→ `PLAN` → `DESIGN` → `SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** `MASTER_CONTEXT.md`, `SYSTEM_INSTRUCTIONS.md`,
`USER_REQUEST_PATTERNS.md`, `AI_CAPABILITIES.md`, `QA_METHODOLOGY.md`,
`TEST_CASE_GENERATION.md`, `VALIDATION_ENGINE.md`, `EXCEL_SPECIFICATION.md`.

**Validation Checks Performed:** Full set from Scenario 1, plus Workflow Validation
where the linked pages describe status transitions.

**Deliverables Produced:** Standard set. Per `EXCEL_SPECIFICATION.md`
source-to-sheet mapping, correlated sources describing one feature produce a single
feature worksheet titled after the Confluence page.

---

## Scenario 3 — Generate from Multiple Confluence Pages

**User Request:** "Generate test cases from these three Confluence pages: `<URL-1>`,
`<URL-2>`, `<URL-3>`."

**Inputs:** Multiple Confluence URLs; no Jira key.

**AI Reasoning Summary:** Treated as multiple requirement sources. Whether the pages
describe one feature or several determines sheet segmentation; provenance is
preserved per page so coverage remains traceable to origin.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` (each page via Atlassian MCP)
→ source consolidation → `REQ_VALIDATE` → `ANALYZE` → `PLAN` → `DESIGN` →
`SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** Standard set. `EXCEL_SPECIFICATION.md` governs
whether distinct features yield one worksheet each or correlate into one.

**Validation Checks Performed:** Requirement Coverage, Acceptance Criteria, Business
Rule, Test Case Quality, Duplicate Detection (across pages), Requirement
Traceability, Workbook, QA Readiness.

**Deliverables Produced:** Standard set, with one feature worksheet per distinct
feature and a consolidated Master Summary spanning all pages.

---

## Scenario 4 — Generate from an Uploaded Word Document with Multiple User Stories

**User Request:** "Here's a requirements doc with several user stories — build test
cases for all of them." (Word document attached.)

**Inputs:** One uploaded `.docx` containing multiple user stories.

**AI Reasoning Summary:** The document is parsed and normalized into the same
internal representation as system-sourced requirements. Each user story is treated
as a distinct requirement grouping; provenance references the document and story
heading.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` (parse uploaded document; no
Atlassian MCP call) → `REQ_VALIDATE` → `ANALYZE` (decompose per story) → `PLAN` →
`DESIGN` → `SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** Standard set; `USER_REQUEST_PATTERNS.md` governs
multi-story handling within a single uploaded source.

**Validation Checks Performed:** Full set, with Requirement Coverage and Acceptance
Criteria validated per story and Duplicate Detection across stories.

**Deliverables Produced:** Standard set. Sheet segmentation follows
`EXCEL_SPECIFICATION.md`; distinct stories map to distinct worksheets.

---

## Scenario 5 — Update an Existing Workbook After Acceptance Criteria Change

**User Request:** "The AC on `<JIRA-KEY>` changed — update the existing workbook."
(Prior workbook provided or referenced.)

**Inputs:** The updated Jira story (or changed AC text) plus the previously generated
workbook.

**AI Reasoning Summary:** Interpreted as an incremental regeneration, not a
from-scratch run. The skill re-acquires the current requirements, re-establishes
acceptance-criteria coverage, and reconciles against the existing workbook —
preserving unaffected test cases, revising affected ones, and adding cases for new
criteria. Regeneration writes a NEW `_v{N}` file rather than overwriting the prior
version (owned by `_base`). Removed criteria and their orphaned cases are surfaced
for reviewer decision rather than deleted silently.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` (current story + existing
workbook) → `REQ_VALIDATE` (diff current vs prior AC set) → `ANALYZE` → `PLAN`
(re-map coverage to the new AC set) → `DESIGN` (revise/add only affected cases) →
`SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` (new `_v{N}` workbook + refreshed coverage
ledger) → `SUMMARY` (report coverage delta vs prior version) → `RETURN`.

**Knowledge Files Referenced:** Standard set; `MASTER_CONTEXT.md` precedence governs
reconciliation where the change conflicts with retained content; `_base` owns the
`_v{N}` versioning and coverage-delta reporting.

**Validation Checks Performed:** Acceptance Criteria (against the new set),
Requirement Coverage, Coverage Completeness (CV-06/07) + Coverage Ledger
(CV-08/09/10), Duplicate Detection, Workbook, QA Readiness.

**Deliverables Produced:** A new `<name>_v{N}.xlsx` workbook plus its refreshed
`<name>_v{N}.coverage.json` coverage ledger, and a response-level Generation Summary
that reports the coverage delta versus the prior version (added, revised, and
orphaned-for-review cases) alongside validation, open questions, and assumptions.

---

## Scenario 6 — Generate Only Negative Test Cases

**User Request:** "Generate only the negative test cases for `<JIRA-KEY>`."

**Inputs:** A Jira issue key with a scenario-type constraint (negative only).

**AI Reasoning Summary:** The capability is unchanged; the request narrows the output
scope to the negative scenario class. Full analysis and coverage planning still run
so that the negative set is complete and traceable; only authoring is scoped to
negative cases. The scope restriction is recorded as an explicit assumption for the
reviewer, since positive/edge coverage is intentionally omitted.

**Workflow Execution:** `INIT` → `INTENT` (capture scenario-type filter) → `ACQUIRE`
→ `REQ_VALIDATE` → `ANALYZE` → `PLAN` (identify negative-relevant criteria) →
`DESIGN` (author negative cases only) → `SELF_REVIEW` → `VALIDATE` (scoped) →
`ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** Standard set; `QA_METHODOLOGY.md` defines what
qualifies as a negative scenario.

**Validation Checks Performed:** Acceptance Criteria (negative applicability),
Business Rule (violation paths), Test Case Quality, Coverage Completeness (CV-06/07) + Coverage Ledger (CV-08/09/10),
Workbook, QA Readiness. Scenario-diversity checks are interpreted against the
declared negative-only scope.

**Deliverables Produced:** Standard set, scoped to negative cases, with the scope
constraint stated in the Generation Summary and Assumptions.

---

## Scenario 7 — Generate Only Edge Cases

**User Request:** "I just need edge cases for `<JIRA-KEY>`."

**Inputs:** A Jira issue key with a scenario-type constraint (edge only).

**AI Reasoning Summary:** Output is scoped to the edge scenario class — boundaries and
unusual-but-valid conditions. Planning still identifies all edge-relevant criteria so
the edge set is complete; the deliberate omission of positive/negative coverage is
recorded as an assumption.

**Workflow Execution:** `INIT` → `INTENT` (capture edge filter) → `ACQUIRE` →
`REQ_VALIDATE` → `ANALYZE` → `PLAN` (identify boundary/edge criteria) → `DESIGN`
(author edge cases only) → `SELF_REVIEW` → `VALIDATE` (scoped) → `ASSEMBLE` →
`SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** Standard set; `QA_METHODOLOGY.md` defines
boundary/edge scenario identification.

**Validation Checks Performed:** Acceptance Criteria (edge applicability), Test Case
Quality, Preconditions, Expected Result, Coverage Completeness (CV-06/07) + Coverage Ledger (CV-08/09/10), Workbook, QA
Readiness.

**Deliverables Produced:** Standard set, scoped to edge cases, with scope noted in
the Generation Summary and Assumptions.

---

## Scenario 8 — Generate Regression Test Cases

**User Request:** "Produce a regression set for `<JIRA-KEY>` / this feature."

**Inputs:** A Jira key or feature reference, with a regression intent.

**AI Reasoning Summary:** Interpreted as prioritizing coverage that protects existing,
stable behavior most at risk from change — core positive flows, enforced business
rules, and critical transitions. The regression framing is a prioritization and
selection lens over the standard capability, not a different design method. Selection
rationale is recorded so the reviewer can confirm scope.

**Workflow Execution:** `INIT` → `INTENT` (capture regression intent) → `ACQUIRE` →
`REQ_VALIDATE` → `ANALYZE` → `PLAN` (prioritize regression-relevant coverage) →
`DESIGN` → `SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** Standard set; `QA_METHODOLOGY.md` governs
risk-and-priority reasoning that informs regression selection.

**Validation Checks Performed:** Requirement Coverage, Business Rule, Workflow, Test
Case Quality, Coverage Completeness (CV-06/07) + Coverage Ledger (CV-08/09/10), Workbook, QA Readiness.

**Deliverables Produced:** Standard set, with a regression-scope statement and
selection rationale in the Generation Summary and Assumptions.

---

## Scenario 9 — Generate Smoke Test Cases

**User Request:** "Give me a smoke test set for `<JIRA-KEY>` / this release."

**Inputs:** A Jira key or feature/release reference, with a smoke-test intent.

**AI Reasoning Summary:** Interpreted as a minimal, high-value set proving core
happy-path functionality is operational — breadth over depth. Like regression, this
is a selection lens over the standard capability. The reduced depth relative to full
coverage is recorded as an explicit assumption.

**Workflow Execution:** `INIT` → `INTENT` (capture smoke intent) → `ACQUIRE` →
`REQ_VALIDATE` → `ANALYZE` → `PLAN` (select core happy-path coverage) → `DESIGN` →
`SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** Standard set; `QA_METHODOLOGY.md` governs
priority-based selection.

**Validation Checks Performed:** Requirement Coverage (core flows), Test Case
Quality, Preconditions, Expected Result, Workbook, QA Readiness.

**Deliverables Produced:** Standard set, scoped to smoke coverage, with scope and
depth caveats in the Generation Summary and Assumptions.

---

## Scenario 10 — Requirements Contain Ambiguity

**User Request:** "Generate test cases for `<JIRA-KEY>`." (Source content is
ambiguous.)

**Inputs:** A Jira key whose requirement text is unclear or open to multiple
interpretations.

**AI Reasoning Summary:** Ambiguity is detected during requirement validation.
Non-blocking ambiguity is recorded as an open point and generation proceeds under a
clearly stated assumption; blocking ambiguity routes to the requirement clarification
checkpoint before any test case is authored. Behavior is never invented to fill a gap.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` → `REQ_VALIDATE` (ambiguity
classified) → [blocking → `CP-2` clarification → resume, or abandon → `HALT`];
[non-blocking → record open point] → `ANALYZE` → `PLAN` → `DESIGN` → `SELF_REVIEW`
→ `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** `USER_REQUEST_PATTERNS.md` (ambiguity handling),
`MASTER_CONTEXT.md` (precedence), plus the standard generation set.

**Validation Checks Performed:** Acceptance Criteria, Requirement Coverage,
Coverage Completeness (CV-06/07) + Coverage Ledger (CV-08/09/10), plus QA Readiness confirming open points are documented.

**Deliverables Produced:** Standard set. Ambiguities appear as Open Questions and, if
generation proceeded, the interpretation used appears in Assumptions.

---

## Scenario 11 — Acceptance Criteria Missing

**User Request:** "Create test cases for `<JIRA-KEY>`." (Story has no acceptance
criteria.)

**Inputs:** A Jira story lacking explicit acceptance criteria.

**AI Reasoning Summary:** The absence of acceptance criteria is a validation finding.
Where the requirement remains testable, the skill proceeds under explicitly stated
assumptions derived from the described behavior and records the gap; where criteria
are essential and cannot be inferred, it routes to the requirement clarification
checkpoint. Acceptance criteria are never fabricated as if authoritative.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` → `REQ_VALIDATE` (missing-AC
finding) → [essential-and-uninferable → `CP-2` → resume/`HALT`]; [inferable → record
assumptions] → `ANALYZE` → `PLAN` → `DESIGN` → `SELF_REVIEW` → `VALIDATE` →
`ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** `USER_REQUEST_PATTERNS.md` (input sufficiency),
`SYSTEM_INSTRUCTIONS.md` (traceability objective), plus the standard generation set.

**Validation Checks Performed:** Acceptance Criteria, Requirement Coverage,
Coverage Completeness (CV-06/07) + Coverage Ledger (CV-08/09/10), QA Readiness.

**Deliverables Produced:** Standard set. The missing-AC condition and any assumed
criteria are prominent in Open Questions and Assumptions.

---

## Scenario 12 — Conflicting Requirements Between Jira and Confluence

**User Request:** "Generate test cases for `<JIRA-KEY>` and its linked spec." (Jira
and Confluence disagree.)

**Inputs:** A Jira story and a linked Confluence page with conflicting statements.

**AI Reasoning Summary:** The conflict is detected during requirement validation.
Where the precedence rules resolve it, the skill applies precedence and records the
decision; where they do not, the conflict is recorded and routed to the requirement
clarification checkpoint. The skill does not silently pick an interpretation.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` (both sources) → source
consolidation → `REQ_VALIDATE` (conflict detected) → [precedence resolves → record
decision]; [unresolved → `CP-2` → resume/`HALT`] → `ANALYZE` → `PLAN` → `DESIGN` →
`SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** `MASTER_CONTEXT.md` (conflict precedence),
`USER_REQUEST_PATTERNS.md`, plus the standard generation set.

**Validation Checks Performed:** Requirement Coverage, Acceptance Criteria, Business
Rule, Coverage Completeness (CV-06/07) + Coverage Ledger (CV-08/09/10), QA Readiness.

**Deliverables Produced:** Standard set. The conflict, its resolution or open status,
and the source that prevailed are recorded in Conflicts, Open Questions, and
Assumptions.

---

## Scenario 13 — Business Rules Found Only in a Design Document

**User Request:** "Generate test cases for `<JIRA-KEY>`; the design doc has the
detailed rules." (Design document linked or uploaded.)

**Inputs:** A Jira story plus a design document (linked Confluence page or uploaded
file) that is the sole source of certain business rules.

**AI Reasoning Summary:** The design document is treated as a first-class requirement
source and consolidated with the story. Business rules present only in the design doc
are captured, decomposed, and covered like any other rule, with provenance pointing
to the design document so their origin is traceable.

**Workflow Execution:** `INIT` → `INTENT` → `ACQUIRE` (story + design doc) → source
consolidation → `REQ_VALIDATE` → `ANALYZE` (decompose design-doc rules) → `PLAN` →
`DESIGN` → `SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` → `SUMMARY` → `RETURN`.

**Knowledge Files Referenced:** Standard set; `QA_METHODOLOGY.md` governs
business-rule decomposition and coverage.

**Validation Checks Performed:** Business Rule (design-doc rules), Acceptance
Criteria, Requirement Coverage, Coverage Completeness (CV-06/07) + Coverage Ledger (CV-08/09/10), Workbook, QA Readiness.

**Deliverables Produced:** Standard set, with design-doc-sourced rules covered and
their source-anchored provenance recorded in the `<name>.coverage.json` coverage
ledger.

---

## Scenario 14 — Workbook with One Worksheet per User Story

**User Request:** "Generate the workbook with a separate sheet for each user story."

**Inputs:** Multiple user stories (Jira keys or an uploaded multi-story document) with
an explicit sheet-segmentation preference.

**AI Reasoning Summary:** The request specifies output structure: one feature
worksheet per user story. The skill honors this segmentation during assembly while
still producing the mandatory Master Summary sheet. Segmentation
that conflicts with the specification's correlation rules is reconciled per
`EXCEL_SPECIFICATION.md` and noted.

**Workflow Execution:** `INIT` → `INTENT` (capture per-story segmentation) →
`ACQUIRE` → `REQ_VALIDATE` → `ANALYZE` (per story) → `PLAN` → `DESIGN` →
`SELF_REVIEW` → `VALIDATE` → `ASSEMBLE` (one worksheet per story) → `SUMMARY` →
`RETURN`.

**Knowledge Files Referenced:** Standard set; `EXCEL_SPECIFICATION.md` governs sheet
composition, ordering, and the mandatory summary sheets.

**Validation Checks Performed:** Requirement Coverage (per story), Duplicate
Detection, Workbook (sheet composition and ordering), QA Readiness.

**Deliverables Produced:** Standard set, with one feature worksheet per user story
plus the Master Summary sheet.

---

## Scenario 15 — Validation Failure Requiring Regeneration

**User Request:** "Generate test cases for `<JIRA-KEY>`." (A validation defect arises
during the run.)

**Inputs:** Any supported source; a defect is detected at the validation gate — for
example, an acceptance criterion left uncovered or a rule with positive-only coverage.

**AI Reasoning Summary:** The validation gate is blocking. On failure, the skill
invokes the automatic-correction and re-validation loop — regenerating only the
deficient coverage and re-entering validation — within the bounded retry limit. Only
after validation passes is a deliverable assembled; failures unresolved within the
limit escalate to human review rather than releasing incomplete output.

**Workflow Execution:** `INIT` → … → `DESIGN` → `SELF_REVIEW` → `VALIDATE` (fail) →
automatic correction re-enters `DESIGN`/`VALIDATE` (bounded retry) → `VALIDATE`
(pass) → `ASSEMBLE` → `SUMMARY` → `RETURN`. If unresolved after the retry bound:
`CP-3` → `HALT` with diagnostics.

**Knowledge Files Referenced:** `VALIDATION_ENGINE.md` (validation flow, gap
detection, automatic correction, re-validation), plus the standard generation set.

**Validation Checks Performed:** The full validation category set, re-executed after
correction until all critical checks pass (or escalation on exhaustion).

**Deliverables Produced:** On success, the standard set, with the Validation Summary
recording the initial finding, the correction applied, and the passing re-validation.
On exhaustion, no workbook is released; a diagnostic explains the unresolved failure
and required action.

---

## Cross-Scenario Behavior Notes

- **Read-only sources.** Across every scenario, Jira and Confluence are accessed
  through Atlassian MCP for reading only; the skill never writes to Jira or
  Confluence (see `skill.md` Non-Goals).
- **Human review is standing.** Every successful deliverable is returned
  review-required regardless of scenario; the failure-triggered checkpoints
  (`CP-1`/`CP-2`/`CP-3`) are in addition to this standing posture.
- **Scope constraints are recorded, not assumed away.** Scenarios that narrow output
  (negative-only, edge-only, regression, smoke) always record the omitted coverage as
  an explicit assumption so the reviewer understands what was and was not covered.
- **Fail-safe over partial output.** No scenario returns partial, unvalidated, or
  fabricated deliverables; unresolved conditions resolve to a documented open point,
  a human checkpoint, or a safe `HALT`.
- **Coverage ledger travels with the workbook.** Across every scenario a successful
  run emits the REQUIRED `<name>.coverage.json` coverage ledger alongside the
  workbook; a missing or malformed ledger is blocking (CV-11).
- **IDs are namespaced and registered.** Cross-workbook Test Case ID uniqueness is
  enforced by NS-01/NS-02 against `project_registry.json` and `id_ledger.json`; after
  a delivered workbook passes, its IDs are registered via
  `validate_workbook.py --register <workbook>`.
- **Single source of truth.** Every scenario delegates its domain logic to the
  `Knowledge/` documents named in its Knowledge Files Referenced field; this guide
  demonstrates execution behavior only.
