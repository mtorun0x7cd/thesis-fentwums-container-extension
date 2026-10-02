<!--
SPDX-FileCopyrightText: 2026 Mert Torun
SPDX-License-Identifier: CC-BY-4.0
-->

# Evaluation apparatus

This folder holds what Chapter 6 of the thesis measured and how: the benchmark harness, the evaluation scripts, the raw results of the three test machines, the tables and figures derived from them, the hardware designs of the measured workloads, and two supplementary sets of designs. The scripts and the results are kept as they ran; where the documentation of 2026-06-30 had gone stale, it is corrected, and every correction is in the documentation only.

| Path | Content | In the thesis | Licence |
| --- | --- | --- | --- |
| [`harness/`](harness/) | `ContainerBenchmarkHarness`, which runs one tool through the real `DockerExecutionStrategy` of the pinned extension | 6.3, 6.3.1 | MIT |
| [`benchmarking_suite/benchmark.py`](benchmarking_suite/benchmark.py) | Single-workload driver: warm-up, timing, statistics, environment capture, artifact hashes | 6.3.3, 6.3.4 | MIT |
| [`benchmarking_suite/run_evaluation.py`](benchmarking_suite/run_evaluation.py) | The workload matrix, one command per machine | 6.3, 6.4 | MIT |
| [`benchmarking_suite/aggregate.py`](benchmarking_suite/aggregate.py) | Writes `summary.csv`, `summary.md`, `determinism.md` and the figures | 6.4, 6.5.3 | MIT |
| [`benchmarking_suite/results/`](benchmarking_suite/results/) | Raw results, one JSON file per workload and machine, and the tables and figures derived from them | Tables 6.1 to 6.4 | CC BY 4.0 |
| [`integration/`](integration/) | The designs of the measured workloads (`iCE40_Flow`, `ECP5_Flow`, `Verilog_Blink`), further fixtures, a smoke runner and a harness smoke test | 6.4 (the three designs); the rest is supplementary | MIT; six fixtures from OneWare Studio are excepted, see [`NOTICE`](../NOTICE) |
| [`examples/`](examples/) | Eight example projects for the GateMate evaluation board | supplementary, not cited in the thesis | MIT |
| [`docs/`](docs/) | The methodology and the protocol of the native baseline | 6.3, 6.5.2 | CC BY 4.0 |
| [`global.json`](global.json) | .NET SDK 10.0.300 or a later feature band; the three machines ran 10.0.301 | 6.2.1 | MIT |

## Paths named in the thesis

The apparatus lived in the repository of the extension until 2026-06-30, when the upstream commit `0e16a87` moved it here. The thesis names some files by their paths there:

| In the thesis | In this repository |
| --- | --- |
| `src/ContainerBenchmarkHarness/Program.cs` (6.3, Listing C.1) | [`evaluation/harness/Program.cs`](harness/Program.cs) |
| `benchmark.py`, `run_evaluation.py` (6.3) | [`evaluation/benchmarking_suite/`](benchmarking_suite/) |
| `src/ContainerExtension/` (Table A.1, Listing C.1) | `FEntwumS.ContainerExtension/src/ContainerExtension/`, in the submodule |
| the extension "on the main branch" (Appendix A) | the submodule `FEntwumS.ContainerExtension`, pinned at `5fa2f5f`, the state of the extension when the thesis was submitted |

## Claims and their evidence

Each quantitative statement of Chapter 6 is classified as one of: *measured here*, with its data file in this folder; *derived*, computed from measured data; *measured, evidence not in this repository*; *analytic*, an estimate the thesis states as such; *cited*, taken from a source; or *stated without a source*. [`ERRATA.md`](../ERRATA.md) holds the corrections the entries name.

| Thesis | Statement | Evidence | Kind |
| --- | --- | --- | --- |
| 6.2.1 | Host, CPU, memory, operating system and container runtime of the three machines | The `system` block of every result file: operating system and release, CPU model as the system reports it, logical cores, memory in GB, Python and Docker versions | measured here, as far as the block reaches; the product name of the Windows CPU, the core split, the Windows build number and the nominal memory are not in it, and the file `machine.json` the thesis names is not in this repository |
| 6.4.1, Table 6.1 | CLI and strategy means with 95 % confidence intervals and the extension overhead on Machine 1 | [`results/macos-arm64/`](benchmarking_suite/results/macos-arm64/), [`results/summary.csv`](benchmarking_suite/results/summary.csv) | measured here; the tables are derived by `aggregate.py` |
| 6.4.2, Table 6.2 | Native, CLI and strategy means, the container floor and both overhead ratios on Machine 2 | [`results/linux-amd64/`](benchmarking_suite/results/linux-amd64/) | measured here |
| 6.4.3, Table 6.3 | CLI and strategy means on Machine 3, including the bimodal `pnr_ice40_nextpnr` strategy run | [`results/windows-amd64/`](benchmarking_suite/results/windows-amd64/); the per-iteration times are in the file | measured here |
| 6.4.1 to 6.5.1 | Marginal cost of the extension (strategy minus CLI) and its comparison with the lifecycle floor | The three result folders | derived; [`ERRATA.md`](../ERRATA.md), E-019, sets the three per-host figures on one basis |
| 6.5.1 | The multiplier α ≈ 1 for native-architecture execution | `results/linux-amd64/`: the container floor stays between 0.258 s and 0.327 s while the native time ranges from 16 ms to 0.51 s | derived |
| 6.5.1, 6.5.5 | 8.94 % average penalty of the hardware TSO mode | Reference [15] of the thesis | cited; see E-021 |
| 6.5.2 | Version parity of Yosys, GHDL and Icarus Verilog on Machine 2 | `experiment.native_tool_version` in the Linux result files holds the native strings of Yosys and Icarus Verilog; nextpnr, icepack and ecppack are recorded as unresolved | measured here for Yosys and Icarus Verilog; the GHDL check is not in this repository |
| 6.5.2 | The parity gate rejecting the Windows native toolchain (MinGW build) | none | measured, evidence not in this repository |
| 6.5.3, Table 6.4 | Six FPGA artifacts byte-identical on three hosts; `Blink.vvp` different | `output_artifacts_sha256` in the result files, [`results/determinism.md`](benchmarking_suite/results/determinism.md) | measured here |
| 6.5.3 | Image digests `90b9ccab` (Machine 1, built on the host) and `6a7572d6` (Machines 2 and 3) | `experiment.image_digest` in the result files | measured here |
| 6.5.3 | `Blink.vvp` differs between two runs on Machine 3; the exported image re-run on Machine 1 gives the same six artifacts | none | measured, evidence not in this repository |
| 6.4.4, Listing C.2 | Four processes, 16 threads each, 1,000 events per thread; each process completing 16,000 events in 2,602 ms | Listing C.2 of the thesis, which records the result of the parent process only | measured, raw log not in this repository; see E-020 |
| 6.4.5 | 15 µs serialisation, 45 µs and 90 µs mutex costs, 1.86 ms and 18.6 s | Equations (6.1) and (6.2) | analytic; the thesis states the constants as illustrative |
| 6.5.4 | gRPC-FUSE "up to 10x", virtio-blk "3-5x" | none | stated without a source; see E-023 |
| 6.5.5 | Instruction expansion of 1.6× to 2.2×; 500 to 1000 cycles per system call | none | stated without a source; see E-027 and E-028 |
| 6.5.7 | The named-pipe attach defect and the validated corrected path | The Machine 3 result files, all iterations with exit code 0 | measured here for the timed run |
| Listing C.1 | The exception raised at `DockerExecutionStrategy.cs:line 2525` | none | recorded with an earlier state of the extension: the throw stands at line 2452 at the pinned commit, at line 2421 at `1884317`, and at line 2525 at `0810f49` of 2026-06-22 |

## Provenance of the results

| Folder | Machine | Recorded host | Results taken | `benchmark.py` | State of the extension and the harness | Image digest |
| --- | --- | --- | --- | --- | --- | --- |
| `macos-arm64` | 1 | Darwin 25.6.0, Apple M4 Max, 16 logical cores, 128 GB; Docker 29.4.0 (OrbStack) | 2026-06-30, 21:03 to 21:10 (UTC+2) | SHA-256 `62b49f26…`: the file at upstream commit `1884317`, which differs from the committed one in seven lines of path handling | `1884317` (recorded), 19 commits before the pin | `sha256:90b9ccab…`, built on the host |
| `linux-amd64` | 2 | Linux 7.0.0-15-generic, Intel Core Ultra 9 285H, 16 logical cores, 61.0 GB; Docker 29.1.3 (Ubuntu 26.04 LTS) | 2026-07-02, 12:52 to 13:08 | SHA-256 `05c43db4…`, the committed file | not recorded | `sha256:6a7572d6…` |
| `windows-amd64` | 3 | Windows 11, CPU reported as "Intel64 Family 6 Model 170 Stepping 4", 22 logical cores, 31.46 GB; Docker 29.6.1 (Docker Desktop) | 2026-07-02, 09:27 to 09:37 | SHA-256 `05c43db4…`, the committed file | not recorded | `sha256:6a7572d6…` |

The pinned commit `5fa2f5f` is the state of the extension when the thesis was submitted, not the state the measurements ran on. Between `1884317` and the pin, the upstream commits change `DockerExecutionStrategy.cs` (53 lines) and `RegistryClient.cs` (34 lines), raise the version to 1.0.10, and remove the harness and the evaluation scripts, which `0e16a87` moved here. The Windows results predate the commit time of the upstream commit that holds the named-pipe correction Section 6.5.7 describes (`22ed5f6`, 10:19 on the same day); since a commit time does not show when the code was written, the state that ran on Machines 2 and 3 cannot be named.

`harness/Program.cs` and `harness/link.xml` are byte-identical with their state at `1884317`; the project file differs only in the form of its package versions and in the path of the project reference. The restore lock file of the harness at `1884317` is kept as evidence in [`harness/packages.lock.upstream-1884317.json`](harness/packages.lock.upstream-1884317.json) (SHA-256 `7229eb86825283b62253dc14f8a2ad5984f4a7cd19faad57e5c4bee0e02cae02`, from upstream commit `651e1e7` of 2026-06-30). It resolves `Microsoft.Extensions.DependencyInjection` 10.0.9, `OneWare.Essentials` 1.0.19 and `Docker.DotNet` 3.125.15, the versions the project file names. Under its name, restore does not read it. It was written under the central package management of the extension, while this project names its versions itself, so whether it restores in locked mode against this file is open: that check (`dotnet restore --locked-mode`) needs the package feed and has not been run, and the project has no lock file of its own yet.

The SHA-256 of `benchmark.py` stands in every Linux and Windows result file; the file stays unchanged so that the value can be checked. The SHA-256 of each input design stands in every result file as well.

## Terms

| Term | Meaning |
| --- | --- |
| native | The tool run directly on the host. Enabled with `run_evaluation.py --with-native`; key `native` in the result files |
| CLI, `cli` | The tool run through `docker run --rm` with the workspace mounted at `/workspace`. `--backend cli`; key `docker` |
| strategy | The tool run through `ContainerBenchmarkHarness` and the real `DockerExecutionStrategy.ExecuteAsync`. `--backend dotnet`; key `docker_dotnet` |
| `lifecycle_floor` | The no-op command `true` in the container: the fixed cost of one invocation with no tool work |
| Ext. overhead | Strategy mean divided by CLI mean |
| Δcont | CLI mean minus native mean: the additive container floor (Machine 2) |
| α | The multiplier of native compute time inside the container (Equation (6.3)); about 1 on native-architecture hardware |
| version-parity gate | A native baseline is admitted only where each native tool reports the version string of the tool in the image (6.5.2) |
| CV-adaptive repetition | At least 30 measured iterations, continued until the coefficient of variation is at most 15 % or 60 iterations are reached |
| Holm correction | The Holm-Bonferroni adjustment of the p-values across the workload, platform and backend matrix (`*_holm` columns of `summary.csv`) |

## Rerunning the evaluation

The measurement needs Docker, the .NET SDK and Python 3 on each host, and the submodule `FEntwumS.ContainerExtension`. From the root of a clone:

1. Build the toolchain image. Its inputs are pinned in `FEntwumS.ContainerExtension/docker/oss-cad-suite/Dockerfile`: the Ubuntu base image by digest (`sha256:53958ec7…`) and the oss-cad-suite release 2026-06-30 (`oss-cad-suite-linux-x64-20260630.tgz`) by SHA-256 (`28f10189…`).

   ```sh
   git submodule update --init FEntwumS.ContainerExtension
   FEntwumS.ContainerExtension/docker/build_oss_cad_suite.sh     # tags fentwums/oss-cad-suite:2026-06-30
   ```

2. Publish the harness next to the scripts:

   ```sh
   dotnet publish evaluation/harness/ContainerBenchmarkHarness.csproj -c Release -o evaluation/benchmarking_suite/harness_bin
   ```

3. Run the workload matrix on each host, naming the image of the measurement. `run_evaluation.py` defaults to `fentwums/oss-cad-suite:latest`, a tag the image build sets locally beside the dated one, and `benchmark.py` alone defaults to another image, so pass `--image` every time:

   ```sh
   python3 evaluation/benchmarking_suite/run_evaluation.py --image fentwums/oss-cad-suite:2026-06-30
   ```

   On a Linux amd64 host with the same oss-cad-suite release installed natively, add `--with-native` for the native baseline; [`docs/amd64-native-baseline-protocol.md`](docs/amd64-native-baseline-protocol.md) gives the parity check that must pass first.

4. Collect the `results/<platform>/` folders of all hosts in one `results/` folder and aggregate them:

   ```sh
   python3 evaluation/benchmarking_suite/aggregate.py
   ```

The image is build-only and is not on a registry, so a rebuilt image has its own digest (thesis, 6.5.3); its tool binaries come from the same checksummed archive. The check of a rerun is therefore the six FPGA artifacts, whose SHA-256 values were the same on all three machines:

| Workload | Artifact | SHA-256 |
| --- | --- | --- |
| `synth_ice40_yosys` | `ice40_blink.json` | `c9d719c17f01113e1e72a8e5bbe050bc35ca3b0b0f2fdeefe696a516ec3a0c46` |
| `synth_ecp5_yosys` | `ecp5_blink.json` | `65bb1549bab3067dc30509a6e3ad8be23ddbc1823300d031106ef6bada302563` |
| `pnr_ice40_nextpnr` | `ice40_blink.asc` | `31350507657f945e90cce6c6f4224410e55193cfdcbdcafcd206f3f380f045ba` |
| `pnr_ecp5_nextpnr` | `ecp5_blink.config` | `ab2628df3a28a9bc59e160da140160a85a35dabb23129c38332ff5ad8837fddc` |
| `pack_ice40_icepack` | `ice40_blink.bin` | `a8b0b3aa554c2cfdf4990a88c89a48aafe85798a73d0f400f4be74763c887f29` |
| `pack_ecp5_ecppack` | `ecp5_blink.bit` | `37e5e6ab10042f3aa91f512e9c88e1c7434643c9ba967a2346ac032e7eead9f0` |

[`results/determinism.md`](benchmarking_suite/results/determinism.md) shows the first twelve characters of each value, and every result file holds them in full under `output_artifacts_sha256`. The seventh artifact, `Blink.vvp` of `sim_iverilog`, differs from run to run, because Icarus Verilog names objects after heap addresses (6.5.3).

The result timestamps give the time a run takes, without the image build and the harness publish: about 7 minutes on Machine 1, 16 minutes on Machine 2 with the native baseline, and 10 minutes on Machine 3.

The telemetry stress test of Section 6.4.4 is a synthetic microbenchmark of the logging path, not part of the workload matrix. The harness defaults to 1 process, 10 threads and 100 iterations; the thesis ran it with:

```sh
dotnet run --project evaluation/harness/ContainerBenchmarkHarness.csproj -c Release -- stress-telemetry --processes 4 --threads 16 --iterations 1000
```

To check that the committed tables follow from the committed raw results, without Docker:

```sh
make aggregate-check
```

The check runs in two steps. [`scripts/check_result_statistics.py`](../scripts/check_result_statistics.py) recomputes the `statistics` and `comparison` blocks of every result file from the per-iteration times stored in it, with the functions of the committed `benchmark.py`; all 96 blocks of the 24 files are reproduced, within the last bit of a floating-point number, and every recorded iteration returned exit code 0. `aggregate.py` then writes the tables from the result files into the build folder: `summary.md` and `determinism.md` come out byte-identical with the committed ones, and `summary.csv` identical up to its line endings, because the csv module writes CRLF and the repository stores LF.

## Limits

- The macOS host runs the amd64 image under Rosetta 2, so no native baseline was taken there; its figures isolate the marginal cost of the extension, not the cost of containerisation (6.1).
- α is isolated on Machine 2 only; Machine 3 has no same-build native toolchain (6.5.2).
- Each host ran one container runtime; a comparison of runtimes is future work (7.2).
- The workloads are short single-tool dispatches; the relative overhead is large for sub-second work and shrinks as work grows (6.5.1).
- The native versions of nextpnr, icepack and ecppack were not resolved by the harness; their parity rests on the shared oss-cad-suite release (Table 6.2, note).
- `Blink.vvp` is excluded from the determinism claim (6.5.3).
- The contention constants of 6.4.5 are illustrative, and several figures of 6.5.4 and 6.5.5 have no source; the table above names them.
- A full rerun needs three hosts and an image build; the results of a rerun belong in a separate, dated folder and do not replace these.
- The integration test report, the harness smoke report, the log of the stress test, the log of the cross-host re-run and the `machine.json` files of the thesis are not in this repository.
- `examples/` and the scripts `integration/run_all.sh` and `integration/run_harness_smoke.sh` are supplementary: the thesis does not cite them, and they produced none of its figures.
