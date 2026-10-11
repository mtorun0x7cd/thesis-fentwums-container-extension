# Cross-platform evaluation suite

Reproduces the empirical evaluation in the Master's thesis *"Design and Implementation of a Modular
Architecture for the Transparent Integration of Containerized Execution Environments for Heterogeneous
Open-Source Binaries in OneWare Studio"*. The evaluation has three axes:

1. **Functional transparency.** The unmodified FPGA toolchain (synthesis, place-and-route, bitstream,
   simulation) runs through the containerised backends; in the measurement for the thesis, every
   iteration of the seven workloads exited with code 0 on the three hosts.
2. **Output determinism and portability.** The produced netlists and bitstreams are SHA-256 hashed on
   every machine. Identical hashes across platforms show that the toolchain pinned in the image gives
   the same outputs on each host; the measurement found the six artifacts of two designs identical on
   three hosts and two builds of the image. No container output was compared with a native one.
3. **Execution-overhead characterisation.** Native against container, and raw `docker run` against the
   real `DockerExecutionStrategy` code path, reported with 95% confidence intervals.

See [`../docs/evaluation.md`](../docs/evaluation.md) for the full methodology and [`../README.md`](../README.md)
for the provenance of the committed results and the classification of each number of the thesis.

## Components

| Script | Purpose |
| --- | --- |
| `benchmark.py` | Single-workload driver: warmup, measured iterations, 95% Student-t confidence intervals, Welch unpaired and (interleaved) paired t-tests, Cohen's d, CV-adaptive repetition, full environment capture, separated image-pull cost, output-artifact hashing. |
| `run_evaluation.py` | Cross-platform orchestrator over the fixed workload matrix (iCE40 and ECP5 synthesis, place-and-route, and pack, plus Verilog simulation). One command per machine. |
| `aggregate.py` | Combines the per-platform results into `summary.csv`, `determinism.md` (cross-machine artifact-hash matrix), `summary.md`, and `figures/` (95% CI bar charts). |
| `harness_bin/` | Published `ContainerBenchmarkHarness`, which runs a tool through the real `DockerExecutionStrategy`. Build artifact (git-ignored). |

## Requirements

- Python 3.9 to 3.12 (standard library only for the tables; `pip install matplotlib` is needed for figures).
  The three machines ran 3.9.6, 3.11.6 and 3.12.10. Under Python 3.14, `run_evaluation.py` stops before
  the first workload, because the argparse of 3.14 rejects the bare `%` in the help text of
  `--target-cv`; see [`../README.md`](../README.md#rerunning-the-evaluation).
- A running container engine (Docker, Podman, OrbStack, ...).
- For the strategy backend, the .NET SDK 10.0.300 or any later 10.0 SDK, as `../global.json` allows (the
  three machines ran 10.0.301), and the submodule `FEntwumS.ContainerExtension`.
- The toolchain image. The measurement used `fentwums/oss-cad-suite:2026-06-30`, built locally from
  `FEntwumS.ContainerExtension/docker/`; it is on no registry. `run_evaluation.py` defaults to
  `fentwums/oss-cad-suite:latest`, a tag the same build sets, and `benchmark.py` on its own to another
  image, so pass `--image` explicitly. For a native baseline (`--with-native`), the same tools must be on
  the host `PATH` at matching versions.

## Reproduce (run on each machine)

```bash
# Build the real-strategy backend once per machine. Run from this folder, so that dotnet reads
# ../global.json, which selects the SDK.
dotnet publish ../harness/ContainerBenchmarkHarness.csproj -c Release -o harness_bin

# Run the full workload matrix (docker CLI + the real strategy path).
python3 run_evaluation.py --image fentwums/oss-cad-suite:2026-06-30

# On a host where the native tools are installed at the container versions, add the native baseline:
python3 run_evaluation.py --image fentwums/oss-cad-suite:2026-06-30 --with-native
```

Each run writes `results/<platform>/<workload>.json` (for example `results/linux-amd64/synth_ice40_yosys.json`),
tagged automatically by OS and architecture, with full environment metadata, per-iteration timings, 95%
CIs, and the artifact hashes.

## Aggregate across machines

Copy every machine's `results/<platform>/` directory into one tree, then:

```bash
python3 aggregate.py
```

This produces, under `results/`:

- `summary.csv`: one row per platform × workload × backend (mean, 95% CI, CV, native overhead, p-value).
- `determinism.md`: the cross-platform artifact-hash matrix (do the bitstreams match across machines?). Its opening paragraph is the text `aggregate.py` writes, kept as generated, and is read with the scope of item 2 above: identical hashes show that the toolchain pinned in the image gives the same outputs on each host, for the corpus, the hosts and the runtimes measured.
- `summary.md`: a human-readable overview grouped by platform.
- `figures/time_<platform>.png`: mean execution time with 95% CI error bars (requires matplotlib).

## Single-workload use

```bash
# Native vs. container CLI vs. the real strategy, interleaved for a paired comparison, CV-adaptive.
python3 benchmark.py --backend all --interleave --target-cv 10 --max-iterations 50 \
  --artifacts ice40_blink.json --output out.json \
  --cmd yosys -p "synth_ice40 -top ice40_blink -json ice40_blink.json" ice40_blink.v

# Separate image-pull cost from steady-state execution.
python3 benchmark.py --measure-pull --backend cli --cmd yosys --version

# Compare two result files.
python3 benchmark.py --compare results/linux-amd64/synth_ice40_yosys.json results/macos-arm64/synth_ice40_yosys.json
```

## Notes

- The `DockerExecutionStrategy` runs **one tool per invocation**, mirroring how OneWare drives the
  toolchain; it is not a shell and does not execute `sh -c` pipelines. The workload matrix therefore
  uses single-tool phases in dependency order.
- On Apple Silicon the toolchain image runs as `linux/amd64` under emulation (upstream omits GHDL from
  the arm64 releases), so a native baseline there would mix containerisation with emulation and is not
  taken. The overhead reported for that host is the strategy backend against the CLI backend, both
  under the same emulation (thesis, Sections 6.1 and 6.4.1).
