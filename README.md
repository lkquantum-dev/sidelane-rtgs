# SideLane-RTGS

**A protocol-level, reproducible testbed for post-quantum migration of RTGS, calibrated against BIS Project Leap Phase 2.** Slow PQC verification is moved to a *side lane* — off the synchronous settlement path — via a pre-credit / asynchronous-verify / compensating-rollback cycle.

Artifact for the paper:

> **A Protocol-Level, Reproducible Testbed for Post-Quantum Migration of RTGS: Engineering Realisation and Validation of the Modular Decoupling Scheme.** Rui Liu. (Manuscript, 2026. 中文版:《面向 RTGS 后量子迁移的协议级可复现测试床:模块化解耦方案的工程实现与验证》。)

Companion papers:
- Analytical: *A Cost-Model Audit of Project Leap Phase 2: Latency, Capacity, and Migration Safety in Post-Quantum RTGS.* R. Liu, N. Zeng. Accepted at WorldS4 2026 (Springer LNNS).
- Architecture: 《金融基础设施后量子迁移的模块化解耦架构》. 刘锐 等. 已录用,《科技导报》(in Chinese).

## Quick start

The one-click launcher checks/installs Java, verifies the files, and shows a run menu:

- **Windows** — open this folder and **double-click `setup-windows.bat`**.
- **Linux / Ubuntu** — in this folder, run **`bash setup-ubuntu.sh`**.
- **Any OS with Docker** — `cd sim/docker && docker compose up --build`, then open http://127.0.0.1:8080

No build step: the testbed ships as a prebuilt JAR. Per-platform details are below.

## What this is

A runnable, protocol-level digital twin of an RTGS post-quantum migration:

- Every role (participant bank, NSP, New NSP, New ESMIG, ESMIG, PQC-SVS, RTGS core) is a **real process** speaking a **real TCP envelope protocol**, carrying **real ISO 20022 pacs.008 + BAH** messages (schema-validated against the official XSDs);
- **Real cryptography**: nested ML-DSA-87 + RSA-2048 signatures at the BAH, ML-KEM-768 + RSA-OAEP hybrid KEM + AES-256-GCM tunnel at the DEP leg;
- Three topologies: **inline baseline** (Leap's behaviour), **side-lane**, and **coordinator** (PQC-SVS drives the ledger via the pre-credit / async-verify / compensating-rollback cycle S1–S4b);
- The Watchdog inequality `T_timeout ≥ E[T_pqc] + 2·T_RTT + k·σ` enforced online via EWMA estimates;
- Same image deploys as a **single process** or a **12-container Docker topology** (with optional `tc netem` WAN shaping).

All figures and tables in the paper regenerate deterministically from the CSVs in `bench/out/`.

## Layout

```
sim/app/sidelane-sim.jar         Testbed executable (prebuilt, JDK 21): nodes, protocol,
                                 crypto bridge, ISO 20022 validation, bench harness, WebUI
sim/docker/      Dockerfile + compose topologies (single image / 12-container tier-3)
setup-windows.bat                Windows one-click env-check + launcher menu
setup-ubuntu.sh                  Linux one-click env-check + launcher menu
sim/run_webui.ps1 / .sh          Interactive WebUI launcher (Windows / Linux)
bench/run_bench.ps1 / .sh        One-click experiments E2–E8 → bench/out/*.csv
bench/e9_wan.py, e9_wan.ps1      Cross-container WAN-shaping harness (E9)
bench/plot.py                    Regenerate all charts from CSVs (plot_cn.py: Chinese labels)
bench/arch_figs.py               Regenerate architecture & sequence diagrams (Fig. 1–2)
bench/out/                       CSVs behind every figure/table in the paper
bench/fig/                       Pre-rendered figures, PNG (Chinese via plot_cn.py)
native/                          LK LEGO PQC library, binary distribution (see below)
```

The testbed executable is distributed **prebuilt** (`sim/app/sidelane-sim.jar`, Java 17
bytecode). Three ways to run it, by platform.

## Run on Windows (single process)

**One-click:** double-click `setup-windows.bat` — it checks for Java (offers to install
via winget if missing), verifies the files, and gives a menu (WebUI / experiments /
quick self-test).

Or run the launchers directly. Prereqs: Java 17+ runtime on `PATH` (or set `JAVA_HOME`).
No build step. Uses `native/windows-x64/dllpqcpro.dll`.

```powershell
# interactive digital-twin WebUI at http://127.0.0.1:8080
powershell -ExecutionPolicy Bypass -File sim/run_webui.ps1

# headless: run experiments E2-E8 (all, or a subset: e2 e5 ...)
powershell -ExecutionPolicy Bypass -File bench/run_bench.ps1
```

## Run on Linux / Ubuntu (single process)

**One-click:** `bash setup-ubuntu.sh` — it checks for Java (offers to `apt install` if
missing), verifies the files, and gives a menu (WebUI / experiments / self-test / Docker).

Or run the launchers directly. Prereqs: Java 17+ runtime on `PATH`
(`sudo apt install openjdk-21-jre-headless`, or 17+). No build step. Uses
`native/linux-x64/libpqcpro_unix.so`.

```bash
# interactive digital-twin WebUI at http://127.0.0.1:8080
bash sim/run_webui.sh

# headless: run experiments E2-E8 (all, or a subset: e2 e5 ...)
bash bench/run_bench.sh
```

## Run with Docker (any OS: Windows / Ubuntu / macOS)

Prereqs: Docker (Desktop or Engine) + Compose. No Java needed on the host.

```bash
cd sim/docker
docker compose up --build                          # single image, WebUI at :8080
docker compose -f compose.tier3.yaml up --build    # 12-container topology
NET_DELAY=5ms docker compose up --build            # inject per-hop delay (tc netem)
```

The cross-container WAN sweep (E9) drives the 12-container topology:

```bash
python bench/e9_wan.py        # Linux/macOS host
# or:  powershell -File bench/e9_wan.ps1   # Windows host
```

## Regenerate figures from the CSVs

Prereqs: Python 3 + matplotlib.

```bash
python bench/plot.py        # English charts -> bench/fig/
python bench/arch_figs.py   # architecture + sequence diagrams (Fig. 1-2)
python bench/plot_cn.py     # optional: Chinese-label charts -> bench/fig_cn/
```

## Cryptography backend

The PQC primitives (ML-DSA-87, ML-KEM-768) are provided by the **LK LEGO** PQC platform,
a production-grade C library by Suzhou LangKong Post-Quantum Technology Co., Ltd.
It is distributed here **in binary form only** for replication (`native/`); the classical
RSA layer uses the standard Java JCA. The testbed talks to the library through a narrow,
flat C ABI (the exported symbols are visible in the binaries), so an alternative backend
exposing the same surface can substitute it; protocol-level results do not depend on the
specific backend, only absolute microbenchmark numbers do.

## Reported environment

12th-gen Intel CPU, JDK 21, native LK LEGO library. Absolute latency/throughput numbers
are environment-dependent; the paper's claims concern protocol behaviour and calibrated
latency composition (see the paper's "fidelity boundary" section).

## License

Scripts and data (`bench/`, `sim/docker/` build files): research/evaluation use — see [LICENSE](LICENSE).
Executables (`sim/app/sidelane-sim.jar`, `native/` libraries): proprietary, run-only for
research/replication, redistribution restricted — see [LICENSE](LICENSE) and `native/README.md`.
Third-party components: see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
