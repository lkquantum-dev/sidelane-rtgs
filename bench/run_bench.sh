#!/usr/bin/env bash
# SideLane-RTGS experiments E2-E8 (headless; prebuilt JAR, needs Java 17+ runtime)
# usage: bench/run_bench.sh            # all experiments
#        bench/run_bench.sh e6         # only E6
#        bench/run_bench.sh e2 e5      # selected
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAVA="${JAVA_HOME:+$JAVA_HOME/bin/}java"
JAR="$ROOT/sim/app/sidelane-sim.jar"
JNA="$ROOT/sim/docker/lib/jna-5.14.0.jar"
PLUG="$ROOT/native/linux-x64"          # LK LEGO binary (libpqcpro_unix.so)
exec "$JAVA" -cp "$JAR:$JNA" "-Dlego.lib.dir=$PLUG" "-Dfile.encoding=UTF-8" "-Dbench.out=$ROOT/bench/out" com.lk.sim.bench.Bench "$@"
