# User Request Patterns — PS AI QA Assistant

> Version: 1.0  
> Last Updated: 2026-07-22  
> Status: Approved  
> Classification: Internal — Professional Services QA  
> Review Cycle: Quarterly  
> Companion Documents: AI_CAPABILITIES.md, MASTER_CONTEXT.md, SYSTEM_INSTRUCTIONS.md, VALIDATION_ENGINE.md

---

## 1. Purpose

USER_REQUEST_PATTERNS.md defines the intent recognition and request routing framework for the PS AI QA Assistant. It enables the AI assistant to:

- Parse natural language requests from QA engineers, leads, and managers.
- Determine the user's intended business outcome.
- Select the correct AI capability (per AI_CAPABILITIES.md).
- Validate that required inputs are present before execution begins.
- Handle ambiguity consistently across all PS projects.

This document is the bridge between what the user says and what the assistant does. It ensures that identical requests from different users on different projects produce identical routing decisions.

| Audience | Value |
|----------|-------|
| AI runtime | Deterministic intent → capability mapping |
| QA Engineers | Predictable behavior regardless of phrasing |
| QA Leads | Consistent routing across teams and projects |
| Architects | Extensible framework for future capabilities |

---

## 2. Intent Recognition Workflow

Every user request passes through the following stages before any capability executes:

```
User Request (natural language)
        │
        ▼
┌─────────────────────────────┐
│  1. Intent Detection        │  Classify the request against known intent patterns
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  2. Confidence Assessment   │  Evaluate match confidence (High / Medium / Low)
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  3. Ambiguity Resolution    │  If confidence < High → ask clarifying questions
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  4. Capability Selection    │  Map confirmed intent to CAP-{NN}
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  5. Input Validation        │  Verify all required inputs are present
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  6. Input Collection        │  Retrieve missing inputs via Atlassian MCP or user
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  7. Capability Execution    │  Execute the selected capability's workflow
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  8. Validation              │  Run VALIDATION_ENGINE checks
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  9. Deliverable             │  Return validated output with summary
└─────────────────────────────┘
```

### Stage Exit Criteria

| Stage | May Not Proceed Until |
|-------|----------------------|
| Intent Detection | At least one intent pattern matches |
| Confidence Assessment | Confidence level is determined |
| Ambiguity Resolution | Confidence is High (user confirmed or pattern unambiguous) |
| Capability Selection | Exactly one capability is selected per intent |
| Input Validation | All mandatory inputs are identified |
| Input Collection | All mandatory inputs are retrieved and readable |
| Capability Execution | Capability workflow completes without fatal errors |
| Validation | All validation checks pass per VALIDATION_ENGINE.md |

---

## 3. Supported User Intents

---

### INT-01: Generate Test Cases

**Routes To:** CAP-01 — Generate Manual Test Cases

**Description:** The user wants execution-ready manual test cases produced from one or more requirement sources and delivered as a formatted Excel workbook.

#### Intent Patterns

| Category | Example Phrases |
|----------|----------------|
| Direct request | "Generate test cases for PROJ-123" |
| | "Create manual test cases from this Confluence page" |
| | "Prepare execution-ready test cases" |
| | "Write QA test cases for this story" |
| Contextual | "I need test cases for this feature" |
| | "Help me create TCs for sprint 42" |
| | "Generate QA scenarios for the billing module" |
| Abbreviated | "TCs for PROJ-123" |
| | "Test cases please" (with prior context providing the source) |
| Variant | "Create regression test cases for…" |
| | "Generate smoke test cases for…" |
| | "Build a test suite for…" |

#### Keyword Indicators

Primary: `test case`, `test cases`, `TC`, `TCs`, `manual test`, `QA scenarios`, `test suite`

Secondary: `generate`, `create`, `prepare`, `write`, `build`, `produce`

#### Confidence Rules

| Condition | Confidence |
|-----------|-----------|
| Primary keyword + source reference (Jira key, URL, file) | High |
| Primary keyword without source | High (prompt for source) |
| Secondary keyword only + QA context | Medium (confirm intent) |
| Ambiguous phrasing | Low (ask clarification) |

#### Required Inputs

| Input | Mandatory | Collection Method |
|-------|-----------|------------------|
| Requirement source (at least one) | ✅ | Jira key → `getJiraIssue`; Confluence URL → `getConfluencePage`; File → Read tool; Text → direct |
| Linked Confluence pages | Retrieve if available | Follow links from Jira story |
| Scope clarification (if multiple features) | When ambiguous | Ask user |

#### Expected Output

Excel workbook per EXCEL_SPECIFICATION.md containing a Master Summary sheet and feature worksheets with test cases. (The Review Summary sheet was removed in v2.4.)

---

### INT-02: Review Requirements

**Routes To:** CAP-02 — Requirement Review

**Status:** Deprioritized — built, trialed, and removed; not currently planned. CAP-02 is **not currently available**: do not run it or fabricate a review deliverable. Acknowledge the request, tell the user requirement review is not currently offered, and route to the closest available capability — generate execution-ready test cases (INT-01), which surfaces missing or untestable acceptance criteria as a by-product.

**Description:** The user wants an assessment of requirement quality, completeness, and testability — without generating test cases.

#### Intent Patterns

| Category | Example Phrases |
|----------|----------------|
| Direct request | "Review the requirements for PROJ-456" |
| | "Analyze this user story for testability" |
| | "Check if the acceptance criteria are complete" |
| | "Validate this story before QA starts" |
| Quality-focused | "Are these requirements testable?" |
| | "Find missing acceptance criteria in PROJ-456" |
| | "What's wrong with this story?" |
| | "Is this story ready for QA?" |
| Gap-oriented | "What's missing from these requirements?" |
| | "Identify ambiguities in this specification" |

#### Keyword Indicators

Primary: `review requirements`, `analyze requirements`, `validate story`, `testability`, `missing acceptance criteria`, `requirement quality`

Secondary: `review`, `analyze`, `assess`, `check`, `validate`, `missing`

#### Confidence Rules

| Condition | Confidence |
|-----------|-----------|
| Primary keyword + source reference | High |
| "Review" + Jira/Confluence source (no mention of test cases) | High |
| "Review" alone without context | Medium (could be requirement review or test case review) |
| "What's missing" without qualifier | Medium (could be gap analysis — INT-03) |

#### Disambiguation from INT-01

If the user says "review" alongside "test cases" or "TCs," route to INT-01 instead. INT-02 is specifically about requirement quality, not test case generation.

#### Required Inputs

| Input | Mandatory | Collection Method |
|-------|-----------|------------------|
| Requirement source (at least one) | ✅ | Same as INT-01 |

#### Expected Output

Structured review report: completeness assessment, missing ACs, missing business rules, ambiguities, risk assessment, recommendations.

---

### INT-03: Gap Analysis

**Routes To:** CAP-03 — Gap Analysis

**Status:** Planned — not yet built. CAP-03 is **not currently available**: do not fabricate a gap-analysis deliverable. Acknowledge the request, explain that gap analysis is planned, and offer the closest available capability — test case generation (INT-01).

**Description:** The user wants to identify gaps between documented requirements and expected coverage — what is missing, under-specified, or untestable.

#### Intent Patterns

| Category | Example Phrases |
|----------|----------------|
| Direct request | "Perform a gap analysis on PROJ-789" |
| | "Identify gaps in this specification" |
| | "What functionality is missing?" |
| Coverage-focused | "Analyze coverage gaps" |
| | "What areas are not covered by these requirements?" |
| Risk-oriented | "Where are the risk areas in this feature?" |
| | "What could go wrong based on these requirements?" |

#### Keyword Indicators

Primary: `gap analysis`, `gaps`, `missing functionality`, `coverage gaps`, `risk areas`

Secondary: `missing`, `uncovered`, `incomplete`, `risk`

#### Confidence Rules

| Condition | Confidence |
|-----------|-----------|
| "Gap analysis" + source reference | High |
| "What's missing" + feature/requirement context | Medium (could be INT-02) |
| "Risk areas" without source | Low (ask for source and confirm intent) |

#### Disambiguation from INT-02

INT-02 focuses on requirement quality (are the requirements well-written?). INT-03 focuses on requirement completeness (are all requirements present?). If intent is unclear, present both options.

#### Required Inputs

| Input | Mandatory | Collection Method |
|-------|-----------|------------------|
| Requirement source(s) | ✅ | Same as INT-01 |
| Feature scope description | Recommended | Ask user if not apparent |

#### Expected Output

Gap report: coverage analysis, missing functional areas, risk areas, recommendations.

---

### INT-04: Generate RTM

**Routes To:** CAP-04 — Requirement Traceability Matrix

**Status:** Planned — standalone capability, not yet built (design-time traceability is owned by QA_METHODOLOGY.md). CAP-04 is **not currently available**: do not fabricate an RTM deliverable. Acknowledge the request, explain that a standalone RTM is planned, and offer the closest available capability — test case generation (INT-01).

**Description:** The user wants a standalone Requirement Traceability Matrix mapping requirements → acceptance criteria → business rules → test cases → coverage status.

#### Intent Patterns

| Category | Example Phrases |
|----------|----------------|
| Direct request | "Generate an RTM for PROJ-101" |
| | "Create a traceability matrix" |
| | "Show requirement traceability" |
| | "Map test cases to requirements" |
| Compliance-oriented | "Prove test coverage for this feature" |
| | "Audit trail for test coverage" |

#### Keyword Indicators

Primary: `RTM`, `traceability matrix`, `requirement traceability`, `traceability`

Secondary: `coverage proof`, `audit trail`, `map test cases`, `trace`

#### Confidence Rules

| Condition | Confidence |
|-----------|-----------|
| "RTM" or "traceability matrix" + source | High |
| "Map test cases to requirements" | High |
| "Show coverage" alone | Medium (could be coverage report within INT-01) |

#### Note on Traceability in CAP-01

As of v2.4, CAP-01 (test case generation) no longer embeds an RTM in its Excel workbook — it maintains AC-to-TC traceability as a design-time discipline while authoring. INT-04 routes to a standalone RTM capability (CAP-04, Planned) for when a traceability matrix is needed as its own deliverable, e.g. when test cases already exist.

#### Required Inputs

| Input | Mandatory | Collection Method |
|-------|-----------|------------------|
| Requirement source(s) | ✅ | Same as INT-01 |
| Existing test cases (if not generating new) | When applicable | User provides or references prior output |

#### Expected Output

Traceability matrix: Req ID → AC ID → Business Rule → Test Cases → Coverage Status, with coverage metrics.

---

### INT-05: Generate Test Data

**Routes To:** CAP-05 — Test Data Generation

**Description:** The user wants structured test data sets — positive, negative, boundary, and role-based — aligned with field definitions and test scenarios.

#### Intent Patterns

| Category | Example Phrases |
|----------|----------------|
| Direct request | "Generate test data for PROJ-202" |
| | "Create boundary test data" |
| | "Generate negative test data for the form fields" |
| | "Prepare test data for this feature" |
| Specific | "Generate role-based test data" |
| | "Create invalid input data sets" |
| | "What test data do I need for this story?" |

#### Keyword Indicators

Primary: `test data`, `boundary data`, `negative data`, `positive data`, `role-based data`, `invalid data`

Secondary: `data sets`, `sample data`, `data generation`

#### Confidence Rules

| Condition | Confidence |
|-----------|-----------|
| "Test data" + source reference or field context | High |
| "Generate data" without "test" qualifier | Medium (could be non-QA request) |
| "Boundary values" or "invalid inputs" | High (test data context is clear) |

#### Required Inputs

| Input | Mandatory | Collection Method |
|-------|-----------|------------------|
| Field definitions or requirement source | ✅ | Jira/Confluence/document with field specs |
| Specific data types requested | Recommended | Ask if only partial types needed |

#### Expected Output

Structured data sets: positive, negative, boundary, role-based, with data dictionary.

---

### INT-06: Regression Impact Analysis

**Routes To:** CAP-06 — Regression Impact Analysis

**Description:** The user wants to understand the regression scope after a requirement or feature change — what needs re-testing and what is safe.

#### Intent Patterns

| Category | Example Phrases |
|----------|----------------|
| Direct request | "What regression testing is needed for PROJ-303?" |
| | "Perform regression impact analysis" |
| | "What's the regression scope for this change?" |
| Change-driven | "We changed the approval workflow — what do we need to retest?" |
| | "Impact of changes to PROJ-303" |
| | "Regression recommendation for this sprint" |
| Scope questions | "What's the blast radius of this change?" |
| | "Which test cases are affected by this update?" |

#### Keyword Indicators

Primary: `regression`, `regression impact`, `regression scope`, `retest`, `impact analysis`

Secondary: `affected test cases`, `blast radius`, `change impact`, `re-test`

#### Confidence Rules

| Condition | Confidence |
|-----------|-----------|
| "Regression" + change description or Jira key | High |
| "Impact" + specific feature change | High |
| "What needs retesting" without context | Medium (ask for change scope) |

#### Required Inputs

| Input | Mandatory | Collection Method |
|-------|-----------|------------------|
| Change description or updated Jira story | ✅ | User provides or Atlassian MCP retrieval |
| Existing test suite (for impact mapping) | Recommended | User provides or references prior output |

#### Expected Output

Impact report: affected modules, affected test cases, new TC recommendations, regression scope (smoke / targeted / full), risk areas, effort estimate.

---

### INT-07: Defect Analysis (Planned)

**Routes To:** CAP-07 — Defect Analysis

**Status:** Planned capability — not currently available; accept the request, explain planned functionality, do not promise or fabricate deliverables.

#### Intent Patterns

| Category | Example Phrases |
|----------|----------------|
| Root cause | "Why did this bug escape testing?" |
| | "Analyze defect PROJ-BUG-42" |
| Prevention | "What test cases would have caught this defect?" |
| | "How do we prevent this type of bug?" |

#### Handling

Acknowledge the request. Explain that defect analysis is a planned capability. Offer alternative assistance:

- Generate test cases for the area where the defect occurred (INT-01)
- Review requirements for the affected module (INT-02)
- Perform gap analysis on the affected feature (INT-03)

---

### INT-08: Automation Candidate Identification (Planned)

**Routes To:** CAP-08 — Automation Candidate Identification

**Status:** Planned capability — not currently available; accept the request, explain planned functionality, do not promise or fabricate deliverables.

#### Intent Patterns

| Category | Example Phrases |
|----------|----------------|
| Direct request | "Which test cases should we automate?" |
| | "Identify automation candidates" |
| ROI-focused | "What's the ROI of automating these test cases?" |
| | "Prioritize test cases for automation" |

#### Handling

Acknowledge the request. Explain that automation candidate identification is a planned capability. Offer to generate well-structured manual test cases (INT-01) that can serve as a foundation for future automation prioritization.

---

## 4. Ambiguity Handling

### 4.1 Confidence Levels

| Level | Definition | Action |
|-------|-----------|--------|
| **High** | Request matches a primary keyword pattern with clear context | Proceed to capability selection |
| **Medium** | Request partially matches or could map to multiple intents | Present the most likely options and ask the user to confirm |
| **Low** | Request does not clearly match any known intent | Ask an open clarifying question without suggesting capabilities |

### 4.2 Ambiguity Resolution Rules

| Rule | Description |
|------|-------------|
| Never assume intent | If confidence is not High, ask before executing |
| Never execute the wrong capability | A clarification round-trip is always cheaper than wrong output |
| Offer likely options | When presenting choices, order by likelihood |
| Limit choices to 3 | Do not overwhelm the user — present the top 3 most likely intents |
| Preserve context | Remember the user's clarification for the remainder of the session |
| One question at a time | Ask a single focused question, not a list |

### 4.3 Common Ambiguity Scenarios

| Scenario | Resolution |
|----------|-----------|
| "Review this" (no qualifier) | Ask: "Would you like me to review the requirement quality, or generate test cases?" |
| "What's missing?" (no context) | Ask: "Are you looking for a requirement quality review or a gap analysis?" |
| "Help me with PROJ-123" (no action) | Ask: "What would you like me to do with PROJ-123? I can generate test cases, review requirements, perform gap analysis, or generate an RTM." |
| "Analyze this" (ambiguous action) | Ask: "Would you like a requirement review, gap analysis, or regression impact analysis?" |
| Source URL without action | Ask: "I can see the source. What would you like me to do? Generate test cases, review requirements, or something else?" |

### 4.4 Context Carryover

If the user has already established context in the conversation:

| Prior Context | New Request | Resolution |
|--------------|-------------|-----------|
| User provided a Jira key earlier | "Generate test cases" | Use the previously provided Jira key — do not re-ask |
| Test cases were just generated | "Now review the requirements" | Use the same source — confirm if scope has changed |
| User specified "for PROJ-123" | "Also do gap analysis" | Apply to the same source — confirm intent |

---

## 5. Multi-Intent Requests

### 5.1 Detection

A multi-intent request contains two or more distinct capability triggers:

| Example | Detected Intents |
|---------|-----------------|
| "Review requirements and generate test cases for PROJ-123" | INT-02 + INT-01 |
| "Generate test cases and create an RTM" | INT-01 + INT-04 (RTM is a separate, standalone capability as of v2.4) |
| "Do a gap analysis, then generate test cases" | INT-03 + INT-01 |
| "Review, generate TCs, and create test data" | INT-02 + INT-01 + INT-05 |

### 5.2 Execution Order

When multiple intents are confirmed, execute in dependency order:

```
1. Requirement Review (INT-02)     — understand quality first
       │
       ▼
2. Gap Analysis (INT-03)           — identify missing areas
       │
       ▼
3. Test Case Generation (INT-01)   — generate from complete understanding
       │
       ▼
4. Test Data Generation (INT-05)   — align data to generated TCs
       │
       ▼
5. RTM Generation (INT-04)         — trace everything produced
       │
       ▼
6. Regression Analysis (INT-06)    — assess change impact
```

### 5.3 Multi-Intent Rules

| Rule | Description |
|------|-------------|
| Confirm before executing | List the detected intents and proposed order; ask user to confirm |
| Sequential execution | Execute one capability at a time; complete validation before starting the next |
| Shared context | Later capabilities inherit analysis from earlier ones (e.g., INT-01 uses findings from INT-02) |
| Independent validation | Each capability's output is validated independently per VALIDATION_ENGINE.md |
| Consolidated delivery | When practical, deliver all outputs together with a unified summary |
| Standalone RTM | As of v2.4 INT-01 does not embed an RTM; if INT-04 is also requested, treat it as a separate standalone capability (CAP-04, Planned) rather than a by-product of INT-01 |

---

## 6. Required Inputs

### 6.1 Input Requirements by Capability

| Capability | Mandatory Inputs | Optional Inputs |
|-----------|------------------|----------------|
| CAP-01: Test Cases | ≥1 requirement source | Scope clarification, priority focus |
| CAP-02: Requirement Review | ≥1 requirement source | Review focus areas |
| CAP-03: Gap Analysis | ≥1 requirement source | Feature scope description |
| CAP-04: RTM | ≥1 requirement source | Existing test case mapping |
| CAP-05: Test Data | Field definitions or requirement source | Specific data types |
| CAP-06: Regression Impact | Change description + affected source | Existing test suite |

### 6.2 Input Collection Rules

| Rule | Description |
|------|-------------|
| Validate before executing | Never begin capability execution with missing mandatory inputs |
| Collect via Atlassian MCP first | For Jira and Confluence sources, retrieve programmatically |
| Ask once | Do not repeatedly ask for the same input within a session |
| Accept multiple formats | Same source can be Jira key, Confluence URL, file path, or pasted text |
| Confirm multi-source grouping | If multiple sources are provided, confirm whether they represent one feature or multiple |

### 6.3 Input Validation Checks

| Check | Action on Failure |
|-------|------------------|
| Jira key format invalid | Ask user to verify the key |
| Confluence URL unreachable | Report the error; ask for alternative source |
| File format unsupported | List supported formats; ask for conversion |
| Pasted text too short (< 50 characters) | Ask if this is the complete requirement |
| No requirement source provided | Ask what the user wants to analyze |
| Jira story has no description or AC | Warn the user; proceed with available content; flag gaps |

---

## 7. Response Standards

### 7.1 Pre-Execution Response

Before executing any capability, the assistant confirms:

| Element | Example |
|---------|---------|
| Detected intent | "I'll generate execution-ready manual test cases." |
| Selected capability | "Using: CAP-01 — Generate Manual Test Cases" |
| Source(s) identified | "Source: PROJ-123 + 2 linked Confluence pages" |
| Input status | "All required inputs are available." |

### 7.2 During-Execution Communication

| Milestone | Communication |
|-----------|--------------|
| Requirement analysis complete | Brief summary: N requirements, M acceptance criteria identified |
| Test case generation complete | "Generated N test cases across M scenarios" |
| Validation complete | "All validation checks passed" or "N issues found — correcting" |

### 7.3 Post-Execution Deliverable

Every final response includes:

| Element | Required |
|---------|----------|
| Deliverable (file or structured output) | ✅ |
| Summary (sources, counts, coverage) | ✅ |
| Open points and assumptions (if any) | ✅ |
| Confidence assessment | ✅ |
| Validation status | ✅ |

### 7.4 Response Quality Rules

| Rule | Description |
|------|-------------|
| Professional tone | Enterprise-grade language; no casual phrasing |
| Structured format | Use tables, lists, and headings — not prose paragraphs |
| Concise unless asked | Provide summary by default; expand on request |
| Actionable | Every recommendation or finding includes a clear next step |
| Validated | VALIDATION_ENGINE.md checks must pass before any output is returned |

---

## 8. Future Expansion

### 8.1 Adding New Intents

The routing framework supports additive extension:

| Step | Action |
|------|--------|
| 1 | Define the new intent in this document (INT-{NN}) |
| 2 | Create the corresponding capability in AI_CAPABILITIES.md (CAP-{NN}) |
| 3 | Add intent patterns, keyword indicators, and confidence rules |
| 4 | Define required inputs and expected outputs |
| 5 | Add disambiguation rules against existing intents |
| 6 | Update the multi-intent execution order if the new intent has dependencies |

### 8.2 Extensibility Principles

| Principle | Implementation |
|-----------|---------------|
| Additive routing | New intents are added without modifying existing intent definitions |
| Backward compatible | Existing intent patterns continue to work unchanged |
| Independent confidence | Each intent has its own confidence rules |
| Shared infrastructure | All intents use the same ambiguity resolution, input validation, and response standards |
| Version controlled | Intent additions are tracked in the document governance log |

### 8.3 Planned Future Intents

| Intent | Capability | Status |
|--------|-----------|--------|
| INT-09: Generate API Test Cases | API test generation from OpenAPI specs | Planned |
| INT-10: Generate Automation Scripts | Playwright / Selenium script generation | Planned |
| INT-11: Release Readiness Assessment | Aggregate coverage and risk assessment | Planned |
| INT-12: Dashboard Generation | Visual QA dashboards | Planned |
| INT-13: Requirement Comparison | Diff two requirement versions | Planned |

---

## Appendix A: Intent Quick Reference

> **Maturity is owned by `AI_CAPABILITIES.md` §7.2 — values below mirror it, they do not
> define it.** One vocabulary: Planned / Pilot / Production. Built today: only INT-01
> (TestCaseAuthoring, Production). INT-02 (Requirement Review) was built, trialed, and
> **deprioritized** (a blocking pre-gen gate does not fit bulk QA workflow — see
> `Skills/SKILLS_REGISTRY.md`). The rest remain Planned until a skill folder + workflow exist.

| Intent | Primary Keywords | Routes To | Maturity (see AI_CAPABILITIES §7.2) |
|--------|-----------------|-----------|----------|
| INT-01 | test case, TCs, test suite | CAP-01 | Production |
| INT-02 | review requirements, testability, missing AC | CAP-02 | Deprioritized — built, trialed, and removed; not currently planned |
| INT-03 | gap analysis, missing functionality, coverage gaps | CAP-03 | Planned |
| INT-04 | RTM, traceability matrix, trace | CAP-04 | Planned (standalone; not embedded in CAP-01 as of v2.4) |
| INT-05 | test data, boundary data, negative data | CAP-05 | Planned |
| INT-06 | regression, impact analysis, retest | CAP-06 | Planned |
| INT-07 | defect analysis, root cause, escaped bug | CAP-07 | Planned |
| INT-08 | automation candidates, automate, ROI | CAP-08 | Planned |

## Appendix B: Disambiguation Matrix

This matrix resolves the most common intent overlaps:

| User Phrase | Possible Intents | Resolution Strategy |
|-------------|-----------------|---------------------|
| "Review this story" | INT-01, INT-02 | Ask: review quality or generate test cases? |
| "What's missing?" | INT-02, INT-03 | Ask: requirement completeness or functional gaps? |
| "Analyze PROJ-123" | INT-01, INT-02, INT-03 | Ask: generate TCs, review quality, or find gaps? |
| "Help with testing" | INT-01, INT-05, INT-06 | Ask: generate TCs, create test data, or regression scope? |
| "Generate coverage report" | INT-01, INT-04 | Ask: generate TCs with coverage or standalone RTM? |
| "Check this feature" | INT-02, INT-03 | Ask: review requirements or identify gaps? |
| "Prepare for QA" | INT-01, INT-02 | Default to INT-01 if ACs exist; suggest INT-02 first if story looks incomplete |

## Appendix C: Document Governance

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-07-22 | PS QA Team | Initial release — 8 intents, routing framework, disambiguation matrix |

---

*End of User Request Patterns Specification*
