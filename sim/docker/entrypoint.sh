#!/usr/bin/env bash
set -e

# 可选:netem 注入真实网络延迟/抖动
#   单镜像(SimServer):NET_DEV=lo(默认),整形容器内回环
#   多容器(node/web):NET_DEV=eth0,整形容器出口 → 节点间真实 RTT
NET_DEV="${NET_DEV:-lo}"
if [ -n "${NET_DELAY:-}" ]; then
  ARGS="delay ${NET_DELAY}"
  [ -n "${NET_JITTER:-}" ] && ARGS="${ARGS} ${NET_JITTER}"
  if tc qdisc replace dev "${NET_DEV}" root netem ${ARGS} 2>/dev/null; then
    echo "[sim] netem: ${NET_DEV} ${ARGS}"
  else
    echo "[sim] 警告:无法设置 netem(需 cap_add: NET_ADMIN);原速运行"
  fi
fi

case "${APP:-sim}" in
  node) MAIN=com.lk.sim.node.NodeMain ;;
  web)  MAIN=com.lk.sim.web.WebServer ;;
  *)    MAIN=com.lk.sim.web.SimServer ;;
esac

exec java -cp "/app/sidelane-sim.jar:/app/libs/jna.jar" \
  -Dlego.lib.dir=/app/lib -Dfile.encoding=UTF-8 \
  "${MAIN}"
