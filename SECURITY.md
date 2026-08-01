# Security Policy

## Status

This repository holds the source of a **submitted master's thesis** — the LaTeX
manuscript and its evaluation harness. The compiled document is a release asset
and is not tracked here. It is not a deployed software system: it builds a LaTeX
document and drives a benchmark harness, and carries no runtime, no network
service, and no hosted application.

## Scope

The repository contains the thesis manuscript (LaTeX, BibTeX/BibLaTeX), the
evaluation pipeline (a Python benchmarking suite and a C# benchmark harness),
shell integration tests, and FPGA example projects. The extension under study,
`FEntwumS.ContainerExtension`, and the upstream OneWare components are pinned as
read-only git submodules; their source is maintained upstream and is neither
redistributed nor modified here. There are no credentials and no
network-facing component in this repository.

## Known limitations

The security properties of the containerized execution model — rootless,
non-privileged containers with dropped capabilities — are described and
measured in the thesis, not enforced by this repository. The example projects
and integration fixtures exist for demonstration and measurement only and are
not hardened for production use.

## Reporting

To report a factual error, a broken build, or any other substantive issue worth
recording, contact <info@mtorun0x7cd.com>. As an actively maintained thesis
repository, corrections that affect the published record are handled through the
normal revision / erratum process; a persistent URN/DOI will be assigned by the
TH Köln institutional repository.
