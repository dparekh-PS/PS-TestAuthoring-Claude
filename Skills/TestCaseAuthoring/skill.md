---
name: TestCaseAuthoring
description: >-
  Orchestrates the end-to-end generation of execution-ready manual test cases
  from Jira user stories and their linked Confluence pages via Atlassian MCP.
  Ingests requirements, coordinates the QA reasoning and validation pipeline
  defined in the Knowledge base, and returns a review-ready Excel workbook with
  full acceptance-criteria traceability. Trigger when a QA engineer references a
  Jira issue key, a Confluence URL, an uploaded requirement document, or pasted
  requirement text and asks for manual test cases.
version: 2.5
date: 2026-07-25
status: Approved
classification: Internal — Professional Services QA
governs: Knowledge/ (single source of truth)
inherits: Skills/_base/workflow.base.md (Inheritance v1.1)
changelog: >-
  v2.5 (2026-07-25) — Aligned deliverables to the Excel workbook plus its required
  `<name>.coverage.json` coverage ledger; coverage gated by CV-06/07 and verified
  per-feature by CV-08/09/10 (missing/malformed ledger is blocking, CV-11); added
  ID namespacing/registration (NS-01/02, `--register`) to the ASSEMBLE/RETURN
  lifecycle; removed RTM as a deliverable/growth item; de-duplicated Risk Assessment;
  set coherent version aligned with workflow Inheritance v1.1.
---

# TestCaseAuthoring Skill

## Overview

TestCaseAuthoring is the primary orchestration component of the PS AI Test
Authoring Platform. It coordinates the complete workflow that converts product
requirements — sourced from Jira, Confluence, uploaded documents, or plain text
— into execution-ready manual test cases packaged as a review-ready Excel
workbook.

The skill is an orchestration layer, not a knowledge repository. It owns *how*
the capability executes and *which* Knowledge documents govern each stage; it
does not restate the QA methodology, test-authoring rules, validation logic, or
workbook schema. Those concerns are owned exclusively by the documents in the
`Knowledge/` folder, which the platform treats as the single source of truth.
TestCaseAuthoring invokes that authoritative body of knowledge in a defined
sequence and enforces the contracts between stages.

Within the platform, this skill occupies the coordination tier: it sits above
the domain Knowledge (methodology, generation standard, validation engine,
workbook specification) and below the user-facing request surface (intent
recognition). It is the component a QA engineer's request resolves to when the
intended outcome is manual test case generation.

## Purpose

The business objective of TestCaseAuthoring is to reduce the time and
inconsistency inherent in manually translating requirements into test artifacts,
while raising and standardizing quality across all Professional Services
projects. It exists to let QA engineers obtain complete, traceable,
execution-ready test coverage from a requirement source in minutes rather than
days, and to guarantee that identical requirements produce identical, auditable
deliverables regardless of who requests them or which project they belong to.

The skill delivers this objective without displacing human judgment: every
deliverable it returns is positioned as a review-ready draft that a QA engineer
validates and owns, not an automatically accepted artifact.

## Responsibilities

TestCaseAuthoring is responsible for orchestrating, not for authoring domain
logic. Its responsibilities are:

- **Request resolution** — accepting a generation request, confirming its intent
  is manual test case generation, and identifying the requirement source(s)
  supplied.
- **Requirement ingestion coordination** — retrieving requirement material from
  the appropriate source system (Atlassian MCP, uploaded files, or inline text)
  and normalizing it into a consistent internal representation for downstream
  stages.
- **Source linkage resolution** — detecting Confluence pages linked from a Jira
  issue and consolidating multi-source and mixed-source inputs into a single
  coherent requirement set.
- **Pipeline sequencing** — invoking the governing Knowledge documents in the
  correct order, passing the output of each stage as the contracted input to the
  next.
- **Decision gating** — evaluating completeness, ambiguity, and readiness at
  defined checkpoints, and routing to clarification or human review when a gate
  cannot be satisfied automatically.
- **Quality-gate enforcement** — ensuring the validation pipeline has executed
  and passed before any deliverable is released.
- **Deliverable assembly and return** — assembling the defined artifacts into the
  Excel workbook and returning them to the requester with a clear review posture.
- **Failure containment** — detecting stage failures, failing safely, and
  returning actionable guidance rather than partial or unvalidated output.

The skill does not define what a good test case is, how coverage is measured, how
validation rules operate, or how the workbook is formatted. Those responsibilities
belong to the Knowledge documents referenced below.

## Supported Inputs

The skill accepts the following request inputs and normalizes each into the
internal requirement representation consumed by the pipeline:

- **Jira Issue Key** — a single issue key (for example, a story or task
  identifier). Treated as the primary requirement source; linked Confluence pages
  are resolved automatically.
- **Confluence URL** — a direct link to a Confluence page. Treated as a
  standalone requirement source or as supplementary context to a Jira issue.
- **Uploaded Documents** — requirement documents provided as files (PDF, DOCX,
  TXT, MD). Parsed and normalized into the same internal representation as
  system-sourced requirements.
- **Plain Text Requirements** — requirement text pasted directly into the
  request. Treated as a first-class source when no system reference is available.
- **Multiple Requirements** — a set of issue keys, URLs, or documents submitted
  together for batch processing, producing one consolidated deliverable with
  per-source segmentation.
- **Mixed Sources** — any combination of the above in a single request (for
  example, a Jira key plus an uploaded design document plus pasted clarifications),
  reconciled into a unified requirement set before generation.

Input recognition and the rules for disambiguating underspecified requests are
governed by `USER_REQUEST_PATTERNS.md`; this skill consumes that framework rather
than defining its own parsing rules.

## Supported Requirement Sources

TestCaseAuthoring operates against the following requirement systems and channels:

- **Jira (via Atlassian MCP)** — the primary system of record for user stories,
  acceptance criteria, and issue metadata. All Jira retrieval is performed through
  the Atlassian MCP integration; the skill does not access Jira through any other
  channel.
- **Confluence (via Atlassian MCP)** — the primary source of supporting
  functional specifications, design documentation, and workflow detail. Confluence
  pages are retrieved through the Atlassian MCP integration, whether supplied
  directly by URL or resolved as links from a Jira issue.
- **Uploaded documents** — offline requirement artifacts provided at request time,
  used when requirements live outside the Atlassian ecosystem.
- **Inline text** — requirement content pasted directly, used for lightweight or
  ad-hoc requests.

Atlassian MCP is the exclusive access path for all Jira and Confluence data. The
skill reads from these systems only; it never writes to them (see Non-Goals).

## Generated Deliverables

A successful run returns two files plus a response-level generation summary. The
Excel workbook is the primary deliverable; the coverage ledger is a required
sidecar file that travels with it. Coverage, validation, assumptions, and open
questions are reported as sections of the run's response text, not as separate
files or workbook sheets.

- **Excel Workbook** — the consolidated `.xlsx` deliverable: a six-column Master
  Summary sheet plus one eight-column feature worksheet per feature (no Review
  Summary sheet and no RTM sheet as of v2.4). It packages the execution-ready
  manual test cases into a single, self-contained file. Its sheet composition,
  ordering, and formatting are owned exclusively by `EXCEL_SPECIFICATION.md`.
- **Coverage Ledger (`<workbook-name>.coverage.json`)** — a REQUIRED sidecar file
  that records the per-feature, source-anchored AC-to-test-case mapping. It is
  authored during extraction from the source (not reverse-engineered) and is what
  the validator checks against for per-feature coverage completeness (CV-08/09/10);
  a missing or malformed ledger is blocking (CV-11).
- **Manual Test Cases** — execution-ready, self-contained manual test cases with
  preconditions, steps, expected results, and test data, carried in the workbook's
  feature worksheets. Structure and content standards are owned by
  `TEST_CASE_GENERATION.md` and `QA_METHODOLOGY.md`.
- **Generation Summary (response-level)** — the run's response text, which reports
  coverage completeness, validation outcome, assumptions, and open questions as
  sections directing the reviewer to areas requiring human judgment. These are
  response sections, not workbook sheets or separate files.

## Knowledge Dependencies

The skill delegates all domain reasoning to the `Knowledge/` folder. Each
dependency is described below by why it exists, when the skill invokes it, and
what responsibility it owns. The skill does not reproduce any of their content.

- **MASTER_CONTEXT.md** — *Why it exists:* to unify the entire Knowledge base into
  one coherent operating framework and to define document precedence when guidance
  conflicts. *When used:* consulted first, at request initialization, to establish
  the authoritative reasoning frame and conflict-resolution order. *Responsibility
  it owns:* knowledge orchestration priority and cross-document precedence.

- **SYSTEM_INSTRUCTIONS.md** — *Why it exists:* to define the assistant's identity,
  expertise, responsibilities, and primary objective as a Senior QA Test Analyst.
  *When used:* consulted at initialization to set behavioral and quality
  expectations that apply across every stage. *Responsibility it owns:* the
  standing behavioral contract and non-negotiable objectives.

- **USER_REQUEST_PATTERNS.md** — *Why it exists:* to translate natural-language
  requests into a confirmed intent and a validated set of required inputs. *When
  used:* during request resolution, before ingestion begins. *Responsibility it
  owns:* intent recognition, confidence assessment, ambiguity resolution, and
  input sufficiency checks.

- **AI_CAPABILITIES.md** — *Why it exists:* to catalog supported capabilities and
  the common execution lifecycle each one follows. *When used:* during request
  resolution to confirm the request maps to the test-case-generation capability
  and to bind it to the shared lifecycle. *Responsibility it owns:* capability
  definition, triggering conditions, and lifecycle conformance.

- **QA_METHODOLOGY.md** — *Why it exists:* to define the test-design discipline —
  decomposition, scenario design, and coverage philosophy. *When used:* during the
  analysis and design stage, before any test case is authored. *Responsibility it
  owns:* how requirements are decomposed and how scenario coverage is determined.

- **TEST_CASE_GENERATION.md** — *Why it exists:* to define the QA reasoning loop
  and the standard for authoring individual test cases. *When used:* during the
  generation stage, after design and before validation. *Responsibility it owns:*
  the reasoning sequence and the structural and content standard for each test
  case.

- **CONGA_DOMAIN_REFERENCE.md** — *Why it exists:* to supply the correct Conga CPQ/CLM
  domain vocabulary (objects, Status vs Status Category lifecycle, standard action labels,
  versioning, renewals, document-generation/e-sign, integration/billing touchpoints).
  *When used:* during analysis and generation, so steps and expected results use concrete
  product terminology rather than generic phrasings. *Responsibility it owns:* domain
  terminology only — it never overrides the "never invent" guardrail; unverified project
  specifics stay marked `(wording TBC)` / `(config TBC)`.

- **VALIDATION_ENGINE.md** — *Why it exists:* to serve as the final quality gate,
  detecting gaps and defects and driving automatic correction before output.
  *When used:* after generation and before deliverable assembly. *Responsibility
  it owns:* validation execution flow, gap detection, correction, and
  re-validation criteria.

- **EXCEL_SPECIFICATION.md** — *Why it exists:* to define the exact structure,
  sheet composition, ordering, and formatting of the workbook deliverable. *When
  used:* during deliverable assembly, after validation passes. *Responsibility it
  owns:* the workbook schema and formatting contract.

## Skill Execution Lifecycle

The following describes orchestration only. It states the sequence of stages,
the checkpoint between them, and the governing document at each stage; it does not
describe QA reasoning, which is owned by the Knowledge base.

1. **Initialization** — Load the authoritative reasoning frame and precedence
   rules (`MASTER_CONTEXT.md`) and standing behavioral contract
   (`SYSTEM_INSTRUCTIONS.md`).
2. **Request resolution** — Confirm the request intent and validate input
   sufficiency (`USER_REQUEST_PATTERNS.md`, `AI_CAPABILITIES.md`). If intent is
   ambiguous or required inputs are missing, route to the AI Decision Framework
   before proceeding.
3. **Requirement ingestion** — Retrieve and normalize requirement material from
   the resolved source(s). Jira and Confluence retrieval is performed via Atlassian
   MCP; uploaded documents and inline text are parsed into the same internal
   representation.
4. **Source consolidation** — Resolve Confluence links from Jira issues and merge
   multiple or mixed sources into a single requirement set, recording source
   provenance for traceability.
5. **Analysis and design** — Decompose requirements and design scenario coverage
   (`QA_METHODOLOGY.md`).
6. **Test case generation** — Execute the reasoning loop and author test cases to
   standard (`TEST_CASE_GENERATION.md`).
7. **Validation** — Run the validation pipeline, gap detection, automatic
   correction, and re-validation (`VALIDATION_ENGINE.md`). This is a mandatory
   gate; the lifecycle cannot advance until it passes.
8. **Deliverable assembly** — Assemble validated content into the workbook
   (`EXCEL_SPECIFICATION.md`) and write the required `<name>.coverage.json` coverage
   ledger alongside it. Regeneration writes a new `_v{N}` file rather than
   overwriting a prior version (owned by `_base/workflow.base.md`). Test Case ID
   uniqueness is checked cross-workbook via NS-01/NS-02 against
   `project_registry.json` and `id_ledger.json`.
9. **Return** — Return the workbook and its coverage ledger to the requester with an
   explicit review-required posture, and report coverage/validation/assumptions/open
   questions in the response. After the workbook passes and is delivered, RETURN
   registers its IDs via `validate_workbook.py --register <workbook>`. Human review
   is a defined step in the workflow, not an optional follow-up.

At any stage, an unrecoverable failure transfers control to the Error Handling
Strategy, which fails safely rather than continuing the pipeline.

## AI Decision Framework

This framework governs the routing decisions the skill makes at its checkpoints.
It determines *whether and how* to proceed; it does not determine *what* test
cases to produce, which remains owned by the Knowledge base.

- **Requirement completeness** — Before ingestion completes, the skill assesses
  whether the supplied source(s) contain sufficient information to proceed, applying
  the input-sufficiency criteria of `USER_REQUEST_PATTERNS.md`. Insufficient input
  routes to clarification rather than best-effort generation.
- **Ambiguity** — When intent or requirement meaning is unclear and confidence is
  below the threshold defined in `USER_REQUEST_PATTERNS.md`, the skill raises
  targeted clarifying questions before committing to generation, rather than
  inventing behavior.
- **Missing acceptance criteria** — When a requirement source lacks explicit
  acceptance criteria, the skill records the gap as an open point and either
  requests confirmation or proceeds under clearly stated assumptions surfaced in the
  run's generation summary — never by fabricating criteria.
- **Missing Confluence** — When a Jira issue references a Confluence page that
  cannot be resolved or retrieved, the skill notes the missing context, continues
  from available sources where viable, and flags the reduced context for reviewer
  attention.
- **Validation failures** — When validation reports defects, the skill relies on
  the automatic-correction and re-validation loop of `VALIDATION_ENGINE.md`; it
  releases a deliverable only after validation passes and escalates to human review
  if a failure cannot be resolved automatically.
- **Multiple requirement sources** — When several sources are supplied, the skill
  consolidates them into one requirement set, reconciles overlaps, and preserves
  per-source provenance so coverage remains traceable to origin.
- **Human review requirements** — Every deliverable is returned as review-required.
  The skill additionally escalates for mandatory human judgment when it detects
  unresolved conflicts, low-confidence interpretations, or assumptions that
  materially affect coverage.

## Quality Gates

No deliverable is returned until the following gates are satisfied. The gates are
orchestration checkpoints; the validation *rules* they invoke are defined in
`VALIDATION_ENGINE.md` and are not restated here.

- **Intent and input gate** — Confirmed intent and sufficient, validated inputs
  per `USER_REQUEST_PATTERNS.md`.
- **Coverage gate** — Coverage completeness gated by CV-06/07 (from the Master
  Summary) and verified per-feature by the coverage ledger (CV-08/09/10), with a
  missing or malformed ledger blocking (CV-11), per the coverage philosophy of
  `QA_METHODOLOGY.md`. Rule codes and severities are single-sourced in
  `validate_workbook.py`.
- **Validation gate** — The validation pipeline defined in `VALIDATION_ENGINE.md`
  has executed, all critical checks pass, and any automatic corrections have been
  re-validated. This gate is mandatory and blocking.
- **Deliverable conformance gate** — The assembled workbook conforms to
  `EXCEL_SPECIFICATION.md`.
- **Review-readiness gate** — Assumptions, open points, and conflicts are recorded
  in the run's generation summary so the deliverable is fit for human review.

If any gate cannot be satisfied, the skill does not return a partial deliverable;
it returns guidance via the Error Handling Strategy.

## Error Handling Strategy

The skill fails safely: it never returns partial, unvalidated, or fabricated
output, and it always returns actionable guidance describing what happened and how
to proceed.

- **Jira cannot be accessed** — The skill reports the access failure, distinguishes
  between connectivity, permission, and not-found conditions where possible, and
  requests the corrective action (for example, verifying the issue key or Atlassian
  MCP connection). It does not proceed against an unreadable primary source.
- **Confluence cannot be accessed** — The skill records the missing supporting
  context, continues from available sources when the requirement remains testable,
  and clearly flags the reduced context in the run's generation summary. If Confluence is the
  sole source and is unreachable, it halts and requests correction.
- **Requirements are incomplete** — The skill halts before generation, states which
  information is missing, and requests clarification rather than producing
  speculative coverage.
- **Acceptance criteria are missing** — The skill surfaces the gap, proceeds only
  under explicitly stated assumptions when appropriate, and records those
  assumptions as open points for the reviewer; it never invents acceptance
  criteria.
- **Sources conflict** — The skill applies the precedence rules of
  `MASTER_CONTEXT.md` where they resolve the conflict, and otherwise records the
  conflict as an open point for human decision rather than silently choosing an
  interpretation.
- **Validation fails** — The skill invokes automatic correction and re-validation
  per `VALIDATION_ENGINE.md`. If validation still cannot pass, it withholds the
  deliverable and returns a diagnostic summary of the unresolved failures.

## Non-Goals

TestCaseAuthoring intentionally does not:

- **Execute test cases** — it authors test cases; it does not run them or record
  results.
- **Modify Jira** — it reads Jira via Atlassian MCP and never creates, edits,
  transitions, or comments on issues.
- **Modify Confluence** — it reads Confluence via Atlassian MCP and never creates or
  edits pages or comments.
- **Replace QA review** — every deliverable is review-required; the skill augments
  human QA judgment and never substitutes for it.
- **Upload to test management tools** — it produces import-ready output but does not
  integrate with or push to Zephyr, qTest, TestRail, or similar tools.
- **Make business decisions** — it surfaces conflicts, gaps, and assumptions for
  human resolution rather than deciding product or business questions itself.
- **Generate automated test scripts** — it produces manual test cases, not Selenium,
  Playwright, or other automation code.

## Success Criteria

The skill's execution is successful when all of the following measurable conditions
hold:

- **Complete requirement coverage** — every supplied requirement is represented in
  the deliverable with no silently dropped source.
- **Acceptance criteria covered** — acceptance-criteria coverage is gated by CV-06/07
  and verified per-feature by the `<name>.coverage.json` coverage ledger
  (CV-08/09/10), per `QA_METHODOLOGY.md`. The design-time traceability matrix is an
  authoring aid only and is not emitted as a workbook sheet or deliverable.
- **Validation completed successfully** — the validation pipeline in
  `VALIDATION_ENGINE.md` has executed and all critical checks pass.
- **Review-ready output** — assumptions, open points, and conflicts are documented
  so a reviewer can act without re-deriving them.
- **Execution-ready workbook** — the deliverable conforms to
  `EXCEL_SPECIFICATION.md` and is self-contained, such that a QA engineer can
  execute from it without referring back to the source requirements.
- **Deterministic consistency** — identical inputs yield equivalent deliverables
  regardless of requester or project.

## Future Extensibility

The skill is designed so that new QA capabilities attach as additional pipeline
stages or sibling capabilities without altering its orchestration contracts. Its
stable interfaces — the normalized requirement representation, the staged pipeline
with gated checkpoints, and delegation to a governing Knowledge document per stage
— allow the following evolutions to be introduced by adding Knowledge documents and
routing rules rather than by rewriting the orchestration layer:

- **Risk Assessment** — a capability that scores requirements and scenarios by
  business impact and technical risk to drive risk-based test prioritization.
- **Gap Analysis** — a capability that compares requirement coverage against existing
  test suites to identify untested behavior.
- **Regression Impact Analysis** — a capability that identifies test cases affected
  by a requirement change to scope regression effort.
- **Future AI QA capabilities** — additional analytical or generative capabilities
  that conform to the shared execution lifecycle in `AI_CAPABILITIES.md` and reuse
  the existing ingestion, decision, quality-gate, and error-handling infrastructure.

Each future capability is expected to reuse this skill's ingestion, decision
framework, quality gates, and error-handling behavior, and to delegate its domain
logic to a dedicated Knowledge document — preserving the separation between
orchestration and knowledge that defines the platform.
