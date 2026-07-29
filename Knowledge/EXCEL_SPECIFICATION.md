# Excel Workbook Specification — PS AI QA Assistant

> Version: 2.5  
> Last Updated: 2026-07-23  
> Status: Approved  
> Classification: Internal — Professional Services QA  
> Review Cycle: Quarterly  
> Companion Documents: SYSTEM_INSTRUCTIONS.md, QA_METHODOLOGY.md, TEST_CASE_GENERATION.md, VALIDATION_ENGINE.md

> **This document is the single authority for the workbook output contract.** No other
> document may define, restate, or override columns, sheet structure, ID format, or
> naming. The machine-enforceable form of this contract lives in
> `Skills/TestCaseAuthoring/validate_workbook.py` — that script and this document MUST
> agree, and every generated workbook MUST pass the validator before delivery.

> **v2.0 changes:** (1) feature-sheet columns B and C renamed to `Requirement Title`
> and `Test Case Title`; (2) Test Case ID is now globally unique and project+story
> scoped (`{ProjectKey}-{Story}-TC-{NNN}`, e.g. `SAMP-125-TC-001`); (3) execution-tracking
> columns (Test Type, Actual Result, Status) are explicitly OUT of scope — they live in
> the test-management tool (Zephyr), not the workbook; (4) an embedded schema-version
> stamp is now mandatory.

---

## 1. Workbook Structure

### 1.1 Purpose

The Excel workbook is the primary deliverable of the PS AI QA Assistant. It contains all generated test cases, traceability data, coverage metrics, and review artifacts in a single, self-contained file that a QA engineer can execute from without referring to external documents.

### 1.2 Sheet Composition

Every generated workbook contains the following sheets in strict order:

| Position | Sheet Name | Purpose | Always Present |
|----------|-----------|---------|----------------|
| 1 | Master Summary | Aggregate metrics across all features | Yes |
| 2–N | {Feature Name} | Test cases for a specific feature/Confluence page | Yes (≥1) |

> **v2.4 — Review Summary removed (stakeholder request).** The workbook no longer contains a
> Review Summary sheet. Assumptions, open points, conflicts, the confidence assessment, and
> the Requirement Traceability Matrix are **not** emitted to the workbook. Consequence: the
> validator no longer machine-verifies coverage or detects orphan test cases from an RTM
> (that was RT-01..04 / CV-02 / CV-04); requirement traceability is a design-time concern
> only (see `VALIDATION_ENGINE.md`).

### 1.3 Sheet Ordering Rules

1. **Master Summary** is always the first sheet (leftmost tab)
2. **Feature worksheets** follow in the order their source material was processed
3. The workbook must contain at least 2 sheets (Master Summary + ≥1 feature sheet)

### 1.4 Workbook Properties

| Property | Value |
|----------|-------|
| Format | `.xlsx` (Office Open XML) |
| Compatibility | Excel 2016+, Google Sheets, LibreOffice Calc |
| Maximum sheets | No artificial limit — one per feature |
| Maximum rows per sheet | No artificial limit — generate as many TCs as needed |
| Character encoding | UTF-8 |
| Password protection | None (human review requires editing) |

---

## 2. Master Summary Sheet

### 2.1 Purpose

The Master Summary provides a single-glance overview of the entire test suite — total counts, coverage percentages, and per-feature breakdowns. A QA Lead or Test Manager should be able to assess completeness from this sheet alone.

### 2.2 Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ROW 1:  Title Row — "Test Case Generation Summary"                     │
│  ROW 2:  Generation Date | Source Information                           │
│  ROW 3:  (blank separator)                                              │
│  ROW 4:  Column Headers                                                 │
│  ROW 5+: Per-feature data rows                                          │
│  LAST:   Totals row                                                     │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Title Section (Rows 1–3)

| Row | Column A | Column B |
|-----|----------|----------|
| 1 | **Test Case Generation Summary** (merged across all columns A–F, bold, 14pt) | |
| 2 | Generation Date: {YYYY-MM-DD HH:MM} | Source: {Jira Key(s)} and/or {Confluence Page Title(s)} |
| 3 | *(blank separator row)* | |

### 2.4 Metrics Table (Row 4+)

The Master Summary has exactly **six columns** (v2.5). No other columns may be added.

**Column Headers (Row 4):**

| Column | Header | Description |
|--------|--------|-------------|
| A | Feature / Source | Feature name or Confluence page title |
| B | Source Reference | Jira key or Confluence page ID |
| C | Requirements | Count of identified requirements (Req IDs) |
| D | Acceptance Criteria | Count of identified ACs (AC IDs) |
| E | Test Cases | Count of generated test cases |
| F | AC Coverage % | (ACs with ≥1 TC / Total ACs) × 100 |

> **Removed in v2.5 (stakeholder request):** `Business Rules`, `Under-tested ACs (Pos-only)`,
> and `Open Points` columns. Business-rule coverage and scenario-balance remain design-time
> validation concerns (`VALIDATION_ENGINE.md`); they are no longer reported in the workbook.

**Data Rows (Row 5+):** One row per feature worksheet.

**Totals Row (Last):**

| Column | Content |
|--------|---------|
| A | **TOTAL** (bold) |
| B | *(blank)* |
| C–E | SUM of respective columns |
| F | Overall AC Coverage % (calculated from totals, not averaged) |

### 2.5 Formatting

| Element | Style |
|---------|-------|
| Title row | Bold, 14pt, merged across columns A–F |
| Column headers | Bold, dark blue background (#1F4E79), white text, frozen |
| Data rows | Alternating white / light gray (#F2F2F2) |
| Totals row | Bold, light blue background (#D6E4F0), top border |
| AC Coverage 100% | Green text (#006100) |
| AC Coverage <100% | Red text (#9C0006), red background (#FFC7CE) |

---

## 3. Feature Worksheets (One Per Confluence Page / Feature)

### 3.1 Purpose

Each feature worksheet contains the complete set of execution-ready test cases for one feature or Confluence page. A QA engineer executes tests directly from this sheet.

### 3.2 Source-to-Sheet Mapping

| Source Configuration | Sheet Strategy |
|---------------------|---------------|
| Single Jira story, no linked Confluence | One feature sheet named after the story summary |
| Single Jira story + one linked Confluence page | One feature sheet named after the Confluence page title |
| Single Jira story + multiple linked Confluence pages (same feature) | One feature sheet correlating all sources |
| Multiple Jira stories (distinct features) | One feature sheet per distinct feature |
| Multiple Confluence pages (distinct features) | One feature sheet per Confluence page |
| Multiple sources describing the same feature | Correlated into ONE feature sheet |

### 3.3 Sheet Header Section

| Row | Content |
|-----|---------|
| 1 | Feature title (bold, 12pt, merged across all columns) |
| 2 | Source: {Jira key and/or Confluence page title with ID} |
| 3 | *(blank separator row)* |
| 4 | Column headers (see Section 5) |
| 5+ | Test case data rows |

### 3.4 Test Case Row Layout

Each test case occupies **one or more rows** depending on step count. TC-level fields are
**merged vertically across the test case's step rows — the value appears once, in the top
row.** (The diagram below is illustrative; the "(merged)" labels in it are correct — see the
merged-cell rule below the diagram.)

```
┌──────────┬─────────────────┬──────────────┬──────────────┬──────┬────────────┬─────────────────┬──────────┐
│ TC ID    │ Requirement     │ Title        │ Pre-         │ Step#│ Test Step  │ Expected Result │ Priority │
│ (merged) │ Name (merged)   │ (merged)     │ Conditions   │      │            │                 │ (merged) │
│          │                 │              │ (merged)     │      │            │                 │          │
├──────────┼─────────────────┼──────────────┼──────────────┼──────┼────────────┼─────────────────┼──────────┤
│ TC-001   │ User Login      │ [Positive]   │ User account │  1   │ Navigate   │ Login page      │ High     │
│          │                 │ Verify       │ exists with  │      │ to login   │ displays with   │          │
│          │                 │ successful   │ valid creds; │      │ page URL   │ email and       │          │
│          │                 │ login with   │ account is   │      │            │ password fields  │          │
│          │                 │ valid creds  │ active       │      │            │                 │          │
│          │                 │              │              ├──────┼────────────┼─────────────────┤          │
│          │                 │              │              │  2   │ Enter      │ Email field     │          │
│          │                 │              │              │      │ 'john@     │ accepts input;  │          │
│          │                 │              │              │      │ acme.com'  │ no error shown  │          │
│          │                 │              │              │      │ in Email   │                 │          │
│          │                 │              │              ├──────┼────────────┼─────────────────┤          │
│          │                 │              │              │  3   │ Enter      │ Password field  │          │
│          │                 │              │              │      │ 'P@ss123'  │ masks input     │          │
│          │                 │              │              │      │ in Password│                 │          │
│          │                 │              │              ├──────┼────────────┼─────────────────┤          │
│          │                 │              │              │  4   │ Click      │ User is         │          │
│          │                 │              │              │      │ 'Sign In'  │ redirected to   │          │
│          │                 │              │              │      │ button     │ dashboard;      │          │
│          │                 │              │              │      │            │ welcome message │          │
│          │                 │              │              │      │            │ shows user name │          │
└──────────┴─────────────────┴──────────────┴──────────────┴──────┴────────────┴─────────────────┴──────────┘
```

**Merged-cell rule (v2.3 — the standard layout):** `Test Case ID`, `Requirement Title`,
`Test Case Title`, `Pre-Conditions`, and `Priority` are **merged vertically** across all of
a test case's step rows, so each appears **once**, in the top row, vertically-top aligned.
`Step#`, `Test Step`, and `Expected Result` are NOT merged — one row per step. This gives
the clean "one value per test case" presentation (see §6.6) applied to every workbook via
`apply_merged_layout.py`.

**A new test case begins on the row where `Test Case ID` is populated;** continuation step
rows leave the merged TC-level columns blank (they belong to the merge above). This is how
tools and the validator delimit test cases.

**Import trade-off (documented, accepted).** Merged cells do not survive CSV / Zephyr import
cleanly (TC-level fields arrive blank after the first step row) and interfere with in-sheet
sort/filter. When importing into a test-management tool, first produce a flat export (a
forward-filled copy) rather than importing the merged workbook directly. The merged layout
is the human-review deliverable; the flat export is the machine-import form.

---

## 4. Review Summary Sheet — REMOVED (v2.4)

The Review Summary sheet has been **removed** at stakeholder request. The workbook no longer
emits any of the following to Excel:

- Confidence assessment (overall confidence, clarity/completeness factors, recommendation)
- Assumptions, Open Points, Conflicts
- The Requirement Traceability Matrix (former Section E) and its validator checks (RT-01..04)

**Implications (accepted):**
- Coverage is no longer machine-recomputed and orphan test cases are no longer detected from
  an RTM. Traceability is a *design-time* concern (author every TC from a real AC per
  `VALIDATION_ENGINE.md`); it is not verifiable from the delivered workbook.
- Requirement ambiguities/assumptions (e.g. an undefined business rule) are no longer carried
  in the deliverable. If they need to be communicated, surface them outside the workbook.

If this content is ever wanted back, restore this section and re-enable the RTM checks in
`validate_workbook.py`.

---

## 5. Required Columns

### 5.1 Mandatory Columns for Feature Worksheets

The following columns are required on every feature worksheet. They appear in this exact order. No columns may be added to or removed from this specification.

| Position | Column Header | Data Type | Description |
|----------|--------------|-----------|-------------|
| A | Test Case ID | Text | Globally unique identifier: `{ProjectKey}-{Story}-TC-{NNN}` (e.g. `SAMP-125-TC-001`) |
| B | Requirement Title | Text | Source requirement this TC validates |
| C | Test Case Title | Text | Prefixed descriptive title: `[Positive]`, `[Negative]`, or `[Edge Case]` |
| D | Pre-Conditions | Text | System state, user role, and data setup required |
| E | Step# | Integer | Sequential step number within the test case |
| F | Test Step | Text | Single atomic action the tester performs |
| G | Expected Result | Text | Observable outcome for the corresponding step |
| H | Priority | Text | `High`, `Medium`, or `Low` |

**Excluded by design (do NOT add):** `Test Type`, `Actual Result`, and `Status` are
execution-tracking fields, not authoring fields. They are owned by the test-management
tool (Zephyr) after import, not by this workbook. `Test Type` is redundant with the
`[Positive]`/`[Negative]`/`[Edge Case]` prefix already carried in `Test Case Title`.
The validator treats any 9th column as a Fatal WV-04 violation.

### 5.2 Column Constraints

| Column | Constraint | Validation Rule |
|--------|-----------|-----------------|
| Test Case ID | Globally unique | No duplicate TC IDs anywhere; format `{ProjectKey}-{Story}-TC-{NNN}` |
| Requirement Title | Non-empty | Every TC must reference a requirement |
| Test Case Title | Non-empty; starts with prefix | Must begin with `[Positive]`, `[Negative]`, or `[Edge Case]` |
| Pre-Conditions | Non-empty | Must specify at minimum: user role |
| Step# | Sequential integer ≥1 | Starts at 1 per TC; no gaps |
| Test Step | Non-empty | Every step row has an action |
| Expected Result | Non-empty | Every step row has an expected result |
| Priority | Enumerated | Must be exactly `High`, `Medium`, or `Low` |

### 5.3 Empty Value Policy

| Scenario | Rule |
|----------|------|
| TC-level field on a continuation step row | Blank because the column is **merged** with the test case's first row — this is correct (the value lives once, in the top row) |
| Test Step is empty | **Invalid** — every step must have an action |
| Expected Result is empty | **Invalid** — every step must have an expected result |
| Pre-Conditions has no data context | **Warning** — should specify data setup, not just role |
| Priority is missing | **Invalid** — must be assigned |

---

## 6. Formatting Standards

### 6.1 Typography

| Element | Font | Size | Style |
|---------|------|------|-------|
| Sheet title (Row 1) | Calibri | 12pt | Bold |
| Source reference (Row 2) | Calibri | 10pt | Italic |
| Column headers (Row 4) | Calibri | 10pt | Bold |
| Data cells | Calibri | 10pt | Regular |
| Totals row (Master Summary) | Calibri | 10pt | Bold |

### 6.2 Color Palette

| Usage | Background | Text Color | Hex (BG) | Hex (Text) |
|-------|-----------|------------|----------|------------|
| Column headers | Dark blue | White | #1F4E79 | #FFFFFF |
| Data row (odd) | White | Black | #FFFFFF | #000000 |
| Data row (even) | Light gray | Black | #F2F2F2 | #000000 |
| Totals row | Light blue | Black | #D6E4F0 | #000000 |
| Priority High | No fill | Dark red | — | #9C0006 |
| Priority Medium | No fill | Dark yellow | — | #9C5700 |
| Priority Low | No fill | Dark green | — | #006100 |
| Coverage 100% | Light green | Dark green | #C6EFCE | #006100 |
| Coverage <100% | Light red | Dark red | #FFC7CE | #9C0006 |
| Confidence High | Light green | Dark green | #C6EFCE | #006100 |
| Confidence Medium | Light yellow | Dark yellow | #FFEB9C | #9C5700 |
| Confidence Low | Light red | Dark red | #FFC7CE | #9C0006 |

### 6.3 Borders

| Element | Border Style |
|---------|-------------|
| All data cells | Thin (#D9D9D9) on all sides |
| Column headers | Medium bottom border (#1F4E79) |
| Totals row | Medium top border (#1F4E79) |
| Between test cases | Medium bottom border (#B4C6E7) on the last step row of each TC |

### 6.4 Cell Alignment

| Column | Horizontal | Vertical | Wrap Text |
|--------|-----------|----------|-----------|
| Test Case ID | Left | Top | No |
| Requirement Name | Left | Top | Yes |
| Title | Left | Top | Yes |
| Pre-Conditions | Left | Top | Yes |
| Step# | Center | Top | No |
| Test Step | Left | Top | Yes |
| Expected Result | Left | Top | Yes |
| Priority | Center | Top | No |

### 6.5 Column Widths

| Column | Width (characters) | Rationale |
|--------|-------------------|-----------|
| A (TC ID) | 12 | Fixed-width IDs fit comfortably |
| B (Requirement) | 30 | Sufficient for requirement names |
| C (Title) | 45 | Descriptive titles need space |
| D (Pre-Conditions) | 40 | Multi-line preconditions |
| E (Step#) | 7 | Single or double digit |
| F (Test Step) | 50 | Detailed atomic steps |
| G (Expected Result) | 55 | Detailed observable outcomes |
| H (Priority) | 10 | "High", "Medium", "Low" |

### 6.6 Merged-Cell Layout (standard presentation)

Every generated feature worksheet is delivered with the TC-level columns **merged vertically
per test case**. This is the standard presentation, applied to all workbooks:

- `Test Case ID`, `Requirement Title`, `Test Case Title`, `Pre-Conditions`, and `Priority`
  are merged across all of a test case's step rows and appear **once** (top row,
  vertically-top aligned). `Step#`, `Test Step`, and `Expected Result` are one row per step.
- The reader sees **one block per test case** — a single ID, requirement, title, and set of
  preconditions spanning its steps — matching the standard PS test-case sheet look.
- A medium bottom border separates consecutive test cases.
- It is applied by `Skills/TestCaseAuthoring/apply_merged_layout.py` as the final
  presentation step of `ASSEMBLE`. It changes presentation only — same 8 columns, same IDs,
  same sheet contract.
- **Import note:** because merges do not survive CSV/Zephyr import, generate a flat
  (forward-filled) export for import rather than importing the merged workbook directly.

---

## 7. Naming Conventions

### 7.1 File Naming

There is ONE naming rule. Every workbook filename begins with `TC-`, identifies the
source, and ends with the generation date. There is no date-only default.

| Scenario | Pattern | Example |
|----------|---------|---------|
| Single Jira story (standard) | `TC-{ProjectKey}-{Number}_{YYYYMMDD}.xlsx` | TC-SAMP-125_20260723.xlsx |
| Sprint batch | `TC-{ProjectKey}_Sprint-{N}_{YYYYMMDD}.xlsx` | TC-SAMP_Sprint-42_20260723.xlsx |
| Multiple stories (custom) | `TC-{ProjectKey}_Batch_{YYYYMMDD}_{HHmmss}.xlsx` | TC-SAMP_Batch_20260723_143022.xlsx |
| Regeneration | Append `_v{N}` before extension | TC-SAMP-125_20260723_v2.xlsx |

Legacy patterns such as `{Key}_TestCases_{date}` or `{Key}-TestCases-{date}` are
non-conformant and must be renamed on migration.

### 7.2 Test Case ID Format

```
{ProjectKey}-{Story}-TC-{NNN}
```

- Example: `SAMP-125-TC-001` (project `SAMP`, story `125`, sequential `001`)
- Zero-padded three-digit sequential number, extended to four digits past TC-999
- **Globally unique** — the project+story prefix guarantees no collision across
  workbooks, projects, or business units. `TC-001` alone is prohibited.
- Sequence restarts at `001` per workbook; global uniqueness comes from the prefix,
  not the number
- Never reused or recycled; assigned in generation order
- This is the single ID rule. Any earlier text implying "unique within the sheet" or
  "unique within the workbook" is superseded — the ID is globally unique.

#### 7.2.1 Project namespacing & cross-workbook uniqueness (enforced)

The `{ProjectKey}` is the namespace that keeps IDs distinct across many projects and business
units. Two operational-state files beside the validator make "globally unique" *enforced*
rather than merely conventional:

| File | Role |
|------|------|
| `Skills/TestCaseAuthoring/project_registry.json` | Declares the known project keys (key, name, business unit, Jira project, enabled). Onboard a project/BU by adding a row. |
| `Skills/TestCaseAuthoring/id_ledger.json` | Persistent record of every Test Case ID ever issued, keyed by ID → `{workbook, date}`. |

The validator enforces:

- **NS-01 (Fatal)** — a workbook reuses a Test Case ID already issued in a *different*
  workbook (per the ledger). This catches the cross-workbook collision that the per-workbook
  DV-09 check cannot see (two separate runs both emitting `SAMP-125-TC-001`).
- **NS-02 (Warning)** — a Test Case ID uses a `{ProjectKey}` that is not an enabled project in
  the registry; register the project so its IDs are namespaced and governed.

IDs enter the ledger only when a **passed** workbook is explicitly registered:

```
python Skills/TestCaseAuthoring/validate_workbook.py --register <workbook.xlsx>
```

Registration is part of delivery (the workflow's `ASSEMBLE`/`RETURN`): register the workbook
when it is delivered, so future runs cannot silently reuse its IDs.

### 7.3 Priority Values

Only these exact string values are permitted:

| Value | Formatting |
|-------|-----------|
| `High` | Dark red text |
| `Medium` | Dark yellow text |
| `Low` | Dark green text |

### 7.4 Title Prefixes

Only these exact prefixes are permitted:

| Prefix | Usage |
|--------|-------|
| `[Positive]` | Happy path, valid data, expected success |
| `[Negative]` | Invalid data, unauthorized access, error conditions |
| `[Edge Case]` | Boundary values, race conditions, unusual valid scenarios |

---

## 8. Sheet Naming Rules

### 8.1 Feature Sheet Names

| Rule | Specification |
|------|--------------|
| Source | Derived from Confluence page title or Jira story summary |
| Maximum length | 31 characters (Excel limitation) |
| Truncation | If source name exceeds 31 characters, truncate at 28 characters and append "..." |
| Invalid characters | Remove: `\ / * ? : [ ]` (Excel prohibited characters) |
| Uniqueness | If two features produce the same sheet name, append ` (2)`, ` (3)`, etc. |
| Casing | Title Case |

### 8.2 Fixed Sheet Names

| Sheet | Name | Modifiable |
|-------|------|-----------|
| Master Summary | `Master Summary` | No |

### 8.3 Examples

| Source Title | Sheet Name |
|-------------|-----------|
| "Quote Management Configuration" | `Quote Management Configurati...` |
| "User Login and Authentication" | `User Login And Authentication` |
| "API Integration: Salesforce/ERP" | `API Integration SalesforceERP` |
| "Settings" | `Settings` |
| "Settings" (duplicate) | `Settings (2)` |

---

## 9. Workbook Validation Rules

The complete set of deterministic validation rules — **every code (WV-/DV-/CV-/ER-/SV-) and
its severity** — is owned by `Skills/TestCaseAuthoring/validate_workbook.py` and published as
the generated **Machine-Enforced Rule Catalog** in `VALIDATION_ENGINE.md`. It is deliberately
**not restated here**: a second copy is precisely the drift this consolidation removed (this
section previously listed a `WV-07` and `CV-05` the validator never implemented, and omitted
DV-11/12/13, ER-01/02, SV-01/02). `Skills/lint_docs.py` fails if any doc drifts from the
validator. For the authoritative list, see that catalog or run:

```
python Skills/TestCaseAuthoring/validate_workbook.py --rules
```

This specification owns the **output contract those rules check** — the eight columns (§5),
sheet structure (§1–§4), ID format (§7.2), and schema stamp (§13.2). The validator and this
document must agree, and the linter enforces it.

**Coverage completeness** is machine-gated by CV-06/CV-07 against the Master Summary. CV-02
and CV-04 were removed in v2.4 (they depended on the Review Summary RTM, which no longer
exists); CV-06/CV-07 (v2.5) restore coverage-completeness verification using only the Master
Summary — no extra sheet or columns. **Honest limit:** these verify coverage of the ACs the
run *extracted*; they cannot confirm extraction captured every AC in the source — that stays a
design-time extraction-fidelity concern in `VALIDATION_ENGINE.md`.

### 9.4 Duplicate Detection

| Detection Target | Duplicate Criterion | Action |
|-----------------|---------------------|--------|
| TC IDs | Same `{ProjectKey}-{Story}-TC-{NNN}` value appears twice | Reassign one ID; verify content is not duplicate |
| Test cases | Same AC + same scenario type + same verification outcome | Remove lower-quality duplicate; keep more detailed version |
| Sheet names | Two sheets resolve to the same name | Append disambiguation suffix |

---

## 10. Coverage Reporting

### 10.1 Location

Coverage metrics are reported in the **Master Summary** sheet only (per-feature and
aggregate coverage percentages). (v2.4: the Review Summary AC-level breakdown was removed.)

The itemized, source-anchored acceptance-criterion-to-test-case mapping behind those
percentages lives in a **coverage ledger sidecar** — `<workbook-name>.coverage.json`, a
companion file, **not a worksheet** (the workbook stays clean). It is required for verified
coverage and is checked by `validate_workbook.py` (CV-08/09/10; a missing ledger is CV-11).
The ledger format and rules are owned by `VALIDATION_ENGINE.md` — see "Coverage Ledger".

### 10.2 Coverage Metrics

| Metric | Formula | Display Location |
|--------|---------|-----------------|
| AC Coverage % | (ACs with ≥1 TC / Total ACs) × 100 | Master Summary Column F |
| Requirements Covered | Count of Req IDs with ≥1 associated TC | Master Summary Column C |
| Business Rule Coverage | (Rules with Positive + Negative TCs / Total Rules) × 100 | Not emitted (design-time check only) |
| Scenario balance / Positive-only | (design-time check only — no longer a Master Summary column as of v2.5) | Not emitted |

### 10.3 Coverage Visual Indicators

| Condition | Visual Treatment |
|-----------|-----------------|
| AC Coverage = 100% | Green text, green background in Master Summary |
| AC Coverage < 100% | Red text, red background in Master Summary |

### 10.4 Coverage Completeness Rule

The workbook must NOT be delivered if AC Coverage is below 100%. This is **machine-enforced**
by `validate_workbook.py` (CV-06): any Master Summary row reporting < 100% (or blank) coverage
is a Fatal finding and the workbook is not returned. The Master Summary must show the **true**
coverage figure (recomputed from the actual AC↔TC mapping the run built at design time), never
an inflated one — reporting 100% while an AC is uncovered is a coverage-honesty violation.

The only legitimate way to have < 100% is genuinely unretrievable source material; in that
case do not ship the suite — surface the gap to the requester (outside the workbook) and stop.

---

## 11. Confidence Reporting — REMOVED (v2.4)

The Confidence Assessment lived in the Review Summary sheet, which has been removed. The
workbook no longer reports a confidence level or recommendation. Any confidence/risk signal
about a thin requirement should be communicated outside the workbook.

---

## 12. Version Information

### 12.1 Workbook Version Tracking

| Property | Location | Content |
|----------|----------|---------|
| Generation version | Master Summary Row 2 | "Generated by PS AI QA Assistant v{X.Y}" |
| Generation timestamp | Master Summary Row 2 | ISO 8601 date-time |
| Regeneration indicator | File name suffix | `_v{N}` appended for subsequent generations |

### 12.2 Regeneration Rules

| Scenario | Behavior |
|----------|----------|
| First generation | File named per standard convention (no version suffix) |
| Re-generation (same inputs) | Append `_v2`, `_v3`, etc. to filename |
| New inputs (different story/sprint) | New file with standard naming (no version suffix) |
| Partial correction by human | Not tracked in workbook — human edits are outside AI scope |

---

## 13. Metadata

### 13.1 Metadata Location

Metadata is embedded in the Master Summary sheet (Rows 1–3) and in Excel document properties.

### 13.2 Embedded Metadata

| Field | Location | Example |
|-------|----------|---------|
| Workbook title | Master Summary Row 1 | "Test Case Generation Summary" |
| Generation date | Master Summary Row 2, Column A | "Generation Date: 2026-07-23 13:15" |
| Source references | Master Summary Row 2, Column B | "Source: SAMP-125, Confluence Page 45678" |
| Generator version | Excel document properties (Author) | "PS AI QA Assistant v1.0" |
| **Schema version** | **Excel document properties (Keywords)** | **must contain `schema:2.5`** |
| Total test cases | Master Summary Totals Row | Calculated from feature sheets |

**Schema version is mandatory.** Every workbook must embed `schema:2.5` in its document
Keywords so any consumer can tell which version of this specification the file conforms
to. The validator raises a Blocking `SV-01` finding if it is absent. Bump this stamp
whenever the column set, ID format, or sheet contract changes.

### 13.3 Excel Document Properties

| Property | Value |
|----------|-------|
| Title | "Test Cases — {Feature/Project}" |
| Author | "PS AI QA Assistant" |
| Subject | "Manual Test Cases" |
| Keywords | Jira key(s), feature names |
| Comments | "AI-generated. Pending human QA review." |
| Category | "QA Test Artifacts" |

---

## 14. Error Handling

### 14.1 Generation Errors

| Error | Handling | User Communication |
|-------|----------|-------------------|
| Zero test cases generated | Do not create workbook | Report: "No testable content found in source material" |
| Feature sheet has zero TCs | Omit the empty feature sheet | Report: "Feature '{name}' produced no test cases — source may lack testable requirements" |
| Validation check fails | Enter self-correction loop | Report only after correction attempts are exhausted |
| Excel library error | Retry once; if persistent, report | Report: "Workbook generation failed — {technical detail}" |
| File write permission denied | Suggest alternative output path | Report: "Cannot write to {path} — suggest alternative directory" |

### 14.2 Data Quality Errors in Output

| Error | Detection | Handling |
|-------|-----------|----------|
| Blank mandatory cell | Blank-mandatory checks in the RULES catalog (DV-02/03/04/05/12/13; DV-01 is a different check) | Block generation; fix in self-correction loop |
| Invalid priority value | Priority-enum check in the RULES catalog | Auto-correct to nearest valid value; log correction |
| Duplicate TC ID | Duplicate-ID check in the RULES catalog (DV-09) | Reassign ID; verify content distinctness |
| Master Summary mismatch | Coverage/consistency checks in the RULES catalog (CV-01/CV-06/CV-07) | Recalculate summary values from actual data |

> The authoritative codes and severities for the checks above live in the **Machine-Enforced
> Rule Catalog** (`VALIDATION_ENGINE.md`), generated from `validate_workbook.py` — see §9. Do
> not treat this table as the code list.

### 14.3 Empty Value Rules

| Scenario | Rule |
|----------|------|
| Pre-Conditions has no content | **Invalid** — minimum: user role specified |
| Expected Result is empty for a step | **Invalid** — every step has an expected result |
| Test Step is empty for a step row | **Invalid** — remove the empty step row |
| Requirement Name is empty | **Invalid** — must reference source requirement |
| (Review Summary removed in v2.4 — no assumptions/open-points/conflicts handling in the workbook) | — |

---

## 15. Large Requirement Handling

### 15.1 Definition

A "large requirement" is any source that produces:
- More than 100 test cases per feature, OR
- More than 5 feature worksheets, OR
- More than 500 total test cases across the workbook

### 15.2 Handling Strategy

| Concern | Strategy |
|---------|----------|
| Sheet row limits | Excel supports 1,048,576 rows — no practical concern for manual TCs |
| Readability | The merged TC-level layout is standard on every sheet (§6.6), giving one block per test case; especially valuable at high TC counts |
| Navigation | Include hyperlinked table of contents on Master Summary for >5 feature sheets |
| Performance | Avoid volatile formulas; use static values for summary metrics |
| TC ID range | Extend to TC-{NNNN} (four digits) when total TCs exceed 999 |

### 15.3 Sheet Splitting Rules

| Condition | Action |
|-----------|--------|
| Single feature produces >200 TCs | Consider logical sub-grouping within the sheet using section headers |
| Single feature has >10 distinct requirement areas | Split into sub-feature sheets: `{Feature} - {Area}` |
| Workbook exceeds 10 feature sheets | Add table of contents with hyperlinks on Master Summary |

### 15.4 Cross-Sheet References

When a single test case references requirements from multiple features:
- The TC appears on the **primary feature's** sheet
- The cross-feature dependency is noted outside the workbook (no Review Summary sheet in v2.4)
- The Master Summary counts the TC under the primary feature only (no double-counting)

---

## 16. Performance Considerations

### 16.1 File Size Optimization

| Technique | Implementation |
|-----------|---------------|
| Avoid embedded images | No logos, screenshots, or embedded media |
| Minimize formatting objects | Use cell styles, not individual cell formatting |
| Static summary values | Master Summary uses computed values, not COUNTIF/SUMIF formulas |
| No conditional formatting formulas | Use pre-applied cell colors based on data values |
| No data validation dropdowns | Workbook is output-only; no input validation needed |

### 16.2 Expected File Sizes

| TC Count | Estimated File Size | Acceptable |
|----------|-------------------|------------|
| 1–50 TCs | 50–150 KB | Yes |
| 51–200 TCs | 150–500 KB | Yes |
| 201–500 TCs | 500 KB – 1.5 MB | Yes |
| 500+ TCs | 1.5–5 MB | Yes, with optimization |
| >5 MB | Investigate formatting bloat | Review for optimization |

### 16.3 Compatibility

| Application | Minimum Version | Notes |
|-------------|----------------|-------|
| Microsoft Excel | 2016 | Full feature support |
| Microsoft Excel Online | Current | Full support; merged TC-level cells render correctly |
| Google Sheets | Current | Import .xlsx; formatting may shift slightly |
| LibreOffice Calc | 7.0+ | Full .xlsx read support |
| Zephyr Import | Current | Column mapping required during import |

### 16.4 Zephyr Import Compatibility

The column structure is designed for direct import into Zephyr Scale / Zephyr Squad:

| Workbook Column | Zephyr Mapping |
|----------------|---------------|
| Test Case ID | External ID / Custom field |
| Requirement Title | Label or custom field |
| Test Case Title | Test Case Name |
| Pre-Conditions | Precondition field |
| Step# + Test Step | Test Steps (sequential) |
| Expected Result | Expected Result (per step) |
| Priority | Priority field |

Execution fields (`Test Type`, `Actual Result`, `Status`) are created and owned in
Zephyr after import; they are intentionally absent from the workbook.

---

## Appendix A: Complete Column Reference

v2.3 layout: TC-level columns are **merged vertically** per test case (value appears once,
in the top row). Step-level columns are one row per step.

| Col | Header | Type | Merged per TC | Required | Validation |
|-----|--------|------|---------------|----------|------------|
| A | Test Case ID | Text | Yes (merged; value in top row) | Yes | Globally unique, format {ProjectKey}-{Story}-TC-{NNN} |
| B | Requirement Title | Text | Yes (merged) | Yes | Non-empty |
| C | Test Case Title | Text | Yes (merged) | Yes | Non-empty, prefixed |
| D | Pre-Conditions | Text | Yes (merged) | Yes | Non-empty, includes role |
| E | Step# | Integer | No | Yes | Sequential ≥1 per TC |
| F | Test Step | Text | No | Yes | Non-empty, single action |
| G | Expected Result | Text | No | Yes | Non-empty, specific |
| H | Priority | Text | Yes (merged) | Yes | Enum: High/Medium/Low |

## Appendix B: Freeze Pane and Filter Specification

| Sheet | Freeze Pane Position | Auto-Filter Range |
|-------|---------------------|-------------------|
| Master Summary | Below Row 4 (header row) | Columns A–F, Row 4 |
| Feature Sheets | Below Row 4 (header row) | Columns A–H, Row 4 (sheets use the standard merged TC-level layout per §3.4/§6.6; note the accepted trade-off that merges complicate in-sheet sort/filter and CSV/Zephyr import — use a flat export for import, per §3.4) |

## Appendix C: Document Governance

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-07-22 | PS QA Team | Initial release |
| 2.0 | 2026-07-23 | PS QA Team | Renamed columns B/C to Requirement Title / Test Case Title; globally unique project+story-scoped TC IDs; execution columns explicitly excluded; mandatory embedded schema-version stamp; single-authority + validator alignment; removed date-only filename default. |
| 2.1 | 2026-07-23 | PS QA Team | Replaced vertical cell merges with forward-fill (TC-level values repeat on every step row) so sort/filter/grouping and Zephyr/CSV import work and the layout scales; merges now prohibited (validator FF-01/02/03); added machine-checkable Requirement Traceability Matrix (Review Summary Section E) with reverse-traceability/orphan detection. |
| 2.2 | 2026-07-23 | PS QA Team | Made collapsible row grouping per test case the standard presentation on every feature sheet (§6.6), applied by `apply_grouping.py` in ASSEMBLE. Presentation-only. |
| 2.3 | 2026-07-23 | PS QA Team | Reverted to the standard **merged-cell layout** (per stakeholder request): TC-level columns (ID, Requirement Title, Test Case Title, Pre-Conditions, Priority) merged vertically so each shows once per test case, applied by `apply_merged_layout.py`. Validator updated to the merged model (a new TC begins where Test Case ID is populated; forward-filled workbooks still tolerated); FF-01/02/03 removed. Embedded stamp bumped to `schema:2.3`. Documented CSV/Zephyr import trade-off (use a flat export for import). Same 8 columns/IDs. |
| 2.5 | 2026-07-23 | PS QA Team | **Trimmed the Master Summary to six columns** (stakeholder request): removed `Business Rules`, `Under-tested ACs (Pos-only)`, and `Open Points`. Remaining: Feature/Source, Source Reference, Requirements, Acceptance Criteria, Test Cases, AC Coverage %. Business-rule/scenario-balance remain design-time validation concerns, not reported columns. Stamp `schema:2.5`. |
| 2.4 | 2026-07-23 | PS QA Team | **Removed the Review Summary sheet** (per stakeholder request): no confidence assessment, assumptions, open points, conflicts, or Requirement Traceability Matrix in the workbook. Workbook is now Master Summary + feature sheet(s). Validator: WV-02 removed, RTM checks (RT-01..04) and CV-02/CV-04 removed, feature sheets = everything after Master Summary. Stamp `schema:2.4`. **Trade-off:** coverage is no longer machine-recomputed and orphan TCs are no longer detected from the workbook; traceability is design-time only. |

---

*End of Excel Workbook Specification*
