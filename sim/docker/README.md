# SideLane-RTGS 组态仿真 · Docker(跨平台)

一份 **Linux 镜像**,在 **Windows / Ubuntu / macOS** 上经 Docker 一致运行。容器内是 5 个真实节点
(真 TCP + 真嵌套混合签名/验签 + 真实 ISO 20022),内嵌组态 WebUI。
PQC 原生层用 Linux 版 `libpqcpro_unix.so`(取自 `native/linux-x64/`,随镜像打包,仅依赖 glibc)。

## 一键启动
```bash
cd sim/docker
docker compose up --build
# 浏览器打开 http://localhost:8080
```
停止:`docker compose down`。

> 已在 x64 Windows + Docker Desktop(WSL2,Docker 29.x)实跑通过:构建→启动→5 节点就绪→
> 真 ML-DSA-87/ML-KEM-768 验签 + 真 ISO 20022 schema 校验 + 看门狗 + 结算全链路。

## 两个曾踩的坑(已在代码/镜像里修好,无需你处理)
1. **`.so` 可执行栈被内核拒绝**:`cannot enable executable stack as shared object requires`。
   原因是库内手写汇编未带 `.note.GNU-stack` → PT_GNU_STACK 标了可执行(0x7)。
   修复:`docker/clear_execstack.py` 清掉 PF_X(0x7→0x6),**已在 Dockerfile 构建期自动执行**(自愈,换库也不怕)。
2. **绑定 127.0.0.1 → 容器端口映射不通**:WebUI/节点改绑 `0.0.0.0`,Docker 的 `8080:8080` 才到得了。

## 注入真实网络延迟(让看门狗不等式更真实)
不设则节点间走容器回环(微秒级)。设 `NET_DELAY` 后,用 netem 对 `lo` 注入单向延迟,
节点间 TCP 的 **RTT ≈ 2×NET_DELAY**,论文看门狗 `T_timeout ≥ E[Tc]+2·T_RTT+k·σ` 中的
`2·T_RTT` 项即变成可观的毫秒级:

- **Linux/macOS:**
  ```bash
  NET_DELAY=5ms NET_JITTER=1ms docker compose up --build
  ```
- **Windows PowerShell:**
  ```powershell
  $env:NET_DELAY="5ms"; $env:NET_JITTER="1ms"; docker compose up --build
  ```
(需 `cap_add: NET_ADMIN`,compose 已配置。)

## 镜像内容
- `eclipse-temurin:21-jre` 运行时 + `iproute2`(netem)
- `/app/sidelane-sim.jar`(预编译)+ `/app/libs/jna.jar` + `/app/lib/libpqcpro_unix.so`
- 入口 `entrypoint.sh`:按 `NET_DELAY` 选配 netem,再启 `com.lk.sim.web.SimServer`
- 构建期用仓库内 JNA jar 直接 `javac` 编译,**不联网拉依赖**

## 与原生(便携 JDK)运行的关系
- 本机快速跑:`powershell -File sim/run_webui.ps1`(用 Windows dll)
- 跨平台/可复现/可整形网络:本目录 `docker compose up`(用 Linux .so)
- 两者跑的是**同一套 Java 代码**,仅原生库与网络环境不同。

## 真 Tier 3:12 容器(并排双流水线,11 节点 + Web 聚合)
两条流水线各节点一个独立容器、各自 netem;Web 聚合容器收事件、发页面、转发控制。
```
① Leap 基线: part-a → nsp-a → esmig-a → rtgs-a(内联验签)
② 论文方案: part-b → nsp-b → new-nsp-b → new-esmig-b → esmig-b → rtgs-b → svs-b
```
```bash
cd sim/docker
docker compose -f compose.tier3.yaml up --build        # → http://localhost:8080(点 ▶ 并排对比)
# 节点间真实 RTT(整形各容器 eth0 出口):
NET_DELAY=5ms NET_JITTER=1ms docker compose -f compose.tier3.yaml up --build
```
> 已实测:12 容器全部 Up、跨容器握手成功、`/compare` 同时跑通两条线并在 Web 聚合。
- 节点容器入口 `com.lk.sim.node.NodeMain`(读环境变量 NODE_ID/ROLE/PORT/CONNECT/ROUTE,事件 HTTP 上报 `web:8080/ingest`,控制面 `:8090`)。
- Web 容器入口 `com.lk.sim.web.WebServer`(页面+SSE+`/ingest`聚合+`/submit`/`/config`转发到节点)。
- 拨号带重试 → 容器启动顺序无关;节点按主机名连接(Docker DNS)。
- **已用 6 个本机进程模拟验证**:跨进程事件聚合 + 完整编排 + 控制转发全部跑通(Docker 仅再加命名空间隔离与 netem)。

> 单镜像版(`compose.yaml`,1 容器内 5 节点)更轻量;多容器版(`compose.tier3.yaml`)更贴近真实分布式部署。两者同一份代码、同一镜像,仅 `APP` 环境变量不同。
