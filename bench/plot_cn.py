#!/usr/bin/env python3
# 中文版图:读 bench/out/*.csv → bench/fig_cn/(图内文字中文,SimHei)
import csv, os, statistics as st
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

FONT = "C:/Windows/Fonts/simhei.ttf"
fm.fontManager.addfont(FONT)
_name = fm.FontProperties(fname=FONT).get_name()
plt.rcParams["font.sans-serif"] = [_name]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "out")
FIG  = os.path.join(HERE, "fig_cn")
os.makedirs(FIG, exist_ok=True)

def read(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), bbox_inches="tight", dpi=150)
    plt.close(fig); print("  ->", name)

BLUE, RED, GREEN, ORANGE = "#2b6cb0", "#c53030", "#2f855a", "#dd6b20"

def fig3():
    rows = read("E2_decision_vs_delay.csv")
    if not rows: return
    agg = defaultdict(lambda: defaultdict(list))
    for r in rows: agg[int(r["verify_delay_ms"])][r["mode"]].append(float(r["decision_ms"]))
    xs = sorted(agg)
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(xs, [st.median(agg[d]["A"]) for d in xs], "o-", color=RED, label="① 基线(内联验签,关键路径)")
    ax.plot(xs, [st.median(agg[d]["B"]) for d in xs], "s-", color=GREEN, label="② 方案(预授信,异步验签)")
    ax.plot(xs, xs, "--", color="#999", lw=1, label="y = 验签延迟(参考线)")
    ax.axvline(209.9, color=ORANGE, ls=":", lw=1.5)
    ax.text(209.9, ax.get_ylim()[1]*0.05, " Leap 209.9ms", color=ORANGE, fontsize=8)
    ax.set_xlabel("注入验签延迟 (ms)"); ax.set_ylabel("结算决策延迟 (ms,中位)")
    ax.legend(fontsize=8); ax.grid(alpha=.3)  # 标题不入图,图题见正文图注
    save(fig, "fig3_decision_vs_delay")

def fig4():
    rows = read("E3_throughput.csv")
    if not rows: return
    d = defaultdict(dict)
    for r in rows: d[r["mode"]][int(r["N"])] = r
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    for mode, col, lab in (("A", RED, "① 基线"), ("B", GREEN, "② 方案")):
        Ns = sorted(d[mode])
        a1.plot(Ns, [float(d[mode][n]["tps"]) for n in Ns], "o-", color=col, label=lab)
        a2.plot(Ns, [float(d[mode][n]["e2e_p99_ms"]) for n in Ns], "s-", color=col, label=lab)
    a1.set_xlabel("并发 N"); a1.set_ylabel("决策吞吐 (tps)"); a1.set_title("(a)", fontsize=9, loc="left"); a1.legend(fontsize=8); a1.grid(alpha=.3)
    a2.set_xlabel("并发 N"); a2.set_ylabel("端到端 p99 (ms)"); a2.set_title("(b)", fontsize=9, loc="left"); a2.legend(fontsize=8); a2.grid(alpha=.3)
    save(fig, "fig4_throughput")

def fig5():
    rows = read("E4_message_size.csv")
    if not rows: return
    agg = defaultdict(lambda: defaultdict(list))
    for r in rows: agg[int(r["iso_bytes"])][r["mode"]].append(float(r["decision_ms"]))
    xs = sorted(agg)
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for mode, col, lab in (("A", RED, "① 基线"), ("B", GREEN, "② 方案")):
        ax.plot([x/1024 for x in xs], [st.median(agg[x][mode]) for x in xs], "o-", color=col, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel("ISO 20022 报文尺寸 (KiB,对数)"); ax.set_ylabel("决策延迟 (ms,中位)")
    ax.legend(fontsize=8); ax.grid(alpha=.3, which="both")  # 标题不入图
    save(fig, "fig5_message_size")

def fig6():
    rows = read("E5_watchdog.csv")
    if not rows: return
    xs = [int(r["verify_delay_ms"]) for r in rows]
    C = [float(r["E_Tc_ms"]) for r in rows]; R = [float(r["twoRTT_ms"]) for r in rows]
    K = [float(r["k_sigma_ms"]) for r in rows]; T = [float(r["T_timeout_ms"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.bar(range(len(xs)), C, label="E[T_c]", color=BLUE)
    ax.bar(range(len(xs)), R, bottom=C, label="2·T_RTT", color=GREEN)
    ax.bar(range(len(xs)), K, bottom=[c+r for c,r in zip(C,R)], label="k·σ", color=ORANGE)
    ax.plot(range(len(xs)), T, "k*-", label="T_timeout(实测)")
    ax.set_xticks(range(len(xs))); ax.set_xticklabels(xs)
    ax.set_xlabel("注入验签延迟 (ms)"); ax.set_ylabel("毫秒")
    ax.legend(fontsize=8); ax.grid(alpha=.3, axis="y")  # 标题不入图
    save(fig, "fig6_watchdog")

def fig_e8():
    rows = read("E8_crypto_microbench.csv")
    if not rows: return
    zh = {"nested_sign":"嵌套签名","nested_verify":"嵌套验签","kem_encap":"KEM 封装",
          "kem_decap":"KEM 解封","dep_seal":"DEP 密封","dep_open":"DEP 解封"}
    ops = [zh.get(r["operation"], r["operation"]) for r in rows]
    p50 = [float(r["p50_us"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ax.barh(ops, p50, color=BLUE)
    for i,v in enumerate(p50): ax.text(v, i, f" {v:.0f}", va="center", fontsize=8)
    ax.set_xlabel("p50 延迟 (微秒)")
    ax.grid(alpha=.3, axis="x")  # 标题不入图
    save(fig, "fig_e8_crypto")

def fig7():
    rows = read("E9_wan.csv")
    if not rows: return
    agg = defaultdict(lambda: defaultdict(list))
    for r in rows: agg[int(r["net_delay_ms"])][r["mode"]].append(float(r["decision_ms"]))
    xs = sorted(agg)
    a = [st.median(agg[d]["A"]) for d in xs]; b = [st.median(agg[d]["B"]) for d in xs]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(xs, a, "o-", color=RED, label="① 基线(到 RTGS 共 3 跳)")
    ax.plot(xs, b, "s-", color=GREEN, label="② 方案(经 DEP+枢纽共 6 跳)")
    if len(xs) > 1:
        import numpy as np
        sa = np.polyfit(xs, a, 1)[0]; sb = np.polyfit(xs, b, 1)[0]
        ax.text(0.04, 0.92, f"基线斜率={sa:.2f} ms/ms\n方案斜率={sb:.2f} ms/ms",
                transform=ax.transAxes, fontsize=8, va="top",
                bbox=dict(boxstyle="round", fc="#f4f4f4", ec="#ccc"))
    ax.set_xlabel("每跳单向网络延迟 (ms,tc netem)"); ax.set_ylabel("结算决策延迟 (ms,中位)")
    ax.legend(fontsize=8); ax.grid(alpha=.3)  # 标题不入图
    save(fig, "fig7_wan")

if __name__ == "__main__":
    print("中文字体:", _name, "| 输出:", FIG)
    for fn in (fig3, fig4, fig5, fig6, fig_e8, fig7):
        try: fn()
        except Exception as e: print("  !", fn.__name__, e)
    print("done")
