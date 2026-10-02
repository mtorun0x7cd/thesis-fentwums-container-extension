#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Mert Torun
# SPDX-License-Identifier: MIT
"""Recompute the statistics of every result file from its raw times.

aggregate.py builds the tables of Chapter 6 from the `statistics` and
`comparison` blocks that benchmark.py wrote into each result file during the
run; `make aggregate-check` shows that the committed tables follow from those
blocks. This script closes the remaining step: it recomputes each block from
the per-iteration times stored beside it, with the functions of the committed
benchmark.py (calculate_stats, welch_t_test, cohens_d), and compares. It also
checks that every recorded iteration returned exit code 0.

The results of 2026-06-30 and 2026-07-02 were computed on Python 3.9, 3.11
and 3.12; floating-point results may differ in the last bit between versions,
so values are compared with a relative tolerance of 1e-9.

    check_result_statistics.py              check all result files
    check_result_statistics.py --selftest   prove that a changed time is found

Exit status: 0 every block is reproduced, 1 a block differs, 2 the files could
not be read or no block was found.
"""

import glob
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUITE = ROOT / "evaluation" / "benchmarking_suite"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SUITE))
import benchmark  # noqa: E402  (the measured code itself)

REL = 1e-9


def close(a, b):
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None:
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if math.isnan(a) and math.isnan(b):
            return True
        return a == b or abs(a - b) <= REL * max(abs(a), abs(b))
    return a == b


def differ(recorded, computed, where):
    """The keys of `recorded` whose values `computed` does not reproduce."""
    out = []
    if isinstance(recorded, dict):
        if not isinstance(computed, dict):
            return ["%s: recorded a block, recomputed %r" % (where, computed)]
        for key, value in recorded.items():
            out += differ(value, computed.get(key), "%s.%s" % (where, key))
    elif not close(recorded, computed):
        out.append("%s: recorded %r, recomputed %r" % (where, recorded, computed))
    return out


def check_file(data, name):
    """(number of blocks compared, list of differences) for one result file."""
    results = data.get("results") or {}
    found, blocks = [], 0
    times = {}
    for key, block in results.items():
        if key == "comparison" or not isinstance(block, dict) or not block.get("times"):
            continue
        times[key] = block["times"]
        blocks += 1
        found += differ(block.get("statistics"), benchmark.calculate_stats(block["times"]),
                        "%s %s.statistics" % (name, key))
        bad = [code for code in block.get("return_codes") or [] if code != 0]
        if bad:
            found.append("%s %s: %d iteration(s) with a non-zero exit code" % (name, key, len(bad)))
    for key, entry in (results.get("comparison") or {}).items():
        if key == "cli_vs_dotnet":
            base, other = times.get("docker"), times.get("docker_dotnet")
        elif key.startswith("native_vs_"):
            base, other = times.get("native"), times.get(key[len("native_vs_"):])
        else:
            found.append("%s comparison.%s: unknown comparison" % (name, key))
            continue
        if not base or not other:
            found.append("%s comparison.%s: the raw times it compares are missing" % (name, key))
            continue
        blocks += 1
        ms, mo = benchmark.calculate_stats(base)["mean"], benchmark.calculate_stats(other)["mean"]
        computed = {"welch": benchmark.welch_t_test(base, other), "cohens_d": benchmark.cohens_d(base, other),
                    "relative_overhead_x": round(mo / ms, 4), "absolute_overhead_sec": round(mo - ms, 6)}
        found += differ(entry, computed, "%s comparison.%s" % (name, key))
    return blocks, found


def load():
    files = sorted(glob.glob(str(SUITE / "results" / "*" / "*.json")))
    if not files:
        raise OSError("no result file under %s" % (SUITE / "results"))
    return [(Path(f).relative_to(SUITE / "results").as_posix(), json.loads(Path(f).read_text(encoding="utf-8")))
            for f in files]


def selftest():
    data = load()
    name, first = next((n, d) for n, d in data if (d.get("results") or {}).get("docker"))
    blocks, found = check_file(first, name)
    if found or not blocks:
        print("  [FAIL] selftest: %s is not reproduced to begin with" % name)
        return 1
    changed = json.loads(json.dumps(first))
    changed["results"]["docker"]["times"][0] += 0.001
    _, found = check_file(changed, name)
    print("  [%s] one raw time changed by 1 ms in %s: %s" % ("ok" if found else "FAIL", name,
                                                              "%d difference(s) found" % len(found) if found else "not found"))
    return 0 if found else 1


def main(argv):
    try:
        if len(argv) > 1 and argv[1] == "--selftest":
            return selftest()
        data = load()
    except (OSError, ValueError) as exc:
        print("  [ERR]  %s; nothing was compared" % exc, file=sys.stderr)
        return 2
    total, found = 0, []
    for name, content in data:
        blocks, diffs = check_file(content, name)
        total += blocks
        found += diffs
    if not total:
        print("  [ERR]  no statistics block was found; nothing was compared", file=sys.stderr)
        return 2
    for line in found:
        print("  [DIFF] %s" % line)
    if found:
        print("  [FAIL] %d difference(s) in %d block(s) of %d result file(s)" % (len(found), total, len(data)))
        return 1
    print("  [OK]   %d statistics and comparison blocks of %d result files are reproduced from their raw times"
          % (total, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
