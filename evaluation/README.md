<!--
SPDX-FileCopyrightText: 2026 Mert Torun
SPDX-License-Identifier: CC-BY-4.0
-->

# Evaluation apparatus

This folder holds what Chapter 6 of the thesis measured and how: the benchmark harness, the evaluation scripts, the raw results of the three test machines, the tables and figures derived from them, the original files of the cross-host control of Section 6.5.3, the hardware designs of the measured workloads, and two supplementary sets of designs. The result files are kept as the runs wrote them. Not every script is the state that ran: Machine 1 ran an earlier state of `benchmark.py` and `run_evaluation.py`, `aggregate.py` and `integration/run_harness_smoke.sh` changed after the measurements, and the figures were rewritten; [the scripts and figures after the measurements](#the-scripts-and-figures-after-the-measurements) lists each with its dates. Where the documentation of 2026-06-30 had gone stale, it is corrected in the documentation, not in the scripts.

| Path | Content | In the thesis | Licence |
| --- | --- | --- | --- |
| [`harness/`](harness/) | `ContainerBenchmarkHarness`, which runs one tool through the real `DockerExecutionStrategy` of the pinned extension | 6.3, 6.3.1 | MIT |
| [`benchmarking_suite/benchmark.py`](benchmarking_suite/benchmark.py) | Single-workload driver: warm-up, timing, statistics, environment capture, artifact hashes | 6.3.3, 6.3.4 | MIT |
| [`benchmarking_suite/run_evaluation.py`](benchmarking_suite/run_evaluation.py) | The workload matrix, one command per machine | 6.3, 6.4 | MIT |
| [`benchmarking_suite/aggregate.py`](benchmarking_suite/aggregate.py) | Writes `summary.csv`, `summary.md`, `determinism.md` and the figures | 6.4, 6.5.3 | MIT |
| [`benchmarking_suite/results/`](benchmarking_suite/results/) | Raw results, one JSON file per workload and machine, and the tables and figures derived from them; under `supplementary/`, the original files of the cross-host control | Tables 6.1 to 6.4; 6.5.3 | CC BY 4.0 |
| [`integration/`](integration/) | The designs of the measured workloads (`iCE40_Flow`, `ECP5_Flow`, `Verilog_Blink`), further fixtures, a smoke runner and a harness smoke test | 6.4 (the three designs); the rest is supplementary | MIT; six fixtures from OneWare Studio are excepted, see [`NOTICE`](../NOTICE) |
| [`examples/`](examples/) | Eight example projects for the GateMate evaluation board | supplementary, not cited in the thesis | MIT |
| [`docs/`](docs/) | The methodology and the protocol of the native baseline | 6.3, 6.5.2 | CC BY 4.0 |
| [`global.json`](global.json) | .NET SDK 10.0.300 or any later 10.0 SDK, for commands run in this folder; the three machines ran 10.0.301 | 6.2.1 | MIT |

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
| 6.3.2 | The system load of Machine 1 verified as idle (< 1 %) before execution | none | measured, evidence not in this repository; the thesis records no thread placement, see E-017 |
| 6.3.4 | Two warm-up runs; at least 30 measured iterations, continued until the CV is at most 15 % or 60 iterations are reached | The `experiment` block of every result file (`warmup` 2, `iterations` 30, `target_cv_percent` 15.0, `max_iterations` 60) and the number of times stored per backend | measured here |
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
| 6.5.3 | The image Machine 3 ran, exported with `docker save` and loaded unchanged on Machine 1, gives the same six FPGA artifacts there | [`results/supplementary/shared-image-control/`](benchmarking_suite/results/supplementary/shared-image-control/): the six result files of that run and the note written with them | measured here; see [the cross-host control](#the-cross-host-control) |
| 6.5.3 | `Blink.vvp` differs between two runs on Machine 3 | none | measured, evidence not in this repository |
| 6.4.4, Listing C.2 | Four processes, 16 threads each, 1,000 events per thread; each process completing 16,000 events in 2,602 ms | Listing C.2 of the thesis, which records the result of the parent process only | measured, raw log not in this repository; see E-020 |
| 6.4.4 | An in-process throughput of roughly 6,150 events per second | 16,000 events in 2,602 ms, as Listing C.2 records them | derived; for the parent process only, see E-020 |
| 6.4.5 | 15 µs serialisation, 45 µs and 90 µs mutex costs, 1.86 ms and 18.6 s | Equations (6.1) and (6.2) | analytic; the thesis states the constants as illustrative |
| 6.5.4 | gRPC-FUSE "up to 10x", virtio-blk "3-5x" | none | stated without a source; see E-023 |
| 6.5.5 | Instruction expansion of 1.6× to 2.2×; 500 to 1000 cycles per system call; 16 KB pages on macOS against 4 KB pages for Linux binaries | none | stated without a source; see E-027 and E-028 for the first two |
| 6.5.5 | CrossMapping improving translation performance by 8.5 % on ARMv8 and 7.3 % on RISC-V; Risotto improving emulation throughput by up to 19.7 %, 6.7 % on average | References [12] and [11] of the thesis | cited |
| 6.5.6 | An unhandled `ArgumentException` of a standalone process surfacing as exit code 134 (`SIGABRT`, mapped to -6) | none; Listing C.1 shows the exception, not the exit code | stated without a source |
| 6.5.7 | The named-pipe attach defect and the validated corrected path | The Machine 3 result files, all iterations with exit code 0 | measured here for the timed run |
| Listing C.1 | The exception raised at `DockerExecutionStrategy.cs:line 2525` | none | recorded with an earlier state of the extension: the throw stands at line 2452 at the pinned commit, at line 2421 at `1884317`, and at line 2525 at `0810f49` of 2026-06-22 |

## Provenance of the results

| Folder | Machine | Recorded host | Results taken | `benchmark.py` | State of the extension and the harness | Image digest |
| --- | --- | --- | --- | --- | --- | --- |
| `macos-arm64` | 1 | Darwin 25.6.0, Apple M4 Max, 16 logical cores, 128 GB; Docker 29.4.0 (OrbStack) | 2026-06-30, 21:03 to 21:10 (UTC+2) | SHA-256 `62b49f26…`: the file at upstream commit `1884317`, which differs from the committed one in seven lines of path handling | `1884317` (recorded), 19 commits before the pin | `sha256:90b9ccab…`, built on the host |
| `linux-amd64` | 2 | Linux 7.0.0-15-generic, Intel Core Ultra 9 285H, 16 logical cores, 61.0 GB; Docker 29.1.3 (Ubuntu 26.04 LTS) | 2026-07-02, 12:52 to 13:08 (UTC+2) | SHA-256 `05c43db4…`, the committed file | not recorded | `sha256:6a7572d6…` |
| `windows-amd64` | 3 | Windows 11, CPU reported as "Intel64 Family 6 Model 170 Stepping 4", 22 logical cores, 31.46 GB; Docker 29.6.1 (Docker Desktop) | 2026-07-02, 09:27 to 09:37 (UTC+2) | SHA-256 `05c43db4…`, the committed file | not recorded | `sha256:6a7572d6…` |

The pinned commit `5fa2f5f` is the state of the extension when the thesis was submitted, not the state the measurements ran on. Between `1884317` and the pin, the upstream commits change two source files of the extension, `DockerExecutionStrategy.cs` (53 lines) and `RegistryClient.cs` (34 lines), and raise its version to 1.0.10; the rest of the difference is unit tests, documentation, workflows, build configuration and the marketplace manifest, and the removal of the harness, the evaluation scripts, the integration fixtures and the example projects, which `0e16a87` moved here. The Windows results predate the commit time of the upstream commit that holds the named-pipe correction Section 6.5.7 describes (`22ed5f6`, 10:19 on the same day); since a commit time does not show when the code was written, the state that ran on Machines 2 and 3 cannot be named.

`harness/Program.cs` and `harness/link.xml` are byte-identical with their state at `1884317`; the project file differs in the form of its package versions and in the path of the project reference, and since 2026-10-05 in the property `RestorePackagesWithLockFile`. The restore lock file of the harness at `1884317` is kept as evidence in [`harness/packages.lock.upstream-1884317.json`](harness/packages.lock.upstream-1884317.json) (SHA-256 `7229eb86825283b62253dc14f8a2ad5984f4a7cd19faad57e5c4bee0e02cae02`, from upstream commit `651e1e7` of 2026-06-30). It resolves `Microsoft.Extensions.DependencyInjection` 10.0.9, `OneWare.Essentials` 1.0.19 and `Docker.DotNet` 3.125.15, the versions that the project file and the pinned extension name; under its name, restore does not read it. The lock file restore reads, [`harness/packages.lock.json`](harness/packages.lock.json) (SHA-256 `86d48ad67e92838b93b24a1b53da6858730adb5b0bfa361670f32e7389d74cfb`), postdates the measurements: it was written on 2026-10-05 with the .NET SDK 10.0.301 by a restore of the harness alone, and it records the same versions and content hashes as the upstream file for the 90 packages both list. The upstream file lists one package more, `Microsoft.NET.ILLink.Tasks` 10.0.9, which the SDK adds only to a project that sets `IsAotCompatible`, as the build properties of the extension did for the harness while it lived there. `dotnet restore --locked-mode` of the harness alone passes against the lock file under the SDKs 10.0.301 and 10.0.401. A restore that includes the extension project also needs the extension's analyzer packages, and was not run. The build of the harness in `evaluation.yml` restores without `--locked-mode`: NuGet then takes the versions the lock file records and fails on a package whose content differs from its recorded hash, but when the project no longer matches the lock file, it rewrites the file in the runner's copy instead of failing.

The SHA-256 of `benchmark.py` stands in every Linux and Windows result file; the file stays unchanged so that the value can be checked. Every result file records under `experiment.input_file_sha256` the SHA-256 of each file named on its command line that existed when the result was written: the design, netlist, configuration or constraint file the workload reads and, where the command line names it, the file the workload writes. The `lifecycle_floor` files record none.

Outside ASCII, the scripts of this folder hold only five em dashes in comments and strings of `benchmark.py` and ten em dashes and one ellipsis in comments and output strings of `aggregate.py`. They stay as they are: `benchmark.py` is the code that ran on Machines 2 and 3, whose result files record its SHA-256; `summary.md` carries byte for byte the em dashes that `aggregate.py` writes; and the ellipsis stands in a comment that was added to `aggregate.py` after the measurements, which the next section lists.

### The scripts and figures after the measurements

The result files record which `benchmark.py` ran, by its SHA-256, and the result files of Machine 1 also the commit of its checkout; nothing records the state of the other scripts. Compared with these records, with the upstream history of the extension and with the history of the earlier repository of this thesis, which first committed the apparatus on 2026-07-12:

| File | What ran | Changed after the measurements |
| --- | --- | --- |
| `benchmarking_suite/benchmark.py` | Machine 1: the file at upstream `1884317` (SHA-256 `62b49f26…`), which differs from the committed one in seven lines of path handling. Machines 2 and 3 and the cross-host control: the committed file (`05c43db4…`) | no |
| `benchmarking_suite/run_evaluation.py` | Machine 1: the file at `1884317`, which differs from the committed one in two lines, an unused variable and the folder that a comment names. Machines 2 and 3: not recorded | no |
| `benchmarking_suite/aggregate.py` | Not recorded. The file is the same at `1884317`, at the move and in the first commit of the earlier repository, and the committed file writes the committed tables byte for byte (`make aggregate-check`) | on 2026-07-15, in the earlier repository (commit `4629221`): a comment, which holds the file's one ellipsis, and the argument `metadata={"Software": None}` in the call that saves the figures; the tables do not change |
| `results/figures/*.png` | Machine 1: rendered on 2026-06-30 from the macOS results (upstream `144d703`). Machines 2 and 3: first committed on 2026-07-12 | rewritten on 2026-07-15 in the same commit, 74,761 to 76,246 bytes instead of 63,183 to 64,659: the same pixels, without the text entry `Software` and the resolution entry `pHYs` that the earlier files carried |
| the result files and tables under `results/` | written by the runs and by `aggregate.py` | no: the 24 result files and the three tables equal the first commit of the earlier repository, and the eight macOS result files equal upstream `144d703`, the commit that followed the run of Machine 1 |
| `integration/run_all.sh` | no run of it is cited in the thesis | no: byte-identical with `1884317` |
| `integration/run_harness_smoke.sh` | no run of it is cited in the thesis | on 2026-09-07, in the earlier repository (commit `57231c7`): the paths of this layout, a check that names a missing path, and a build phase of its own for the harness |
| `harness/Program.cs`, `harness/link.xml` | Machine 1: the state of `1884317`. Machines 2 and 3: not recorded | no: byte-identical with `1884317` |
| `harness/ContainerBenchmarkHarness.csproj` | as for `Program.cs` | the form of the package versions and the path of the project reference, as first committed on 2026-07-12, and the property `RestorePackagesWithLockFile` since 2026-10-05 |

### The cross-host control

[`results/supplementary/shared-image-control/`](benchmarking_suite/results/supplementary/shared-image-control/) holds the original files of the control that Section 6.5.3 describes: the image Machine 3 ran (`sha256:6a7572d6…`) was exported with `docker save` and loaded unchanged on Machine 1, and the six FPGA workloads were run against it once each through the CLI backend. Each of the six artifact hashes equals the one in the three result folders above. The run took place on 2026-07-02 at 11:07 (UTC+2), between the runs of Machine 3 and Machine 2. The result files record the committed `benchmark.py` (SHA-256 `05c43db4…`) and a harness commit, `7828e51`, that is in neither the history of this repository nor that of the extension; the CLI backend does not use the harness. `NOTES.txt` is the note written with the results. The files were found on 2026-10-02 in an untracked folder of the author's working copy of the earlier repository of this thesis, read for personal data, and added unchanged. `aggregate.py` and `make aggregate-check` read only the three platform folders, so the control enters no table.

| File | Bytes | SHA-256 | Last modified (UTC+2) |
| --- | --- | --- | --- |
| `NOTES.txt` | 1,025 | `00451e3a273f6b40c0af4ad3fdc935186471a20e4202369803d6e33747f44d59` | 2026-07-02 11:09:11 |
| `synth_ice40_yosys.json` | 2,024 | `b3f6dbcb1ac8db5b69a94385d9be0f272a66e635c4e144f9ed358c17a2d6fe15` | 2026-07-02 11:09:11 |
| `synth_ecp5_yosys.json` | 2,002 | `e81aa56110a234faff98d9b7749bceddf5e70f1bcbc3b67e88c6dbfcf41e1fcd` | 2026-07-02 11:09:11 |
| `pnr_ice40_nextpnr.json` | 2,165 | `588196d65b9cd20808cb8b489da45f168c4a6429bdc33b90f66ae577ee2c8620` | 2026-07-02 11:09:11 |
| `pnr_ecp5_nextpnr.json` | 2,244 | `9b8229ab6d4def2c38e2a2c65b3d4b4e2e976cfbe9bb71b2754d58a09f063bbc` | 2026-07-02 11:09:11 |
| `pack_ice40_icepack.json` | 2,078 | `c618c44a5df4a5fbf60d82db743383c80b551f27016a938312fbcfeba9c52f31` | 2026-07-02 11:09:11 |
| `pack_ecp5_ecppack.json` | 2,007 | `5ad3972f0b3241424712c8f09b380ba3aaf70fd96fff9c964a0de9af145594c0` | 2026-07-02 11:09:11 |

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

The measurement needs Docker, the .NET SDK 10.0.300 or any later 10.0 SDK (the three machines ran 10.0.301) and Python 3 on each host, and the submodule `FEntwumS.ContainerExtension`. From the root of a clone:

1. Build the toolchain image. Its inputs are pinned in `FEntwumS.ContainerExtension/docker/oss-cad-suite/Dockerfile`: the Ubuntu base image by digest (`sha256:53958ec7…`) and the oss-cad-suite release 2026-06-30 (`oss-cad-suite-linux-x64-20260630.tgz`) by SHA-256 (`28f10189…`). The build downloads that archive from the release of YosysHQ/oss-cad-suite-build; it is 719,033,749 bytes, the size the GitHub release API reported for it on 2026-09-24.

   ```sh
   git submodule update --init FEntwumS.ContainerExtension
   FEntwumS.ContainerExtension/docker/build_oss_cad_suite.sh     # tags fentwums/oss-cad-suite:2026-06-30
   ```

2. Publish the harness next to the scripts. The command runs in `evaluation/`, because `dotnet` reads `global.json` from the working directory and its parents, not from the folder of the project:

   ```sh
   (cd evaluation && dotnet publish harness/ContainerBenchmarkHarness.csproj -c Release -o benchmarking_suite/harness_bin)
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
(cd evaluation && dotnet run --project harness/ContainerBenchmarkHarness.csproj -c Release -- stress-telemetry --processes 4 --threads 16 --iterations 1000)
```

To check that the committed tables follow from the committed raw results, without Docker:

```sh
make aggregate-check
```

The check runs in two steps. [`scripts/check_result_statistics.py`](../scripts/check_result_statistics.py) recomputes the `statistics` and `comparison` blocks of every result file from the per-iteration times stored in it, with the functions of the committed `benchmark.py`, and compares them with a relative tolerance of 1e-9, because floating-point results can differ slightly between Python versions and platforms: all 96 blocks of the 24 files are reproduced, and every recorded iteration returned exit code 0. Measured on 2026-10-05 on macOS (arm64), 1,009 of the 1,032 numeric values in these blocks come out equal bit for bit under Python 3.9.6 and 1,013 under Python 3.14.7; the largest relative difference, 2.9e-14 and 2.8e-14, is in both cases that of a Welch p-value. `aggregate.py` then writes the tables from the result files into the build folder: `summary.md` and `determinism.md` come out byte-identical with the committed ones, and `summary.csv` identical up to its line endings, because the csv module writes CRLF and the repository stores LF.

## Limits

- The macOS host runs the amd64 image under Rosetta 2, so no native baseline was taken there; its figures isolate the marginal cost of the extension, not the cost of containerisation (6.1).
- α is isolated on Machine 2 only; Machine 3 has no same-build native toolchain (6.5.2).
- Each host ran one container runtime; a comparison of runtimes is future work (7.2).
- The workloads are short single-tool dispatches; the relative overhead is large for sub-second work and shrinks as work grows (6.5.1).
- On Machine 3 the strategy backend ran with the extension's check of the named-pipe server switched on. `harness/Program.cs` sets `BypassNamedPipeCheckSetting` to `false`, where the extension's default is `true`, so every harness process checks the server of the pipe twice before the tool runs ([`docs/evaluation.md`](docs/evaluation.md#native-container-cli-and-the-real-strategy-path)). The Windows result files record no harness commit; every committed state of the harness since upstream `477699c` of 2026-06-28, which switched off its telemetry and SDK logging as Section 6.3.3 describes, sets the same value. The strategy figures of Machine 3, its marginal cost of the extension among them, therefore include this check, and its share of them was not measured. On Machines 1 and 2 the check does not run.
- The native versions of nextpnr, icepack and ecppack were not resolved by the harness; their parity rests on the shared oss-cad-suite release (Table 6.2, note).
- `Blink.vvp` is excluded from the determinism claim (6.5.3).
- The contention constants of 6.4.5 are illustrative, and several figures of 6.5.4 and 6.5.5 have no source; the table above names them.
- A full rerun needs three hosts and an image build; the results of a rerun belong in a separate, dated folder and do not replace these.
- The integration test report, the harness smoke report, the log of the stress test and the `machine.json` files of the thesis are not in this repository; of the original evidence outside the result folders, only the cross-host control is.
- `examples/` and the scripts `integration/run_all.sh` and `integration/run_harness_smoke.sh` are supplementary: the thesis does not cite them, and they produced none of its figures.
