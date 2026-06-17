#!/usr/bin/env python3
"""Grade TDD skill eval output from snapshot data.

Usage:
  grade.py <outputs_dir>      # grade single eval → outputs_dir/grading.json
  grade.py <iteration_dir>    # grade all evals → per-eval grading.json + iteration_dir/benchmark.json
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


RED_FAIL_PATTERN = re.compile(
    r'FAIL|--- FAIL|build failed|undefined:|cannot use|syntax error|no non-test Go files',
    re.IGNORECASE
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except FileNotFoundError:
        return ""


def parse_history(snapshots_dir: Path) -> list[dict]:
    """Parse history.log into a list of {phase, cycle} dicts."""
    entries = []
    for line in read_text(snapshots_dir / "history.log").splitlines():
        m = re.search(r'PHASE=(\w+)\s+CYCLE=(\d+)', line)
        if m:
            entries.append({'phase': m.group(1), 'cycle': int(m.group(2))})
    return entries


def collect_snap_dirs(snapshots_dir: Path) -> dict[int, dict[str, Path]]:
    """Map cycle number → {phase → snapshot dir}."""
    result: dict[int, dict[str, Path]] = {}
    if not snapshots_dir.exists():
        return result
    for d in sorted(snapshots_dir.iterdir()):
        if not d.is_dir():
            continue
        m = re.match(r'cycle-(\d+)-(red|green|refactor)$', d.name)
        if m:
            cycle, phase = int(m.group(1)), m.group(2)
            result.setdefault(cycle, {})[phase] = d
    return result


def extract_added_test_funcs(diff_text: str) -> list[str]:
    """Extract function names added in a diff (+func TestXxx)."""
    return re.findall(r'^\+func (Test\w+)\(', diff_text, re.MULTILINE)


def git_refactor_noops(repo_dir: Path) -> tuple[int, int]:
    """Return (noop_count, total_refactor_count) by inspecting repo git log."""
    if not repo_dir.exists():
        return 0, 0
    result = subprocess.run(
        ['git', 'log', '--format=%H %s'],
        cwd=repo_dir, capture_output=True, text=True
    )
    noop, total = 0, 0
    for line in result.stdout.splitlines():
        parts = line.split(' ', 1)
        if len(parts) == 2 and 'refactor:' in parts[1]:
            total += 1
            commit_hash = parts[0]
            diff_result = subprocess.run(
                ['git', 'diff', '--name-only', f'{commit_hash}~1', commit_hash, '--', '*.go'],
                cwd=repo_dir, capture_output=True, text=True
            )
            if not diff_result.stdout.strip():
                noop += 1
    return noop, total


def grade_eval(outputs_dir: Path) -> dict:
    snapshots_dir = outputs_dir / "snapshots"
    repo_dir = outputs_dir / "repo"
    timing_path = outputs_dir / "timing.json"
    if not timing_path.exists():
        timing_path = outputs_dir.parent / "timing.json"

    snap_dirs = collect_snap_dirs(snapshots_dir)
    history = parse_history(snapshots_dir)

    # P11: red_authenticity_rate
    red_snaps = [(c, snap_dirs[c]['red']) for c in sorted(snap_dirs) if 'red' in snap_dirs[c]]
    red_authentic = sum(
        1 for _, snap in red_snaps
        if RED_FAIL_PATTERN.search(read_text(snap / "test_output.txt"))
    )
    red_total = len(red_snaps)
    red_authenticity_rate = red_authentic / red_total if red_total else None

    # P1: phase_write_order_rate
    # GREEN and REFACTOR snapshots should have .go changes in git_diff (not just .tdd/PHASE)
    gr_snaps = [
        (c, phase, snap_dirs[c][phase])
        for c in sorted(snap_dirs)
        for phase in ('green', 'refactor')
        if phase in snap_dirs[c]
    ]
    phase_order_pass = sum(
        1 for _, _, snap in gr_snaps
        if re.search(r'^diff --git a/(?!\.tdd/).*\.go', read_text(snap / "git_diff.txt"), re.MULTILINE)
    )
    phase_order_total = len(gr_snaps)
    phase_write_order_rate = phase_order_pass / phase_order_total if phase_order_total else None

    # P4: red_preceded_green_rate
    green_preceded = 0
    green_hist_total = 0
    for i, entry in enumerate(history):
        if entry['phase'] != 'green':
            continue
        green_hist_total += 1
        cycle = entry['cycle']
        for j in range(i - 1, -1, -1):
            if history[j]['cycle'] == cycle:
                if history[j]['phase'] == 'red':
                    green_preceded += 1
                break
    red_preceded_green_rate = green_preceded / green_hist_total if green_hist_total else None

    # P3: green_phase_purity
    green_snaps = [(c, snap_dirs[c]['green']) for c in sorted(snap_dirs) if 'green' in snap_dirs[c]]
    green_pure = sum(
        1 for _, snap in green_snaps
        if not re.search(r'^diff --git a/.*_test\.go', read_text(snap / "git_diff.txt"), re.MULTILINE)
    )
    green_total = len(green_snaps)
    green_phase_purity = green_pure / green_total if green_total else None

    # P2: refactor_noop_rate
    refactor_noop, refactor_total = git_refactor_noops(repo_dir)
    refactor_noop_rate = refactor_noop / refactor_total if refactor_total else None

    # P7: test_first_rate
    # Track which test functions first appeared in a RED snapshot (with failure)
    test_funcs_first_red: set[str] = set()
    for _, snap in red_snaps:
        diff = read_text(snap / "git_diff.txt")
        added_funcs = extract_added_test_funcs(diff)
        if added_funcs and RED_FAIL_PATTERN.search(read_text(snap / "test_output.txt")):
            test_funcs_first_red.update(added_funcs)

    # Collect all test functions from final test files
    all_test_funcs: set[str] = set()
    for f in outputs_dir.glob("*_test.go"):
        for m in re.finditer(r'^func (Test\w+)\(', read_text(f), re.MULTILINE):
            all_test_funcs.add(m.group(1))
    # Also check repo working tree
    if repo_dir.exists():
        for f in repo_dir.glob("*_test.go"):
            for m in re.finditer(r'^func (Test\w+)\(', read_text(f), re.MULTILINE):
                all_test_funcs.add(m.group(1))

    test_first_total = len(all_test_funcs)
    test_first_pass = len(all_test_funcs & test_funcs_first_red)
    test_first_rate = test_first_pass / test_first_total if test_first_total else None

    # Tier 3: efficiency
    tokens_per_cycle = tool_calls_per_cycle = None
    total_cycles = len(snap_dirs)
    if timing_path.exists() and total_cycles > 0:
        timing = json.loads(timing_path.read_text())
        if timing.get('subagent_tokens'):
            tokens_per_cycle = round(timing['subagent_tokens'] / total_cycles, 1)
        if timing.get('tool_uses'):
            tool_calls_per_cycle = round(timing['tool_uses'] / total_cycles, 1)

    def pct(v):
        return round(v * 100, 1) if v is not None else None

    return {
        "tier1": {
            "red_authenticity_rate": pct(red_authenticity_rate),
            "phase_write_order_rate": pct(phase_write_order_rate),
            "red_preceded_green_rate": pct(red_preceded_green_rate),
            "green_phase_purity": pct(green_phase_purity),
            "refactor_noop_rate": pct(refactor_noop_rate),
            "test_first_rate": pct(test_first_rate),
        },
        "tier3": {
            "tokens_per_cycle": tokens_per_cycle,
            "tool_calls_per_cycle": tool_calls_per_cycle,
        },
        "detail": {
            "total_cycles": total_cycles,
            "red_authentic": red_authentic,
            "red_total": red_total,
            "phase_order_pass": phase_order_pass,
            "phase_order_total": phase_order_total,
            "green_preceded": green_preceded,
            "green_hist_total": green_hist_total,
            "green_pure": green_pure,
            "green_total": green_total,
            "refactor_noop": refactor_noop,
            "refactor_total": refactor_total,
            "test_first_pass": test_first_pass,
            "test_first_total": test_first_total,
        },
    }


def aggregate(grades: dict[str, dict]) -> dict:
    """Average Tier 1 metrics across all evals (simple average, None skipped)."""
    tier1_keys = [
        "red_authenticity_rate",
        "phase_write_order_rate",
        "red_preceded_green_rate",
        "green_phase_purity",
        "refactor_noop_rate",
        "test_first_rate",
    ]
    averages = {}
    for key in tier1_keys:
        values = [g["tier1"][key] for g in grades.values() if g["tier1"].get(key) is not None]
        averages[key] = round(sum(values) / len(values), 1) if values else None

    return {
        "tier1_average": averages,
        "evals": grades,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)

    # Detect mode: outputs_dir has snapshots/, iteration_dir has subdirs with outputs/
    if (target / "snapshots").exists():
        # Single eval mode
        result = grade_eval(target)
        out_path = target / "grading.json"
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"Wrote {out_path}")
        print(json.dumps(result["tier1"], indent=2, ensure_ascii=False))
    else:
        # Iteration mode: find all eval subdirs with outputs/snapshots/
        grades = {}
        for eval_dir in sorted(target.iterdir()):
            outputs_dir = eval_dir / "outputs"
            if not (outputs_dir / "snapshots").exists():
                continue
            print(f"Grading {eval_dir.name}...")
            result = grade_eval(outputs_dir)
            grading_path = outputs_dir / "grading.json"
            grading_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            grades[eval_dir.name] = result

        if not grades:
            print("No eval directories found with snapshots/", file=sys.stderr)
            sys.exit(1)

        benchmark = aggregate(grades)
        bench_path = target / "benchmark.json"
        bench_path.write_text(json.dumps(benchmark, indent=2, ensure_ascii=False))
        print(f"\nWrote {bench_path}")
        print("\nTier 1 averages:")
        print(json.dumps(benchmark["tier1_average"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
