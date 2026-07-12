#!/usr/bin/env bash
# SideLane-RTGS · Ubuntu/Linux 环境准备与启动器
# 用法:  bash setup-ubuntu.sh            # 检查环境并进入菜单
#         bash setup-ubuntu.sh --check    # 仅检查环境,不进菜单
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1

if [ -t 1 ]; then C='\033[36m'; G='\033[32m'; Y='\033[33m'; R='\033[31m'; N='\033[0m'; else C=''; G=''; Y=''; R=''; N=''; fi
sect() { printf "\n${C}%s${N}\n" "$1"; }
ok()   { printf "  ${G}[OK]${N}  %s\n" "$1"; }
warn() { printf "  ${Y}[!] ${N}  %s\n" "$1"; }
bad()  { printf "  ${R}[X] ${N}  %s\n" "$1"; }

# ---- Java 检测:返回主版本到 $JAVA_MAJOR,可执行路径到 $JAVA_BIN ----
JAVA_BIN=""; JAVA_MAJOR=0
detect_java() {
  local cand=""
  [ -n "${JAVA_HOME:-}" ] && [ -x "$JAVA_HOME/bin/java" ] && cand="$JAVA_HOME/bin/java"
  [ -z "$cand" ] && command -v java >/dev/null 2>&1 && cand="$(command -v java)"
  [ -z "$cand" ] && return 1
  local v; v="$($cand -version 2>&1 | head -1)"
  local major; major="$(printf '%s' "$v" | sed -E 's/.*version "([0-9]+).*/\1/')"
  [ "$major" = "1" ] && major=8
  JAVA_BIN="$cand"; JAVA_MAJOR="${major:-0}"
  return 0
}

printf "${C}==================================================${N}\n"
printf "${C} SideLane-RTGS  ·  Ubuntu/Linux 环境准备与启动器${N}\n"
printf "${C}==================================================${N}\n"

sect "1) 检查 Java 运行时(需 17 及以上)"
if detect_java && [ "$JAVA_MAJOR" -ge 17 ]; then
  ok "Java $JAVA_MAJOR  →  $JAVA_BIN"
else
  [ "$JAVA_MAJOR" -gt 0 ] && bad "找到 Java $JAVA_MAJOR,版本过低(需 17+)" || bad "未找到 Java"
  if [ "$CHECK" = 1 ]; then
    warn "请安装:sudo apt-get install -y openjdk-21-jre-headless"
    exit 1
  fi
  if command -v apt-get >/dev/null 2>&1; then
    printf "\n"; read -r -p "   是否用 apt 安装 openjdk-21-jre-headless?(需 sudo)[y/N] " ans
    if printf '%s' "$ans" | grep -qi '^y'; then
      sudo apt-get update && sudo apt-get install -y openjdk-21-jre-headless
      detect_java && [ "$JAVA_MAJOR" -ge 17 ] && ok "已安装 Java $JAVA_MAJOR" || { bad "安装后仍未检测到 Java,请检查"; exit 1; }
    else
      warn "请手动安装 Java 17+ 后重试。"; exit 1
    fi
  else
    warn "未检测到 apt。请按发行版安装 Java 17+(OpenJDK)后重试。"; exit 1
  fi
fi

sect "2) 校验运行所需文件"
declare -A NEED=(
  ["测试床程序 (JAR)"]="sim/app/sidelane-sim.jar"
  ["JNA 库"]="sim/docker/lib/jna-5.14.0.jar"
  ["LK LEGO 原生库"]="native/linux-x64/libpqcpro_unix.so"
  ["WebUI 启动脚本"]="sim/run_webui.sh"
  ["基准启动脚本"]="bench/run_bench.sh"
)
allok=1
for k in "${!NEED[@]}"; do
  if [ -f "$ROOT/${NEED[$k]}" ]; then ok "$k"; else bad "$k  缺失:${NEED[$k]}"; allok=0; fi
done
[ "$allok" = 1 ] || { printf "\n"; bad "仓库文件不完整,请确认已完整克隆/解压。"; exit 1; }

printf "\n"; ok "环境就绪。"
[ "$CHECK" = 1 ] && exit 0

has_docker() { command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; }

while true; do
  sect "3) 选择要做什么"
  printf "    [1] 启动交互式 WebUI(原生)   浏览器 http://127.0.0.1:8080,Ctrl+C 停止\n"
  printf "    [2] 跑全部基准实验 E2-E8(原生) 结果写入 bench/out/*.csv\n"
  printf "    [3] 快速自检(只跑 E8,约 10 秒)\n"
  printf "    [4] Docker:单镜像              需已装 Docker + Compose\n"
  printf "    [5] Docker:12 容器完整拓扑     需已装 Docker + Compose\n"
  printf "    [q] 退出\n"
  read -r -p "   输入选项:" c
  case "$c" in
    1) bash "$ROOT/sim/run_webui.sh" ;;
    2) bash "$ROOT/bench/run_bench.sh" ;;
    3) bash "$ROOT/bench/run_bench.sh" e8; printf "\n"; ok "自检完成,见 bench/out/E8_crypto_microbench.csv" ;;
    4) if has_docker; then ( cd "$ROOT/sim/docker" && docker compose up --build ); else bad "未检测到可用 Docker"; fi ;;
    5) if has_docker; then ( cd "$ROOT/sim/docker" && docker compose -f compose.tier3.yaml up --build ); else bad "未检测到可用 Docker"; fi ;;
    q|Q) break ;;
    *) warn "无效选项" ;;
  esac
done
printf "${C}再见。${N}\n"
