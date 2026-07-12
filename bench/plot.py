#!/usr/bin/env python3
# 读 bench/out/*.csv → 出论文图(PNG+PDF)到 bench/fig/
import csv, os, statistics as st
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "out")
FIG  = os.path.join(HERE, "fig")
os.makedirs(FIG, exist_ok=True)

def read(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), bbox_inches="tight", dpi=150)
    plt.close(fig)
    print("  ->", name)

BLUE, RED, GREEN, ORANGE = "#2b6cb0", "#c53030", "#2f855a", "#dd6b20"

# ---------- 图3:E2 决策延迟 vs 验签延迟 ----------
def fig3():
    rows = read("E2_decision_vs_delay.csv")
    if not rows: return
    agg = defaultdict(lambda: defaultdict(list))  # delay -> mode -> [ms]
    for r in rows:
        agg[int(r["verify_delay_ms"])][r["mode"]].append(float(r["decision_ms"]))
    xs = sorted(agg)
    a = [st.median(agg[d]["A"]) for d in xs]
    b = [st.median(agg[d]["B"]) for d in xs]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(xs, a, "o-", color=RED, label="① Baseline (inline verify, on critical path)")
    ax.plot(xs, b, "s-", color=GREEN, label="② Scheme (pre-credit, async verify)")
    ax.plot(xs, xs, "--", color="#999", lw=1, label="y = verify delay (ref)")
    ax.axvline(209.9, color=ORANGE, ls=":", lw=1.5)
    ax.text(209.9, ax.get_ylim()[1]*0.05, " Leap 209.9ms", color=ORANGE, fontsize=8)
    ax.set_xlabel("Injected verify delay (ms)")
    ax.set_ylabel("Settlement-decision latency (ms, median)")
    ax.legend(fontsize=8); ax.grid(alpha=.3)  # no in-figure title; caption in paper
    save(fig, "fig3_decision_vs_delay")

# ---------- 图4:E3 吞吐 + e2e p99 ----------
def fig4():
    rows = read("E3_throughput.csv")
    if not rows: return
    d = defaultdict(dict)
    for r in rows:
        d[r["mode"]][int(r["N"])] = r
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    for mode, col, lab in (("A", RED, "① Baseline"), ("B", GREEN, "② Scheme")):
        Ns = sorted(d[mode])
        ax1.plot(Ns, [float(d[mode][n]["tps"]) for n in Ns], "o-", color=col, label=lab)
        ax2.plot(Ns, [float(d[mode][n]["e2e_p99_ms"]) for n in Ns], "s-", color=col, label=lab)
    ax1.set_xlabel("Concurrency N"); ax1.set_ylabel("Decision throughput (tps)"); ax1.set_title("(a)", fontsize=9, loc="left"); ax1.legend(fontsize=8); ax1.grid(alpha=.3)
    ax2.set_xlabel("Concurrency N"); ax2.set_ylabel("End-to-end p99 (ms)"); ax2.set_title("(b)", fontsize=9, loc="left"); ax2.legend(fontsize=8); ax2.grid(alpha=.3)
    save(fig, "fig4_throughput")

# ---------- 图5:E4 报文尺寸敏感性 ----------
def fig5():
    rows = read("E4_message_size.csv")
    if not rows: return
    agg = defaultdict(lambda: defaultdict(list))  # iso_bytes -> mode -> ms
    for r in rows:
        agg[int(r["iso_bytes"])][r["mode"]].append(float(r["decision_ms"]))
    xs = sorted(agg)
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for mode, col, lab in (("A", RED, "① Baseline"), ("B", GREEN, "② Scheme")):
        ax.plot([x/1024 for x in xs], [st.median(agg[x][mode]) for x in xs], "o-", color=col, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel("ISO 20022 message size (KiB, log)")
    ax.set_ylabel("Decision latency (ms, median)")
    ax.legend(fontsize=8); ax.grid(alpha=.3, which="both")
    save(fig, "fig5_message_size")

# ---------- 图6:E5 看门狗分量 ----------
def fig6():
    rows = read("E5_watchdog.csv")
    if not rows: return
    xs = [int(r["verify_delay_ms"]) for r in rows]
    C  = [float(r["E_Tc_ms"]) for r in rows]
    R  = [float(r["twoRTT_ms"]) for r in rows]
    K  = [float(r["k_sigma_ms"]) for r in rows]
    T  = [float(r["T_timeout_ms"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.bar(range(len(xs)), C, label="E[T_c]", color=BLUE)
    ax.bar(range(len(xs)), R, bottom=C, label="2·T_RTT", color=GREEN)
    ax.bar(range(len(xs)), K, bottom=[c+r for c,r in zip(C,R)], label="k·σ", color=ORANGE)
    ax.plot(range(len(xs)), T, "k*-", label="T_timeout (realised)")
    ax.set_xticks(range(len(xs))); ax.set_xticklabels(xs)
    ax.set_xlabel("Injected verify delay (ms)")
    ax.set_ylabel("ms")
    ax.legend(fontsize=8); ax.grid(alpha=.3, axis="y")
    save(fig, "fig6_watchdog")

# ---------- E8 微基准条形 ----------
def fig_e8():
    rows = read("E8_crypto_microbench.csv")
    if not rows: return
    en = {"nested_sign": "Nested sign", "nested_verify": "Nested verify",
          "kem_encap": "KEM encap", "kem_decap": "KEM decap",
          "dep_seal": "DEP seal", "dep_open": "DEP open"}
    ops = [en.get(r["operation"], r["operation"]) for r in rows]
    p50 = [float(r["p50_us"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ax.barh(ops, p50, color=BLUE)
    for i,v in enumerate(p50): ax.text(v, i, f" {v:.0f}µs", va="center", fontsize=8)
    ax.set_xlabel("p50 latency (µs)")
    ax.grid(alpha=.3, axis="x")
    save(fig, "fig_e8_crypto")

# ---------- 图7:E9 WAN 决策延迟 vs 每跳网络延迟 ----------
def fig7():
    rows = read("E9_wan.csv")
    if not rows: return
    agg = defaultdict(lambda: defaultdict(list))  # net_delay -> mode -> [ms]
    for r in rows:
        agg[int(r["net_delay_ms"])][r["mode"]].append(float(r["decision_ms"]))
    xs = sorted(agg)
    a = [st.median(agg[d]["A"]) for d in xs]
    b = [st.median(agg[d]["B"]) for d in xs]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(xs, a, "o-", color=RED, label="① Baseline (3 hops to RTGS)")
    ax.plot(xs, b, "s-", color=GREEN, label="② Scheme (6 hops via DEP+coordinator)")
    # 线性拟合斜率(每 ms 每跳)
    if len(xs) > 1:
        import numpy as np
        sa = np.polyfit(xs, a, 1)[0]; sb = np.polyfit(xs, b, 1)[0]
        ax.text(0.04, 0.92, f"slope A={sa:.2f} ms/ms\nslope B={sb:.2f} ms/ms",
                transform=ax.transAxes, fontsize=8, va="top",
                bbox=dict(boxstyle="round", fc="#f4f4f4", ec="#ccc"))
    ax.set_xlabel("Per-hop one-way network delay (ms, tc netem)")
    ax.set_ylabel("Settlement-decision latency (ms, median)")
    ax.legend(fontsize=8); ax.grid(alpha=.3)
    save(fig, "fig7_wan")

if __name__ == "__main__":
    print("figures ->", FIG)
    for fn in (fig3, fig4, fig5, fig6, fig_e8, fig7):
        try: fn()
        except Exception as e: print("  !", fn.__name__, e)
    print("done")
