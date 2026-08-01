# OneWare Container Extension - Deterministic Build Script

# Check if submodules are initialized
SUBMODULES_STATUS := $(shell if [ ! -d "OneWare/src" ] && [ ! -f "OneWare/LICENSE" ]; then echo "missing"; fi)
ifeq ($(SUBMODULES_STATUS),missing)
$(warning [WARNING] Git submodules do not appear to be initialized. Run: git submodule update --init --recursive)
endif

# The paper, slides and handout sources are kept out of the published tree (see
# .gitignore), so their targets are generated only where the directory is
# present. A clone therefore offers no target it cannot build.
SECONDARY_DOCS := $(wildcard slides paper handout)

.PHONY: all report clean $(SECONDARY_DOCS)

# Toolchain Configuration
LATEXMK := latexmk

# All build artifacts and final PDFs live under .tmp.nosync (iCloud-excluded via
# the .nosync suffix, git-ignored, never committed; CI rebuilds them on demand).
OUT    := .tmp.nosync/latex
PDFDIR := .tmp.nosync/pdf

# Enforce deterministic, reproducible builds
export SOURCE_DATE_EPOCH ?= $(shell git log -1 --pretty=%ct 2>/dev/null || date +%s)
export FORCE_SOURCE_DATE = 1

all: report $(SECONDARY_DOCS)

report:
	mkdir -p $(OUT)/report/chapters $(OUT)/report/appendices $(PDFDIR)
	@echo "Compiling report/main.tex (LuaLaTeX + fontspec)..."
	cd report && $(LATEXMK) -norc -r latexmk.conf -outdir=../$(OUT)/report main.tex
	cp $(OUT)/report/main.pdf $(PDFDIR)/main.pdf
	@echo "Report build complete. Final PDF is in $(PDFDIR)/main.pdf"

# One recipe for every secondary document: each builds <dir>/<dir>.tex.
$(SECONDARY_DOCS):
	mkdir -p $(OUT)/$@ $(PDFDIR)
	@echo "Compiling $@/$@.tex..."
	cd $@ && $(LATEXMK) -norc -pdf -interaction=nonstopmode -file-line-error -synctex=1 -outdir=../$(OUT)/$@ $@.tex
	cp $(OUT)/$@/$@.pdf $(PDFDIR)/$@.pdf
	@echo "Build complete. Final PDF is in $(PDFDIR)/$@.pdf"

clean:
	@echo "Cleaning ephemeral LaTeX artifacts..."
	-cd report && $(LATEXMK) -norc -r latexmk.conf -C -outdir=../$(OUT)/report main.tex
	@for d in $(SECONDARY_DOCS); do (cd "$$d" && $(LATEXMK) -norc -C -outdir="../$(OUT)/$$d" "$$d.tex") || true; done
	rm -rf $(OUT) $(PDFDIR)
	@echo "Removing stray root PDF files..."
	rm -f report/main.pdf main.pdf
	@for d in $(SECONDARY_DOCS); do rm -f "$$d/$$d.pdf" "$$d.pdf"; done
	@echo "Cleaning auxiliary files in the document directories..."
	find report $(SECONDARY_DOCS) -type f \( \
		-name "*.aux" -o -name "*.log" -o -name "*.out" -o -name "*.toc" -o \
		-name "*.bbl" -o -name "*.blg" -o -name "*.fdb_latexmk" -o -name "*.fls" -o \
		-name "*.synctex.gz" -o -name "*.synctex(busy)" -o -name "*.acn" -o -name "*.acr" -o \
		-name "*.alg" -o -name "*.bcf" -o -name "*.ist" -o -name "*.lof" -o \
		-name "*.lot" -o -name "*.run.xml" -o -name "*.glo" -o -name "*.glg" -o \
		-name "*.gls" -o -name "*.soc" -o -name "*.nav" -o \
		-name "*.snm" -o -name "*.vrb" -o -name "*.maf" -o -name "*.mtc*" -o \
		-name "*.lol" \
	\) -delete
