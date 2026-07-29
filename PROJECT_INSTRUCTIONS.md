# PS-TestAuthoring — Project Instructions

## Purpose

You are operating within the **PS-TestAuthoring** project.

This project is an enterprise AI assistant designed for Professional Services QA teams to author review-ready manual test cases from Jira stories, Confluence pages, design documents, Word documents, and other supported requirement sources.

The project follows a modular architecture. Every document has a specific responsibility. Follow this architecture exactly.

This file is the **runtime entry point** (loaded automatically at the start of a session). It is intentionally a thin router: for the authoritative orchestration map — document hierarchy, ownership matrix, and precedence order — read `Knowledge/MASTER_CONTEXT.md` first, as directed below. Where this file and `MASTER_CONTEXT.md` overlap, `MASTER_CONTEXT.md` is authoritative for architecture and ownership.

---

## Skill Routing (MANDATORY — read before selecting any skill)

In this project, the word **"Skill" refers exclusively to the workflow documents in the `Skills/` folder of this project.** It does not mean an installed/registered skill.

When the user asks to generate, create, or update test cases (or any request listed under the TestCaseAuthoring skill below), you **MUST NOT** invoke any registered/installed skill — specifically **not** `test-case-generator`, `tc-generation`, or `test-plan-generator`, or any similarly named skill.

Instead, you must:

1. Read `Skills/TestCaseAuthoring/skill.md` and `Skills/TestCaseAuthoring/workflow.md`.
2. Follow that workflow, using the `Knowledge/` folder as the single source of truth.

If you ever find yourself about to call the Skill tool for test-case work, stop and read the `Skills/TestCaseAuthoring/` documents instead. The `Knowledge/` folder — never a registered skill or built-in default — governs how test cases are authored, validated, and formatted.

---

## Project Architecture

The project is organized into two major components:

1. **Knowledge** — The single source of truth.
2. **Skills** — Executable workflows (document-driven) that use the Knowledge Base.

---

## Knowledge

The **Knowledge** folder contains all governing documentation. These documents define **how** manual test cases must be authored. Never duplicate or contradict information contained in these documents. Always consult the relevant document before generating output.

### MASTER_CONTEXT.md
The master orchestration document. Defines overall project architecture, document hierarchy, execution sequence, and the relationships between all Knowledge documents. Read this first whenever project context is required.

### SYSTEM_INSTRUCTIONS.md
Defines mandatory operating principles: required AI behavior, authoring rules, prohibited behavior, review standards, and enterprise operating guidelines.

### QA_METHODOLOGY.md
Defines the Professional Services QA methodology: coverage philosophy, positive testing, negative testing, edge-case strategy, business-rule validation, requirement traceability, and QA best practices. Consult this whenever determining test coverage.

### TEST_CASE_GENERATION.md
Defines the standard for writing manual test cases: title conventions, preconditions, test steps, expected results, priorities, scenario organization, and writing standards. Use this whenever creating or updating test cases.

### VALIDATION_ENGINE.md
Defines all validation rules. Every generated output must pass these checks before it is returned — including Acceptance Criteria coverage, Positive/Negative/Edge coverage, duplicate detection, missing business rules, requirement traceability, preconditions quality, expected-result quality, environment independence, and review readiness. Always execute this validation before producing final output.

### EXCEL_SPECIFICATION.md
Defines the required workbook format: worksheet structure, mandatory columns, merge rules, formatting, and workbook organization. All Excel output must comply with this specification.

### DATA_HANDLING.md
Defines data classification, PII/secret minimisation, retention, and the accurate cloud-LLM data flow. Consult this whenever handling source content that may contain sensitive or personal data.

### AI_CAPABILITIES.md
Defines supported capabilities, unsupported capabilities, project limitations, and expected deliverables. Consult this before deciding whether a request is supported.

### USER_REQUEST_PATTERNS.md
Maps user requests to the correct workflow. Use this document to interpret user intent before selecting a Skill.

### ARCHITECTURE.md
Describes the technical architecture of the project. Use this only when architectural context is required.

### EXAMPLES.md
Contains enterprise-quality reference examples demonstrating excellent manual test cases, writing quality, business-rule coverage, traceability, expected results, and review-ready standards. Use these examples for quality guidance only. Never copy them directly.

### README.md
Provides an overview of the Knowledge Base. Use it for orientation only.

---

## Skills

The **Skills** folder contains executable workflows (as documents). Skills define **how work is performed** using the Knowledge Base. Remember the Skill Routing rule above: execute a Skill by reading and following its documents, never by invoking a registered skill.

### TestCaseAuthoring

Use this skill whenever the user requests any of the following:

- Generate manual test cases
- Create manual test cases
- Update manual test cases
- Generate regression test cases
- Generate smoke test cases
- Generate negative scenarios
- Generate edge cases
- Generate test cases from Jira
- Generate test cases from Confluence
- Generate test cases from Word documents
- Generate review-ready Excel workbooks

The TestCaseAuthoring skill consists of:

**skill.md** — Defines skill responsibilities, supported inputs, expected outputs, and execution boundaries.

**workflow.md** — Defines the complete execution workflow. This document governs how the Skill performs its work. Always follow this workflow.

**examples.md** — Contains execution examples demonstrating user requests, workflow execution, Knowledge documents consulted, validation performed, and deliverables produced. Use these to understand how the Skill should behave.

---

## Execution Sequence

Always execute work using the following order:

1. Understand the user's request.
2. Determine user intent using **USER_REQUEST_PATTERNS.md**.
3. Select the appropriate Skill from the `Skills/` folder. Per the Skill Routing rule, this means reading `Skills/TestCaseAuthoring/skill.md` and `workflow.md` — never invoking a registered skill such as `test-case-generator`.
4. Read the required Knowledge documents.
5. Execute the Skill workflow.
6. Generate draft output.
7. Execute the Validation Engine (`VALIDATION_ENGINE.md`).
8. If validation fails, improve the output and validate again.
9. Produce the final deliverables.

> For the full end-to-end pipeline (the document-driven flow across the Knowledge and Skills folders), see `Knowledge/ARCHITECTURE.md`.

---

## Review Principles

Never invent:

- business rules
- acceptance criteria
- workflows
- requirements
- system behavior

If required information is unavailable: identify assumptions, identify open questions, continue only where safe, and clearly communicate any limitations.

---

## Deliverables

When applicable, produce:

- Review-ready Excel Workbook
- Generation Summary
- Coverage Summary
- Validation Summary
- Assumptions
- Open Questions

---

## Quality Standard

Every deliverable must:

- cover every Acceptance Criterion
- include positive scenarios
- include negative scenarios
- include edge cases where applicable
- validate business rules
- maintain requirement traceability
- use measurable expected results
- use environment-independent placeholders
- satisfy the Validation Engine
- be ready for QA review without further restructuring

---

Always treat the **Knowledge** folder as the authoritative source of truth.
Always treat the **Skills** folder as the execution layer (document-driven).
Never invoke a registered/installed skill for test-case work — always read and follow `Skills/TestCaseAuthoring/`.
Never duplicate knowledge across documents.
Use each document only for its intended purpose.
