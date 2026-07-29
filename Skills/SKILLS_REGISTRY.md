---
name: Skills Registry
type: Skill Manifest
version: 1.0
status: Approved
classification: Internal — Professional Services QA
---

# Skills Registry

The single manifest of every skill in the project. Each skill = the shared substrate in
`Skills/_base/workflow.base.md` + its own domain states + its output spec + one row here.
Adding a skill must not require editing the base workflow or any other skill.

## Registered skills

| Skill | Status | Trigger intents (owned by USER_REQUEST_PATTERNS.md) | Domain states (added to base) | Knowledge dependencies | Output | Machine validator |
|-------|--------|------------------------------------------------------|-------------------------------|------------------------|--------|-------------------|
| **TestCaseAuthoring** | Production | INT-01 (generate/create/update manual test cases, regression/smoke/negative/edge, from Jira/Confluence/Word) | `ANALYZE → PLAN → DESIGN` | QA_METHODOLOGY, TEST_CASE_GENERATION, VALIDATION_ENGINE, EXCEL_SPECIFICATION | Review-ready `.xlsx` workbook (EXCEL_SPECIFICATION v2.5) | `Skills/TestCaseAuthoring/validate_workbook.py` — also enforces the coverage ledger (CV-08..11), cross-workbook ID uniqueness (NS-01/02) and PII/secret checks (DP-01/02), backed by `project_registry.json` + `id_ledger.json` + per-workbook `<wb>.coverage.json` |

## Deprioritized (evaluated, deliberately not built)

| Skill | Decision | Rationale |
|-------|----------|-----------|
| RequirementReview | **Deprioritized — built, trialed, and removed; not currently planned.** | Built and trialed (SAMP-110, SAMP-125), then removed. As a blocking pre-generation gate it does not fit the QA team's bulk workflow: the QA team cannot fix acceptance criteria themselves, so every NOT-READY verdict forces a hand-off to the SAs and a re-request for generation. At batch scale this creates significant back-and-forth and stalls test-case delivery. Requirement quality belongs with the SAs/BAs who own the stories, not as a QA-side gate at generation time. (Note: the useful hardening it prompted — fetching the Jira Acceptance Criteria custom field correctly — was kept in `_base` and benefits TestCaseAuthoring.)

## Planned skills (not yet built)

These are the growth targets. Each becomes a new folder `Skills/<Name>/` with a `skill.md`,
a `workflow.md` that declares only its domain states, one Knowledge document, and a row
promoted from the table below. They inherit the base substrate unchanged.

| Skill | Purpose | Likely domain states | New Knowledge doc |
|-------|---------|----------------------|-------------------|
| RequirementAnalysis | Deeper quality scoring / metrics over a set of requirements | `DECOMPOSE → SCORE → REPORT` | REQUIREMENT_ANALYSIS.md |
| TraceabilityAnalysis | Standalone RTM across artifacts | `MAP → RECONCILE → MATRIX` | (reuses the design-time traceability contract in QA_METHODOLOGY.md — Requirement Traceability; no dedicated spec anchor yet) |
| RegressionPlanning | Select regression scope from change set | `IMPACT → SELECT → PRIORITIZE` | REGRESSION_STRATEGY.md |
| RiskAssessment | Risk-based test prioritization | `IDENTIFY_RISKS → SCORE → PRIORITIZE` | RISK_MODEL.md |
| TestDataGeneration | Derive test data sets from rules | `EXTRACT_RULES → DERIVE → TABULATE` | TEST_DATA_STRATEGY.md |
| AutomationScriptGeneration | Draft automation from manual TCs | `MAP_STEPS → EMIT → LINT` | AUTOMATION_STANDARD.md |
| ImpactAnalysis | Blast-radius of a change | `TRACE_DEPS → ASSESS → REPORT` | IMPACT_MODEL.md |
| TestExecutionPlanning | Sequence/assign execution | `GROUP → SEQUENCE → ASSIGN` | EXECUTION_PLANNING.md |
| DefectAnalysis | Cluster/triage defects | `INGEST → CLUSTER → SUMMARIZE` | DEFECT_TAXONOMY.md |

## How to add a skill (checklist)

1. Copy `Skills/_template/` to `Skills/<NewSkill>/`.
2. In its `workflow.md`, declare only the domain states (the base substrate is inherited).
3. Add the skill's Knowledge document under `Knowledge/` and register it in
   `MASTER_CONTEXT.md` §6 (Document Map + Ownership Matrix + precedence).
4. Add the skill's trigger intent to `USER_REQUEST_PATTERNS.md` and its capability to
   `AI_CAPABILITIES.md`.
5. Add a machine validator for its deliverable (or reuse an existing one).
6. Promote the skill from "Planned" to "Registered" in the table above.

No step requires editing `_base/workflow.base.md` or another skill — that is the test of
whether the architecture is genuinely extensible.
