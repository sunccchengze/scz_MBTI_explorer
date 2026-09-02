#!/usr/bin/env python3
"""Create and audit local MBTI evidence cases without pretending to score a test.

This utility manages structure only. It does not infer a type, assign function
percentages, or replace a validated psychometric instrument.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
TYPES = {
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ",
}
STATES = {"normal", "stress", "recovery", "relationship", "public-role", "unknown"}
STRENGTHS = {"weak", "medium", "strong"}
CONFIDENCE = {None, "low", "medium", "medium-high", "high"}


def parse_candidates(raw: str) -> list[str]:
    candidates = [item.strip().upper() for item in raw.split(",") if item.strip()]
    invalid = [item for item in candidates if item not in TYPES]
    if invalid:
        raise ValueError(f"invalid MBTI type(s): {', '.join(invalid)}")
    if len(candidates) != len(set(candidates)):
        raise ValueError("candidate types must be unique")
    if not 2 <= len(candidates) <= 6:
        raise ValueError("provide 2-6 candidate types")
    return candidates


def new_case(target: str, question: str, candidates: list[str], consent: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "target": target,
        "question": question,
        "consent_scope": consent,
        "candidates": [
            {"type": candidate, "status": "active", "notes": ""}
            for candidate in candidates
        ],
        "evidence": [],
        "corrections": [],
        "falsifiers": [],
        "conclusion": {
            "leading_type": None,
            "runner_up": None,
            "confidence": None,
            "summary": "",
        },
    }


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def string_list(value: Any, field: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return []
    return value


def validate_case(case: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(case, dict):
        return ["case root must be a JSON object"], warnings

    if case.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    for field in ("target", "question"):
        if not isinstance(case.get(field), str) or not case[field].strip():
            errors.append(f"{field} must be a non-empty string")

    consent = case.get("consent_scope")
    if consent not in {"self", "authorized-third-party", "unknown"}:
        errors.append("consent_scope must be self, authorized-third-party, or unknown")
    elif consent == "unknown":
        warnings.append("consent_scope is unknown; minimize third-party private material")

    raw_candidates = case.get("candidates")
    candidate_types: list[str] = []
    if not isinstance(raw_candidates, list) or not 2 <= len(raw_candidates) <= 6:
        errors.append("candidates must contain 2-6 objects")
    else:
        for index, candidate in enumerate(raw_candidates):
            prefix = f"candidates[{index}]"
            if not isinstance(candidate, dict):
                errors.append(f"{prefix} must be an object")
                continue
            mbti_type = candidate.get("type")
            if mbti_type not in TYPES:
                errors.append(f"{prefix}.type is invalid: {mbti_type!r}")
            else:
                candidate_types.append(mbti_type)
            if candidate.get("status") not in {"active", "ruled-out"}:
                errors.append(f"{prefix}.status must be active or ruled-out")
        if len(candidate_types) != len(set(candidate_types)):
            errors.append("candidate types must be unique")

    evidence = case.get("evidence")
    evidence_ids: set[str] = set()
    contexts: set[str] = set()
    has_contradiction = False
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
        evidence = []
    for index, item in enumerate(evidence):
        prefix = f"evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif evidence_id in evidence_ids:
            errors.append(f"duplicate evidence id: {evidence_id}")
        else:
            evidence_ids.add(evidence_id)
        for field in ("observation", "source", "context"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{prefix}.{field} must be a non-empty string")
        if isinstance(item.get("context"), str) and item["context"].strip():
            contexts.add(item["context"].strip())
        if item.get("state") not in STATES:
            errors.append(f"{prefix}.state must be one of {sorted(STATES)}")
        if item.get("strength") not in STRENGTHS:
            errors.append(f"{prefix}.strength must be one of {sorted(STRENGTHS)}")
        supports = string_list(item.get("supports"), f"{prefix}.supports", errors)
        contradicts = string_list(item.get("contradicts"), f"{prefix}.contradicts", errors)
        string_list(item.get("alternative_explanations"), f"{prefix}.alternative_explanations", errors)
        for field, values in (("supports", supports), ("contradicts", contradicts)):
            unknown = sorted(set(values) - set(candidate_types))
            if unknown:
                errors.append(f"{prefix}.{field} references unknown candidates: {', '.join(unknown)}")
        overlap = sorted(set(supports) & set(contradicts))
        if overlap:
            errors.append(f"{prefix} both supports and contradicts: {', '.join(overlap)}")
        has_contradiction = has_contradiction or bool(contradicts)

    for field in ("corrections", "falsifiers"):
        string_list(case.get(field), field, errors)

    conclusion = case.get("conclusion")
    if not isinstance(conclusion, dict):
        errors.append("conclusion must be an object")
    else:
        leading = conclusion.get("leading_type")
        runner_up = conclusion.get("runner_up")
        confidence = conclusion.get("confidence")
        for field, value in (("leading_type", leading), ("runner_up", runner_up)):
            if value is not None and value not in candidate_types:
                errors.append(f"conclusion.{field} must be null or an existing candidate")
        if leading is not None and leading == runner_up:
            errors.append("leading_type and runner_up must differ")
        if confidence not in CONFIDENCE:
            errors.append("conclusion.confidence must be null, low, medium, medium-high, or high")
        if leading and not runner_up:
            warnings.append("a serious conclusion should retain a runner-up")
        if confidence in {"medium-high", "high"}:
            if len(evidence) < 4:
                warnings.append("medium-high/high confidence has fewer than 4 evidence entries")
            if len(contexts) < 2:
                warnings.append("medium-high/high confidence lacks evidence from 2 contexts")
            if not has_contradiction:
                warnings.append("medium-high/high confidence has no recorded contradictory evidence")
            if not case.get("falsifiers"):
                warnings.append("medium-high/high confidence has no falsifier")

    if not evidence:
        warnings.append("case has no evidence yet")
    return errors, warnings


REPORT_SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("working hypothesis", ("工作假设", "最佳类型", "best-supported", "working hypothesis")),
    ("runner-up", ("第二名", "备选", "runner-up", "alternative type")),
    ("evidence", ("证据", "evidence")),
    ("differential", ("关键对决", "为何不是", "differential", "why not")),
    ("uncertainty/falsifier", ("不确定", "反证", "falsif", "uncertainty")),
    ("boundary", ("非临床", "不是临床", "not clinical", "not a clinical")),
)

OVERCLAIM_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"(?:100\s*%|百分之百).{0,8}(?:确定|准确|肯定|certainty|accurate)", "absolute certainty claim"),
    (r"(?:科学证明|scientifically proven).{0,12}(?:你是|type|mbti)", "scientific-proof claim"),
    (r"(?:永远|必然|一定会|never|always).{0,16}(?:因为|because|型|type)", "deterministic type claim"),
    (r"\b(?:Ni|Ne|Si|Se|Ti|Te|Fi|Fe)\s*[:：=]?\s*\d{1,3}\s*%", "unqualified function percentage"),
)


def audit_report(text: str) -> list[str]:
    findings: list[str] = []
    lowered = text.lower()
    for section, markers in REPORT_SECTIONS:
        if not any(marker.lower() in lowered for marker in markers):
            findings.append(f"missing section or concept: {section}")
    for pattern, label in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            findings.append(f"overclaim risk: {label}")
    if re.search(r"\b(?:INTJ|INTP|ENTJ|ENTP|INFJ|INFP|ENFJ|ENFP|ISTJ|ISTP|ESTJ|ESTP|ISFJ|ISFP|ESFJ|ESFP)-(?:A|T)\b", text) and not re.search(
        r"(?:16Personalities|非官方|不是官方|not official)", text, re.IGNORECASE
    ):
        findings.append("A/T suffix appears without a 16Personalities/non-official caveat")
    return findings


def command_init(args: argparse.Namespace) -> int:
    try:
        candidates = parse_candidates(args.candidates)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    case = new_case(args.target, args.question, candidates, args.consent)
    payload = json.dumps(case, ensure_ascii=False, indent=2) + "\n"
    if args.output == "-":
        sys.stdout.write(payload)
    else:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(f"created {output}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    try:
        case = load_json(Path(args.path))
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    errors, warnings = validate_case(case)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    print("MBTI case validation passed")
    return 0


def command_audit_report(args: argparse.Namespace) -> int:
    try:
        text = Path(args.path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.path}")
        return 2
    findings = audit_report(text)
    for finding in findings:
        print(f"FINDING: {finding}")
    if not findings:
        print("MBTI report audit passed")
    return 1 if args.strict and findings else 0


def command_self_test(_: argparse.Namespace) -> int:
    case = new_case("demo", "ENTJ or INTJ?", ["ENTJ", "INTJ", "ESTJ"], "self")
    errors, warnings = validate_case(case)
    if errors or "case has no evidence yet" not in warnings:
        print(f"ERROR: initial-case self-test failed: errors={errors}, warnings={warnings}")
        return 1
    case["evidence"] = [
        {
            "id": "E01",
            "observation": "Coordinates people even without a formal role",
            "source": "self report",
            "context": "volunteer project",
            "state": "normal",
            "supports": ["ENTJ"],
            "contradicts": ["INTJ"],
            "alternative_explanations": ["learned leadership"],
            "strength": "medium",
            "next_question": "What happens to energy after coordination?",
        }
    ]
    errors, _ = validate_case(case)
    if errors:
        print(f"ERROR: populated-case self-test failed: {errors}")
        return 1
    good_report = "工作假设\n第二名\n证据\n关键对决\n不确定与反证\n这不是临床诊断"
    if audit_report(good_report):
        print(f"ERROR: report self-test failed: {audit_report(good_report)}")
        return 1
    print("mbti_case self-test passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Structure and audit evidence-led MBTI cases; does not score personality."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="create an empty evidence case")
    init.add_argument("--target", required=True, help="subject label; use a non-identifying label when possible")
    init.add_argument("--question", required=True, help="typing question or disputed pair")
    init.add_argument("--candidates", required=True, help="comma-separated list of 2-6 MBTI types")
    init.add_argument(
        "--consent",
        choices=("self", "authorized-third-party", "unknown"),
        default="unknown",
    )
    init.add_argument("--output", default="-", help="output JSON path, or - for stdout")
    init.set_defaults(func=command_init)

    validate = subparsers.add_parser("validate", help="validate a case JSON file")
    validate.add_argument("path")
    validate.add_argument("--strict", action="store_true", help="treat warnings as failures")
    validate.set_defaults(func=command_validate)

    audit = subparsers.add_parser("audit-report", help="audit an MBTI report for missing safeguards")
    audit.add_argument("path")
    audit.add_argument("--strict", action="store_true", help="fail when findings are present")
    audit.set_defaults(func=command_audit_report)

    self_test = subparsers.add_parser("self-test", help="run dependency-free internal checks")
    self_test.set_defaults(func=command_self_test)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
