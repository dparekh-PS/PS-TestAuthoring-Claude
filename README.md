# PS-TestAuthoring

An enterprise, **document-driven AI assistant** for Professional Services QA teams. It
turns requirement sources — Jira stories, Confluence pages, Word/PDF documents — into
**review-ready manual test cases** delivered as a formatted, traceable Excel workbook.

> **This is not a standalone application.** There is no compiled service to install and no
> `src/`. The system is a set of governing Markdown documents (`Knowledge/`) plus an
> execution layer (`Skills/`) that an AI assistant reads and follows at runtime. The only
> executable code is the Python tooling under `Skills/` — a deterministic workbook
> validator (`validate_workbook.py`), a documentation linter (`lint_docs.py`), a
> presentation/merged-layout step (`apply_merged_layout.py`), and a coverage-ledger
> generator (`build_coverage_ledger.py`) — plus two operational JSON state files
> (`project_registry.json`, `id_ledger.json`) that back cross-workbook ID uniqueness.

## What it produces

One `.xlsx` per run, conforming to `Knowledge/EXCEL_SPECIFICATION.md`:

- **Master Summary** — per-feature metrics and coverage.
- **Feature worksheets** — the test cases (8-column schema, globally-unique IDs,
  forward-filled rows).

Under the current output contract (EXCEL_SPECIFICATION v2.5) the workbook contains only the
Master Summary and feature worksheet(s). The Review Summary sheet (confidence assessment,
assumptions, open points, conflicts, and the Requirement Traceability Matrix) was removed in
v2.4 and is no longer emitted; requirement traceability is a design-time discipline rather
than a workbook sheet.

Output is always a **proposal pending human QA review**.

## Repository layout

```
PS-Test Authoring/
├── README.md                     ← this file
├── PROJECT_INSTRUCTIONS.md       Project-level routing & rules
├── Knowledge/                    Single source of truth (governing documents)
│   ├── MASTER_CONTEXT.md         Orchestration, ownership matrix, precedence
│   ├── SYSTEM_INSTRUCTIONS.md    Identity, principles, guardrails
│   ├── USER_REQUEST_PATTERNS.md  Intent detection / routing
│   ├── QA_METHODOLOGY.md         Test-design methodology
│   ├── TEST_CASE_GENERATION.md   Authoring standard
│   ├── VALIDATION_ENGINE.md      Validation rules + self-correction
│   ├── EXCEL_SPECIFICATION.md    Workbook output contract
│   ├── AI_CAPABILITIES.md        Capability catalog + maturity
│   ├── DATA_HANDLING.md          Data classification, PII/secret rules, data flow
│   ├── EXAMPLES.md               Conformant worked examples
│   ├── ARCHITECTURE.md           Architectural context
│   └── README.md                 Knowledge-base orientation
└── Skills/                       Execution + enforcement layer
    ├── README.md                 How the layer + checks work
    ├── SKILLS_REGISTRY.md        Manifest of skills
    ├── lint_docs.py              Documentation linter
    ├── _base/ , _template/       Shared workflow substrate + new-skill skeleton
    └── TestCaseAuthoring/        The one built skill
        ├── skill.md , workflow.md , examples.md   Skill contract + domain states + examples
        ├── validate_workbook.py  Deterministic workbook validator (ASSEMBLE gate)
        ├── apply_merged_layout.py Standard merged-cell presentation step
        ├── build_coverage_ledger.py Coverage-ledger generator (<wb>.coverage.json sidecar)
        ├── project_registry.json Known project keys / business units (namespacing)
        └── id_ledger.json        Persistent record of every issued Test Case ID (global uniqueness)
```

Coverage is verified against a per-workbook `<workbook>.coverage.json` sidecar (not a
worksheet), and cross-workbook Test Case ID uniqueness is enforced via the project
registry + ID ledger (namespacing checks NS-01/NS-02).

## The two automated gates

```bash
pip install openpyxl --break-system-packages

# 1) every generated workbook must pass the schema/traceability validator
python Skills/TestCaseAuthoring/validate_workbook.py *.xlsx

# 2) the governing docs must stay internally consistent
python Skills/lint_docs.py
```

Both exit non-zero on failure and are designed to run in CI. See `Skills/README.md` for
details and `REMEDIATION_SCORECARD.md` for the current architecture assessment.

## Runtime

The assistant runs on an AI/LLM runtime with read access to Atlassian (Jira/Confluence)
via MCP and file access for uploaded documents. Ingested content is sent to the configured
cloud LLM provider for analysis — see `Knowledge/DATA_HANDLING.md` for the accurate
data-flow and PII/secret handling rules.

## Status

Built and Production for the **TestCaseAuthoring** capability. Additional skills
(Requirement Review, Traceability Analysis, Regression Planning, Risk Assessment, etc.)
are **Planned** — see `Skills/SKILLS_REGISTRY.md` and `Knowledge/AI_CAPABILITIES.md` §7.2.

---

Professional Services QA · Internal use only.
