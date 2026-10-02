#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Mert Torun
# SPDX-License-Identifier: MIT
"""Check that CITATION.cff, codemeta.json and the BibTeX entry of the README agree.

The three describe one repository and one thesis in three formats, and nothing
but this check keeps them in step. It compares, between CITATION.cff and
codemeta.json: the name of the repository, its version, its licence, the
author with ORCID iD and affiliation, the DOI, the title, the date of
publication and the licence of the thesis. It then parses the @mastersthesis
entry in the README's bibtex block and compares its author, title, school,
year and DOI with the preferred citation of CITATION.cff.

    check_metadata.py            check the three files
    check_metadata.py --selftest prove that a changed DOI, version or title is found

Exit status: 0 they agree, 1 a value differs, 2 a file could not be read.
Needs PyYAML.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPDX = "https://spdx.org/licenses/"


class ReadError(Exception):
    """A file could not be read or parsed."""


def load(root):
    try:
        import yaml
    except ImportError:
        raise ReadError("PyYAML is not installed")
    try:
        cff = yaml.safe_load((root / "CITATION.cff").read_text(encoding="utf-8"))
        meta = json.loads((root / "codemeta.json").read_text(encoding="utf-8"))
        readme = (root / "README.md").read_text(encoding="utf-8")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise ReadError(str(exc))
    if not isinstance(cff, dict) or not isinstance(meta, dict):
        raise ReadError("CITATION.cff or codemeta.json is not a mapping")
    return cff, meta, readme


def bibtex_entry(readme):
    """The fields of the one @mastersthesis entry in a bibtex block of the README."""
    blocks = re.findall(r"```bibtex\n(.*?)```", readme, re.S)
    entries = [b for b in blocks if "@mastersthesis{" in b]
    if len(entries) != 1:
        raise ReadError("the README holds %d @mastersthesis entries in bibtex blocks, not one" % len(entries))
    body = entries[0]
    fields = {}
    for match in re.finditer(r"^\s*([a-z]+)\s*=\s*\{(.*)\},?\s*$", body, re.M):
        fields[match.group(1)] = match.group(2)
    if body.count("{") != body.count("}"):
        raise ReadError("the braces of the BibTeX entry are not balanced")
    return fields


def unbrace(text):
    return re.sub(r"[{}]", "", text)


def compare(cff, meta, readme):
    found = []

    def same(what, a, b):
        if a != b:
            found.append("%s: %r against %r" % (what, a, b))

    pc = cff.get("preferred-citation") or {}
    ref = meta.get("referencePublication") or {}
    same("repository name (CFF title, codemeta name)", cff.get("title"), meta.get("name"))
    same("version", str(cff.get("version")), str(meta.get("version")))
    licences = meta.get("license") if isinstance(meta.get("license"), list) else [meta.get("license")]
    if SPDX + str(cff.get("license")) not in licences:
        found.append("licence: CFF %r is not among codemeta %r" % (cff.get("license"), licences))
    same("repository", cff.get("repository-code"), meta.get("codeRepository"))
    authors = cff.get("authors") or [{}]
    people = meta.get("author") or [{}]
    same("author family name", authors[0].get("family-names"), people[0].get("familyName"))
    same("author given name", authors[0].get("given-names"), people[0].get("givenName"))
    same("author ORCID iD", authors[0].get("orcid"), people[0].get("@id"))
    same("affiliation", authors[0].get("affiliation"), (people[0].get("affiliation") or {}).get("name"))
    same("DOI address", "https://doi.org/" + str(pc.get("doi")), ref.get("@id"))
    same("CFF url of the thesis", pc.get("url"), ref.get("@id"))
    same("title of the thesis", pc.get("title"), ref.get("name"))
    same("publication date", str(pc.get("date-published")), ref.get("datePublished"))
    same("licence of the thesis", SPDX + str(pc.get("license")), ref.get("license"))
    try:
        bib = bibtex_entry(readme)
    except ReadError as exc:
        found.append(str(exc))
        return found
    family, given = authors[0].get("family-names"), authors[0].get("given-names")
    same("BibTeX author", bib.get("author"), "%s, %s" % (family, given))
    same("BibTeX title", unbrace(bib.get("title", "")), pc.get("title"))
    same("BibTeX school", bib.get("school"), (pc.get("institution") or {}).get("name"))
    same("BibTeX year", bib.get("year"), str(pc.get("year")))
    same("BibTeX doi", bib.get("doi"), str(pc.get("doi")))
    same("BibTeX url", bib.get("url"), pc.get("url"))
    same("BibTeX type", bib.get("type"), pc.get("thesis-type"))
    return found


def selftest():
    cff, meta, readme = load(ROOT)
    failures = 0
    if compare(cff, meta, readme):
        print("  [FAIL] selftest: the files of this repository do not agree, so no mutation can be judged")
        return 1
    cases = [
        ("a changed DOI in codemeta.json", lambda c, m, r: (c, dict(m, referencePublication=dict(m["referencePublication"], **{"@id": m["referencePublication"]["@id"] + "0"})), r)),
        ("a changed version in CITATION.cff", lambda c, m, r: (dict(c, version="9.9.9"), m, r)),
        ("a changed title in the BibTeX entry", lambda c, m, r: (c, m, r.replace("title  = {Design", "title  = {Desing", 1))),
        ("a second BibTeX entry", lambda c, m, r: (c, m, r + "\n```bibtex\n@mastersthesis{x,\n}\n```\n")),
    ]
    for name, mutate in cases:
        found = compare(*mutate(cff, meta, readme))
        ok = bool(found)
        failures += not ok
        print("  [%s] %s: %s" % ("ok" if ok else "FAIL", name, "; ".join(found) if found else "not found"))
    if failures:
        print("  [FAIL] selftest: %d of %d mutation(s) went unnoticed" % (failures, len(cases)))
        return 1
    print("  [OK]   selftest: %d mutations found" % len(cases))
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        try:
            return selftest()
        except ReadError as exc:
            print("  [ERR]  %s" % exc, file=sys.stderr)
            return 2
    try:
        cff, meta, readme = load(ROOT)
    except ReadError as exc:
        print("  [ERR]  %s; nothing was compared" % exc, file=sys.stderr)
        return 2
    found = compare(cff, meta, readme)
    for line in found:
        print("  [DIFF] %s" % line)
    if found:
        print("  [FAIL] CITATION.cff, codemeta.json and the README's BibTeX entry differ in %d place(s)" % len(found))
        return 1
    print("  [OK]   CITATION.cff, codemeta.json and the README's BibTeX entry agree")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
