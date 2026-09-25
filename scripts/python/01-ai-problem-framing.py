#!/usr/bin/env python3
"""AI-001: evaluate fixed keyword rules on fictional policies and synthetic cases.

No trained model, hosted service, random process, or real learner data is used.
Run with the repository's .venv interpreter. Outputs are repository-relative.
"""
from pathlib import Path
import csv
import hashlib
import json
import platform
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/reference"
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "results/figures"
FAMILIES = ["Direct", "Paraphrase", "Multi-topic", "Outside scope"]


def route_question(question, policies):
    """Return one policy only for a unique whole-word keyword match."""
    tokens = set(re.findall(r"[a-z]+", question.lower()))
    matches = [pid for pid, policy in policies.items()
               if tokens.intersection(policy["keywords"])]
    if len(matches) == 1:
        pid = matches[0]
        return pid, "one_match", policies[pid]["passage"]
    return "REVIEW", "no_match" if not matches else "multiple_matches", ""


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(name, rows):
    total = len(rows)
    correct = sum(r["correct"] for r in rows)
    automatic = sum(r["actual_route"] != "REVIEW" for r in rows)
    wrong = sum(r["wrong_automatic"] for r in rows)
    review = total - automatic
    unnecessary = sum(r["unnecessary_review"] for r in rows)
    return dict(family=name, total=total, correct=correct, automatic=automatic,
                wrong_automatic=wrong, review=review, unnecessary_review=unnecessary,
                correct_rate=correct / total if total else "NA", review_rate=review / total if total else "NA",
                wrong_automatic_rate=wrong / automatic if automatic else "NA")


def plot_results(summary):
    groups = summary[1:]
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    fig.subplots_adjust(left=0.17, right=0.96, top=0.78, bottom=0.22)
    series = [("correct", "Correct route (including valid review)", "#247A78"),
              ("unnecessary_review", "Unnecessary review", "#E5AC43"),
              ("wrong_automatic", "Wrong automatic route", "#BC4B51")]
    left = [0] * len(groups)
    for field, label, color in series:
        values = [g[field] for g in groups]
        ax.barh(FAMILIES, values, left=left, label=label, color=color,
                edgecolor="white", height=0.6)
        for i, value in enumerate(values):
            if value:
                ax.text(left[i] + value / 2, i, str(value), ha="center", va="center",
                        color="#132A36" if field == "unnecessary_review" else "white",
                        weight="bold", fontsize=12)
        left = [a + b for a, b in zip(left, values)]
    ax.invert_yaxis()
    max_count = max(g["total"] for g in groups)
    ax.set_xlim(0, max(1, max_count))
    ax.set_xticks(range(max_count + 1))
    ax.set_xlabel("Number of synthetic questions", labelpad=10)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False, ncol=1,
              fontsize=9)
    fig.text(0.06, 0.94, "A single score hides different failures", fontsize=19,
             weight="bold", color="#183A4A")
    fig.text(0.06, 0.875, f"Keyword-routing baseline • {summary[0]['total']} constructed cases • No AI model run",
             fontsize=11, color="#52636D")
    fig.savefig(FIGURES / "01-baseline-routing-results.png", dpi=180, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def plot_workflow():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.04, top=0.98)
    ax.text(0.25, 5.5, "Define the task and the boundary", fontsize=22,
            weight="bold", color="#183A4A")
    ax.text(0.25, 5.0, "Course-policy lookup • A passage or a review flag • Staff retain authority",
            fontsize=12, color="#52636D")
    boxes = [(0.3, 3.15, "1  Staff question", "One registration\nquestion at a time"),
             (4.35, 3.15, "2  Approved policies", "Four fictional passages\nNo personal records"),
             (8.4, 3.15, "3  Keyword routing", "One match: passage\nZero or many: review"),
             (8.4, 0.85, "4  Inspectable output", "Policy ID + passage\nor REVIEW status"),
             (4.35, 0.85, "5  Administrator check", "Check scope and support\nResolve or escalate"),
             (0.3, 0.85, "6  Staff response", "Human prepares response\nNo automatic sending")]
    for x, y, title, body in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 3.25, 1.35,
                     boxstyle="round,pad=0.08,rounding_size=0.1",
                     facecolor="#EDF5F5" if x != 4.35 or y != 0.85 else "#FFF2D8",
                     edgecolor="#93B1BA", linewidth=1.2))
        ax.text(x + 0.16, y + 0.95, title, fontsize=11.5, weight="bold", color="#183A4A")
        ax.text(x + 0.16, y + 0.43, body, fontsize=10.5, va="center", linespacing=1.5,
                color="#344B57")
    for start, end in [((3.65, 3.83), (4.22, 3.83)), ((7.7, 3.83), (8.27, 3.83)),
                       ((10.0, 3.02), (10.0, 2.32)), ((8.27, 1.53), (7.72, 1.53)),
                       ((4.22, 1.53), (3.67, 1.53))]:
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", color="#52636D", lw=1.8))
    ax.text(0.25, 0.2, "Knowledge boundary: approved collection only. Unsupported questions require review.",
            fontsize=11, color="#52636D")
    fig.savefig(FIGURES / "01-ai-task-workflow.png", dpi=180, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def main():
    policy_path = DATA / "01-course-policies.json"
    cases_path = DATA / "01-framing-cases.csv"
    policies = json.loads(policy_path.read_text(encoding="utf-8"))
    with cases_path.open(newline="", encoding="utf-8") as handle:
        cases = list(csv.DictReader(handle))
    if not cases or len({r["case_id"] for r in cases}) != len(cases):
        raise ValueError("Cases must be nonempty and have unique identifiers.")
    rows = []
    for case in cases:
        if case["expected_route"] not in {*policies, "REVIEW"}:
            raise ValueError(f"Unknown expected route: {case['case_id']}")
        if case["family"] not in FAMILIES:
            raise ValueError(f"Unknown family: {case['family']}")
        actual, status, passage = route_question(case["question"], policies)
        correct = actual == case["expected_route"]
        rows.append({**case, "actual_route": actual, "status": status, "passage": passage,
                     "correct": correct, "wrong_automatic": not correct and actual != "REVIEW",
                     "unnecessary_review": not correct and actual == "REVIEW"})
    summary = [summarize("Overall", rows)] + [
        summarize(f, [r for r in rows if r["family"] == f]) for f in FAMILIES]
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    write_csv(TABLES / "01-routing-results.csv", rows)
    write_csv(TABLES / "01-routing-summary.csv", summary)
    plot_workflow()
    plot_results(summary)
    inputs = [policy_path, cases_path, Path(__file__).resolve()]
    metadata = {"chapter": "AI-001", "data": "fictional policies and synthetic questions",
                "method": "deterministic whole-word keyword routing; no trained model",
                "python_version": platform.python_version(), "matplotlib_version": matplotlib.__version__,
                "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in inputs}}
    (TABLES / "01-run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    total = summary[0]
    print(f"Correct routes: {total['correct']}/{total['total']}")
    print(f"Wrong automatic routes: {total['wrong_automatic']}/{total['automatic']}")
    print(f"Review cases: {total['review']}/{total['total']}")
    for folder in (TABLES, FIGURES):
        for path in sorted(folder.glob("01-*")):
            print(f"Saved {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
