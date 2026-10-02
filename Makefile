# SPDX-FileCopyrightText: 2026 Mert Torun
# SPDX-License-Identifier: MIT
#
# Build and check the thesis and the evaluation apparatus.
#
#   make thesis           typeset thesis/main.tex into $(OUT)/thesis/main.pdf
#   make check            run ChkTeX over the thesis sources; any warning fails
#   make verify-deposit   check publication/ against SHA256SUMS and compare the
#                         text of the build with the deposited file
#   make aggregate-check  recompute the statistics of every result file from its
#                         raw times, and the result tables from the result
#                         files, and compare both with what is committed
#   make harness          build the benchmark harness (needs the submodule
#                         FEntwumS.ContainerExtension and the .NET SDK)
#
# All output goes to $(OUT), which is git-ignored; the source tree is not
# written to, Python's bytecode cache included.

SHELL       := /bin/bash
.SHELLFLAGS := -euo pipefail -c

OUT     ?= build
LATEXMK ?= latexmk
BIBER   ?= biber
PYTHON  ?= python3
DOTNET  ?= dotnet

DEPOSIT := publication/Torun_Containerized_Execution_OneWare.pdf
RESULTS := evaluation/benchmarking_suite/results

# The build date is fixed to the creation date of the deposited file,
# 2026-07-02T19:05:35Z, so that no build depends on the date of the last commit
# and two builds of the same sources in one directory give the same bytes (the
# PDF identifier depends on the directory).
export SOURCE_DATE_EPOCH ?= 1783019135
export FORCE_SOURCE_DATE := 1
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: thesis check verify-deposit aggregate-check harness

thesis:
	mkdir -p "$(OUT)/thesis"
	cd thesis && $(LATEXMK) -norc -r latexmk.conf -e '$$biber=q{$(BIBER) %O %S}' \
		-outdir="$(abspath $(OUT))/thesis" main.tex

check:
	find thesis -name '*.tex' -not -path 'thesis/setup/*' -exec chktex -q -I0 -l .chktexrc {} +

verify-deposit: thesis
	cd publication && if command -v sha256sum >/dev/null; then sha256sum -c SHA256SUMS; \
		else shasum -a 256 -c SHA256SUMS; fi
	$(PYTHON) scripts/compare_pdf_text.py "$(OUT)/thesis/main.pdf" "$(DEPOSIT)"

aggregate-check:
	$(PYTHON) scripts/check_result_statistics.py
	mkdir -p "$(OUT)/aggregate-check"
	for platform in linux-amd64 macos-arm64 windows-amd64; do \
		mkdir -p "$(OUT)/aggregate-check/$$platform"; \
		cp "$(RESULTS)/$$platform/"*.json "$(OUT)/aggregate-check/$$platform/"; \
	done
	$(PYTHON) evaluation/benchmarking_suite/aggregate.py --results-dir "$(OUT)/aggregate-check"
	cmp "$(OUT)/aggregate-check/summary.md" "$(RESULTS)/summary.md"
	cmp "$(OUT)/aggregate-check/determinism.md" "$(RESULTS)/determinism.md"
	tr -d '\r' < "$(OUT)/aggregate-check/summary.csv" | cmp - "$(RESULTS)/summary.csv"
	@echo "summary.md and determinism.md are byte-identical; summary.csv is identical up to line endings."

# The build runs in evaluation/, so that evaluation/global.json selects the SDK.
harness:
	test -f FEntwumS.ContainerExtension/src/ContainerExtension/ContainerExtension.csproj || \
		{ echo "The submodule is missing: git submodule update --init FEntwumS.ContainerExtension" >&2; exit 2; }
	cd evaluation && $(DOTNET) build harness/ContainerBenchmarkHarness.csproj -c Release \
		--artifacts-path "$(abspath $(OUT))/dotnet"
