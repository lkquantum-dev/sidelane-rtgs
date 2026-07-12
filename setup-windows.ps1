# SideLane-RTGS · Windows 环境准备与启动器
# 用法:双击 setup-windows.bat,或  powershell -ExecutionPolicy Bypass -File setup-windows.ps1
#      加 -Check 仅检查环境不进菜单:  ... -File setup-windows.ps1 -Check
param([switch]$Check)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Head($t) { Write-Host ""; Write-Host $t -ForegroundColor Cyan }
function OK($t)   { Write-Host "  [OK]  $t" -ForegroundColor Green }
function WARN($t) { Write-Host "  [!]   $t" -ForegroundColor Yellow }
function BAD($t)  { Write-Host "  [X]   $t" -ForegroundColor Red }

# ---- 1. 找 Java 并解析主版本 ----
function Find-Java {
  $cands = @()
  if ($env:JAVA_HOME) { $cands += (Join-Path $env:JAVA_HOME "bin\java.exe") }
  $onPath = (Get-Command java.exe -ErrorAction SilentlyContinue)
  if ($onPath) { $cands += $onPath.Source }
  foreach ($j in $cands) {
    if ($j -and (Test-Path $j)) {
      $out = (cmd /c "`"$j`" -version 2>&1") | Out-String
      $m = [regex]::Match($out, 'version "([0-9]+)(\.[0-9]+)?')
      if ($m.Success) {
        $major = [int]$m.Groups[1].Value
        if ($major -eq 1) { $major = 8 }  # "1.8" 记为 8
        return [pscustomobject]@{ Path = $j; Major = $major }
      }
    }
  }
  return $null
}

Write-Host "==================================================" -ForegroundColor White
Write-Host " SideLane-RTGS  ·  Windows 环境准备与启动器" -ForegroundColor White
Write-Host "==================================================" -ForegroundColor White

Write-Head "1) 检查 Java 运行时(需 17 及以上)"
$java = Find-Java
if ($java -and $java.Major -ge 17) {
  OK "Java $($java.Major)  →  $($java.Path)"
} else {
  if ($java) { BAD "找到 Java $($java.Major),但版本过低(需 17+)" }
  else       { BAD "未找到 Java" }
  if ($Check) {
    WARN "请安装 Java 17+ 后重试:https://adoptium.net"
    exit 1
  }
  Write-Host ""
  $ans = Read-Host "   是否用 winget 自动安装 Temurin 21 JRE?(需联网,可能弹管理员授权)[y/N]"
  if ($ans -match '^[Yy]') {
    try {
      winget install --id EclipseAdoptium.Temurin.21.JRE -e --accept-package-agreements --accept-source-agreements
      WARN "安装完成。请【关闭本窗口重新双击】本脚本,让 PATH 生效。"
    } catch {
      BAD "winget 安装失败:$_"
    }
  } else {
    WARN "请手动安装 Java 17+:https://adoptium.net  (安装时勾选 Add to PATH / Set JAVA_HOME)"
  }
  Write-Host ""
  Read-Host "按回车退出"
  exit 1
}

# ---- 2. 校验仓库文件 ----
Write-Head "2) 校验运行所需文件"
$need = @{
  "测试床程序 (JAR)" = "sim\app\sidelane-sim.jar"
  "JNA 库"           = "sim\docker\lib\jna-5.14.0.jar"
  "LK LEGO 原生库"   = "native\windows-x64\dllpqcpro.dll"
  "WebUI 启动脚本"   = "sim\run_webui.ps1"
  "基准启动脚本"     = "bench\run_bench.ps1"
}
$allok = $true
foreach ($k in $need.Keys) {
  $p = Join-Path $root $need[$k]
  if (Test-Path $p) { OK "$k" } else { BAD "$k  缺失:$($need[$k])"; $allok = $false }
}
if (-not $allok) {
  Write-Host ""
  BAD "仓库文件不完整,请确认已完整克隆/解压。"
  if (-not $Check) { Read-Host "按回车退出" }
  exit 1
}

Write-Host ""
OK "环境就绪。"
if ($Check) { exit 0 }

# ---- 3. 菜单 ----
if ($env:JAVA_HOME) { $env:PATH = "$env:JAVA_HOME\bin;$env:PATH" }
while ($true) {
  Write-Head "3) 选择要做什么"
  Write-Host "    [1] 启动交互式 WebUI     (浏览器 http://127.0.0.1:8080,Ctrl+C 停止)"
  Write-Host "    [2] 跑全部基准实验 E2-E8 (结果写入 bench\out\*.csv)"
  Write-Host "    [3] 快速自检             (只跑 E8 密码学微基准,约 10 秒)"
  Write-Host "    [q] 退出"
  $c = Read-Host "   输入选项"
  switch ($c) {
    "1" { & powershell -ExecutionPolicy Bypass -File (Join-Path $root "sim\run_webui.ps1") }
    "2" { & powershell -ExecutionPolicy Bypass -File (Join-Path $root "bench\run_bench.ps1") }
    "3" { & powershell -ExecutionPolicy Bypass -File (Join-Path $root "bench\run_bench.ps1") e8
          Write-Host ""; OK "自检完成,见 bench\out\E8_crypto_microbench.csv" }
    "q" { break }
    "Q" { break }
    default { WARN "无效选项" }
  }
}
Write-Host "再见。" -ForegroundColor Cyan
