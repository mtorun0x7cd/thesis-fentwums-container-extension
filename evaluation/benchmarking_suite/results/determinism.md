# Output-determinism across platforms

Each toolchain artifact (bitstream / netlist) is SHA-256 hashed after generation on every
machine. Identical hashes across platforms are direct evidence that the containerized
architecture makes tool outputs machine-independent.

Platforms compared: linux-amd64, macos-arm64, windows-amd64

## pack_ecp5_ecppack

| Artifact | linux-amd64 | macos-arm64 | windows-amd64 | Identical? |
|---|---|---|---|---|
| `ecp5_blink.bit` | 37e5e6ab1004 | 37e5e6ab1004 | 37e5e6ab1004 | YES |

## pack_ice40_icepack

| Artifact | linux-amd64 | macos-arm64 | windows-amd64 | Identical? |
|---|---|---|---|---|
| `ice40_blink.bin` | a8b0b3aa554c | a8b0b3aa554c | a8b0b3aa554c | YES |

## pnr_ecp5_nextpnr

| Artifact | linux-amd64 | macos-arm64 | windows-amd64 | Identical? |
|---|---|---|---|---|
| `ecp5_blink.config` | ab2628df3a28 | ab2628df3a28 | ab2628df3a28 | YES |

## pnr_ice40_nextpnr

| Artifact | linux-amd64 | macos-arm64 | windows-amd64 | Identical? |
|---|---|---|---|---|
| `ice40_blink.asc` | 31350507657f | 31350507657f | 31350507657f | YES |

## sim_iverilog

| Artifact | linux-amd64 | macos-arm64 | windows-amd64 | Identical? |
|---|---|---|---|---|
| `Blink.vvp` | 229bc0467b2f | f2cf898fe9db | 0d8322d8717e | NO |

## synth_ecp5_yosys

| Artifact | linux-amd64 | macos-arm64 | windows-amd64 | Identical? |
|---|---|---|---|---|
| `ecp5_blink.json` | 65bb1549bab3 | 65bb1549bab3 | 65bb1549bab3 | YES |

## synth_ice40_yosys

| Artifact | linux-amd64 | macos-arm64 | windows-amd64 | Identical? |
|---|---|---|---|---|
| `ice40_blink.json` | c9d719c17f01 | c9d719c17f01 | c9d719c17f01 | YES |

