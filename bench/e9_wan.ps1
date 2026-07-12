# E9 WAN 外部效度:对 12 容器 Tier3 的 11 个节点容器 eth0 注入 tc netem 逐级延迟,
# 测每跳单向延迟 → 决策延迟(基线 3 跳 / 方案 6 跳)+ 跨容器正确性(S1 双结算 / S4 双拒绝)。
$ErrorActionPreference = "Continue"
$root = (Resolve-Path "$PSScriptRoot/..").Path
$nodes = @("sidelane-part-a","sidelane-nsp-a","sidelane-esmig-a","sidelane-rtgs-a",
           "sidelane-part-b","sidelane-nsp-b","sidelane-new-nsp-b","sidelane-new-esmig-b","sidelane-esmig-b","sidelane-svs-b","sidelane-rtgs-b")
$out = "$root/bench/out/E9_wan.csv"
"net_delay_ms,mode,sample,decision_ms" | Out-File -Encoding utf8 $out
$correct = "$root/bench/out/E9_correctness.csv"
"net_delay_ms,scenario,partA_final,partB_final" | Out-File -Encoding utf8 $correct

function Set-Netem($ms) {
  foreach ($c in $nodes) {
    if ($ms -le 0) { docker exec $c tc qdisc del dev eth0 root 2>$null | Out-Null }
    else { docker exec $c tc qdisc replace dev eth0 root netem delay "${ms}ms" 2>$null | Out-Null }
  }
}

# 确保验签延迟=0(隔离纯网络效应)
Invoke-WebRequest -Uri "http://localhost:8080/config?verifyDelayMs=0" -UseBasicParsing | Out-Null

foreach ($d in @(0,5,10,20)) {
  Write-Host "=== NET_DELAY=${d}ms ==="
  Set-Netem $d
  Start-Sleep 2
  $log = "$root/bench/out/_e9_${d}.log"
  if (Test-Path $log) { Remove-Item -LiteralPath $log -Force }
  $p = Start-Process -FilePath "curl.exe" -ArgumentList "-N","-s","http://localhost:8080/events" -RedirectStandardOutput $log -WindowStyle Hidden -PassThru
  Start-Sleep 2
  # 15 次正常并排
  for ($i=0; $i -lt 15; $i++) { Invoke-WebRequest -Uri "http://localhost:8080/scenario?s=S1" -UseBasicParsing | Out-Null; Start-Sleep 1 }
  Start-Sleep 2
  # 1 次 S4 验正确性
  Invoke-WebRequest -Uri "http://localhost:8080/scenario?s=S4" -UseBasicParsing | Out-Null; Start-Sleep 3
  Invoke-WebRequest -Uri "http://localhost:8080/scenario?s=S1" -UseBasicParsing | Out-Null; Start-Sleep 3
  Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
  # 解析 decision
  $lines = Get-Content $log
  $sa=0;$sb=0
  foreach ($ln in $lines) {
    if ($ln -match '"detail":"A\|decision\|([0-9.]+)') { "$d,A,$sa,$($Matches[1])" | Out-File -Append -Encoding utf8 $out; $sa++ }
    if ($ln -match '"detail":"B\|decision\|([0-9.]+)') { "$d,B,$sb,$($Matches[1])" | Out-File -Append -Encoding utf8 $out; $sb++ }
  }
  Write-Host "  collected A=$sa B=$sb decision samples"
}
Set-Netem 0
Write-Host "E9 done -> $out"
