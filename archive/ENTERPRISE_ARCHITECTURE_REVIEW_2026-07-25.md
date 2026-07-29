> **⚠ SUPERSEDED / POINT-IN-TIME RECORD.** This is a dated snapshot; several of its findings have since been remediated. For the current state and score, see `STATE_OF_THE_SYSTEM_2026-07-25.md`.

# PS-TestAuthoring — Enterprise Architecture Review

> Reviewer role: Principal AI Architect (Enterprise AI, Knowledge Engineering, Prompt Engineering, Multi-Document Reasoning, QA Automation)
> Date: 2026-07-25
> Scope: the entire system (Knowledge + Skills + enforcement code), reviewed as one AI platform, not file-by-file
> Verdict basis: reviewed against the stated goal — the **enterprise standard** for Professional Services QA at 100+ engineers, many projects, many business units, many Salesforce implementations. Judged for long-term scale, not POC.

---

## Executive Summary

PS-TestAuthoring is a **well-conceived document-driven agent with one genuinely excellent idea executed only partway.** The central bet — that domain truth lives in versioned Markdown "Knowledge" with a single owner per concept, that "Skills" are thin executable workflows over that truth, and that a deterministic Python gate disposes of what the LLM proposes — is the right architecture for this problem. When that pattern is actually applied (the workbook validator, the doc-linter, DATA_HANDLING.md, the `_base` FSM), the system is strong.

The problem is that **the pattern is applied to only 2 of ~16 shared concepts, and the system already exhibits exactly the drift it was built to prevent.** The value proposition is "single source of truth, no contradictions." A four-way independent audit found the opposite in the current state: ~14 authoring rules triplicated across three documents; the schema version cited as v2.0, v2.1, v2.4, and v2.5 in different files simultaneously; an authoritative placeholder rule contradicted by its own examples two pages later; a retired RTM artifact still described with live cell-colors and completion criteria in four documents; two files each declaring themselves "the single authority"; and a reference architecture that contradicts the real output contract. None of these is fatal alone. Together they are the credibility risk an Enterprise Architecture Board will fixate on, because integrity-of-truth is the entire premise.

Separately, the system is **not yet enterprise-ready on three hard axes**: (1) it has no multi-project / multi-BU model at all — IDs are unique by convention only, and routing assumes a single project; (2) every *semantic* quality guarantee the docs advertise (duplicate detection, traceability/orphan detection, scenario balance, risk-justified priority, environment-independence, coverage *fidelity*) is unenforced — "100% coverage" is self-graded by the model; and (3) the merged-cell Excel layout trades away filter, sort, import, and predictable rendering at exactly the scale (thousands of rows) where those matter.

**Overall score: 5.0 / 10** — a high-quality POC and a correct architectural thesis, carrying enough consistency and enforcement debt that it should not pass a production board without a focused remediation pass. The good news: the fixes are mostly consolidation and enforcement, not redesign. The core thesis is sound.

---

## Scoring

| Area | Score | One-line justification |
|------|:---:|------------------------|
| Architecture | 6 / 10 | Correct layering + ownership-matrix design, undermined by two competing entry points and a reference doc that contradicts the live contract. |
| Knowledge Base | 5 / 10 | Single-source pattern understood but applied to 2 of ~16 concepts; ~14 rules triplicated; placeholder policy self-contradicts; 4 schema versions coexist. |
| Skills | 5 / 10 | Real reusable substrate + complete FSM, but the skill re-copies the base (already drifted) and the layer only extends cheaply to workbook-clones. |
| Validation | 4 / 10 | Deterministic structural gate is solid; every semantic guarantee is unenforced and coverage is self-certified. |
| AI Reasoning | 5 / 10 | Strong "never invent" spine, actively undercut by min-count padding pressure, fabricated-precondition prompts, and "identify implicit requirements" invitations. |
| Maintainability | 4 / 10 | Massive duplication = large drift surface, and it has already drifted (versions, registries, workflow copy). Linter helps but covers little of it. |
| Scalability | 3 / 10 | No multi-project/BU model; merged cells break filter/sort/import; row-height heuristic is font-dependent; documented flat-export path has no implementation. |
| Reusability | 5 / 10 | `_base` + `_template` are real, but there is no shared validator interface, no inter-skill data schema, and the base hard-codes exactly 3 domain-state slots + Jira-coupled acquisition. |
| Documentation | 5 / 10 | Extensive, with commendable honesty banners — but aspirational ARCHITECTURE/AI_CAPABILITIES bulk, stale registries, and wrong file trees pull it down. |
| Enterprise Readiness | 4 / 10 | No namespacing, self-graded coverage, unenforced PII rules, convention-only ID uniqueness, no governance automation. |
| **Overall** | **5.0 / 10** | Correct thesis, strong POC, pervasive integrity/enforcement debt; not board-ready without a consolidation + enforcement pass. |

> Note vs the earlier `REMEDIATION_SCORECARD.md` (which landed ~7.5): that scorecard measured the *deltas we shipped* and trusted the docs' own claims. This review independently re-read the current tree and found substantial residual drift the scorecard didn't surface (unbumped version headers, RTM tombstones, ARCHITECTURE contradictions, dead `apply_grouping.py`, stale registry). A board review weights integrity-of-truth heavily, so it lands lower. Both can be true: we improved a lot, and the honest current state is ~5.

---

## Strengths

- **The core architecture is right.** Knowledge (truth) / Skills (execution) / deterministic gate (disposition) is the correct decomposition. The ownership-matrix + precedence-order design in MASTER_CONTEXT §6 is genuinely good thinking.
- **`validate_workbook.py` is the best artifact in the system** — single-responsibility, self-documenting, merged-cell-aware, and it enforces the structural contract the LLM cannot be trusted to self-certify. The "LLM proposes, script disposes" principle is exactly right.
- **`lint_docs.py` exists at all.** A CI linter for documentation hygiene (mojibake, retired vocabulary, stale schema, bare IDs, broken refs) is a mature move most doc-driven systems never make.
- **`_base/workflow.base.md` is a real substrate.** The FSM is complete — source acquisition, requirement validation, self-review-before-gate, assemble, and a HALT path with a full error-recovery table and bounded retries. This is well above POC quality.
- **DATA_HANDLING.md is a model document** — one responsibility, current, self-consistent, and it actively *resolves* a legacy "all processing is local" falsehood rather than perpetuating it.
- **Intellectual honesty is present.** Several docs carry "this is illustrative / not the current system" banners, and TEST_CASE_GENERATION §12 documents that a stale checklist was removed. The team knows drift is the enemy — the discipline just isn't uniformly applied.

---

## Weaknesses

- **Single-source-of-truth is preached, not practiced.** Only *validation* and *Excel schema* are consolidated to one owner. ~14 authoring rules (priority rubric, decomposition, scenario taxonomy, coverage formula, title/step/precondition standards, test-data convention, expected-result rules, RTM) are stated in 2–3 documents each. Every duplicate is a future contradiction.
- **Version drift is already live.** EXCEL_SPECIFICATION is referenced as v2.0 (TEST_CASE_GENERATION §4.1), v2.1 (EXAMPLES §13, SKILLS_REGISTRY), v2.4 (SYSTEM_INSTRUCTIONS, TEST_CASE_GENERATION §12), and v2.5 (actual). SYSTEM_INSTRUCTIONS (header v2.0) and QA_METHODOLOGY (header v1.0) describe v2.4 behavior their own governance tables predate.
- **RTM tombstones everywhere.** The Requirement Traceability Matrix was removed as a sheet in v2.4, yet it is still described with 🔴/🟠 cell-color indicators, "RTM is complete" completion criteria, and matrix record structures across SYSTEM_INSTRUCTIONS, QA_METHODOLOGY, TEST_CASE_GENERATION, and EXAMPLES.
- **Two entry points, neither owns the other.** `PROJECT_INSTRUCTIONS.md` (the actually auto-loaded runtime doc) and MASTER_CONTEXT.md both claim to be the authoritative entry point; MASTER_CONTEXT's "complete and authoritative" file map omits both root docs and four real Skills files.
- **The reference architecture contradicts reality.** ARCHITECTURE.md §4/§8 specify four sheets (Test Cases, Traceability Matrix, Coverage Summary, Metadata) that the v2.5 contract does not produce, plus a JSON/TS schema that does not exist, plus a third pipeline vocabulary.
- **Dead and non-functional code is shipped.** `apply_grouping.py` is superseded by `apply_merged_layout.py`, is referenced by nothing in the pipeline, and is a silent no-op on the merged workbooks the system now produces.

---

## Critical Issues (board blockers)

1. **Self-graded coverage.** CV-06 checks that the model's own "AC Coverage %" cell reads ~100%. It cannot confirm the extracted AC set is complete or even real. The headline enterprise promise — "100% acceptance-criteria coverage" — is enforced by trusting the thing being graded. This is the single most important gap for a QA product.
2. **No multi-project / multi-BU model.** `seen_ids` resets per workbook; two runs of `SAMP-125` both emit `SAMP-125-TC-001` and nothing detects the collision. Routing assumes one project namespace. The stated goal (many projects, many BUs, many Salesforce orgs) has no architectural support — this is a design gap, not a bug.
3. **Placeholder policy is self-contradicting.** QA_METHODOLOGY §8.5 is declared authoritative and forbids `(placeholder <x>)` after a characteristic; TEST_CASE_GENERATION's step examples and QA_METHODOLOGY's own §8.3/§8.4 examples use that exact banned form repeatedly. The model imitates examples, so the authoritative rule loses.
4. **Every semantic validation is aspirational.** Duplicate/near-duplicate detection, orphan/traceability, scenario balance, risk-justified priority, environment-independence, and extraction fidelity are all *described* as validations and *none* are computed. The system can emit 40 near-identical positive cases, invent a business rule, and pass the gate.
5. **Merged-cell layout is a scale trap, and the spec denies it.** Merged TC-level columns break sort/filter/CSV/Zephyr import; Appendix B of EXCEL_SPECIFICATION falsely claims "no merged cells to break sort/filter." The documented flat-export mitigation has no implementation.

---

## Recommended Improvements

- **Collapse the authoring standards to one owner per concept.** SYSTEM_INSTRUCTIONS = identity + workflow spine + guardrails only. QA_METHODOLOGY = design philosophy + coverage model. TEST_CASE_GENERATION = concrete authoring mechanics (columns, titles, steps, expected results, priority). EXAMPLES = corpus only. Every other doc *references*, never restates. Delete the RTM sections wholesale rather than caveating them.
- **Make the machine-checkable layer the contract, and generate the human doc from it.** The `BANNED_EXPECTED` list, DV/ER/CV/SV codes, and severities exist in three hand-synced places that already disagree. Put them in one place (the code, or a single YAML the code and doc both read) and have `lint_docs.py` fail on divergence. Resolve the "two single authorities" standoff between `validate_workbook.py` and EXCEL_SPECIFICATION explicitly: code is authoritative, spec is generated/checked against it.
- **Enforce, or explicitly downgrade, the semantic validations.** Implement the cheap, high-value machine checks now (near-duplicate detection via step/expected shingling; environment-independence via regex for emails/`Q-\d+`/IDs; weak-title detection; priority-distribution sanity; cross-workbook ID registry). For genuinely un-automatable checks (extraction fidelity), stop calling them "validations" — label them model-self-review and add a **sampling audit** protocol instead of implying enforcement.
- **Introduce a multi-project namespace.** A project/BU registry (keys, prefixes, enabled capabilities, data agreement) and a persisted global ID ledger so uniqueness is enforced, not assumed.
- **Separate the human "view" from the canonical machine layer.** Author into a flat, unmerged, one-row-per-step canonical sheet (filterable, importable, diffable); apply merging as a *rendered view* or a separate export. This removes the scale trap without losing the readability the merged view gives.
- **Bump every version header, delete `apply_grouping.py`, and reconcile the registries** (SKILLS_REGISTRY v2.1→v2.5, README "coverage retired" → restored, intents INT-02/INT-03 that route to removed/unbuilt skills).

---

## Missing Components

- A **project/BU configuration model** and a **persistent cross-workbook ID ledger**.
- A **shared validator interface** (`Report`/finding/severity taxonomy) that non-workbook skills can inherit — today every future skill writes a validator from scratch.
- An **owned inter-skill interchange schema** (the "normalized requirement representation" is named everywhere, specified nowhere) so RequirementAnalysis output can feed TestCaseAuthoring.
- **Enforcement for the data/PII rules** — DATA_HANDLING has no validator equivalent; it is honor-system.
- **Enterprise authoring standards that are claimed but absent**: data-driven/parameterized cases, localization/regional variants, regression tagging/naming, and a test-case reuse/library concept (equivalence-partitioning and pairwise are named as competencies but never operationalized).
- **Governance automation**: a scaffold generator for new skills, a lint rule for incomplete skill folders, and a registry-vs-reality consistency check. `_base/workflow.base.md` is not even listed in the precedence/ownership matrix.

---

## Future Roadmap

- **Now → Q1:** consolidation + enforcement pass (see Priority 1). Land the multi-project namespace and the canonical-flat-layer split. Get to a defensible, board-passable core (target overall ≥ 7).
- **Q2:** implement the cheap semantic validators (dup detection, environment-independence, weak-title, priority distribution) and the sampling-audit protocol for un-automatable checks. Ship the shared validator interface + interchange schema so a *second* skill (RiskAssessment or RequirementAnalysis) proves the substrate on a non-workbook deliverable.
- **Q3+:** scale governance — per-skill ownership/versioning/lifecycle, registry automation, PII enforcement, and the enterprise authoring standards (parameterization, localization, regression tagging, reuse library). Only then onboard multiple BUs.

---

## Prioritized Action Plan

### Priority 1 — Must Do (board blockers; do before any production/multi-BU rollout)

1. **Consolidate authoring standards to one-owner-per-concept and delete RTM sections** across SYSTEM_INSTRUCTIONS, QA_METHODOLOGY, TEST_CASE_GENERATION, EXAMPLES. Replace duplicated rules with references.
2. **Fix the placeholder self-contradiction** — make every example in TEST_CASE_GENERATION and QA_METHODOLOGY conform to the authoritative §8.5 characteristic-first rule.
3. **Single-source the validation codes/severities/blacklist** (code authoritative; doc generated/checked; linter fails on divergence). Resolve the "two single authorities" between validator and EXCEL_SPECIFICATION.
4. **Introduce multi-project namespacing + a persistent global ID ledger**; make cross-workbook ID collision a machine check.
5. **Replace self-graded coverage** with a defensible mechanism: either verify AC extraction against the source, or reframe coverage as model-self-review + mandatory sampling audit, and stop advertising enforced "100%".
6. **Bump all version headers, delete `apply_grouping.py`, reconcile the two entry points**, and fix ARCHITECTURE.md's false four-sheet output contract.

### Priority 2 — Should Do (materially raises quality and scale-readiness)

1. **Split the canonical flat machine layer from the merged human view**; implement the flat CSV/Zephyr export the docs already promise; correct Appendix B.
2. **Implement the cheap semantic validators**: near-duplicate detection, environment-independence regex, weak-title detection, priority-distribution sanity, blank-Step# catch.
3. **Ship the shared validator interface + inter-skill interchange schema**, and add `_base/workflow.base.md` to the precedence/ownership matrix.
4. **Reconcile all registries and intents** (SKILLS_REGISTRY v2.5, README coverage-restored, INT-02/INT-03 sync, TraceabilityAnalysis pointing at a deleted §4.7).
5. **Make workflow.md reference `_base` instead of re-copying it** (the copy has already drifted on the Jira/AC acquisition rules).

### Priority 3 — Nice to Have (enterprise polish + future growth)

1. Scaffold generator (`new_skill.py`) + lint rule for incomplete skill folders + registry automation.
2. PII/data-handling validator to make DATA_HANDLING enforceable.
3. Enterprise authoring standards: data-driven/parameterized cases, localization/regional variants, regression tagging, reuse/library.
4. Per-skill governance (owner, version, lifecycle, review/deprecation dates); knowledge namespacing (`Knowledge/skills/<Name>/`) for skill-local truth.
5. Telemetry for the success metrics MASTER_CONTEXT asserts but cannot currently measure.

---

## The architecture I would build from scratch today

Keep the thesis, tighten the execution:

- **One canonical machine model** (a small typed schema for requirement → AC → scenario → test case, in YAML/JSON) as the *actual* single source of truth. Docs and the Excel view are **renderings** of it; the validator checks the model, and the human-readable Markdown standards are generated (or lint-verified) from the same source so they cannot drift.
- **Truth as data, prose as explanation.** Rules that must be enforced (severities, banned phrases, column contract, coverage thresholds) live once, as data, consumed by both code and docs. Markdown explains *why*; it never re-declares the rule.
- **A thin, generic skill runtime** (`_base` FSM + a shared `Report`/severity validator interface + an owned interchange schema) so heterogeneous skills — report producers, matrix producers, workbook producers — all plug in the same way, and one skill's output can feed another's input.
- **Namespaced from day one**: project/BU registry, global ID ledger, per-project capability enablement, per-region data agreements.
- **Excel is an export target, not the working store.** Author flat and canonical; render merged views on demand.

That system delivers the same product this one aims for, but its central claim — no contradictions, provable coverage, safe to scale — would be true by construction rather than by discipline.

*End of review.*
