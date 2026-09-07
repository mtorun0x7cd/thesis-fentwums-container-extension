#!/usr/bin/env bash
# Headless smoke test of the container execution path through ContainerBenchmarkHarness.
# Exercises the real DockerExecutionStrategy (build, unit tests, telemetry stress, and a
# GHDL/Yosys tool invocation) against the committed HDL fixtures in this directory, so a
# regression in the strategy surfaces without launching the OneWare GUI. Bash-only dev tool;
# the cross-platform evaluation lives in ../benchmarking_suite/run_evaluation.py.
set -Eeuo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[0;33m'; NC='\033[0m'

RUN_BUILD=true RUN_UNIT=true RUN_STRESS=true RUN_GHDL=true RUN_YOSYS=true

usage() {
    cat <<'USAGE'
Usage: run_harness_smoke.sh [options]
  -u, --unit      Build and run unit tests only
  -s, --stress    Build and run the telemetry stress test only
  -g, --ghdl      Build and run the GHDL workflow only
  -y, --yosys     Build and run the Yosys workflow only
  -a, --all       Run everything (default)
  -h, --help      Show this help
USAGE
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -u|--unit)   RUN_STRESS=false; RUN_GHDL=false; RUN_YOSYS=false; shift ;;
        -s|--stress) RUN_UNIT=false; RUN_GHDL=false; RUN_YOSYS=false; shift ;;
        -g|--ghdl)   RUN_UNIT=false; RUN_STRESS=false; RUN_YOSYS=false; shift ;;
        -y|--yosys)  RUN_UNIT=false; RUN_STRESS=false; RUN_GHDL=false; shift ;;
        -a|--all)    shift ;;
        -h|--help)   usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALUATION_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# This repository vendors the extension sources under FEntwumS.ContainerExtension/ and keeps
# the evaluation code beside them under evaluation/. Both directories are named once here and
# every project path is derived from them, so the layout stays visible in a single place.
PROJECT_DIR="$REPO_ROOT/FEntwumS.ContainerExtension"
SOLUTION="$PROJECT_DIR/OneWare.ContainerExtension.slnx"
UNIT_TESTS_CSPROJ="$PROJECT_DIR/tests/ContainerExtension.UnitTests/ContainerExtension.UnitTests.csproj"
HARNESS_CSPROJ="$EVALUATION_DIR/harness/ContainerBenchmarkHarness.csproj"

VHDL_DIR="$SCRIPT_DIR/VHDL_Blink"
VERILOG_DIR="$SCRIPT_DIR/Verilog_Blink"
REPORT_FILE="$SCRIPT_DIR/harness_smoke_report.md"

# Fail early and by name if the layout moves. A phase started with a wrong path fails deep
# inside dotnet, where the message no longer names the file that was not found.
for required_path in "$SOLUTION" "$UNIT_TESTS_CSPROJ" "$HARNESS_CSPROJ" "$VHDL_DIR" "$VERILOG_DIR"; do
    if [ ! -e "$required_path" ]; then
        echo -e "${RED}Missing required path: $required_path${NC}" >&2
        exit 1
    fi
done

START_TIME=$SECONDS
{
    echo "# Harness smoke test report"
    echo "Generated on: $(date)"
    echo
    echo "| Phase | Test | Status | Duration |"
    echo "|---|---|---|---|"
} > "$REPORT_FILE"

run_phase() {
    local num="$1" name="$2" cmd="$3"
    echo -e "\n${BLUE}[Phase $num] $name${NC}"
    local start=$SECONDS exit_code=0
    set +e; eval "$cmd"; exit_code=$?; set -e
    local diff=$((SECONDS - start))
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}SUCCESS: $name (${diff}s)${NC}"
        echo "| $num | $name | SUCCESS | ${diff}s |" >> "$REPORT_FILE"
    else
        echo -e "${RED}FAILURE: $name (exit $exit_code, ${diff}s)${NC}"
        echo "| $num | $name | FAILED | ${diff}s |" >> "$REPORT_FILE"
        exit $exit_code
    fi
}

DOCKER_AVAILABLE=true
if ! docker info >/dev/null 2>&1; then
    echo -e "${YELLOW}Docker daemon unavailable; container phases (GHDL, Yosys) will be skipped.${NC}"
    DOCKER_AVAILABLE=false
fi

if [ "$RUN_BUILD" = true ]; then
    # The harness is not a member of the solution, so building the solution alone leaves it
    # without output and every later --no-build phase fails. It is built as its own phase.
    run_phase "1a" "Build solution" "dotnet build \"$SOLUTION\" -c Debug"
    run_phase "1b" "Build harness" "dotnet build \"$HARNESS_CSPROJ\" -c Debug"
fi
if [ "$RUN_UNIT" = true ]; then
    run_phase "2" "Unit tests" "dotnet test \"$UNIT_TESTS_CSPROJ\" -c Debug --no-build"
fi
if [ "$RUN_STRESS" = true ]; then
    run_phase "3" "Telemetry stress" "dotnet run --project \"$HARNESS_CSPROJ\" --no-build -c Debug -- stress-telemetry --processes 2 --threads 4 --iterations 50"
fi
if [ "$RUN_GHDL" = true ] && [ "$DOCKER_AVAILABLE" = true ]; then
    mkdir -p "$VHDL_DIR/build"
    run_phase "4a" "GHDL version" "dotnet run --project \"$HARNESS_CSPROJ\" --no-build -c Debug -- ghdl --version"
    run_phase "4b" "GHDL analyze" "(cd \"$VHDL_DIR\" && dotnet run --project \"$HARNESS_CSPROJ\" --no-build -c Debug -- ghdl -i --workdir=build VHDL_Blink_tb.vhd VHDL_Blink.vhd)"
    run_phase "4c" "GHDL elaborate" "(cd \"$VHDL_DIR\" && dotnet run --project \"$HARNESS_CSPROJ\" --no-build -c Debug -- ghdl -m --workdir=build VHDL_Blink_tb)"
elif [ "$RUN_GHDL" = true ]; then
    echo "| 4 | GHDL workflow | SKIPPED | 0s |" >> "$REPORT_FILE"
fi
if [ "$RUN_YOSYS" = true ] && [ "$DOCKER_AVAILABLE" = true ]; then
    run_phase "5a" "Yosys version" "dotnet run --project \"$HARNESS_CSPROJ\" --no-build -c Debug -- yosys -V"
    run_phase "5b" "Yosys synth" "(cd \"$VERILOG_DIR\" && dotnet run --project \"$HARNESS_CSPROJ\" --no-build -c Debug -- yosys -p \"read_verilog Verilog_Blink.v; synth -top Verilog_Blink\")"
elif [ "$RUN_YOSYS" = true ]; then
    echo "| 5 | Yosys workflow | SKIPPED | 0s |" >> "$REPORT_FILE"
fi

echo -e "\n${GREEN}Smoke test completed in $((SECONDS - START_TIME))s. Report: ${REPORT_FILE}${NC}"
