# 工程伴随论文实验基准:运行 Bench(headless,预编译 JAR)。
# Requires: Java 21+ runtime on PATH (or set $env:JAVA_HOME). No build step.
# 用法: .\bench\run_bench.ps1            # 跑全部实验(覆盖 bench/out 全部 CSV)
#       .\bench\run_bench.ps1 e6         # 只跑 E6(只写 E6_topology.csv)
#       .\bench\run_bench.ps1 e2 e5      # 跑指定若干实验
$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot/.."
if ($env:JAVA_HOME) { $java = "$env:JAVA_HOME/bin/java.exe" } else { $java = (Get-Command java.exe).Source }
$jar  = "$root/sim/app/sidelane-sim.jar"
$jna  = "$root/sim/docker/lib/jna-5.14.0.jar"
$plug = "$root/native/windows-x64"                # LK LEGO binary (dllpqcpro.dll)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "运行 Bench $args ..." -ForegroundColor Green
& $java -cp "$jar;$jna" "-Dlego.lib.dir=$plug" "-Dfile.encoding=UTF-8" "-Dbench.out=$root/bench/out" com.lk.sim.bench.Bench @args
