# Evaluation methodology

This document specifies the empirical evaluation of the transparent-integration
architecture. It tests that the `IToolExecutionStrategy` hybrid runs FPGA tools
inside a container. In the measurement for the thesis, the seven workloads ran
to success in the container on the three hosts, and the six FPGA artifacts of
two designs were byte-identical across the hosts and across two builds of the
image. No output of a container run was compared with that of a native run, so
the evaluation does not show that the container leaves the result of a tool
unchanged against native execution ([`ERRATA.md`](../../ERRATA.md), E-022).
Execution overhead is reported as supporting evidence, not as the contribution
itself.

The methodology mirrors the harness exactly. The measured numbers of Chapter 6
of the thesis are produced by the code described here; its analytic estimates
and the figures it cites from the literature are not, and
[the README of this folder](../README.md) classifies each number. This document
does not restate results; it documents how they are obtained and where they are
written. The relevant sources are:

| Concern | File |
| --- | --- |
| Per-workload measurement and statistics | `evaluation/benchmarking_suite/benchmark.py` |
| Cross-platform workload matrix | `evaluation/benchmarking_suite/run_evaluation.py` |
| Cross-platform aggregation and reporting | `evaluation/benchmarking_suite/aggregate.py` |
| Real strategy code path (the OneWare path) | `evaluation/harness/Program.cs` |
| Headless toolchain coverage smoke test | `evaluation/integration/run_all.sh` |

## Evaluation axes

The evaluation is organised along three independent axes. Each isolates one
property of the architecture and is measured by a distinct part of the harness.

### Functional transparency and toolchain coverage

The architecture is transparent if a tool invocation that succeeds natively also
succeeds when dispatched to the container strategy, across the breadth of the
open-source FPGA toolchain rather than a single tool. Coverage is exercised by
`evaluation/integration/run_all.sh`, which drives the toolchain end to end through
`docker run` over the workload corpus in `evaluation/integration/`: GHDL analysis,
elaboration and simulation (`VHDL_Blink`); Icarus Verilog compile and execute,
Verilator build and execute, and Yosys synthesis (`Verilog_Blink`); SymbiYosys
formal verification (`Formal_Verification`); the iCE40 synthesis to bitstream
flow with Yosys, nextpnr-ice40 and icepack (`iCE40_Flow`); and the ECP5 flow with
Yosys, nextpnr-ecp5 and ecppack (`ECP5_Flow`). Each phase is recorded as
`SUCCESS` or `FAILED` with a wall-clock duration in `evaluation/integration/test_report.md`,
a generated file that git ignores; the report of the run for the thesis is not in
this repository. The runner covers analysis, simulation, synthesis, place-and-route,
bitstream packing and formal verification under containerisation.

### Output determinism and portability across machines

Transparency at the level of exit codes is necessary but not sufficient; the
artifacts produced must also be machine-independent. For every workload that
yields a single stable output (a netlist or a bitstream), `benchmark.py` computes
the SHA-256 of that artifact after the run via the `--artifacts` flag
(`hash_artifacts`). `run_evaluation.py` attaches the artifact list to each
workload, and `aggregate.py` (`write_determinism`) builds a cross-machine matrix:
for each artifact it compares the recorded hashes across all platforms present
and labels the row `YES` when every platform produced an identical digest,
`partial` when the digests that exist agree but not all platforms are present,
and `NO` otherwise. Identical hashes across heterogeneous hosts show that the
toolchain pinned in the image gave the same output on each host. The cross-host
control, run through the CLI backend without the extension, gives the same six
hashes, so the identity belongs to the pinned image rather than to the
extension; the measurement covers six artifacts of two blink designs on three
hosts and two builds of the image.

### Execution-overhead characterisation

Containerisation is only viable if its cost is bounded and quantified. The
overhead axis measures the wall-clock cost of running a workload through a
container relative to running it natively, with confidence intervals and a
hypothesis test rather than point estimates. This is the role of `benchmark.py`'s
per-iteration timing and statistics, detailed below. Overhead is reported both in
absolute seconds and as a relative factor (`relative_overhead_x`), and the
one-time cost of acquiring the image is measured separately so it does not
contaminate the steady-state figure.

## Experimental design

### Cross-platform matrix

The architecture targets heterogeneous hosts, so the evaluation is run on three
machine classes: macOS on arm64, Linux on amd64, and Windows on amd64.
`run_evaluation.py` derives the platform tag from `platform.system()` and
`platform.machine()` (`platform_tag`, normalising to `macos-arm64`,
`linux-amd64`, `windows-amd64`) and writes that machine's results into
`results/<platform-tag>/`. The orchestration is one command per machine: the
operator runs the same invocation on each host, and the per-platform result trees
are later merged by `aggregate.py`. No machine needs to know about the others;
cross-platform comparison happens entirely at aggregation time from the captured
metadata.

### Workload set

The workload matrix is defined declaratively in `run_evaluation.py` (`WORKLOADS`)
and spans the toolchain categories:

| Workload | Category | Directory | Artifact hashed |
| --- | --- | --- | --- |
| `synth_ice40_yosys` | synthesis | `iCE40_Flow` | `ice40_blink.json` |
| `pnr_ice40_nextpnr` | place-and-route | `iCE40_Flow` | `ice40_blink.asc` |
| `pack_ice40_icepack` | bitstream | `iCE40_Flow` | `ice40_blink.bin` |
| `synth_ecp5_yosys` | synthesis | `ECP5_Flow` | `ecp5_blink.json` |
| `pnr_ecp5_nextpnr` | place-and-route | `ECP5_Flow` | `ecp5_blink.config` |
| `pack_ecp5_ecppack` | bitstream | `ECP5_Flow` | `ecp5_blink.bit` |
| `sim_iverilog` | simulation | `Verilog_Blink` | `Blink.vvp` |

Each workload invokes a single FPGA tool, mirroring how OneWare drives the toolchain
with one tool per dispatch, so the `DockerExecutionStrategy` dispatches an argv
vector, never a `sh -c` pipeline. The per-board workloads are ordered by dependency
(synthesis → place-and-route → bitstream packing) so each phase's artifact persists as
the next phase's input. Each workload is self-contained in its directory under
`evaluation/integration/`; the benchmarked input files are SHA-256 hashed and recorded so the
exact inputs are pinned (see *Reproducibility*). End-to-end full-flow and formal
coverage is exercised separately by the `evaluation/integration/run_all.sh` smoke runner.

### Native, container CLI, and the real strategy path

Three execution backends are compared. `benchmark.py --backend` selects the two
container backends (`cli`, `dotnet` or `all`); the native baseline is added by
`run_evaluation.py --with-native`. The result files store the three under the keys
`native`, `docker` and `docker_dotnet`; the thesis calls them native, CLI and
strategy.

1. **Native.** The tool is invoked directly on the host as the baseline. When the
   tool is absent natively, as is common on a clean macOS or CI host, the baseline is
   simply skipped and the containerised backends still run; the native baseline
   is optional (`run_evaluation.py --with-native`).
2. **Docker CLI (`cli`).** The workload is wrapped in `docker run --rm` with the
   workspace bind-mounted at `/workspace` (`build_docker_cli_cmd`). This isolates
   the cost of containerisation itself, independent of the extension.
3. **Strategy (`dotnet`).** The workload runs through `ContainerBenchmarkHarness`
   (`evaluation/harness/Program.cs`), which constructs a real
   `DockerExecutionStrategy` over a `MockSettingsService` and invokes
   `ExecuteAsync`, the code path OneWare Studio uses, including image
   resolution, container lifecycle and stream demultiplexing. Every setting the
   strategy reads has the default that `ContainerExtensionModule.cs` registers,
   the same at `1884317` and at the pin `5fa2f5f`, except four. The log level is
   `Off` instead of `Errors Only` and the telemetry retention `None` instead of
   `25`, so that the writes of SDK logging and telemetry do not run on the
   measured thread and confound the figure. The default image is the fallback
   image `hdlc/ghdl:yosys` instead of `fentwums/oss-cad-suite:latest`; no run
   uses it, because `benchmark.py` sets `ONEWARE_DOCKER_IMAGE` to the image of
   `--image`, which the strategy resolves first. And
   `BypassNamedPipeCheckSetting` is `false`, where the setting "Bypass Named
   Pipe Security Check" of the extension defaults to `true`: on Windows the
   strategy then checks the server of the named pipe before it uses it
   (`VerifyWindowsNamedPipeAsync`), with a connection of its own to the pipe and
   a check of the process that serves it, once when it connects and once at the
   start of `ExecuteAsync`, so twice in every harness process and thus in every
   measured iteration; on other systems the method returns at once. This is the
   load-bearing backend: it measures the code of the extension under these
   settings, not a CLI approximation of it.

`run_evaluation.py` defaults to `--backend all`, exercising both the CLI and the
real strategy path. The overhead attributable to the extension over and above raw
containerisation is computed directly as the cli-vs-strategy delta: a Welch t-test
with Cohen's *d* and a 95 % confidence interval, exported as `cli_vs_dotnet` in the
comparison block. Needing no native baseline, it is available on every host,
including those where no native toolchain is installed.

## Statistical method

The statistics are implemented in `benchmark.py` with the Python standard library
only; no third-party numerical dependency is introduced.

- **Warmup.** Each suite first performs `--warmup` unrecorded runs
  (`perform_benchmark_suite`) to prime OS file caches, CPU caches and, for the
  container backends, any first-run setup, so the measured iterations reflect
  steady state.
- **Confidence intervals.** Every reported mean carries a two-sided 95% Student-t
  confidence interval (`calculate_stats`, `t_critical_95`). Critical values come
  from a table for every `df` up to 30 and for 40, 50, 60, 80, 100 and 120; a
  `df` is rounded down to an integer, one between two table entries steps down
  to the nearest lower entry (conservative: the interval is slightly wider), and
  one above 120 takes the asymptotic `z = 1.960`.
- **CV-adaptive repetition.** A minimum of `--iterations` measured runs is taken;
  if `--target-cv` is set, sampling continues until the coefficient of variation
  falls to or below the target or `--max-iterations` is reached
  (`perform_benchmark_suite`). `run_evaluation.py` defaults to a 15% CV target
  with a floor of 30 and a cap of 60 iterations, so noisy workloads are sampled
  more heavily and quiet ones are not over-sampled.
- **Welch's unpaired t-test.** Native versus each container backend is compared
  with Welch's t-test for unequal variances (`welch_t_test`), reporting `t`,
  Welch-Satterthwaite `df`, a two-sided p-value computed from the regularised
  incomplete beta function (`student_t_two_sided_p`), the mean difference and its
  95% CI, and significance at α = 0.05.
- **Paired t-test (interleaved mode).** With `--interleave`, native and container
  runs alternate per iteration (`perform_interleaved_suite`) so the samples are
  aligned and a paired t-test is valid (`paired_t_test`); the per-iteration
  pairing cancels slow drift in machine load.
- **Effect size.** Cohen's *d* with pooled standard deviation (`cohens_d`)
  accompanies each comparison, separating statistical significance from practical
  magnitude.
- **Outlier flagging.** Iterations more than `--outlier-sigma` (default 2σ) from
  the mean are flagged (`detect_outliers`); they are reported, not silently
  discarded.

## Reproducibility

Each result file is self-describing so that any run can be reproduced and audited
without external notes. `export_json` (`SCHEMA_VERSION = 2`) records:

- **Environment.** OS, release, architecture, CPU model, logical core count,
  total RAM, Python version, and Docker server version, OS, storage driver and
  architecture (`get_cpu_model`, `get_total_ram_gb`, `get_docker_info`).
- **Image identity.** The image reference and its resolved digest
  (`get_image_digest`), pinning the exact toolchain binaries that ran.
- **Input and harness identity.** The SHA-256 of every file named on the
  workload's command line that exists when the result is written
  (`hash_input_files`), the SHA-256 of `benchmark.py` itself, and the short git
  commit of the checkout that holds `benchmark.py` (`get_git_commit`). Where git
  answers, the inputs, the measurement code and the repository state are fixed.
  The Linux and Windows result files of the thesis record no commit (`null`),
  and the files of the cross-host control record `7828e51`, a commit in neither
  the history of this repository nor that of the extension, so for them the
  repository state is not fixed.
- **Output artifacts.** SHA-256 of each produced artifact (`output_artifacts_sha256`),
  the basis of the cross-machine determinism matrix.
- **Separated image-pull cost.** With `--measure-pull`, the image is removed and
  cold-pulled under timing (`measure_pull_cost`), recording pull seconds and image
  size in a distinct `pull_cost` block. The one-time acquisition cost is thus
  never folded into the steady-state execution figures.

All output is constrained to the benchmarking suite directory: `export_json` refuses
to write a path that does not begin with it.

## How to reproduce

### Measurement hygiene

Because the workloads are short and the per-invocation container floor is small, host
noise is the dominant residual variance. Before a run, it is recommended to quiesce each
measurement machine: pin the CPU frequency governor to `performance` (Linux:
`cpupower frequency-set -g performance`), disable turbo/thermal-throttling variability
where possible, close background workloads, and keep the machine on AC power with thermal
headroom. Where the runtime permits, pin the harness to dedicated cores (`taskset`/core
affinity). The result files record the CPU model, the core count and the Docker version,
not these settings. The thesis records the `performance` CPU governor on Machine 2
(Section 6.2.1), the Windows "High Performance" power plan for the timed run on Machine 3
(note to Table 6.3) and an idle check of the system load before the run on Machine 1
(Section 6.3.2); it records no clock frequencies, power states or core placement
([`ERRATA.md`](../../ERRATA.md), E-016 and E-017).

### One command per machine

On each host (macOS/arm64, Linux/amd64, Windows/amd64), with a container runtime
and the .NET SDK 10.0.300 or any later 10.0 SDK available (the three machines ran
10.0.301), build the .NET strategy harness once and run the evaluation:

```bash
# Build the real-strategy backend (once per machine), in evaluation/, where
# global.json selects the .NET SDK.
(cd evaluation && dotnet publish harness/ContainerBenchmarkHarness.csproj \
  -c Release -o benchmarking_suite/harness_bin)

# Run the full cross-platform workload matrix (CLI + real strategy) with the
# image of the measurement.
python3 evaluation/benchmarking_suite/run_evaluation.py \
  --image fentwums/oss-cad-suite:2026-06-30
```

The runner writes one JSON file per workload into
`evaluation/benchmarking_suite/results/<platform-tag>/`. Add `--with-native` on hosts
where the toolchain is installed natively to obtain the overhead baseline; use
`--only <name> ...` to run a subset, and `--image` to pin a specific toolchain
image.

### Aggregate across machines

Collect every machine's `results/<platform-tag>/` tree into a single
`results/` directory, then aggregate:

```bash
python3 evaluation/benchmarking_suite/aggregate.py
```

This emits the reporting artifacts described below. Figures require `matplotlib`;
the tables do not.

### Reading `results/`

| Artifact | Content |
| --- | --- |
| `results/summary.csv` | One row per platform × workload × backend: `n`, mean, 95% CI bounds, CV%, the native-versus-container overhead factor with its Welch p-value, and the cli-versus-strategy extension-overhead factor with its p-value. Both p-values also carry a Holm-Bonferroni-adjusted column (`overhead_p_holm`, `overhead_p_vs_cli_holm`) controlling the family-wise error rate across the whole workload × platform × backend matrix. It also records the real in-container peak memory (`container_peak_mem_mb`, strategy backend, read from the Docker stats stream rather than host-side RUSAGE) and the cold-start decomposition (`lifecycle_floor_s` and `compute_est_s = mean − floor`, where the floor is the no-op `lifecycle_floor` workload's fixed per-invocation container cost). The machine-readable source of every reported number. |
| `results/determinism.md` | The cross-machine artifact-hash matrix; the `Identical?` column is the portability result per artifact. |
| `results/summary.md` | Human-readable per-platform table: mean (95% CI), CV and overhead factor per workload and backend, headed by the machine's CPU, RAM, core count and Docker version. |
| `results/figures/*.png` | Per-platform grouped bar charts of mean execution time with 95% CI error bars (strategy backend), generated only when `matplotlib` is installed. |

## Interpreting the results

The three axes are read against three distinct expectations.

- **Transparency and coverage** hold when every phase in
  `evaluation/integration/test_report.md` and every workload in `results/summary.md`
  completes successfully across the toolchain categories. A failure localises to a
  specific tool and platform rather than a global pass/fail.
- **Determinism** holds where the `Identical?` column in `results/determinism.md`
  reads `YES` for an artifact across all evaluated machines: the netlists and
  bitstreams of the two designs were byte-identical on the three hosts, an
  identity the toolchain pinned in the image accounts for. Concrete hashes and
  the per-artifact verdict are in that file.
- **Overhead** is read from `results/summary.csv` and `results/summary.md`: the
  `overhead_x_vs_native` factor with its Welch p-value quantifies the steady-state
  cost of containerisation, and the gap between the `cli` and `strategy` backends
  isolates any cost the extension adds beyond raw containerisation. The one-time
  image-pull cost is reported separately and must not be conflated with per-run
  overhead. The measured magnitudes are in `results/summary.csv` (per-platform
  means, intervals and overhead factors) rather than reproduced here, so that this
  document remains valid as the data is regenerated.

The overhead figures are supporting evidence for the viability of the
architecture, not its contribution. The transparency and determinism axes
measured less than the contribution the thesis names: the seven single-tool
workloads exited with code 0 in the container on three hosts, and six artifacts
of two designs were byte-identical across the hosts and across two builds of the
image, which the pinned toolchain accounts for. No output of a container run was
compared with a native one, and the report of the coverage run of
`evaluation/integration/run_all.sh` is not in this repository
([`ERRATA.md`](../../ERRATA.md), E-022 and E-031).
