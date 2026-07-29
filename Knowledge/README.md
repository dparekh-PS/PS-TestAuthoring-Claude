# Knowledge Base — PS AI QA Assistant

Orientation for the `Knowledge/` folder. This file is a **map, not an authority** — it
tells you which document owns what, and where to start. It defines no rules of its own.

> **What this project actually is.** PS-TestAuthoring is a **document-driven AI assistant**,
> not a standalone application. There is no Node.js/TypeScript service, no `src/`, and no
> compiled binary. The "engine" is a set of governing Markdown documents (this folder) plus
> an execution layer (`Skills/`) that an AI assistant reads and follows at runtime to turn
> requirements (Jira / Confluence / Word / PDF) into a review-ready Excel workbook. The only
> executable code in the project is the Python tooling under `Skills/` (the workbook
> validator, the doc-linter, and one-off migration scripts).

---

## How the system runs (high level)

```
Requirement source(s)                 Governed by Knowledge/ (this folder)
  Jira / Confluence / Word / PDF   ─▶  executed via Skills/ (workflow + validators)  ─▶  Review-ready .xlsx
                                        │
                                        └─ enforced by Skills/*/validate_workbook.py
```

The AI assistant reads `MASTER_CONTEXT.md` first, routes the request via
`USER_REQUEST_PATTERNS.md`, runs the workflow in `Skills/TestCaseAuthoring/workflow.md`,
authors test cases per the standards below, validates them against `VALIDATION_ENGINE.md`,
and produces a workbook conforming to `EXCEL_SPECIFICATION.md` — which the deterministic
validator then checks before delivery.

## Document index (single-source-of-truth owners)

| Document | Owns | Start here when… |
|----------|------|------------------|
| `MASTER_CONTEXT.md` | Orchestration, ownership matrix, precedence | you need the big picture or a conflict resolved |
| `SYSTEM_INSTRUCTIONS.md` | Identity, principles, guardrails | you need the operating rules |
| `USER_REQUEST_PATTERNS.md` | Intent detection / routing | interpreting what the user asked for |
| `QA_METHODOLOGY.md` | Test-design methodology (why/how to cover) | analysing requirements, designing coverage |
| `TEST_CASE_GENERATION.md` | Authoring standard (how to write a TC) | writing individual test cases |
| `VALIDATION_ENGINE.md` | All validation rules + self-correction | checking output before delivery |
| `EXCEL_SPECIFICATION.md` | Workbook output contract (schema, IDs, naming) | building or checking the `.xlsx` |
| `AI_CAPABILITIES.md` | Capability catalog + maturity | deciding whether a request is in scope |
| `DATA_HANDLING.md` | Data classification, PII/secret rules, data flow | ingesting or producing any content |
| `EXAMPLES.md` | Conformant worked examples | you want a concrete pattern to match |
| `ARCHITECTURE.md` | Architectural context | you need design/troubleshooting context |
| `README.md` (this file) | Orientation only | first time in the folder |

The rule that keeps these consistent: **each concept has exactly one owner** (see
`MASTER_CONTEXT.md` §6.2). Every other document references the owner rather than restating
it, and `Skills/lint_docs.py` fails CI if that discipline slips.

## Execution & enforcement layer

Lives in `Skills/` (see `Skills/README.md`):

- `Skills/TestCaseAuthoring/` — the one built skill (maturity: Production).
- `Skills/_base/workflow.base.md` — shared workflow substrate inherited by every skill.
- `Skills/SKILLS_REGISTRY.md` — manifest of skills and how to add one.
- `Skills/TestCaseAuthoring/validate_workbook.py` — deterministic workbook validator.
- `Skills/lint_docs.py` — documentation linter guarding the invariants above.

## Output

Every run produces one Excel workbook (`.xlsx`) per `EXCEL_SPECIFICATION.md`: a Master
Summary sheet and one feature worksheet per feature. As of v2.4 the Review Summary sheet
(assumptions, open points, conflicts, confidence, and the Requirement Traceability Matrix)
is no longer emitted — those are handled as design-time concerns and surfaced in the run's
generation summary. The workbook is a **proposal pending human QA review**, never an
authoritative record until reviewed.

## Governance

| Version | Date | Change |
|---------|------|--------|
| 2.0 | 2026-07-23 | Rewritten to describe the actual document-driven system (the prior version described a non-existent TypeScript/ExcelJS application). |
