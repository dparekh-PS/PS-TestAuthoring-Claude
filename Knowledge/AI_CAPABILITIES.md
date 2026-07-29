# AI Capabilities Catalog — PS AI QA Assistant

> Version: 1.0  
> Last Updated: 2026-07-22  
> Status: Approved  
> Classification: Internal — Professional Services QA  
> Review Cycle: Quarterly  
> Companion Documents: MASTER_CONTEXT.md, SYSTEM_INSTRUCTIONS.md, VALIDATION_ENGINE.md, USER_REQUEST_PATTERNS.md

> **Scope of this document: a CATALOG, not a spec.** For each capability, the "Processing
> Workflow," "Validation Rules," and any workbook/deliverable structure shown here are a
> **summary for readers**, not an authority. The single owners govern:
> workflow → `Skills/TestCaseAuthoring/workflow.md`; validation → `VALIDATION_ENGINE.md`;
> output contract → `EXCEL_SPECIFICATION.md`; routing → `USER_REQUEST_PATTERNS.md`. If a
> capability summary here disagrees with an owner, the owner wins. Do not add process,
> validation, or schema detail to this file.

---

## 1. Purpose

AI_CAPABILITIES.md serves as the master catalog of all business capabilities supported by the PS AI QA Assistant. It defines what the assistant can do, how each capability is triggered, what inputs it requires, what outputs it produces, and what quality standards it must meet.

This document enables:

| Audience | Value |
|----------|-------|
| QA Engineers | Understand what they can request and what to expect |
| QA Leads | Plan adoption and assess capability coverage |
| AI runtime | Determine which capability to execute based on user intent |
| Architects | Evaluate extensibility and plan future capabilities |

Every capability listed here follows the same enterprise execution lifecycle, uses the same validation framework, and produces output governed by the same quality standards.

---

## 2. Capability Architecture

### 2.1 Execution Lifecycle

Every capability — current or future — follows the same lifecycle:

```
Business Request (user intent)
        │
        ▼
┌─────────────────────────┐
│  Capability Selection   │  Determine which capability matches the request
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Input Collection       │  Retrieve all required source material
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Analysis & Reasoning   │  Apply domain expertise per capability rules
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Artifact Generation    │  Produce the capability's defined deliverables
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Validation             │  Execute validation checks per VALIDATION_ENGINE
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Delivery               │  Return validated deliverable with summary
└─────────────────────────┘
```

### 2.2 Shared Infrastructure

All capabilities share:

| Component | Source |
|-----------|--------|
| Guardrails and principles | SYSTEM_INSTRUCTIONS.md |
| Analysis methodology | QA_METHODOLOGY.md |
| Validation framework | VALIDATION_ENGINE.md |
| Atlassian MCP integration | Atlassian MCP tools (getJiraIssue, getConfluencePage, etc.) |
| Document precedence | MASTER_CONTEXT.md §7 |

---

## 3. Capability Catalog

---

### CAP-01: Generate Manual Test Cases

**Maturity Level:** Production

#### Business Purpose

Transform product requirements into a complete set of execution-ready manual test cases with full acceptance-criteria-level traceability, enabling QA engineers to begin test execution immediately without referring to source requirements.

#### Description

This is the primary capability of the PS AI QA Assistant. It ingests requirements from one or more sources, performs structured analysis and decomposition, identifies all testable scenarios, generates detailed test cases, validates coverage, and produces a professionally formatted Excel workbook.

#### Typical User

QA Engineer, QA Lead, Test Manager

#### Supported Inputs

| Input Type | Detection | Retrieval Method |
|-----------|-----------|-----------------|
| Jira Story | Issue key (e.g., PROJ-123) | `getJiraIssue` via Atlassian MCP |
| Confluence URL | URL with `/wiki/` or Confluence domain | `getConfluencePage` via Atlassian MCP |
| Confluence Page ID | Numeric ID | `getConfluencePage` via Atlassian MCP |
| Word Document | `.docx` file | Read tool |
| PDF Document | `.pdf` file | Read tool |
| Markdown File | `.md` file | Read tool |
| Plain Text | `.txt` file or pasted content | Direct use |
| Multiple Sources | Combination of any above | Multi-source grouping rules apply |

#### Processing Workflow

```
1. Retrieve all source material (Jira + linked Confluence + uploads)
2. Analyze requirements — assign Req IDs (R01…) and AC IDs (AC-1…)
3. Decompose complex requirements into atomic testable units
4. Identify business rules, validations, actors, workflows
5. Design test scenarios with type diversity
6. Generate test cases (≥3 steps, environment-independent data, specific results)
7. Trace every AC to its covering test cases at design time (not an emitted sheet)
8. Document assumptions, open points, conflicts
9. Execute Validation Engine (all stages)
10. Self-correct until all checks pass
11. Generate Excel workbook per EXCEL_SPECIFICATION.md
12. Deliver with summary
```

#### Validation Rules

| Rule | Source |
|------|--------|
| 100% AC coverage (verified at design time; surfaced in the Master Summary) | VALIDATION_ENGINE.md |
| Scenario diversity (no Positive-only for ACs with rules) | VALIDATION_ENGINE.md |
| ≥3 steps per TC with 1:1 expected results | VALIDATION_ENGINE.md |
| Environment-independent test data for Functional/Positive TCs | VALIDATION_ENGINE.md |
| No orphan TCs, no uncovered ACs | VALIDATION_ENGINE.md |
| Workbook structure conformance | VALIDATION_ENGINE.md |

#### Deliverables

| Deliverable | Format | Content |
|-------------|--------|---------|
| Excel Workbook | `.xlsx` | Master Summary + Feature Worksheets (Review Summary sheet removed in v2.4) |
| Master Summary | Sheet 1 | Per-feature metrics: Feature/Source, Source Reference, Requirements, Acceptance Criteria, Test Cases, AC Coverage % (6 columns, v2.5) |
| Feature Worksheets | Sheet 2–N | Test cases: TC ID, Requirement, Title, Pre-Conditions, Step#, Step, Expected Result, Priority |

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| AC Coverage | 100% |
| Scenario Diversity | No Positive-only ACs where rules exist |
| Step Granularity | Every TC ≥3 steps |
| Test Data | Every Functional/Positive TC has descriptive, environment-independent data |
| Traceability | Bidirectional AC↔TC mapping complete |
| Workbook Validation | All structural and content checks pass |

#### Limitations

- Does not generate automated test scripts (future capability)
- Does not execute tests or record results
- Does not upload to test management tools directly
- Coverage is limited to content available in source material

#### Future Enhancements

- Direct export to Zephyr, qTest, TestRail formats
- Webhook-triggered auto-generation on Jira story update
- Comparison against existing test suites for deduplication

---

### CAP-02: Requirement Review

**Maturity Level:** Planned — **deprioritized.** A working skill was built and trialed, then
removed: as a blocking pre-generation gate it does not fit the QA team's bulk workflow (QA
cannot fix ACs, so every NOT-READY verdict forces an SA hand-off and re-request). Requirement
quality is owned by SAs/BAs upstream, not by a QA-side gate. See `Skills/SKILLS_REGISTRY.md`
→ "Deprioritized".

#### Business Purpose

Assess the quality, completeness, and testability of product requirements before test case generation begins. Identify gaps, ambiguities, and risks early — when they are cheapest to fix.

#### Description

The assistant analyzes source requirements and produces a structured quality assessment without generating test cases. This capability helps product owners and business analysts improve requirement quality before handing stories to QA.

#### Typical User

QA Lead, Business Analyst, Product Owner

#### Supported Inputs

| Input Type | Accepted |
|-----------|----------|
| Jira Story | ✅ |
| Confluence URL / Page | ✅ |
| Word / PDF / Markdown / Text | ✅ |

#### Processing Workflow

```
1. Retrieve all source material
2. Analyze for completeness against testability criteria
3. Identify present and missing elements
4. Assess risk level per finding
5. Generate structured review report
```

#### Validation Rules

- Every finding must cite the specific source location
- Risk assessment must follow the priority rubric (SYSTEM_INSTRUCTIONS.md)
- Recommendations must be actionable

#### Deliverables

| Deliverable | Content |
|-------------|---------|
| Completeness Assessment | Which elements are present vs. missing |
| Missing Acceptance Criteria | ACs that should exist but are not documented |
| Missing Business Rules | Rules implied but not explicitly stated |
| Ambiguity Report | Requirements that can be interpreted multiple ways |
| Clarification Requests | Specific questions for the product owner |
| Risk Assessment | Impact rating if gaps are not addressed |
| Recommendations | Prioritized actions to improve requirement quality |

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Every gap is actionable | Finding includes what is missing + recommendation |
| Risk is assessed | Every finding has High/Medium/Low impact |
| Source is cited | Every finding references specific requirement text |

#### Limitations

- Does not rewrite requirements — provides recommendations only
- Does not modify Jira or Confluence content
- Assessment quality depends on source material detail

#### Future Enhancements

- Testability scoring (numeric score per requirement)
- Automated comparison against requirement templates
- Integration with Jira workflow to flag incomplete stories

---

### CAP-03: Gap Analysis

**Maturity Level:** Planned

#### Business Purpose

Identify gaps between documented requirements and expected implementation coverage. Determine what is untestable, under-specified, or missing entirely.

#### Description

The assistant compares the requirement corpus against a comprehensive coverage model to identify functional areas, scenarios, or quality attributes that are not addressed by current documentation.

#### Typical User

QA Lead, Test Manager, Solution Architect

#### Supported Inputs

| Input Type | Accepted |
|-----------|----------|
| Jira Story (single or batch) | ✅ |
| Confluence URL / Page | ✅ |
| Existing test suite (for comparison) | ✅ (future) |

#### Processing Workflow

```
1. Retrieve and analyze all source material
2. Build comprehensive requirement catalog
3. Map requirements against coverage model
4. Identify uncovered functional areas
5. Identify under-specified areas
6. Assess risk per gap
7. Generate gap report
```

#### Validation Rules

- Every gap must be traceable to a missing requirement area
- Risk assessment must be justified
- Report must distinguish between "not documented" and "documented but untestable"

#### Deliverables

| Deliverable | Content |
|-------------|---------|
| Gap Report | Structured list of identified gaps with categories |
| Coverage Analysis | What is covered vs. what is expected |
| Missing Functional Areas | Features or behaviors with no requirement coverage |
| Risk Areas | Gaps ranked by business impact |
| Recommendations | Prioritized actions to close gaps |

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Gaps are specific | Each gap describes exactly what is missing |
| Risk is justified | Each gap includes impact assessment |
| Recommendations are actionable | Each gap has a clear resolution path |

#### Limitations

- Cannot assess gaps in undocumented features (unknown unknowns)
- Comparison against existing test suites is a future enhancement

#### Future Enhancements

- Diff-based gap analysis between requirement versions
- Cross-project gap pattern identification
- Integration with existing test suite for delta coverage

---

### CAP-04: Requirement Traceability Matrix

**Maturity Level:** Planned (standalone)

#### Business Purpose

Generate a standalone Requirement Traceability Matrix (RTM) that proves bidirectional coverage between requirements, acceptance criteria, business rules, and test cases.

#### Description

As of v2.4, CAP-01 (test case generation) no longer emits an RTM into its Excel workbook — requirement traceability is maintained as a design-time discipline while authoring, not as an emitted sheet. This capability would provide standalone RTM generation (as a separate, Planned capability) when test cases already exist or when traceability reporting is needed independently.

#### Typical User

QA Lead, Test Manager, Audit/Compliance

#### Supported Inputs

| Input Type | Accepted |
|-----------|----------|
| Jira Story + linked Confluence | ✅ |
| Previously generated test suite | ✅ |
| Manually provided TC-to-AC mapping | ✅ |

#### Processing Workflow

```
1. Retrieve and catalog all requirements (Req IDs)
2. Extract all acceptance criteria (AC IDs)
3. Identify all business rules
4. Map test cases to ACs
5. Calculate coverage metrics
6. Generate RTM with visual indicators
```

#### Deliverables

| Deliverable | Content |
|-------------|---------|
| Traceability Matrix | Req ID → AC ID → Business Rule → Test Cases → Coverage Status |
| Coverage Metrics | AC Coverage %, BR Coverage %, Role Coverage % |
| Gap Indicators | Uncovered ACs (red), Positive-only ACs (orange) |

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Every AC has an RTM row | 100% — no orphaned ACs |
| Every TC links to an AC | No orphan TCs |
| Coverage is mathematically verified | Calculated from data, not asserted |

#### Limitations

- Traceability accuracy depends on TC-to-AC mapping correctness
- Does not generate test cases — only maps existing ones

#### Future Enhancements

- Standalone RTM export as PDF or CSV
- Version comparison (RTM v1 vs. RTM v2)
- Compliance-oriented RTM templates (SOX, HIPAA)

---

### CAP-05: Test Data Generation

**Maturity Level:** Planned

#### Business Purpose

Generate structured, comprehensive test data sets aligned with test case requirements — reducing the time QA engineers spend creating test data manually.

#### Description

Based on requirement analysis and field definitions, the assistant generates test data covering positive, negative, boundary, and role-based scenarios. Test data describes required data characteristics (data type, status, role, conditions) and is ready for use in test execution without being tied to a specific environment.

#### Typical User

QA Engineer, Test Data Analyst

#### Supported Inputs

| Input Type | Accepted |
|-----------|----------|
| Jira Story with field definitions | ✅ |
| Confluence page with data specifications | ✅ |
| Existing test cases (to generate matching data) | ✅ |
| Field schema / data model documentation | ✅ |

#### Processing Workflow

```
1. Identify all fields and their constraints from source material
2. Determine data types, formats, ranges, and enumerations
3. Generate positive data (valid values within constraints)
4. Generate negative data (invalid values violating constraints)
5. Generate boundary data (min, max, min-1, max+1)
6. Generate role-based data (per-role account credentials and permissions)
7. Validate data against field constraints
8. Output structured data set
```

#### Deliverables

| Deliverable | Content |
|-------------|---------|
| Positive Data Set | Valid values for all fields |
| Negative Data Set | Invalid values per validation rule |
| Boundary Data Set | Limit values per numeric/length constraint |
| Role-Based Data Set | User credentials and expected permissions per role |
| Data Dictionary | Field names, types, constraints, and sample values |

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Every field has positive data | All identified fields covered |
| Every validation rule has negative data | Each rule has a violating value |
| Data is descriptive | Environment-independent characteristics, not "valid input" |
| Data is consistent | Cross-field dependencies respected |

#### Limitations

- Cannot provision data in target systems — provides values only
- Data accuracy depends on field definition completeness in source material
- Does not generate production-like volumes (focus is on scenario coverage)

#### Future Enhancements

- Data generation from database schemas or API specifications
- Synthetic data generation with referential integrity
- Data provisioning scripts for test environments

---

### CAP-06: Regression Impact Analysis

**Maturity Level:** Planned

#### Business Purpose

When requirements change, determine the scope of regression testing needed — identifying impacted modules, high-risk areas, and optimal regression suite composition.

#### Description

The assistant compares changed requirements against the existing test coverage landscape to identify which areas need re-testing, which existing test cases are affected, and where new test cases may be needed.

#### Typical User

QA Lead, Test Manager, Release Manager

#### Supported Inputs

| Input Type | Accepted |
|-----------|----------|
| Changed Jira story (new vs. previous version) | ✅ |
| Updated Confluence specification | ✅ |
| Existing test suite (for impact mapping) | ✅ |
| Change description (text) | ✅ |

#### Processing Workflow

```
1. Analyze the scope of the change
2. Identify directly impacted requirements and ACs
3. Identify indirectly impacted areas (dependencies, shared components)
4. Map impact to existing test cases
5. Categorize test cases: must-rerun, should-rerun, unaffected
6. Identify areas needing new test cases
7. Generate impact report
```

#### Deliverables

| Deliverable | Content |
|-------------|---------|
| Impacted Modules | List of functional areas affected by the change |
| Affected Test Cases | Existing TCs that must be re-executed or updated |
| New Test Case Recommendations | Scenarios not covered by existing suite |
| Regression Scope | Smoke Suite, Targeted Regression, Full Regression candidates |
| High Risk Areas | Areas with highest change impact and lowest current coverage |
| Effort Estimate | Approximate regression effort (TC count × complexity) |

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| All direct impacts identified | Changed requirements map to affected TCs |
| Indirect impacts assessed | Dependencies and shared components evaluated |
| Risk is prioritized | High-risk areas clearly identified |
| Recommendations are actionable | Specific TCs to rerun or create |

#### Limitations

- Accuracy depends on existing test suite documentation quality
- Cannot assess impact on undocumented integrations
- Change scope must be clearly articulated in input

#### Future Enhancements

- Automated change detection via Jira story version comparison
- Integration with CI/CD to trigger regression suites
- Historical defect correlation for risk scoring

---

### CAP-07: Defect Analysis

**Maturity Level:** Planned

#### Business Purpose

Analyze production defects to identify root causes, test coverage gaps, and preventive measures — turning reactive bug fixing into proactive quality improvement.

#### Description

The assistant examines defect reports and correlates them with existing requirements and test coverage to determine why defects escaped testing and how to prevent recurrence.

#### Typical User

QA Lead, Test Manager, Engineering Manager

#### Supported Inputs

| Input Type | Accepted |
|-----------|----------|
| Jira Bug/Defect issues | ✅ (planned) |
| Defect description (text) | ✅ (planned) |
| Existing test suite for correlation | ✅ (planned) |

#### Processing Workflow

```
1. Analyze defect description and reproduction steps
2. Identify the requirement area the defect relates to
3. Check existing test coverage for that area
4. Determine if a test case exists that should have caught the defect
5. If yes: analyze why the TC failed to detect — insufficient steps, wrong data, missing scenario
6. If no: identify the missing test scenario
7. Generate root cause assessment and preventive recommendations
```

#### Deliverables

| Deliverable | Content |
|-------------|---------|
| Root Cause Suggestions | Likely cause categories (missing TC, insufficient TC, environment, data) |
| Coverage Gap Analysis | Which scenario type was missing that would have caught the defect |
| Missing Test Cases | New TCs that would prevent recurrence |
| Preventive Recommendations | Process or coverage improvements |
| Defect Pattern Analysis | Common themes across multiple defects |

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Root cause is justified | Evidence-based analysis, not speculation |
| Missing TCs are actionable | Can be added to regression suite immediately |
| Patterns are identified | Systemic issues surfaced, not just individual fixes |

#### Limitations

- Requires well-documented defect reports with reproduction steps
- Cannot access production logs or debugging information
- Analysis quality depends on defect description detail

#### Future Enhancements

- Automated defect ingestion from Jira defect queries
- Trend analysis across sprints and releases
- Predictive defect modeling based on requirement patterns

---

### CAP-08: Automation Candidate Identification

**Maturity Level:** Planned

#### Business Purpose

Recommend which manual test cases are suitable for automation based on stability, execution frequency, complexity, and expected ROI — enabling targeted automation investment.

#### Description

The assistant evaluates a set of manual test cases against automation suitability criteria and produces a prioritized list of candidates with estimated ROI and implementation complexity.

#### Typical User

QA Lead, Automation Engineer, Test Manager

#### Supported Inputs

| Input Type | Accepted |
|-----------|----------|
| Generated test cases (from CAP-01) | ✅ (planned) |
| Existing manual test suite | ✅ (planned) |
| Automation framework constraints | ✅ (planned) |

#### Processing Workflow

```
1. Analyze each test case for automation suitability factors
2. Score: stability (does the feature change frequently?)
3. Score: repeatability (is the test deterministic?)
4. Score: data-driven potential (can it run with multiple data sets?)
5. Score: execution frequency (how often is it run?)
6. Score: complexity (how many steps, how many integrations?)
7. Calculate composite automation priority score
8. Estimate implementation effort and ROI
9. Generate prioritized candidate list
```

#### Deliverables

| Deliverable | Content |
|-------------|---------|
| Automation Candidates | TCs ranked by automation suitability score |
| Priority Tiers | Tier 1 (automate first), Tier 2 (automate next), Tier 3 (keep manual) |
| ROI Estimates | Expected time savings per TC based on execution frequency |
| Implementation Notes | Per-TC considerations (data setup, environment needs, tool suitability) |
| Framework Recommendations | Suggested automation framework per test type |

#### Success Criteria

| Criterion | Target |
|-----------|--------|
| Scoring is transparent | Each factor contributes visibly to the composite score |
| ROI is defensible | Based on execution frequency × manual effort |
| Recommendations are practical | Account for team skills and tool availability |

#### Limitations

- Cannot assess UI stability without historical change data
- ROI estimates are approximations based on available data
- Does not generate automation scripts (separate future capability)

#### Future Enhancements

- Historical execution data integration for frequency scoring
- Automation script generation for top-tier candidates (Playwright, Selenium)
- Continuous re-evaluation as test suites evolve

---

## 4. Capability Selection Rules

### 4.1 Intent Detection

The assistant determines which capability to execute based on user intent:

| User Intent Pattern | Capability Selected |
|--------------------|--------------------|
| "Generate test cases for…" / "Create TCs for…" | CAP-01: Generate Manual Test Cases |
| "Review the requirements for…" / "Assess testability of…" | CAP-02: Requirement Review |
| "What's missing in…" / "Identify gaps in…" | CAP-03: Gap Analysis |
| "Generate RTM for…" / "Show traceability for…" | CAP-04: Requirement Traceability Matrix |
| "Generate test data for…" / "Create test data…" | CAP-05: Test Data Generation |
| "What regression is needed for…" / "Impact of change to…" | CAP-06: Regression Impact Analysis |
| "Analyze this defect…" / "Why did this bug escape…" | CAP-07: Defect Analysis |
| "Which TCs should we automate…" / "Automation candidates for…" | CAP-08: Automation Candidate Identification |

### 4.2 Selection Rules

| Rule | Description |
|------|-------------|
| Single capability per request | Execute one capability unless explicitly asked for multiple |
| Sequential execution | If multiple capabilities are requested, execute them in the order listed |
| Default capability | If intent is ambiguous, default to CAP-01 (Generate Manual Test Cases) |
| Maturity gate | Do not promise deliverables from Planned-maturity capabilities; describe planned functionality |
| Capability chaining | CAP-01 maintains AC-to-TC traceability at design time but, as of v2.4, does not emit a CAP-04 RTM into its workbook; standalone RTM (CAP-04) is a separate, Planned capability |

### 4.3 Ambiguous Intent Handling

If the user's intent does not clearly map to a capability:

1. Present the capability options relevant to the request
2. Ask for clarification
3. Do not assume — let the user choose

---

## 5. Shared Validation Rules

Every capability must comply with the following shared rules regardless of its specific validation requirements:

| Rule | Source | Applies To |
|------|--------|-----------|
| Follow SYSTEM_INSTRUCTIONS.md guardrails | SYSTEM_INSTRUCTIONS.md §6 | All capabilities |
| Apply QA_METHODOLOGY.md analysis standards | QA_METHODOLOGY.md | All capabilities involving requirement analysis |
| Execute VALIDATION_ENGINE.md checks | VALIDATION_ENGINE.md | All capabilities producing deliverables |
| Conform to EXCEL_SPECIFICATION.md | EXCEL_SPECIFICATION.md | All capabilities producing Excel output |
| Maintain requirement traceability | QA_METHODOLOGY.md — Requirement Traceability | All capabilities involving TCs or RTM |
| Never invent missing requirements | SYSTEM_INSTRUCTIONS.md §2.3 | All capabilities |
| Never deliver unvalidated output | VALIDATION_ENGINE.md | All capabilities |
| Document all assumptions and open points | SYSTEM_INSTRUCTIONS.md §2.4 | All capabilities |
| Use Atlassian MCP for Jira/Confluence data | MASTER_CONTEXT.md §3 | All capabilities accessing Atlassian |

---

## 6. Future Extensibility

### 6.1 Extension Principles

The capability architecture is designed for growth:

| Principle | Implementation |
|-----------|---------------|
| Additive model | New capabilities are added without modifying existing ones |
| Shared lifecycle | Every new capability follows the same execution lifecycle (§2.1) |
| Shared validation | Every new capability uses VALIDATION_ENGINE.md |
| Shared governance | Every new capability gets a specification document in the same format |
| Independent maturity | Each capability matures independently through the maturity model |
| Backward compatible | Adding a capability never degrades existing capabilities |

### 6.2 Planned Future Capabilities

| Capability | Description | Estimated Maturity Timeline |
|-----------|-------------|----------------------------|
| API Test Case Generation | Generate API-specific test cases from OpenAPI/Swagger specs | Near-term |
| Playwright Script Generation | Generate Playwright automation scripts from manual TCs | Near-term |
| Release Readiness Assessment | Aggregate coverage data to assess release risk | Mid-term |
| Dashboard Generation | Visual QA dashboards from coverage and execution data | Mid-term |
| Multi-Format Export | Export to Zephyr, qTest, TestRail native import formats | Near-term |
| Requirement Comparison | Diff two versions of a requirement to identify changes | Mid-term |

### 6.3 Adding a New Capability

To add a new capability:

1. Define the capability using the standard template (§3: Business Purpose, Description, Inputs, Workflow, Validation, Deliverables, Success Criteria, Limitations, Future Enhancements)
2. Assign an initial maturity level
3. Create a specification document if the capability requires detailed standards
4. Register the capability in this catalog with a CAP-{NN} identifier
5. Update MASTER_CONTEXT.md knowledge hierarchy if a new document is added
6. Register the new intent pattern in `USER_REQUEST_PATTERNS.md`

---

## 7. Capability Maturity Model

> **This section is the single source of truth for capability maturity.** Every other
> document (USER_REQUEST_PATTERNS.md, MASTER_CONTEXT.md, SKILLS_REGISTRY.md) must use the
> maturity value stated here and must not invent its own. One vocabulary only —
> **Planned → Pilot → Production → Enterprise Scale** — with no synonyms ("Future" is
> retired; use "Planned").

### 7.1 Maturity Levels

| Level | Name | Definition | Criteria |
|-------|------|-----------|----------|
| 1 | **Planned** | Designed on paper; not yet implemented | Design documented; **no skill folder, workflow, or validator exists** |
| 2 | **Pilot** | Implemented and usable, under active refinement | Skill folder + `workflow.md` exist; validation defined; limited use |
| 3 | **Production** | Fully validated and approved for general use | Full validation pipeline; machine validator enforced; cross-project tested |
| 4 | **Enterprise Scale** | Optimized for high-volume, multi-project deployment | Performance optimized; metrics tracked; governance established |

The honest test for "Pilot or higher": a skill must actually exist under `Skills/` with a
`workflow.md`. A capability that is only described in prose is **Planned**, regardless of
how detailed the description is.

### 7.2 Current Maturity Assessment

| CAP | Capability | Maturity | Basis |
|-----|-----------|----------|-------|
| CAP-01 | Generate Manual Test Cases | **Production** | Real skill: `Skills/TestCaseAuthoring/` + `workflow.md` + `validate_workbook.py`; produces validated workbooks |
| CAP-04 | Requirement Traceability Matrix | **Planned (standalone)** | As of v2.4 CAP-01 no longer emits an RTM sheet (the RTM contract and validator checks RT-01…04 were retired with the Review Summary). Traceability is a design-time discipline within CAP-01; a **standalone** TraceabilityAnalysis skill is **Planned**. |
| CAP-02 | Requirement Review | **Planned (deprioritized)** | Built + trialed, then removed — a blocking pre-gen gate does not fit bulk QA workflow (see SKILLS_REGISTRY "Deprioritized") |
| CAP-03 | Gap Analysis | **Planned** | No skill folder/workflow yet |
| CAP-05 | Test Data Generation | **Planned** | No skill folder/workflow yet |
| CAP-06 | Regression Impact Analysis | **Planned** | No skill folder/workflow yet |
| CAP-07 | Defect Analysis | **Planned** | No skill folder/workflow yet |
| CAP-08 | Automation Candidate Identification | **Planned** | No skill folder/workflow yet |

This assessment matches `Skills/SKILLS_REGISTRY.md` exactly (TestCaseAuthoring = Production;
all others = Planned). The two must always agree.

### 7.3 Maturity Progression

```
Level 1 (Planned)
    │
    │  Implementation begins
    ▼
Level 2 (Pilot)
    │
    │  Validation pipeline complete + cross-project testing
    ▼
Level 3 (Production)
    │
    │  Performance optimization + governance + metrics
    ▼
Level 4 (Enterprise Scale)
```

Each capability progresses independently. A capability at Level 2 does not block a Level 3 capability from operating.

---

## Appendix A: Capability Quick Reference

| CAP | Name | Maturity | Primary Deliverable | Key Input |
|-----|------|----------|--------------------|----|
| 01 | Generate Manual Test Cases | Production | Excel Workbook with TCs (Master Summary + feature sheets) | Jira / Confluence / Documents |
| 02 | Requirement Review | Planned (deprioritized) | — | Jira / Confluence / Documents |
| 03 | Gap Analysis | Planned | Gap Report with Risk Assessment | Jira / Confluence |
| 04 | Requirement Traceability Matrix | Planned (standalone) | RTM with Coverage Metrics | Requirements + Test Cases |
| 05 | Test Data Generation | Planned | Structured Data Sets | Field Definitions / Schemas |
| 06 | Regression Impact Analysis | Planned | Impact Report with Regression Scope | Changed Requirements |
| 07 | Defect Analysis | Planned | Root Cause + Missing TCs | Defect Reports |
| 08 | Automation Candidate Identification | Planned | Prioritized Candidate List | Manual Test Cases |

## Appendix B: Document Governance

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-07-22 | PS QA Team | Initial release — 8 capabilities cataloged |

---

*End of AI Capabilities Catalog*
