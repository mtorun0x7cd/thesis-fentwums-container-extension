#!/bin/bash
# Rebuild the Master's Thesis LaTeX report on Apple Silicon macOS
# Handles the Biber lipo "-extract_family" incompatibility dynamically.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p bin

# Extract thin arm64 binary if not already generated
if [ ! -f bin/biber ]; then
    echo "================================================================="
    echo "Creating thinned arm64 Biber binary in bin/biber to bypass macOS lipo error..."
    echo "================================================================="
    lipo /Library/TeX/texbin/biber -thin arm64 -output bin/biber
    chmod +x bin/biber
fi

echo "================================================================="
echo "Compiling LaTeX Report manually to bypass latexmk iCloud loops..."
echo "================================================================="
mkdir -p .tmp.nosync/latex/chapters .tmp.nosync/latex/appendices .tmp.nosync/pdf
pdflatex -shell-escape -output-directory=.tmp.nosync/latex -interaction=nonstopmode main.tex
./bin/biber .tmp.nosync/latex/main
pdflatex -shell-escape -output-directory=.tmp.nosync/latex -interaction=nonstopmode main.tex
pdflatex -shell-escape -output-directory=.tmp.nosync/latex -interaction=nonstopmode main.tex
cp .tmp.nosync/latex/main.pdf .tmp.nosync/pdf/main.pdf

echo "================================================================="
echo "Report compilation completed successfully!"
echo "================================================================="
