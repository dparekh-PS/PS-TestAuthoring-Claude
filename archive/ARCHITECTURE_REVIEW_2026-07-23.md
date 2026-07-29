> **⚠ SUPERSEDED / POINT-IN-TIME RECORD.** This is a dated snapshot; several of its findings have since been remediated. For the current state and score, see `STATE_OF_THE_SYSTEM_2026-07-25.md`.

# Enterprise Architecture Review — PS-TestAuthoring

**Reviewer role:** Principal AI Architect (Enterprise AI Systems, Knowledge Engineering, Prompt Engineering, QA Automation)
**Date:** 23 July 2026
**Scope:** Entire project reviewed as a single AI system — 11 Knowledge documents, the TestCaseAuthoring skill (3 documents), PROJECT_INSTRUCTIONS, root README, and the 4 shipped Excel workbooks.
**Tone as requested:** brutally honest, adversarial, board-grade. Every claim below is backed by a specific file/line or a shipped artifact.

---

## Executive Summary

PS-TestAuthoring is, at its core, a **well-written prompt/instruction scaffold that is presented as an engineered software product**. That gap between what it *claims to be* and what it *actually is* is the defining issue of this review.

The good news is real and should not be lost: the domain thinking is strong. The QA methodology is thoughtful, the authoring standards are mostly rigorous, and — most importantly — **the actual test cases the system produces are genuinely enterprise-grade**. Atomic steps, role-and-data preconditions, measurable expected results, real business-rule traceability, and documented assumptions/conflicts. If the only question were "can this AI write a good manual test case," the answer is an unambiguous yes.

The bad news is structural and it is serious. The project violates its own foundational principle — "never duplicate knowledge across documents" — on almost every page. The end-to-end workflow is defined **six times at four different step counts** (6 vs 7 vs 9 vs 9 vs 11 vs 12). Validation is defined **three times** with incompatible structures. The Excel output schema is defined in **three places that flatly contradict each other** (8 vs 9 vs 12 columns), and the one hard rule — "No columns may be added or removed" (EXCEL_SPECIFICATION line 253) — is directly contradicted by "no field may be omitted" listing 12 fields (TEST_CASE_GENERATION line 363).

Worst of all, the drift is **visible in the shipped output**. The four workbooks use two mutually incompatible formats and four different filename conventions. The same story (SAMP-125) was generated twice, one day apart, producing **5 requirements / 11 ACs / 12 test cases** one day and **1 requirement / 8 ACs / 24 test cases** the next — both proudly stamped "100% coverage." A "deterministic finite state machine" with a "validation engine" and a "final readiness gate" cannot produce that. This is the empirical proof that the engine, the pipeline, and the validation gates are **advisory prose, not enforced code**.

Layered on top are two credibility problems the board will catch immediately: the documents were authored for **GitHub Copilot / OpenAI** (named in four files, including a reference to a non-existent `.github/copilot-instructions.md`) and then dropped into a Claude/skill runtime; and `Knowledge/README.md` plus `ARCHITECTURE.md` describe a **Node.js/TypeScript/ExcelJS application that does not exist** — there is no `src/`, no `package.json`, no code of any kind.

**Verdict: NOT ready for enterprise production as an "enterprise standard."** It is a strong, promising POC with excellent domain content wrapped in an architecture that overstates itself and cannot yet enforce its own rules. With a focused consolidation effort (detailed in the Action Plan), the same content could become a genuinely solid enterprise platform. But it should not go to 100+ engineers across multiple business units in its current state.

**Overall score: 5.2 / 10.**

---

## Strengths

1. **Test-case content quality is genuinely high.** Shipped examples show atomic steps, role+data preconditions, observable/measurable expected results, `[Positive]`/`[Negative]`/`[Edge Case]` tagging, BR-level traceability, and honestly logged conflicts (e.g., SAMP-125 records that the Jira AC lists three events while Confluence QPN-006 lists four, and states which source it followed). This is the project's crown jewel.
2. **The QA methodology is intellectually sound.** Business-rule categorization, boundary analysis (min/max/min-1/max+1), scenario-diversity mapping per AC, and the "measure coverage at the AC level" philosophy reflect real senior-QA thinking.
3. **The finite-state-machine workflow spec is above average.** 12 named states, a nine-field contract per state, an error-recovery table, bounded retries with loop-prevention, and human checkpoints. As a *specification* this is well-designed; the execution order (cheap `SELF_REVIEW` before the blocking `VALIDATE`) is defensible.
4. **The intent-routing layer (USER_REQUEST_PATTERNS) is clean** — 8 intents with keyword indicators, confidence levels, and disambiguation. In isolation it is the most coherent document in the set.
5. **EXCEL_SPECIFICATION is the strongest single document** — detailed typography, color, merge, naming, and validation rules. It is let down by scale defects and by not being enforced, not by lack of care.
6. **The concrete "reject-list" validation rules are actually checkable.** The banned-phrase lists for weak expected results ("Works correctly," "Email sent") and environment-dependent data (invented Quote IDs, emails, account names) are pattern-matchable and genuinely useful.

---

## Weaknesses

1. **Massive cross-document duplication with active drift** — the single largest problem, and a direct violation of the project's own "never duplicate" rule.
   - Workflow defined **6×**: PROJECT_INSTRUCTIONS (9 steps), MASTER_CONTEXT §8 (7 phases), SYSTEM_INSTRUCTIONS §3 (12 stages), AI_CAPABILITIES CAP-01 (12 steps), ARCHITECTURE §5 (6 stages) and again (11 steps), skill.md (9 stages), workflow.md (12 states). None reconcile.
   - Validation defined **3×**: VALIDATION_ENGINE (13 categories), TEST_CASE_GENERATION §10 (15 checks), QA_METHODOLOGY §11 (a third checklist) — different structures, no shared numbering.
   - Excel schema defined **3×** with contradictions (below).
   - Coverage philosophy, priority rubric, title standards, precondition standards, prohibited-phrase lists, and the future-capabilities roadmap are each duplicated 2–4 times.

2. **The deliverable's shape is undefined.** EXCEL_SPECIFICATION mandates **8 columns** and "No columns may be added or removed" (line 253). TEST_CASE_GENERATION §4.1 mandates **12 fields** and "no field may be omitted" (line 363), adding Test Data, Test Type, Actual Result, Status. QA_METHODOLOGY §8.1 mandates **9 fields**. EXAMPLES.md shows **8**. These cannot all be satisfied. "Test Data" and "Test Type" are called *mandatory* yet have **no column to live in** and are never demonstrated.

3. **Contradictory guidance on the most error-prone field (test data / environment independence).** VALIDATION_ENGINE and EXAMPLES forbid invented account names, IDs, and emails and model `<placeholder>` style. TEST_CASE_GENERATION §4.4 and QA_METHODOLOGY §8.4/§8.5 hardcode exactly that forbidden data ("Acme Corp," "sm_user@test.com," "$500," "Q-2026-001") as *good* examples. QA_METHODOLOGY even contradicts itself (line 53 "not fictitious names or IDs" vs §8.4 modeling fictitious names as best practice).

4. **"Validation Engine" is a checklist in costume.** Roughly 4 of 13 categories are pattern-checkable; the rest are subjective adjectives ("Atomic," "Executable," "balanced coverage," "critical scenario category") an LLM cannot objectively self-score. Every coverage %, traceability %, and confidence level in the "Final Validation Summary" is **self-reported by the model with no independent audit**. An LLM under load will emit "100% coverage — all checks passed" as a plausible completion without having enumerated anything.

5. **Coverage validation is downstream of extraction, so the 100% gate is hollow.** Every check validates AC→TC linkage; nothing validates source→AC *fidelity*. If the model fabricates or misses an AC, it then achieves "100% coverage" of its own fabrication and every gate passes. This is the primary hallucination/miss vector and it is unguarded.

6. **The system overstates itself.** MASTER_CONTEXT, AI_CAPABILITIES, USER_REQUEST_PATTERNS and README target **GitHub Copilot / OpenAI** (with a reference to a non-existent `.github/copilot-instructions.md`); ARCHITECTURE and Knowledge/README describe a **TypeScript/ExcelJS codebase that does not exist**; the root `README.md` is **0 bytes**. Six of eight AI_CAPABILITIES capabilities are Pilot/Future but written in functional present tense.

7. **Orchestration is stale.** MASTER_CONTEXT — the self-declared "authoritative entry point" — never mentions three real files (AI_CAPABILITIES, USER_REQUEST_PATTERNS, EXAMPLES) or the Skills/ tree. Its precedence table ranks only 7 documents; conflicts involving the others are unresolvable by the stated rules. The real routing actually lives in PROJECT_INSTRUCTIONS.

8. **EXAMPLES.md does not conform to the rules it claims to embody.** It asserts "Every example conforms" (line 24), yet its headline example TC-014 has only 2 steps (min is 3); no example reaches the 4-precondition minimum; AC-03.2/AC-03.3 have no positive case (violating "every AC needs a positive"); and it uses a different ID scheme (REQ-03/AC-03.1) than the mandated R01/AC-1.

---

## Critical Issues

These are the issues that, on their own, block "enterprise standard" status.

**C1 — No enforcement layer exists; the output proves it.** The four shipped workbooks use two incompatible formats. Two of them (`SAMP-125_TestCases_2026-07-22`, `SAMP-166-TestCases-20260723`) break rules the spec itself marks **Fatal** (wrong 2nd sheet, extra columns, header casing `Pre-conditions` vs `Pre-Conditions`, 5-column Master Summary vs mandated 9). `SAMP-166` was generated **after** the spec's own "Last Updated" date and still used the non-conformant legacy format on the same day two conformant files were produced. A specification that is violated the day it is published is not being enforced.

**C2 — Non-determinism presented as determinism.** workflow.md guarantees that "given identical inputs … the FSM traverses an identical state path and yields an equivalent deliverable." The SAMP-125 pair (5/11/12 vs 1/8/24 test cases, one day apart, both "100%") empirically disproves this. Calling an LLM pipeline a "deterministic finite state machine" gives reviewers and users false confidence in reproducibility that does not exist.

**C3 — The single-source-of-truth architecture is fiction.** With the workflow defined 6×, validation 3×, and the Excel schema 3× (with direct contradictions), there is no single source of truth. The maintainability model the whole project rests on is already broken at POC scale; at enterprise scale it will be unmanageable.

**C4 — Self-reported validation with no audit.** Coverage %, traceability %, and "Confidence: High/Low" are numbers the model writes about its own work. There is no deterministic recomputation from the workbook. For a QA governance tool, unverifiable quality metrics are a fundamental credibility failure.

**C5 — No globally unique, stable test-case IDs.** IDs are `TC-{NNN}` restarting per sheet/workbook, so `TC-001` in project A ≠ `TC-001` in project B. EXCEL_SPECIFICATION itself contradicts its own ID scope three ways (line 270 "unique within the sheet," line 377 "within the workbook," line 461 "across the entire workbook"). Cross-project traceability, defect linking, and org-level analytics are impossible without stable IDs — a hard blocker for "multiple projects / multiple business units."

---

## Recommended Improvements

**Consolidate to genuine single-source-of-truth documents.** Each concept must live in exactly one file; every other reference must be a pointer, not a copy.

- One **WORKFLOW** owner (recommend `Skills/*/workflow.md`). Delete the workflow bodies from MASTER_CONTEXT, SYSTEM_INSTRUCTIONS, AI_CAPABILITIES, ARCHITECTURE and PROJECT_INSTRUCTIONS; replace with a one-line reference.
- One **VALIDATION** owner (`VALIDATION_ENGINE.md`). Remove the competing checklists from TEST_CASE_GENERATION §10 and QA_METHODOLOGY §11.
- One **OUTPUT SCHEMA** owner (`EXCEL_SPECIFICATION.md`). Remove the column/formatting specs embedded in SYSTEM_INSTRUCTIONS §3.12, ARCHITECTURE §8, MASTER_CONTEXT §5, and AI_CAPABILITIES CAP-01.
- Resolve the 8/9/12-column contradiction **explicitly**: decide whether Test Type / Actual Result / Status are in scope (real QA execution wants them; the current spec forbids them) and make one decision everywhere.

**Add a deterministic post-generation validator (this is the highest-leverage single change).** A small script (Python/openpyxl) that opens the produced `.xlsx` and mechanically enforces WV-01…WV-07, header casing, column set, filename convention, ID uniqueness, blank-cell checks, and recomputes coverage % from the actual RTM. This converts "the model says it validated" into "the file provably conforms," and it is the only way C1/C2/C4 get fixed.

**Fix the environment-independence contradiction.** Pick placeholders (`<approval threshold>`) as the standard, purge the hardcoded "Acme Corp / sm_user@test.com / $500 / Q-2026-001" exemplars from QA_METHODOLOGY and TEST_CASE_GENERATION, and add a `(value TBC)` marker for unknown thresholds/formulas mirroring the existing `(wording TBC)` mechanism.

**Add extraction-fidelity checks.** Before validating AC→TC coverage, add a step that lists each extracted AC beside its source quote/anchor and flags ACs with no verbatim source support as "possibly inferred." This is the only structural defense against the hollow-100% problem.

**Fix the merged-cell / filter contradiction in the Excel spec.** Vertical merges (line 178) break the mandated auto-filter/sort (line 743) and break Zephyr import. Either drop merges in favor of forward-filled repeated values (recommended for scale and import), or drop the filter claim. At thousands of rows, forward-fill is the only workable option.

**Introduce stable, globally-unique IDs.** e.g. `{PROJECT}-{STORY}-TC-{NNN}`, plus an embedded `schemaVersion` cell recording which EXCEL_SPECIFICATION version the file conforms to.

**Persist Req/AC/BR IDs as columns in the feature sheet** so traceability is auditable from the workbook itself, not just asserted in a summary sheet.

**Normalize encoding and versioning.** VALIDATION_ENGINE has mojibake (`â†“`, `âœ“`, `â€¢`) in an "Approved v1.0" file; MASTER_CONTEXT cites VALIDATION_ENGINE sections (§10, §15, "21 checks," "9-stage pipeline," "severity model") that **do not exist** in it. Fix the cross-references or the target.

---

## Missing Components

1. **A deterministic output validator** (the enforcement layer). Today validation is prose only.
2. **A shared/base workflow substrate.** The "reusable machinery" (INIT/INTENT/ACQUIRE, retry, checkpoints) exists *only inside* the one skill. There is no base template, so a second skill must fork it.
3. **Per-skill Knowledge scoping.** `Knowledge/` is a flat namespace wholly owned by TestCaseAuthoring; a future `RISK_MODEL.md` has no ownership boundary.
4. **A complete precedence hierarchy** covering all 11 docs + Skills (currently 7).
5. **Data security / privacy / PII standard** for ingested Jira/Confluence content. ARCHITECTURE's "all processing is local" claim (line 382) is false for a cloud LLM and misleading.
6. **A global, stable ID registry** and cross-project/cross-run duplicate detection.
7. **A regeneration/versioning workflow state** (`_v2` handling); today a re-run silently produces a new file in a new format.
8. **An accurate root README and an accurate ARCHITECTURE** describing the doc-driven system that actually exists.
9. **Reverse traceability / orphan-scenario detection** — nothing checks that every generated TC traces *back* to a real AC.
10. **Risk-based coverage validation** — priority is checked for enum value, never for correctness.

---

## Future Roadmap

**Near term (make the current skill trustworthy):** consolidate to single-source docs; ship the deterministic validator; unify the workbook format and migrate the two legacy files; fix the platform/README/ARCHITECTURE honesty gap; resolve the column and environment-independence contradictions.

**Mid term (make it a platform):** extract a shared base workflow (`Skills/_base/`) and a skill manifest so INIT/INTENT/ACQUIRE/retry/checkpoint logic is inherited, not copied; introduce per-skill Knowledge namespaces; add stable global IDs + schema versioning; build a proper RTM with persisted IDs.

**Longer term (the 10-skill vision):** the future skills you named — RequirementAnalysis, RequirementReview, TraceabilityAnalysis, RegressionPlanning, RiskAssessment, TestDataGeneration, AutomationScriptGeneration, ImpactAnalysis, TestExecutionPlanning, DefectAnalysis — are viable *only after* the base substrate exists. Each becomes "base workflow + N states + one Knowledge doc + one manifest entry." Attempting them on today's monolith means forking the state machine and hand-editing four routing docs per skill. Also on this horizon: Zephyr/qTest export (only after merged-cell fix), and an actual code layer if deterministic guarantees are ever truly required.

---

## Prioritized Action Plan

### Priority 1 — Must Do (before any wider rollout)

1. **Build and wire a deterministic post-generation Excel validator.** Enforce Fatal rules WV-01…WV-07, header casing, exact column set, filename convention, ID uniqueness; recompute and stamp coverage % from the real RTM. Block delivery on failure. *(Fixes C1, C2, C4.)*
2. **Resolve the workbook-schema contradiction and pick ONE format.** Decide the fate of Test Type / Actual Result / Status. Migrate the two legacy files. Make EXCEL_SPECIFICATION the only schema authority. *(Fixes C1, C3.)*
3. **Collapse duplication to single-source-of-truth.** One workflow, one validation spec, one schema, one routing/precedence table covering all docs. Everything else references. *(Fixes C3.)*
4. **Fix the environment-independence contradiction** and add extraction-fidelity checking. *(Primary hallucination defense.)*
5. **Introduce globally-unique, stable TC IDs + embedded schema version.** *(Fixes C5.)*
6. **Correct the platform/honesty gaps:** remove GitHub Copilot references or state the real runtime; rewrite ARCHITECTURE and Knowledge/README to describe the doc-driven system that exists; populate the empty root README.

### Priority 2 — Should Do

7. Add a shared base workflow substrate + skill manifest so the architecture is genuinely multi-skill before a second skill is attempted.
8. Persist Req/AC/BR IDs as feature-sheet columns; add reverse traceability / orphan-scenario detection.
9. Fix the merged-cell vs filter/sort/import contradiction (move to forward-fill).
10. Make MASTER_CONTEXT actually orchestrate: register all 11 docs + Skills, complete the precedence table, fix the broken §-references into VALIDATION_ENGINE.
11. Reconcile capability-maturity labels (Pilot vs Planned vs Production) across USER_REQUEST_PATTERNS, MASTER_CONTEXT, AI_CAPABILITIES.
12. Add a data-security/PII standard for ingested content.

### Priority 3 — Nice to Have

13. Normalize character encoding across all files; enforce a doc-linting CI check.
14. Add scenario-balance thresholds and risk-based coverage rules to VALIDATION_ENGINE.
15. Add a regeneration/versioning workflow state (`_v2`, reconciliation against prior file).
16. Fix the "Scenario Diversity" column misnomer (it stores a *negative* indicator: count of Positive-only ACs).
17. Replace enumerative banned-phrase lists with a positive structural requirement for expected results.

---

## Scoring

| Area | Score /10 | One-line justification |
|---|---|---|
| Architecture | 4 | Modular in intent, but stale orchestrator, aspirational ARCHITECTURE, and no enforcement layer. |
| Knowledge Base | 5 | Excellent domain content undermined by pervasive duplication and direct contradictions. |
| Skills | 5 | Strong FSM spec; monolithic single-skill reality with no reusable base. |
| Validation | 3 | ~4/13 rules checkable; the rest self-reported and unaudited; hollow 100% gate. |
| AI Reasoning | 6 | Sound methodology; high real output quality; but unguarded extraction-fidelity/hallucination path. |
| Maintainability | 3 | Same concept in 3–6 places guarantees drift; already drifting in shipped files. |
| Scalability | 4 | No stable IDs, no schema versioning, merged-cell fragility, flat Knowledge namespace. |
| Reusability | 4 | Reuse story is narrated, not built; second skill requires forking the state machine. |
| Documentation | 5 | Voluminous and well-written, but describes systems that don't exist; empty root README. |
| Enterprise Readiness | 4 | Not ready for 100+ users / multi-BU: no enforcement, no stable IDs, unverifiable metrics. |
| **Overall** | **5.2** | Excellent POC content; architecture overstates itself and cannot enforce its own rules. |

---

## The Architecture I Would Build From Scratch Today

Same philosophy, honest structure, three layers:

1. **Knowledge (pure domain truth, no process, no duplication).** `QA_METHODOLOGY` (why), `AUTHORING_STANDARD` (how a test case is written — absorbs TEST_CASE_GENERATION, single owner of fields/titles/preconditions), `OUTPUT_SCHEMA` (the workbook contract, single owner), `EXAMPLES` (references only, guaranteed-conformant, ideally generated *from* the standard). One concept, one file, enforced by a doc-lint check.

2. **Skills (thin orchestration over a shared base).** `Skills/_base/workflow.md` owns INIT/INTENT/ACQUIRE/retry/checkpoint/error-recovery once. Each skill = base + its own states + one Knowledge doc + a manifest entry. A single `SKILLS_REGISTRY` + `ROUTING` file replaces the intent logic currently smeared across MASTER_CONTEXT, USER_REQUEST_PATTERNS, and PROJECT_INSTRUCTIONS.

3. **Enforcement (the layer that does not exist today).** A deterministic validator script that opens the generated artifact and mechanically checks the OUTPUT_SCHEMA and recomputes coverage from the RTM. The LLM proposes; the validator disposes. This is what lets you *honestly* say "review-ready" and "conformant." Only after this exists does the word "engine" belong anywhere in the project.

Governance: stable global IDs, embedded schema version in every file, complete precedence table, one platform target named honestly, real security/PII handling, and CI doc-linting to catch duplication and broken cross-references before they ship.

Keep the domain content — it is the best part of this project. Rebuild the scaffolding around it so it stops promising an engine it doesn't have.
