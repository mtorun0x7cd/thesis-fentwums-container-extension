# OneWare Container Extension - Deterministic Build Script

# Check if submodules are initialized
SUBMODULES_STATUS := $(shell if [ ! -d "OneWare/src" ] && [ ! -f "OneWare/LICENSE" ]; then echo "missing"; fi)
ifeq ($(SUBMODULES_STATUS),missing)
$(warning [WARNING] Git submodules do not appear to be initialized. Run: git submodule update --init --recursive)
endif

.PHONY: all report slides paper handout clean

# Toolchain Configuration
LATEXMK := latexmk

# All build artifacts and final PDFs live under .tmp.nosync (iCloud-excluded via
# the .nosync suffix, git-ignored, never committed; CI rebuilds them on demand).
OUT    := .tmp.nosync/latex
PDFDIR := .tmp.nosync/pdf

# Enforce deterministic, reproducible builds
export SOURCE_DATE_EPOCH ?= $(shell git log -1 --pretty=%ct 2>/dev/null || date +%s)
export FORCE_SOURCE_DATE = 1

all: report $(wildcard slides paper handout)

report:
	mkdir -p $(OUT)/report/chapters $(OUT)/report/appendices $(PDFDIR)
	@echo "Compiling report/main.tex (LuaLaTeX + fontspec)..."
	cd report && $(LATEXMK) -norc -r latexmk.conf -outdir=../$(OUT)/report main.tex
	cp $(OUT)/report/main.pdf $(PDFDIR)/main.pdf
	@echo "Report build complete. Final PDF is in $(PDFDIR)/main.pdf"

slides:
	mkdir -p $(OUT)/slides $(PDFDIR)
	@echo "Compiling slides/slides.tex..."
	cd slides && $(LATEXMK) -norc -pdf -interaction=nonstopmode -file-line-error -synctex=1 -outdir=../$(OUT)/slides slides.tex
	cp $(OUT)/slides/slides.pdf $(PDFDIR)/slides.pdf
	@echo "Slides build complete. Final PDF is in $(PDFDIR)/slides.pdf"

paper:
	mkdir -p $(OUT)/paper $(PDFDIR)
	@echo "Compiling paper/paper.tex..."
	cd paper && $(LATEXMK) -norc -pdf -interaction=nonstopmode -file-line-error -synctex=1 -outdir=../$(OUT)/paper paper.tex
	cp $(OUT)/paper/paper.pdf $(PDFDIR)/paper.pdf
	@echo "Paper build complete. Final PDF is in $(PDFDIR)/paper.pdf"

handout:
	mkdir -p $(OUT)/handout $(PDFDIR)
	@echo "Compiling handout/handout.tex..."
	cd handout && $(LATEXMK) -norc -pdf -interaction=nonstopmode -file-line-error -synctex=1 -outdir=../$(OUT)/handout handout.tex
	cp $(OUT)/handout/handout.pdf $(PDFDIR)/handout.pdf
	@echo "Handout build complete. Final PDF is in $(PDFDIR)/handout.pdf"

clean:
	@echo "Cleaning ephemeral LaTeX artifacts..."
	-cd report && $(LATEXMK) -norc -r latexmk.conf -C -outdir=../$(OUT)/report main.tex
	-cd slides && $(LATEXMK) -norc -C -outdir=../$(OUT)/slides slides.tex
	-cd paper && $(LATEXMK) -norc -C -outdir=../$(OUT)/paper paper.tex
	-cd handout && $(LATEXMK) -norc -C -outdir=../$(OUT)/handout handout.tex
	rm -rf $(OUT) $(PDFDIR)
	@echo "Removing stray root PDF files..."
	rm -f report/main.pdf main.pdf slides/slides.pdf slides.pdf paper/paper.pdf paper.pdf handout/handout.pdf handout.pdf
	@echo "Cleaning auxiliary files in the document directories..."
	find report $(wildcard paper slides handout) -type f \( \
		-name "*.aux" -o -name "*.log" -o -name "*.out" -o -name "*.toc" -o \
		-name "*.bbl" -o -name "*.blg" -o -name "*.fdb_latexmk" -o -name "*.fls" -o \
		-name "*.synctex.gz" -o -name "*.synctex(busy)" -o -name "*.acn" -o -name "*.acr" -o \
		-name "*.alg" -o -name "*.bcf" -o -name "*.ist" -o -name "*.lof" -o \
		-name "*.lot" -o -name "*.run.xml" -o -name "*.glo" -o -name "*.glg" -o \
		-name "*.gls" -o -name "*.soc" -o -name "*.nav" -o \
		-name "*.snm" -o -name "*.vrb" -o -name "*.maf" -o -name "*.mtc*" -o \
		-name "*.lol" \
	\) -delete
