# Architecture Document — PS AI QA Assistant

> Version: 2.0  
> Last Updated: 2026-07-23  
> Status: Approved (architectural context)

> **Read this first — what is real vs. illustrative.** PS-TestAuthoring as it exists today
> is a **document-driven AI system**: the governing documents in `Knowledge/` plus the
> execution layer in `Skills/` (workflow specs + Python validators), read and followed by an
> AI runtime. There is **no deployed Node.js/TypeScript service, no ExcelJS renderer, and no
> CLI**. Where this document describes software components (a compiled orchestrator,
> ExcelJS, TypeScript interfaces, a CLI), treat them as an **illustrative reference design
> for a possible future engineered implementation, not the current system**. The only
> executable code that exists is the Python tooling under `Skills/`
> (`validate_workbook.py`, `lint_docs.py`, and one-off migration scripts). The real,
> authoritative contracts are the `Knowledge/` documents and those validators.

---

## 1. Purpose

PS AI QA Assistant transforms Jira user stories and their linked Confluence documentation
into execution-ready manual test cases. It eliminates the repetitive, error-prone process of
manually translating requirements into test artifacts — enabling QA teams to focus on
exploratory testing, edge case discovery, and quality strategy rather than documentation.

As deployed, it is a document-driven assistant (see the banner above): an AI runtime follows
the `Knowledge/` standards and `Skills/` workflow, and a deterministic validator enforces the
output contract. "Deterministic pipeline" below refers to that gated flow — the enforceable
guarantees come from the validators, not from the model being inherently deterministic.

---

## 2. Scope

### In Scope

- Reading and parsing Jira stories (summary, description, acceptance criteria, labels, priority, components)
- Fetching and interpreting linked Confluence pages (functional specs, design docs, workflow diagrams)
- Generating structured manual test cases with full traceability
- Producing Excel workbooks formatted for test management tool import
- Supporting batch processing across multiple stories or sprints
- Providing a human review checkpoint before finalization

### Out of Scope

- Automated test script generation (Selenium, Playwright, etc.)
- Test execution or results tracking
- Direct integration with test management tools (Zephyr, qTest) — output is import-ready
- Modifying or updating Jira/Confluence content
- Performance, security, or load test case generation (future consideration)

---

## 3. Inputs

| Source        | Data Extracted                                                                 |
|---------------|-------------------------------------------------------------------------------|
| Jira Story    | Summary, description, acceptance criteria, priority, labels, components, epic  |
| Jira Metadata | Issue type, status, linked issues, sprint, story points                       |
| Confluence    | Linked page body content, child pages, embedded tables, diagrams (as text)    |
| Configuration | Output template, field mappings, generation rules, exclusion filters           |
| User Input    | Jira key(s), sprint name, or JQL query to identify target stories             |

### Input Resolution Strategy

```
User Request (Jira Key / Sprint / JQL)
        │
        ▼
┌─────────────────────┐
│  Jira Story Fetch   │──── Primary requirement source
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Link Extraction    │──── Identifies linked Confluence pages
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Confluence Fetch   │──── Supplementary context & detail
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Context Assembly   │──── Merged, deduplicated requirement corpus
└─────────────────────┘
```

---

## 4. Outputs

### Primary Output: Excel Workbook

Each generation run produces a `.xlsx` workbook containing:

| Sheet              | Purpose                                                    |
|--------------------|------------------------------------------------------------|
| Master Summary     | One row per feature: source reference, requirement/AC counts, test-case count, AC coverage % |
| Feature worksheets | One sheet per feature — the fixed-column test cases defined by `EXCEL_SPECIFICATION.md` |

> Owned by `EXCEL_SPECIFICATION.md`. The Traceability, Coverage Summary, and Metadata sheets
> shown in earlier drafts are obsolete — traceability and coverage are design-time concerns
> surfaced in the Master Summary, not separate sheets (Review Summary/RTM removed in v2.4).

### Test Case Structure

Each test case record contains:

```
┌──────────────────────────────────────────────────────────┐
│  SAMP-123-TC-001                                         │
├──────────────────────────────────────────────────────────┤
│  Title:          Verify login with valid credentials     │
│  Objective:      Confirm successful authentication       │
│  Preconditions:  Active user account exists              │
│  Priority:       High                                    │
│  Type:           Positive                                │
│  Category:       Functional                              │
├──────────────────────────────────────────────────────────┤
│  Step 1:  Navigate to login page                         │
│  Expected: Login form is displayed                       │
│                                                          │
│  Step 2:  Enter valid email and password                 │
│  Expected: Fields accept input without error             │
│                                                          │
│  Step 3:  Click "Sign In"                                │
│  Expected: User is redirected to dashboard               │
├──────────────────────────────────────────────────────────┤
│  Traceability:   PROJ-123 → AC-2                         │
│  Source:         Jira + Confluence (Login Spec v2.1)     │
└──────────────────────────────────────────────────────────┘
```

---

## 5. Internal Workflow

The system operates as a sequential pipeline with clearly defined stages:

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  INGEST │───▶│ ENRICH  │───▶│ REASON  │───▶│ GENERATE│───▶│ REVIEW  │───▶│  OUTPUT │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │               │              │              │
 Fetch from    Pull linked     AI analyzes    Structured     Human QA       Excel file
 Jira via MCP  Confluence      requirements   test cases     validates      written to
               pages           & identifies   are formed     & approves     disk
                               scenarios
```

### Stage Details

#### Stage 1 — Ingest

- Accept user input (Jira key, sprint, or JQL)
- Connect to Jira via Atlassian MCP
- Retrieve story fields: summary, description, acceptance criteria
- Retrieve metadata: priority, labels, components, linked issues

#### Stage 2 — Enrich

- Parse remote links and issue links from the Jira story
- Identify linked Confluence pages
- Fetch Confluence page content (body, child pages if relevant)
- Normalize and merge all requirement text into a unified context document
- Strip formatting noise; preserve tables, lists, and structured content

#### Stage 3 — Reason (AI Core)

- Construct a structured prompt with the assembled context
- Submit to the LLM with role-specific system instructions
- AI identifies:
  - Functional scenarios (happy path)
  - Negative scenarios (invalid inputs, unauthorized access)
  - Boundary conditions (limits, thresholds)
  - Edge cases (concurrency, empty states, special characters)
  - Integration points (downstream effects)
- AI returns structured JSON conforming to the test case schema

#### Stage 4 — Generate

- Parse AI response into typed test case objects
- Assign globally-unique IDs following EXCEL_SPECIFICATION §7.2 (`{ProjectKey}-{Story}-TC-{NNN}`, e.g. `SAMP-125-TC-001`)
- Classify each test case by type and priority
- Build traceability links back to source requirements
- Validate completeness (no empty steps, no missing expected results)

#### Stage 5 — Review (Human Checkpoint)

- A human reviewer opens the generated `.xlsx` workbook and reviews the test cases directly
  in Excel — editing, removing, or annotating as needed. Real review is opening the workbook;
  there is no interactive review application.
- The approve/reject/regenerate actions and review UI described in §9 are an illustrative
  future design (not implemented) — see the honesty banner at the top of this document.

#### Stage 6 — Output

- Render approved test cases into Excel workbook
- Apply formatting, column widths, and header styles
- Surface coverage in the Master Summary (no separate traceability or coverage sheet)
- Emit the `<workbook>.coverage.json` coverage ledger sidecar alongside the workbook
- Write file to configured output directory

---

### End-to-End Knowledge & Skill Execution Flow

The stages above describe the runtime pipeline. The flow below shows how a request is
routed through the document-driven architecture — the `Knowledge/` folder (source of truth)
and the `Skills/` folder (execution layer). Skills are executed by reading and following
their documents; no registered/installed skill is ever invoked for test-case work.

```
┌──────────────────────────────────────────────────────────────┐
│                        USER REQUEST                          │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
   1. Interpret intent  ── Knowledge/USER_REQUEST_PATTERNS.md
      • Identify request type
      • Determine required deliverables
      • Route to the appropriate Skill (in Skills/)
                           │
                           ▼
   2. Capability pre-check ── Knowledge/AI_CAPABILITIES.md
      • Confirm the request is supported BEFORE any generation
      • If unsupported: stop and communicate limitation
                           │
                           ▼
   3. Load governing context & guardrails
      • Knowledge/MASTER_CONTEXT.md      (orchestration & precedence)
      • Knowledge/SYSTEM_INSTRUCTIONS.md (enterprise operating rules)
        — loaded first so all downstream work runs under its rules
                           │
                           ▼
   4. Load selected Skill ── Skills/TestCaseAuthoring/skill.md
      • Validate the request is in scope
      • Define expected inputs & outputs
                           │
                           ▼
   5. Execute Skill workflow ── Skills/TestCaseAuthoring/workflow.md
      • Collect input sources (Jira / Confluence / documents)
      • Extract requirements
      • Identify Acceptance Criteria
      • Identify Business Rules
      • Build execution plan
                           │
                           ▼
   6. Apply QA methodology ── Knowledge/QA_METHODOLOGY.md
      • Coverage philosophy
      • Positive / Negative / Edge Cases
      • Business Rule validation
                           │
                           ▼
   7. Author test cases ── Knowledge/TEST_CASE_GENERATION.md
      • Titles, preconditions, steps, expected results, priorities
      • Knowledge/EXAMPLES.md — writing-quality reference only
                           │
                           ▼
   8. Generate Draft Test Cases
                           │
                           ▼
   9. Validate ── Knowledge/VALIDATION_ENGINE.md
      ✓ Acceptance Criteria coverage   ✓ Scenario coverage
      ✓ Business Rule coverage         ✓ Traceability
      ✓ Preconditions                  ✓ Test Steps
      ✓ Expected Results               ✓ Duplicate detection
      ✓ Environment independence       ✓ Review readiness
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
       Validation Pass            Validation Fail
             │                           │
             │                    Improve output
             │                           │
             └─────────────┬─────────────┘
                           ▼
  10. Build workbook ── Knowledge/EXCEL_SPECIFICATION.md
      • Create workbook • Apply formatting • Apply merge rules
      • Generate final Excel
                           │
                           ▼
  11. Confirm outputs ── Knowledge/AI_CAPABILITIES.md
      • Confirm supported outputs were produced
      • Capture assumptions & open questions
                           │
                           ▼
             Final Deliverables (Review-Ready)
             • Excel Workbook      • Generation Summary
             • Coverage Summary    • Validation Summary
             • Assumptions         • Open Questions
```

**Note on sequencing:** `AI_CAPABILITIES.md` is consulted twice — as an early gate (step 2,
to reject unsupported requests before work begins) and again at the end (step 11, to confirm
the produced outputs and capture assumptions/open questions). `MASTER_CONTEXT.md` and
`SYSTEM_INSTRUCTIONS.md` are loaded up front (step 3) so their precedence and guardrails
govern every subsequent stage.

---

## 6. Core Modules

```
┌─────────────────────────────────────────────────────────────────┐
│                        PS AI QA Assistant                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   CLI        │  │  Config      │  │  Orchestrator        │  │
│  │   Interface  │  │  Manager     │  │  (Pipeline Control)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Integration Layer                            │   │
│  │  ┌────────────────┐  ┌─────────────────────────────┐    │   │
│  │  │  Jira Client   │  │  Confluence Client           │    │   │
│  │  │  (via MCP)     │  │  (via MCP)                   │    │   │
│  │  └────────────────┘  └─────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              AI Layer                                     │   │
│  │  ┌────────────────┐  ┌─────────────────────────────┐    │   │
│  │  │  Prompt        │  │  Response Parser             │    │   │
│  │  │  Builder       │  │  & Validator                 │    │   │
│  │  └────────────────┘  └─────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Output Layer                                 │   │
│  │  ┌────────────────┐  ┌─────────────────────────────┐    │   │
│  │  │  Test Case     │  │  Excel Renderer              │    │   │
│  │  │  Structurer    │  │  (ExcelJS)                   │    │   │
│  │  └────────────────┘  └─────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

| Module               | Responsibility                                                              |
|----------------------|-----------------------------------------------------------------------------|
| CLI Interface        | Parse commands, validate arguments, display progress                        |
| Config Manager       | Load `.env`, YAML templates, merge defaults with overrides                  |
| Orchestrator         | Sequence pipeline stages, handle errors, manage retries                     |
| Jira Client          | Fetch stories, metadata, and links via Atlassian MCP tools                  |
| Confluence Client    | Fetch page content, resolve page hierarchies via Atlassian MCP tools        |
| Prompt Builder       | Assemble context + instructions into structured LLM prompts                 |
| Response Parser      | Extract structured JSON from LLM response, validate schema                  |
| Test Case Structurer | Assign IDs, classify, build traceability, enforce completeness              |
| Excel Renderer       | Format test cases into styled `.xlsx` workbook with multiple sheets         |

---

## 7. Interaction with Atlassian MCP

The assistant communicates with Jira and Confluence exclusively through the Atlassian MCP server. This provides a standardized, secure interface without requiring custom REST API wrappers.

### MCP Tool Usage Map

| Operation                        | MCP Tool                              |
|----------------------------------|---------------------------------------|
| Fetch a Jira story               | `getJiraIssue`                        |
| Search stories by JQL            | `searchJiraIssuesUsingJql`            |
| Get issue links                  | `getJiraIssue` (fields: issuelinks)   |
| Get remote links (Confluence)    | `getJiraIssueRemoteIssueLinks`        |
| Fetch Confluence page            | `getConfluencePage`                   |
| Get child pages                  | `getConfluencePageDescendants`        |
| Search Confluence by CQL         | `searchConfluenceUsingCql`            |
| Resolve Atlassian Cloud ID       | `getAccessibleAtlassianResources`     |

### Data Flow Through MCP

```
PS AI QA Assistant                Atlassian MCP Server               Atlassian Cloud
       │                                  │                                │
       │── getJiraIssue(PROJ-123) ───────▶│                                │
       │                                  │── REST API /issue/PROJ-123 ───▶│
       │                                  │◀── JSON response ──────────────│
       │◀── Structured issue data ────────│                                │
       │                                  │                                │
       │── getConfluencePage(12345) ─────▶│                                │
       │                                  │── REST API /pages/12345 ──────▶│
       │                                  │◀── Page content ───────────────│
       │◀── Markdown/HTML body ───────────│                                │
       │                                  │                                │
```

### Authentication & Security

- Atlassian MCP handles OAuth/API token authentication
- No credentials are stored within the assistant itself
- The assistant operates in read-only mode against Atlassian (no writes)
- **Data flow:** ingested requirement content IS sent to the configured cloud-hosted LLM provider for analysis/generation — processing is NOT local. Data classification, PII/secret minimisation, retention, and the accurate data-flow statement are owned by `DATA_HANDLING.md`. (The earlier "all processing occurs locally" claim was inaccurate and has been corrected there.)

---

## 8. Excel Generation Workflow

### Workbook Structure

> **The workbook output contract is owned by `EXCEL_SPECIFICATION.md`** — this is a summary
> only. The four-sheet layout previously shown here (Test Cases / Traceability Matrix /
> Coverage Summary / Metadata) was never the shipped contract and is obsolete; the
> Traceability Matrix and Review Summary sheets were removed in v2.4.

```
Workbook: TC-<Source>_<YYYYMMDD>.xlsx
├── Sheet 1: "Master Summary"
│   └── One row per feature: source reference, requirement/AC counts,
│       test-case count, and AC coverage % (design-time coverage surfaced here)
└── Sheet 2..N: one feature worksheet per feature
    ├── the fixed columns defined by EXCEL_SPECIFICATION.md
    └── TC-level columns merged vertically across each test case's step rows
```

### Formatting Standards

| Element          | Style                                              |
|------------------|----------------------------------------------------|
| Headers          | Bold, dark background, white text, frozen row      |
| Test Case ID     | Monospace font, left-aligned                       |
| Steps            | Numbered list within cell, wrapped text            |
| Priority High    | Red indicator or conditional formatting            |
| Priority Medium  | Yellow indicator                                   |
| Priority Low     | Green indicator                                    |
| Hyperlinks       | Jira story IDs link back to Atlassian              |

### File Naming Convention

```
TC_{ProjectKey}-{StoryNumber}_{YYYY-MM-DD}.xlsx      (single story)
TC_{ProjectKey}_Sprint-{N}_{YYYY-MM-DD}.xlsx          (sprint batch)
TC_{ProjectKey}_Batch_{YYYY-MM-DD}_{HHmmss}.xlsx      (custom batch)
```

---

## 9. Human QA Review Process

The review stage is a deliberate architectural decision — AI generates proposals, humans approve quality.

### Review Workflow

```
┌────────────────┐
│  AI generates  │
│  test cases    │
└───────┬────────┘
        │
        ▼
┌────────────────┐     ┌──────────────────┐
│  Present to    │────▶│  QA Engineer     │
│  reviewer      │     │  reviews cases   │
└────────────────┘     └───────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
         ┌──────────┐  ┌──────────┐  ┌──────────────┐
         │ Approve  │  │  Reject  │  │ Request      │
         │ (as-is)  │  │  (remove)│  │ Regeneration │
         └──────────┘  └──────────┘  └──────────────┘
                                            │
                                            ▼
                                     ┌──────────────┐
                                     │ Feedback fed  │
                                     │ back to AI    │
                                     └──────────────┘
```

### Review Actions

| Action        | Effect                                                          |
|---------------|-----------------------------------------------------------------|
| Approve       | Test case proceeds to final output unchanged                    |
| Approve+Edit  | QA makes minor edits, then case proceeds                        |
| Reject        | Test case is excluded from output                               |
| Regenerate    | QA provides feedback; AI regenerates that specific case         |
| Add Manual    | QA adds a hand-written test case to the output set              |

### Review Interface (illustrative / not implemented)

The interfaces below are an illustrative future design, **not implemented** — consistent with
the honesty banner at the top of this document. Today, real review is a human opening the
generated `.xlsx` workbook in Excel (see Stage 5).

- **Phase 1 (MVP):** Console-based review — cases printed to terminal, Y/N/E per case
- **Phase 2:** Interactive HTML report with approve/reject buttons
- **Phase 3:** Integration with Confluence — publish draft test plan for team review

---

## 10. Future Extensibility

The architecture is designed for incremental capability expansion:

### Planned Extensions

| Extension                     | Description                                                    | Priority   |
|-------------------------------|----------------------------------------------------------------|------------|
| Test Management Import        | Direct push to Zephyr/qTest/TestRail via their APIs            | High       |
| Regression Awareness          | Compare against existing test suites to avoid duplicates        | High       |
| Multi-Modal Input             | Parse Figma designs or screenshots for UI test cases           | Medium     |
| Risk-Based Prioritization     | Use defect history to weight test case priority                | Medium     |
| Automated Re-generation       | Trigger on Jira story update (webhook-driven)                  | Medium     |
| Test Data Suggestions         | Generate sample test data alongside test steps                 | Low        |
| Localization Testing          | Generate locale-specific test scenarios                        | Low        |
| API Contract Testing          | Read OpenAPI specs to generate API test cases                  | Future     |

### Extension Points

The architecture supports extension through:

1. **Input Adapters** — New data sources (Azure DevOps, GitHub Issues, Figma) can be added without modifying the core pipeline
2. **Prompt Templates** — Domain-specific prompt strategies (security testing, accessibility testing) can be plugged in via YAML templates
3. **Output Renderers** — Additional formats (PDF, HTML, Markdown, direct API push) can be added alongside Excel
4. **Post-Processors** — Hooks after generation for deduplication, risk scoring, or compliance tagging
5. **Review Interfaces** — The review stage accepts any UI frontend that conforms to the approve/reject/regenerate contract

### Design Principles for Extensibility

- Each pipeline stage has a defined input/output contract (TypeScript interfaces)
- Modules communicate through typed data structures, not side effects
- Configuration drives behavior — new capabilities should be toggle-able via config
- The orchestrator is provider-agnostic — AI engine can be swapped without pipeline changes

---

## Appendix: Decision Log

| Decision                              | Rationale                                                       |
|---------------------------------------|-----------------------------------------------------------------|
| Read-only Atlassian access            | Minimizes risk; assistant never modifies source data            |
| Human review before output            | AI output requires validation; prevents silent quality issues   |
| Excel as primary output               | Universal compatibility; no vendor lock-in to test tools        |
| MCP over direct REST                  | Standardized interface; authentication handled externally       |
| Structured JSON from AI               | Deterministic parsing; schema validation possible               |
| Sequential pipeline (not event-driven)| Simpler debugging; predictable execution order                  |

---

*This document describes the product architecture and will be updated as the system evolves through implementation phases.*
