#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Mert Torun
# SPDX-License-Identifier: MIT
"""Compare the text of a thesis build with the text of the deposited file.

The sources in thesis/ reproduce the text of the deposited PDF, not its bytes:
the deposited file was typeset on 2026-07-02 and afterwards linearised, with its
metadata rewritten, by a step that is not part of this repository. This script
checks the text claim.

Method. Both files are read with `pdftotext -layout` (poppler). The output is
split into pages at the form feeds; each page is normalised to Unicode NFKC,
soft hyphens are dropped, and the page is split into tokens at white space. The
two files must have the same number of pages, and every page must hold the same
multiset of tokens in both files. NFKC folds typographic ligatures and
mathematical alphanumerics (U+1D6FC to U+03B1) the way a reader sees them; it
keeps hyphen, en dash and em dash apart, so a dash of another length counts as
a difference. Comparing per page and as a multiset makes the result independent
of the order in which a PDF draws its text, which differs between builds in
tables, while a word that moves to another page still counts.

Differences listed in an allowlist (--allow) are accepted. Each line of it reads
`<page> <tab> -|+ <tab> <token> <tab> <reason>`: `-` for a token only in the
deposited file, `+` for one only in the build. The allowlist is empty for the
record tag epub-3597; after the tag the text of the thesis changes only through
ERRATA.md, and any change to the sources would need its entry here.

    compare_pdf_text.py BUILD.pdf [DEPOSITED.pdf] [--allow FILE]
    compare_pdf_text.py --selftest

Exit status: 0 the texts are equal, 1 they differ, 2 the comparison could not
be made (pdftotext missing, unreadable file, malformed allowlist).
"""

import argparse
import collections
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

DEPOSITED = Path(__file__).resolve().parent.parent / "publication" / "Torun_Containerized_Execution_OneWare.pdf"


class ToolError(Exception):
    """The comparison could not be made."""


def pages_of(pdf):
    """The text of each page of `pdf`, as pdftotext -layout writes it."""
    if shutil.which("pdftotext") is None:
        raise ToolError("pdftotext is not installed (poppler-utils)")
    if not Path(pdf).is_file():
        raise ToolError("%s is not a file" % pdf)
    result = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
                            capture_output=True, check=False)
    if result.returncode != 0:
        raise ToolError("pdftotext failed on %s: %s" % (pdf, result.stderr.decode("utf-8", "replace").strip()))
    pages = result.stdout.decode("utf-8").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def tokens(text):
    """The tokens of one page after normalisation."""
    return unicodedata.normalize("NFKC", text).replace("­", "").split()


def read_allowlist(path):
    """The accepted differences: (page, sign, token) mapped to their count."""
    allowed = collections.Counter()
    if path is None:
        return allowed
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ToolError("cannot read the allowlist %s: %s" % (path, exc))
    for number, line in enumerate(lines, 1):
        if not line.strip() or line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) != 4 or cells[1] not in ("-", "+") or not cells[0].isdigit() or not cells[3].strip():
            raise ToolError("allowlist line %d is not <page> TAB -|+ TAB <token> TAB <reason>" % number)
        allowed[(int(cells[0]), cells[1], cells[2])] += 1
    return allowed


def compare(deposited_pages, build_pages, allowed):
    """The differences that the allowlist does not accept, as readable lines."""
    found = []
    if len(deposited_pages) != len(build_pages):
        found.append("page count: deposited %d, build %d" % (len(deposited_pages), len(build_pages)))
    remaining = collections.Counter(allowed)
    for number, (dep, build) in enumerate(zip(deposited_pages, build_pages), 1):
        dep_tokens, build_tokens = collections.Counter(tokens(dep)), collections.Counter(tokens(build))
        for sign, side in (("-", dep_tokens - build_tokens), ("+", build_tokens - dep_tokens)):
            for token, count in sorted(side.items()):
                for _ in range(count):
                    key = (number, sign, token)
                    if remaining[key] > 0:
                        remaining[key] -= 1
                        continue
                    where = "only in the deposited file" if sign == "-" else "only in the build"
                    found.append("PDF page %d: %r %s" % (number, token, where))
    for (number, sign, token), count in sorted(remaining.items()):
        if count > 0:
            found.append("allowlist entry not used: page %d %s %r" % (number, sign, token))
    return found


def selftest():
    """The comparison must find a hyphen made an en dash, a word added, a word
    moved to another page and a missing page, and must accept a reordered page,
    a ligature and a listed difference."""
    base = ["Machine 1 (macOS Host - Apple Silicon):", "up to a 3-5x write IOPS increase, efficient"]
    cases = [
        ("identical pages", base, [], True),
        ("tokens in another order on one page", ["Apple Silicon): Machine 1 (macOS Host -", base[1]], [], True),
        ("an ffi ligature (U+FB03) against three letters",
         [base[0], "up to a 3-5x write IOPS increase, e\ufb03cient"], [], True),
        ("a hyphen made an en dash", ["Machine 1 (macOS Host \u2013 Apple Silicon):", base[1]], [], False),
        ("3-5x made 3\u20135x", [base[0], "up to a 3\u20135x write IOPS increase, efficient"], [], False),
        ("a word added", [base[0], base[1] + " three"], [], False),
        ("a word moved to the next page", ["Machine 1 (macOS Host - Apple", "Silicon): " + base[1]], [], False),
        ("a page missing", [base[0]], [], False),
        ("a listed difference", [base[0], base[1] + " three"], [(2, "+", "three")], True),
        ("a listed difference that does not occur", base, [(2, "+", "three")], False),
    ]
    failures = 0
    for name, build, allow, should_hold in cases:
        found = compare(base, build, collections.Counter(allow))
        held = not found
        ok = held == should_hold
        failures += not ok
        print("  [%s] %s: %s" % ("ok" if ok else "FAIL", name, "equal" if held else "; ".join(found)))
    if failures:
        print("  [FAIL] selftest: %d of %d case(s) did not turn out as expected" % (failures, len(cases)))
        return 1
    print("  [OK]   selftest: %d cases" % len(cases))
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description="Compare the text of a thesis build with the deposited PDF.")
    parser.add_argument("build", nargs="?", help="the PDF built from thesis/")
    parser.add_argument("deposited", nargs="?", default=str(DEPOSITED), help="the deposited PDF")
    parser.add_argument("--allow", help="accepted differences, see the module documentation")
    parser.add_argument("--selftest", action="store_true", help="prove that the comparison finds what it is for")
    args = parser.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if not args.build:
        parser.error("the build PDF is required")
    try:
        deposited, build = pages_of(args.deposited), pages_of(args.build)
        allowed = read_allowlist(args.allow)
    except ToolError as exc:
        print("  [ERR]  %s; nothing was compared" % exc, file=sys.stderr)
        return 2
    found = compare(deposited, build, allowed)
    words = sum(len(tokens(page)) for page in deposited)
    if found:
        for line in found:
            print("  [DIFF] %s" % line)
        print("  [FAIL] the build differs from the deposited text in %d place(s) over %d page(s)"
              % (len(found), len(deposited)))
        return 1
    print("  [OK]   the build and the deposited file hold the same text: %d pages, %d tokens, %d accepted difference(s)"
          % (len(deposited), words, sum(allowed.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
