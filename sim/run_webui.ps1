# SideLane-RTGS 组态仿真 WebUI 启动脚本(预编译 JAR;需 Java 21+ 运行时)
# Requires: Java 21+ runtime on PATH (or set $env:JAVA_HOME). No build step.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot          # = repo root
if (-not $root) { $root = (Resolve-Path "$PSScriptRoot/..").Path }
if ($env:JAVA_HOME) { $java = "$env:JAVA_HOME/bin/java.exe" } else { $java = (Get-Command java.exe).Source }
$jar  = "$root/sim/app/sidelane-sim.jar"
$jna  = "$root/sim/docker/lib/jna-5.14.0.jar"
$plug = "$root/native/windows-x64"                # LK LEGO binary (dllpqcpro.dll)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "启动 WebUI → http://127.0.0.1:8080" -ForegroundColor Green
& $java -cp "$jar;$jna" "-Dlego.lib.dir=$plug" "-Dfile.encoding=UTF-8" com.lk.sim.web.SimServer
