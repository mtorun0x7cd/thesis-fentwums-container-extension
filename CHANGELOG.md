# Changelog

All notable changes to this repository are listed here. The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/). The first entry is the record tag `epub-3597`; from 1.1.0 on, the versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) and cover the code, the data and the documentation. The text of the thesis changes only through [`ERRATA.md`](ERRATA.md).

This repository was recreated with a new history on 2026-10-02; the earlier release, v1.0.0 of 2026-08-01, was not the version of record and is withdrawn. Its PDF was built by CI from the sources of that day and was not the deposited thesis.

## [1.1.0] - 2026-10-02

### Added

- `README.md`: the thesis, its publication, a summary of the work, the contents, the pinned software, how to reproduce the thesis and the evaluation, the limitations, the corrections, the citation and the licences.
- `ERRATA.md`: the known errors of the deposited thesis, the properties of its catalogue record and of the deposited file, and the web addresses of the thesis that have moved.
- `evaluation/README.md`: every quantitative statement of Chapter 6 with its evidence and kind, the provenance of the results of the three machines, the terms and the rerun recipe.
- `evaluation/harness/packages.lock.upstream-1884317.json`: the restore lock file of the harness as the extension repository held it at commit `1884317`, the state of the macOS measurement on 2026-06-30, kept as evidence. Restore does not read it, and the harness has no lock file of its own yet.
- `evaluation/benchmarking_suite/results/supplementary/shared-image-control/`: the original files of the cross-host control of Section 6.5.3, in which the image of Machine 3 ran unchanged on Machine 1 on 2026-07-02. They were found in 2026 and are added unchanged; `evaluation/README.md` gives their bytes, SHA-256 and dates.
- `scripts/check_result_statistics.py`, which recomputes the statistics of every result file from its raw times with the functions of `benchmark.py`; `make aggregate-check` runs it before it recomputes the tables.
- `SECURITY.md`, `CONTRIBUTING.md`, the correction form, the workflows, the social card and the scripts that check the metadata and the links.

### Changed

- `evaluation/docs/` and `evaluation/benchmarking_suite/README.md` name the paths of this repository instead of those of the extension repository, pass the image of the measurement (`fentwums/oss-cad-suite:2026-06-30`) explicitly, and no longer say that every number of the thesis comes from this code or that the toolchain image is published.
- `evaluation/examples/README.md` marks the example projects as supplementary.
- `Makefile`: `aggregate-check` first recomputes the statistics of the result files; no target writes Python's bytecode cache into the source tree; `harness` builds in `evaluation/`, so that `evaluation/global.json` selects the SDK, as the harness job of `evaluation.yml` does.
- `CITATION.cff` and `codemeta.json` carry the version 1.1.0.
- `codemeta.json` types the thesis as `schema:Thesis`: the CodeMeta 3.0 context defines no term `Thesis`, so the bare name it carried at the record tag did not expand. `scripts/check_metadata.py` checks the type.
- `scripts/compare_pdf_text.py` writes the soft hyphen it drops as an escape sequence, so the script is ASCII; the comparison is unchanged.
- `NOTICE` dates `evaluation/integration/run_harness_smoke.sh` from its own first commit in the extension (2026-06-28), not from that of the other fixtures (2026-06-12).
- `publication/README.md` names the one paragraph whose line breaks differ in a build of the tag (p. 22, PDF p. 37), where the sources tie a citation to the preceding word.
- `publication/README.md` compares the digest the REST API reports for the PDF of the release without its algorithm prefix, so that it can equal its line in `SHA256SUMS`.
- The opt-in pre-commit hook in `.githooks/` scans staged changes with `gitleaks git --staged`, which replaces the deprecated `gitleaks protect`.

## [epub-3597] - 2026-10-02

### Added

- `publication/Torun_Containerized_Execution_OneWare.pdf`, the deposited thesis, byte-identical with the file behind <https://doi.org/10.57683/EPUB-3597>: 557,042 bytes, SHA-256 `f7cb839334f73d2df225a323d0d0473181055a6041cdbca8233f33a8f0c74f93`.
- `thesis/`, the LaTeX sources, which reproduce the text of the deposited file, not its bytes. Sources reconciled in 2026 with the deposited text where the committed sources had diverged: section 7.3 third item, four hyphens. The sources carry the licence of the record, CC BY 4.0, and a build carries the title, author, subject, keywords and creation date of the deposited file.
- `evaluation/`, the benchmark harness, the evaluation scripts, the measured results of the three test machines, the workload designs and the supplementary examples, as they were measured.
- The submodules `FEntwumS.ContainerExtension`, `OneWare`, `OneWare.GhdlExtension` and `FEntwumS.NetlistViewer`, pinned at their state when the thesis was submitted (2026-07-02).
- `Makefile` and `scripts/compare_pdf_text.py`, which build the thesis and compare its text with the deposited file.
- `CITATION.cff`, `codemeta.json`, `NOTICE`, `REUSE.toml` and the licence texts.

[1.1.0]: https://github.com/mtorun0x7cd/thesis-fentwums-container-extension/compare/epub-3597...v1.1.0
[epub-3597]: https://github.com/mtorun0x7cd/thesis-fentwums-container-extension/releases/tag/epub-3597
