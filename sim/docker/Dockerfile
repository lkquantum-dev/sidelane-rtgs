# SideLane-RTGS 组态仿真(校准对照 BIS Project Leap)—— 单镜像(Linux),跨平台一致运行(Win/Ubuntu/Mac via Docker)
# 构建上下文 = 仓库根(见 compose.yaml: context: ../..);节点程序以预编译 JAR 分发(sim/app/sidelane-sim.jar)

# ---- prep:清除 .so 的可执行栈标志(否则现代内核/容器拒绝加载),自愈式,无论源库是否已打补丁 ----
FROM eclipse-temurin:21-jre AS prep
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*
COPY native/linux-x64/libpqcpro_unix.so /so/libpqcpro_unix.so
COPY sim/docker/clear_execstack.py /clear_execstack.py
RUN python3 /clear_execstack.py /so/libpqcpro_unix.so

# ---- runtime:JRE 21 + 预编译 JAR + LK LEGO Linux .so + iproute2(netem)----
FROM eclipse-temurin:21-jre
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY sim/app/sidelane-sim.jar /app/sidelane-sim.jar
COPY sim/docker/lib/jna-5.14.0.jar /app/libs/jna.jar
COPY --from=prep /so/libpqcpro_unix.so /app/lib/libpqcpro_unix.so
COPY sim/docker/entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh
EXPOSE 8080
# NET_DELAY/NET_JITTER 为空则不整形;设了则对 lo 注入(节点间 TCP 的真实 RTT≈2×NET_DELAY)
ENTRYPOINT ["/bin/bash","/app/entrypoint.sh"]
