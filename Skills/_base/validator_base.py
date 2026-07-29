#!/usr/bin/env python3
"""
Shared validator substrate for PS-TestAuthoring skills.
=======================================================

Any skill's machine validator builds on this so that EVERY skill — whether it emits a
workbook, a report, a matrix, or a JSON payload — exposes the same finding model, severity
taxonomy, and exit-code contract. This is the extensibility contract the roadmap skills
(RiskAssessment, TraceabilityAnalysis, DefectAnalysis, …) plug into: import `Report` and
`run_cli`, declare a RULES catalog, and write only the skill-specific checks.

Severity model (highest to lowest):
    FATAL     -> artifact is invalid, must not be delivered
    BLOCKING  -> must be fixed before delivery
    WARNING   -> advisory; does not block

Exit codes (via run_cli):
    0 = PASS (no FATAL/BLOCKING)   1 = FAIL   2 = usage / no artifact given

`Skills/TestCaseAuthoring/validate_workbook.py` is the reference implementation.
"""
import sys, json

SEVERITIES = ("FATAL", "BLOCKING", "WARNING")


class Report:
    """Collects findings for one artifact. `failed` is True on any FATAL or BLOCKING finding."""
    def __init__(self, path):
        self.path = path
        self.findings = []  # list of (severity, code, message)

    def add(self, severity, code, message):
        if severity not in SEVERITIES:
            raise ValueError(f"unknown severity {severity!r} (expected one of {SEVERITIES})")
        self.findings.append((severity, code, message))

    def fatal(self, code, msg):    self.add("FATAL", code, msg)
    def blocking(self, code, msg): self.add("BLOCKING", code, msg)
    def warn(self, code, msg):     self.add("WARNING", code, msg)

    @property
    def failed(self):
        return any(s in ("FATAL", "BLOCKING") for s, _, _ in self.findings)

    def counts(self):
        c = {s: 0 for s in SEVERITIES}
        for s, _, _ in self.findings:
            c[s] += 1
        return c


def print_report(rep):
    c = rep.counts()
    status = "FAIL" if rep.failed else "PASS"
    print(f"\n{'='*70}\n{status}  {rep.path}")
    print(f"  Fatal={c['FATAL']}  Blocking={c['BLOCKING']}  Warning={c['WARNING']}")
    for sev in SEVERITIES:
        for s, code, msg in rep.findings:
            if s == sev:
                print(f"  [{s:8}] {code}: {msg}")
    if not rep.findings:
        print("  No findings.")


def emit_rules_markdown(rules):
    """Render a skill's RULES catalog (list of (code, severity, description)) as a Markdown table."""
    out = ["| Code | Severity | Check |", "|------|----------|-------|"]
    out += [f"| {code} | {sev} | {desc} |" for code, sev, desc in rules]
    return "\n".join(out)


def run_cli(validate_fn, argv, doc=""):
    """Generic validator CLI shared by every skill: `<artifact> [...] [--json]`.
    `validate_fn(path)` must return a Report. Returns the process exit code."""
    as_json = "--json" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        sys.stderr.write(doc or "usage: <validator> <artifact> [...] [--json]\n")
        return 2
    reports = [validate_fn(p) for p in args]
    if as_json:
        print(json.dumps(
            [{"path": r.path, "status": "FAIL" if r.failed else "PASS", "counts": r.counts(),
              "findings": [{"severity": s, "code": c, "message": m} for s, c, m in r.findings]}
             for r in reports], indent=2))
    else:
        for r in reports:
            print_report(r)
    return 1 if any(r.failed for r in reports) else 0
