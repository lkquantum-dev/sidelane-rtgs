#!/usr/bin/env bash
# SideLane-RTGS WebUI launcher (Linux/macOS; prebuilt JAR, needs Java 17+ runtime)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAVA="${JAVA_HOME:+$JAVA_HOME/bin/}java"
JAR="$ROOT/sim/app/sidelane-sim.jar"
JNA="$ROOT/sim/docker/lib/jna-5.14.0.jar"
PLUG="$ROOT/native/linux-x64"          # LK LEGO binary (libpqcpro_unix.so)
echo "WebUI -> http://127.0.0.1:8080"
exec "$JAVA" -cp "$JAR:$JNA" "-Dlego.lib.dir=$PLUG" "-Dfile.encoding=UTF-8" com.lk.sim.web.SimServer
