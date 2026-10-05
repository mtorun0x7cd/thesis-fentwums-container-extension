# Native-vs-container baseline protocol (linux/amd64, windows/amd64)

This protocol specifies how to collect the **valid** native-versus-container execution-overhead
baseline for the overhead study. It complements [the evaluation methodology](evaluation.md): that
document defines the workload matrix, the three backends, and the statistics; this one fixes the single
condition under which a *native* baseline is sound: the native toolchain and the containerised
toolchain must be the **same build on the same architecture, with no emulation in between**.

## Why a dedicated protocol

The reference image `fentwums/oss-cad-suite` is built for `linux/amd64` only and is not published to a
registry (GHDL is not compiled in the upstream arm64 releases; see [Limitations](https://github.com/FEntwumS/FEntwumS.ContainerExtension/blob/5fa2f5fee83331df203f91e5eea6024a7d533b67/docs/articles/limitations.md) at the pinned commit). On an Apple-Silicon (arm64) host the
container therefore runs under the daemon's binary-emulation layer (Rosetta/qemu), while any native
toolchain is arm64. A macOS/arm64 "native vs container" comparison thus measures *containerisation +
ISA emulation* together and does not isolate the cost of the integration layer; any factor it gave
would only be an upper bound for the emulated case. No native baseline was therefore taken on the
macOS host of the thesis, and its figures are the marginal cost of the extension: the strategy backend
against the CLI backend, both under the same emulation (thesis, Sections 6.1 and 6.4.1).

A sound native baseline requires eliminating both confounds at once:

1. **Same architecture, no emulation.** Run on a real `linux/amd64` (or `windows/amd64`) host, where
   the `linux/amd64` image executes natively.
2. **Same toolchain build.** The native binaries must be the *same* `oss-cad-suite` release the image
   is built from, so the only difference between the two arms is the container boundary, not tool
   versions or build flags.

## Toolchain-version parity (the load-bearing step)

The image pins a single `oss-cad-suite` release in `FEntwumS.ContainerExtension/docker/oss-cad-suite/Dockerfile`
(`ARG RELEASE_TAG`, currently `2026-06-30`, with a checksum-verified `linux-x64` tarball). The native
host must install **the same dated release**, so that `yosys`, `ghdl`, `nextpnr-*`, `icepack`/`ecppack`
and `iverilog` are byte-for-byte the binaries that run in the container.

```bash
# 1. Read the pinned release the container is built from (single source of truth).
RELEASE_TAG=$(grep -m1 '^ARG RELEASE_TAG=' FEntwumS.ContainerExtension/docker/oss-cad-suite/Dockerfile | cut -d= -f2)
DATE=${RELEASE_TAG//-/}          # e.g. 2026-06-30 -> 20260630

# 2. Install the matching native oss-cad-suite for the host architecture.
#    Linux/amd64:
URL="https://github.com/YosysHQ/oss-cad-suite-build/releases/download/${RELEASE_TAG}/oss-cad-suite-linux-x64-${DATE}.tgz"
curl -fL "$URL" -o /tmp/oss-cad-suite.tgz
sudo tar xzf /tmp/oss-cad-suite.tgz -C /opt          # -> /opt/oss-cad-suite
export PATH="/opt/oss-cad-suite/bin:$PATH"
export GHDL_PREFIX="/opt/oss-cad-suite/lib/ghdl"
#    Windows/amd64: download oss-cad-suite-windows-x64-${DATE}.exe, extract, and run
#    oss-cad-suite\environment.bat (which sets PATH/GHDL_PREFIX) before the run.

# 3. Verify parity against the container BEFORE measuring. Versions must match exactly.
docker run --rm fentwums/oss-cad-suite:${RELEASE_TAG} yosys --version
yosys --version
docker run --rm fentwums/oss-cad-suite:${RELEASE_TAG} ghdl --version | head -1
ghdl --version | head -1
```

If any native version differs from the container's, stop: the overhead number would conflate a
toolchain-version delta with the containerisation cost. Re-install the exact dated release before
proceeding. The image digest and the host CPU, memory and operating system are captured per run by
`benchmark.py`, and so is the version string the native tool reports (`experiment.native_tool_version`).
In the Linux result files, the only ones with a native baseline, that string names the native Yosys and
Icarus Verilog; for nextpnr, icepack and ecppack it reads "Unknown or executable missing", and the GHDL
check of step 3 is recorded nowhere, because no measured workload runs GHDL.

On Machine 3 of the thesis the check failed: the native Windows release is a MinGW build, while the
image carries a Clang build of the same source, so no native baseline was taken there. The only native
baseline of the thesis is that of the Linux host, Machine 2 (thesis, Sections 6.3.3 and 6.5.2).

## Running the baseline

Following the measurement-hygiene recommendations in [evaluation.md](evaluation.md) (quiesce the host,
pin the CPU governor to `performance`, keep the machine on AC power), then, on each amd64 host:

```bash
# Build the real-strategy harness once per machine, in evaluation/, where
# global.json selects the .NET SDK (10.0.300 or any later 10.0 SDK).
(cd evaluation && dotnet publish harness/ContainerBenchmarkHarness.csproj \
  -c Release -o benchmarking_suite/harness_bin)

# Run the full matrix WITH the native baseline (native + docker CLI + the real strategy).
python3 evaluation/benchmarking_suite/run_evaluation.py \
  --image fentwums/oss-cad-suite:${RELEASE_TAG} --with-native
```

`run_evaluation.py` writes `results/<platform-tag>/` (`linux-amd64`, `windows-amd64`). Collect every
host's tree into one `results/` directory and aggregate:

```bash
python3 evaluation/benchmarking_suite/aggregate.py
```

## What the amd64 baseline establishes

Only on these hosts is `overhead_x_vs_native` (with its Welch p-value and Holm-Bonferroni adjustment in
`results/summary.csv`) attributable to containerisation rather than emulation. The `cli`-vs-`strategy`
delta (`cli_vs_dotnet`), the cost the extension adds over raw `docker run`, needs no native baseline
and is valid on every host, macOS included. The macOS/arm64 run remains useful for functional
transparency, for output determinism (identical artifact hashes across architectures) and for the
marginal cost of the extension, but its overhead figures must not be compared against the amd64
native numbers.
