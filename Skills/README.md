# Skills — Execution Layer

This folder is the **execution layer** of PS-TestAuthoring. Domain truth lives in
`Knowledge/` (the single source of truth); this folder defines *how work runs* and holds
the automated checks that enforce the standards.

## Layout

```
Skills/
├── README.md                     ← you are here
├── SKILLS_REGISTRY.md            Manifest of all skills + how to add one
├── lint_docs.py                  Documentation linter (guards Knowledge/ + Skills/)
├── _base/
│   └── workflow.base.md          Shared workflow substrate inherited by every skill
├── _template/                    Skeleton (skill.md, workflow.md) for a new skill
│   ├── skill.md
│   └── workflow.md
└── TestCaseAuthoring/            The one built skill (maturity: Production)
    ├── skill.md                  Skill contract (inputs, outputs, boundaries)
    ├── workflow.md               Domain states ANALYZE→PLAN→DESIGN; inherits _base
    ├── examples.md               Execution examples
    ├── validate_workbook.py      Deterministic output validator (schema authority in code)
    ├── apply_merged_layout.py    Standard presentation: merge TC-level cells per test case (§6.6)
    ├── project_registry.json     Known project keys / business units (namespacing)
    └── id_ledger.json            Persistent record of every issued Test Case ID (NS-01/02)
```

## The two automated gates

Both are plain Python (only `openpyxl` is needed) and exit non-zero on failure, so they
drop straight into CI or a pre-commit hook.

### 1. Workbook validator — every generated `.xlsx` must pass

Enforces `Knowledge/EXCEL_SPECIFICATION.md` mechanically: sheet order (Master Summary +
feature sheets), the exact 8-column schema, forward-fill (no merged cells), global TC-ID
format, blank/enum checks, and the embedded `schema:` stamp. (RTM reverse-traceability and
coverage checks were retired in v2.4 when the Review Summary sheet was removed.)

```bash
# from the project root
python Skills/TestCaseAuthoring/validate_workbook.py "TC-SAMP-110_20260723.xlsx"
python Skills/TestCaseAuthoring/validate_workbook.py *.xlsx          # batch
python Skills/TestCaseAuthoring/validate_workbook.py --json file.xlsx  # machine output
```

Exit `0` = PASS (no Fatal/Blocking findings); `1` = FAIL. A workbook that does not exit 0
is **not** review-ready and must not be delivered.

### 2. Doc-lint — the Knowledge/ + Skills/ docs must stay consistent

Catches the regressions the architecture review flagged: encoding corruption, retired
maturity vocabulary, stale schema stamps, bare (non-global) TC IDs, broken `§N`
cross-references into VALIDATION_ENGINE, and duplicated schema ownership.

```bash
# from the project root
python Skills/lint_docs.py
```

Exit `0` = clean; `1` = one or more ERRORS (warnings do not fail the run).

## Suggested CI step

```bash
set -e
python Skills/lint_docs.py
python Skills/TestCaseAuthoring/validate_workbook.py *.xlsx
```

## Requirements

```bash
pip install openpyxl --break-system-packages   # only external dependency
```

## Adding a new skill

Follow `SKILLS_REGISTRY.md` → "How to add a skill": copy `_template/`, declare only the
new domain states (the rest is inherited from `_base/workflow.base.md`), add the skill's
Knowledge document and register it in `MASTER_CONTEXT.md`, add a machine validator for its
deliverable, and promote its row in the registry. No step should require editing `_base/`
or another skill — that is the test of extensibility.
