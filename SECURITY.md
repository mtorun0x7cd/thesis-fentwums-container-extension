# Security policy

## Scope

This repository holds the Master's thesis "Design and Implementation of a Modular Architecture for the Transparent Integration of Containerized Execution Environments for Heterogeneous Open-Source Binaries in OneWare Studio" as deposited, its LaTeX sources, and the evaluation apparatus of Chapter 6: a benchmark harness, Python scripts, measured results and hardware designs. It runs no service and is not developed further; no version receives security updates. The extension the thesis describes is pinned here as a submodule and is maintained upstream at <https://github.com/FEntwumS/FEntwumS.ContainerExtension>; its security policy applies to the extension itself.

## What to report privately

- A secret, a credential or personal data committed to this repository by mistake, in a file or in the history.
- A file that is not what this repository says it is, for example a PDF whose SHA-256 differs from `publication/SHA256SUMS`.
- A weakness of the workflows under `.github/` that could let someone change what the repository publishes.

## How to report

Use GitHub's private vulnerability reporting (the tab Security, then Report a vulnerability), or write to [info@mtorun0x7cd.com](mailto:info@mtorun0x7cd.com), naming the file, the problem and how to see it. A weakness of the extension goes to its own repository.

## What is not a vulnerability

The security properties of the extension (non-root execution, dropped capabilities, `no-new-privileges`, path containment, shell-less execution) are design properties described in Section 4.4 of the thesis; the thesis leaves a threat-model analysis of them to separate work. The evaluation scripts, the harness and the example designs are research apparatus, not hardened software. An error in the text of the thesis is a correction, not a security report; see the README, section Corrections.

## What to expect

Reports are read. A reply or a fix is not guaranteed, because the repository is not maintained as software.
