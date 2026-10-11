#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Mert Torun
# SPDX-License-Identifier: MIT
"""Check that CITATION.cff, codemeta.json and the BibTeX entry of the README agree.

The three describe one repository and one thesis in three formats, and nothing
but this check keeps them in step. It compares, between CITATION.cff and
codemeta.json: the name of the repository, its version, its licence, the
author with ORCID iD and affiliation, the DOI, the title, the date of
publication, the language and the licence of the thesis. It also checks two
forms that the CodeMeta 3.0 context needs and that JSON-LD expansion would
otherwise lose without a warning: the context defines neither a term Thesis
nor a term inLanguage and has no @vocab, so codemeta.json types the thesis as
schema:Thesis and gives its language as schema:inLanguage; and the context
reads softwareRequirements as an IRI, so each requirement is a node of type
SoftwareApplication with a name, not a plain string. It then parses the
@mastersthesis entry in the README's bibtex block and compares its author,
title, school, year and DOI with the preferred citation of CITATION.cff.
Last, it holds the index of ERRATA.md against its entries: every entry under
the heading Errata has exactly one row, whose location (the entry's Location
up to its first comma), class and status are those of the entry, no row names
an entry that does not exist, and the sentence before the table counts the
entries per class as they are. A section without an entry is a finding, not a
pass.

    check_metadata.py            check the files
    check_metadata.py --selftest prove that a changed DOI, version, type, title,
                                 language or requirement is found, and an index
                                 row whose class, location or status differs
                                 from its entry, a missing row and a wrong count

Exit status: 0 they agree, 1 a value differs, 2 a file could not be read.
Needs PyYAML.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPDX = "https://spdx.org/licenses/"
THESIS_TYPE = "schema:Thesis"
LANGUAGE = "schema:inLanguage"
REQUIREMENT_TYPE = "SoftwareApplication"


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


def load_errata(root):
    try:
        return (root / "ERRATA.md").read_text(encoding="utf-8")
    except OSError as exc:
        raise ReadError(str(exc))


def errata_index_findings(text):
    """The differences between the index under '## Errata' and the entries below it."""
    section = re.search(r"^## Errata\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not section:
        return ["ERRATA.md has no section Errata"]
    body = section.group(1)
    first = re.search(r"^### ", body, re.M)
    head = body[:first.start()] if first else body
    found, entries = [], []
    for match in re.finditer(r"^### (\S+)\n(.*?)(?=^### |\Z)", body, re.S | re.M):
        fields = dict(re.findall(r"^- \*\*(Location|Class|Status):\*\* (.*)$", match.group(2), re.M))
        missing = [name for name in ("Location", "Class", "Status") if name not in fields]
        if missing:
            found.append("ERRATA.md %s has no %s field" % (match.group(1), " or ".join(missing)))
            continue
        location = fields["Location"].split(",")[0].strip()
        if location.endswith("."):
            location = location[:-1]
        entries.append((match.group(1), location, fields["Class"].strip(), fields["Status"].strip()))
    if not entries and not found:
        return ["ERRATA.md has no entry under Errata, so its index was not compared"]
    rows = {}
    for line in head.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] in ("Entry", "---"):
            continue
        link = re.fullmatch(r"\[([^\]]+)\]\(#([^)]+)\)", cells[0])
        if len(cells) != 4 or not link:
            found.append("ERRATA.md index: a row that is not entry, location, class and status: %r" % line)
            continue
        if link.group(2) != link.group(1).lower():
            found.append("ERRATA.md index: %s links to #%s, not to its anchor" % (link.group(1), link.group(2)))
        rows.setdefault(link.group(1), []).append(cells[1:])
    for ident, location, kind, status in entries:
        got = rows.pop(ident, [])
        if len(got) != 1:
            found.append("ERRATA.md index: %s has %d row(s), not one" % (ident, len(got)))
            continue
        for what, want, have in zip(("location", "class", "status"), (location, kind, status), got[0]):
            if want != have:
                found.append("ERRATA.md index: the %s of %s is %r, the entry says %r" % (what, ident, have, want))
    for ident in rows:
        found.append("ERRATA.md index: a row for %s, which has no entry" % ident)
    counted = re.search(r"^The (\d+) entries by class: (.+)\.$", head, re.M)
    if not counted:
        found.append("ERRATA.md index: no sentence 'The N entries by class: ...' before the table")
    else:
        claimed, actual = {}, {}
        for item in counted.group(2).split("; "):
            pair = re.fullmatch(r'(\d+) "([^"]+)"', item)
            if not pair:
                found.append("ERRATA.md index: %r in the count sentence is not a number and a class" % item)
                continue
            claimed[pair.group(2)] = int(pair.group(1))
        for _, _, kind, _ in entries:
            actual[kind] = actual.get(kind, 0) + 1
        if int(counted.group(1)) != len(entries) or claimed != actual:
            found.append("ERRATA.md index: the sentence counts %s entries, %r; the entries are %d, %r"
                         % (counted.group(1), claimed, len(entries), actual))
    return found


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
    same("type of the thesis in codemeta.json", ref.get("@type"), THESIS_TYPE)
    languages = pc.get("languages") or [None]
    same("language of the thesis (CFF languages, codemeta %s)" % LANGUAGE, languages[0], ref.get(LANGUAGE))
    if "inLanguage" in ref:
        found.append("codemeta.json gives the language of the thesis as inLanguage, a term the CodeMeta 3.0 context "
                     "does not define, so expansion drops it; write %s" % LANGUAGE)
    requirements = meta.get("softwareRequirements")
    if not isinstance(requirements, list) or not requirements:
        found.append("codemeta.json lists no softwareRequirements")
    else:
        for item in requirements:
            if not (isinstance(item, dict) and item.get("@type") == REQUIREMENT_TYPE
                    and isinstance(item.get("name"), str) and item.get("name").strip()):
                found.append("softwareRequirements: %r is not a %s node with a name; the CodeMeta 3.0 context reads "
                             "a plain string there as an IRI" % (item, REQUIREMENT_TYPE))
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
        ("a bare Thesis type in codemeta.json", lambda c, m, r: (c, dict(m, referencePublication=dict(m["referencePublication"], **{"@type": "Thesis"})), r)),
        ("a dropped schema:inLanguage in codemeta.json", lambda c, m, r: (c, dict(m, referencePublication={k: v for k, v in m["referencePublication"].items() if k != LANGUAGE}), r)),
        ("a bare inLanguage in codemeta.json", lambda c, m, r: (c, dict(m, referencePublication=dict({k: v for k, v in m["referencePublication"].items() if k != LANGUAGE}, inLanguage=m["referencePublication"][LANGUAGE])), r)),
        ("a requirement written as a plain string", lambda c, m, r: (c, dict(m, softwareRequirements=[m["softwareRequirements"][0]["name"]] + m["softwareRequirements"][1:]), r)),
        ("a changed title in the BibTeX entry", lambda c, m, r: (c, m, r.replace("title  = {Design", "title  = {Desing", 1))),
        ("a second BibTeX entry", lambda c, m, r: (c, m, r + "\n```bibtex\n@mastersthesis{x,\n}\n```\n")),
    ]
    for name, mutate in cases:
        found = compare(*mutate(cff, meta, readme))
        ok = bool(found)
        failures += not ok
        print("  [%s] %s: %s" % ("ok" if ok else "FAIL", name, "; ".join(found) if found else "not found"))
    errata = load_errata(ROOT)
    if errata_index_findings(errata):
        print("  [FAIL] selftest: the index of ERRATA.md does not agree with its entries, so no mutation can be judged")
        return 1
    row = re.search(r"^\| \[E-001\]\(#e-001\) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", errata, re.M)
    if not row:
        print("  [FAIL] selftest: the index of ERRATA.md has no row for E-001 to mutate")
        return 1
    location, kind, status = (cell.strip() for cell in row.groups())
    other = "typographical" if kind != "typographical" else "attribution"
    errata_cases = [
        ("an index row whose class differs from its entry",
         errata.replace(row.group(0), row.group(0).replace("| %s |" % kind, "| %s |" % other, 1), 1)),
        ("an index row whose location differs from its entry",
         errata.replace(row.group(0), row.group(0).replace("| %s |" % location, "| %s0 |" % location, 1), 1)),
        ("an index row whose status differs from its entry",
         errata.replace(row.group(0), row.group(0)[:-len("| %s |" % status)] + "| %s, checked |" % status, 1)),
        ("an entry without an index row", errata.replace(row.group(0) + "\n", "", 1)),
        ("a count that does not add up", re.sub(r"^The (\d+) entries", lambda m: "The %d entries" % (int(m.group(1)) + 1),
                                                 errata, count=1, flags=re.M)),
    ]
    for name, text in errata_cases:
        found = errata_index_findings(text)
        ok = bool(found) and text != errata
        failures += not ok
        print("  [%s] %s: %s" % ("ok" if ok else "FAIL", name, "; ".join(found) if found else "not found"))
    total = len(cases) + len(errata_cases)
    if failures:
        print("  [FAIL] selftest: %d of %d mutation(s) went unnoticed" % (failures, total))
        return 1
    print("  [OK]   selftest: %d mutations found" % total)
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
        errata = load_errata(ROOT)
    except ReadError as exc:
        print("  [ERR]  %s; nothing was compared" % exc, file=sys.stderr)
        return 2
    found = compare(cff, meta, readme) + errata_index_findings(errata)
    for line in found:
        print("  [DIFF] %s" % line)
    if found:
        print("  [FAIL] %d finding(s) in CITATION.cff, codemeta.json, the README's BibTeX entry and the errata index"
              % len(found))
        return 1
    print("  [OK]   CITATION.cff, codemeta.json and the README's BibTeX entry agree, and so do the errata index and its entries")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
