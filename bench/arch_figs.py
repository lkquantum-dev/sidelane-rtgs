#!/usr/bin/env python3
# 论文图1(测试床架构·双流水线) + 图2(S1–S4b 协同枢纽时序) → bench/fig/(EN) 与 bench/fig_cn/(CN)
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

FONT = "C:/Windows/Fonts/simhei.ttf"
fm.fontManager.addfont(FONT)
plt.rcParams["font.sans-serif"] = [fm.FontProperties(fname=FONT).get_name(), "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))

BLUE="#2b6cb0"; GREEN="#2f855a"; RED="#c53030"; ORANGE="#dd6b20"; GREY="#5b6677"; PUR="#6b46c1"; INK="#1a2233"

def box(ax,x,y,w,h,txt,fc="#eef3fb",ec=BLUE,fs=8,bold=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.5",fc=fc,ec=ec,lw=1.4))
    ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=fs,
            fontweight=("bold" if bold else "normal"),color=INK)

def arrow(ax,p,q,color="#33415f",lw=1.6,style="-|>",ls="-"):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle=style,mutation_scale=12,color=color,lw=lw,ls=ls,shrinkA=2,shrinkB=2))

def save(fig,outdir,name):
    os.makedirs(outdir,exist_ok=True)
    for e in ("png","pdf"): fig.savefig(os.path.join(outdir,f"{name}.{e}"),bbox_inches="tight",dpi=160)
    plt.close(fig); print("  ->",os.path.join(os.path.basename(outdir),name))

# ============================== 文案(EN/CN) ==============================
T = {
 "en": {
  "f1_title":"Fig. 1  Testbed architecture: two protocol-faithful pipelines side by side",
  "p1":"Pipeline ① — Leap baseline (inline)","p2":"Pipeline ② — decoupled scheme (coordinator)",
  "part":"Participant","nsp":"NSP","esmig":"ESMIG","rtgs":"RTGS Core",
  "nnsp":"New NSP","nesmig":"New ESMIG","svs":"PQC-SVS\n(coordinator)",
  "inline":"inline hybrid verify\non the critical path (blocking)",
  "nested":"nested signature:\ninner ML-DSA-87 + outer RSA-2048",
  "dep":"DEP leg: ML-KEM-768 + RSA-OAEP\nhybrid KEM → AES-256-GCM tunnel",
  "gate":"legacy gate:\nouter RSA only",
  "precredit":"pre-credit /\nverdict signals",
  "sidelane":"side-lane verify: inner ML-DSA\n+ EWMA watchdog",
  "variantC":"variant ③ (side-lane, §6.6): identical chain without the coordinator hop;\nRTGS orchestrates VERIFY/VERDICT against a PQC-SVS sidecar",
  "obs":"structured event stream → WebUI digital twin  ·  headless bench harness → CSV (all results)",
  "deploy":"same image: single-process\n(in-VM nodes) or 12-container\nDocker + tc netem",
  "tcp":"real TCP envelope protocol · real ISO 20022 pacs.008 + BAH",
  "f2_title":"Fig. 2  Pre-credit / async-verify / compensating-rollback (S1–S4b), coordinator topology",
  "ln":["Participant","ESMIG (legacy)","PQC-SVS (coordinator)","RTGS ledger"],
  "m_submit":"pacs.008 + BAH (nested sig), via NSP / New NSP / New ESMIG (DEP tunnel)",
  "m_s1":"S1  forward (outer-RSA gate passed)",
  "m_s2":"S2  pre-credit instruction",
  "m_pend":"mark Pending\n(bounded exposure)",
  "m_prov":"provisional receipt PRECREDITED  —  settlement decision ≈ 4 ms",
  "m_s3":"S3  verify inner ML-DSA off the critical path\nwatchdog: T_timeout ≥ E[Tpqc] + 2·T_RTT + k·σ (EWMA, online)",
  "alt_a":"S4a — verdict VALID","m_s4a":"VERDICT: VALID","m_commit":"commit\n(settled)","m_fin_a":"final receipt SETTLED",
  "alt_b":"S4b — invalid / watchdog exhausted (≤ 20 reconcile retries)",
  "m_s4b":"VERDICT: INVALID  /  retry budget exhausted","m_roll":"compensating\nrollback","m_fin_b":"final receipt ROLLED_BACK",
 },
 "cn": {
  "f1_title":"图1  测试床架构:两条协议级流水线并排运行",
  "p1":"流水线① — Leap 基线(内联)","p2":"流水线② — 解耦方案(协同枢纽)",
  "part":"参与行","nsp":"NSP","esmig":"ESMIG","rtgs":"RTGS 核心",
  "nnsp":"New NSP","nesmig":"New ESMIG","svs":"PQC-SVS\n(协同枢纽)",
  "inline":"内联混合验签\n(关键路径·阻塞)",
  "nested":"嵌套签名:\n内 ML-DSA-87 + 外 RSA-2048",
  "dep":"DEP 段:ML-KEM-768 + RSA-OAEP\n混合 KEM → AES-256-GCM 隧道",
  "gate":"存量门控:\n仅验外层 RSA",
  "precredit":"预授信 /\n判定信令",
  "sidelane":"侧道验签:内层 ML-DSA\n+ EWMA 看门狗",
  "variantC":"变体③(侧道,§6.6):链路相同但无枢纽跳;\n由 RTGS 经 VERIFY/VERDICT 编排 PQC-SVS 侧车",
  "obs":"结构化事件流 → WebUI 数字孪生  ·  无头基准框架 → CSV(本文全部数据)",
  "deploy":"同一镜像:单进程(VM 内节点)\n或 12 容器\nDocker + tc netem",
  "tcp":"真实 TCP 信封协议 · 真实 ISO 20022 pacs.008 + BAH",
  "f2_title":"图2  预授信/异步验签/补偿回滚(S1–S4b)·协同枢纽拓扑",
  "ln":["参与行","ESMIG(存量)","PQC-SVS(协同枢纽)","RTGS 账本"],
  "m_submit":"pacs.008 + BAH(嵌套签名),经 NSP / New NSP / New ESMIG(DEP 隧道)",
  "m_s1":"S1  转发(外层 RSA 门控通过)",
  "m_s2":"S2  预授信指令",
  "m_pend":"标记 Pending\n(敞口有界)",
  "m_prov":"临时回执 PRECREDITED — 结算决策 ≈ 4 ms",
  "m_s3":"S3  侧道验签内层 ML-DSA(不在关键路径)\n看门狗:T_timeout ≥ E[Tpqc] + 2·T_RTT + k·σ(EWMA 在线)",
  "alt_a":"S4a — 判定有效","m_s4a":"VERDICT: VALID","m_commit":"最终确认\n(settled)","m_fin_a":"最终回执 SETTLED",
  "alt_b":"S4b — 判定无效 / 看门狗耗尽(≤20 次对账重试)",
  "m_s4b":"VERDICT: INVALID / 重试预算耗尽","m_roll":"补偿回滚","m_fin_b":"最终回执 ROLLED_BACK",
 },
}

# ============================== 图1 架构 ==============================
def fig1(L, outdir):
    fig,ax=plt.subplots(figsize=(10.6,6.2)); ax.set_xlim(0,100); ax.set_ylim(0,64); ax.axis("off")
    # 标题不入图:图题由论文正文图注(图下)给出
    # —— 流水线① 基线 ——
    ax.add_patch(Rectangle((1,48),98,11.5,fc="#fbfcfe",ec="#aabbd0",lw=1.0,ls="--"))
    ax.text(2.5,57.6,L["p1"],fontsize=9,color=GREY,fontweight="bold")
    bw,bh,y1=12,5,50
    xs=[4,22,40,58]
    for x,t in zip(xs,[L["part"],L["nsp"]+"-A",L["esmig"]+"-A",L["rtgs"]+" A"]):
        box(ax,x,y1,bw,bh,t,fs=8)
    for i in range(3): arrow(ax,(xs[i]+bw,y1+bh/2),(xs[i+1],y1+bh/2))
    box(ax,75,y1-0.4,23,5.8,L["inline"],fc="#fdeeee",ec=RED,fs=7.0)
    arrow(ax,(xs[3]+bw,y1+bh/2),(75,y1+2.5),color=RED)
    # —— 流水线② 方案 ——
    ax.add_patch(Rectangle((1,21),98,24,fc="#fbfcfe",ec="#aabbd0",lw=1.0,ls="--"))
    ax.text(2.5,43.0,L["p2"],fontsize=9,color=GREY,fontweight="bold")
    y2=34; w2=11.2
    xs2=[3,17.5,32,46.5,61,75.5]
    names=[L["part"],L["nsp"]+"-B",L["nnsp"],L["nesmig"],L["esmig"]+"-B",L["svs"]]
    cols=[("#eef3fb",BLUE),("#eef3fb",BLUE),("#eefaf0",GREEN),("#eefaf0",GREEN),("#eef3fb",BLUE),("#f3effc",PUR)]
    for x,t,(fc,ec) in zip(xs2,names,cols):
        box(ax,x,y2,w2,6,t,fc=fc,ec=ec,fs=7.5)
    for i in range(5): arrow(ax,(xs2[i]+w2,y2+3),(xs2[i+1],y2+3))
    box(ax,89.5,y2,9,6,L["rtgs"]+" B",fc="#fff7e6",ec=ORANGE,fs=7.5)
    arrow(ax,(xs2[5]+w2,y2+4.2),(89.5,y2+4.2),color=PUR)
    arrow(ax,(89.5,y2+1.8),(xs2[5]+w2,y2+1.8),color=PUR,ls="--")
    ax.text(91.5,y2-2.6,L["precredit"],fontsize=6.5,ha="center",color=PUR)
    # DEP 隧道带
    ax.add_patch(Rectangle((26.5,y2-6.0),37,4.2,fc="#e6f7ee",ec=GREEN,lw=1.0))
    ax.text(45,y2-3.9,L["dep"],fontsize=6.3,ha="center",va="center",color=GREEN)
    # 注释:嵌套签名 / 门控 / 侧道验签
    ax.text(13.5,y2-3.4,L["nested"],fontsize=6.8,ha="center",color=GREY)
    arrow(ax,(8.6,y2-2.0),(8.6,y2),color=GREY,lw=1.0,ls=":")
    ax.text(66.6,y2-3.4,L["gate"],fontsize=6.8,ha="center",color=GREY)
    arrow(ax,(66.6,y2-2.0),(66.6,y2),color=GREY,lw=1.0,ls=":")
    box(ax,68,y2+6.8,22,4.0,L["sidelane"],fc="#f3effc",ec=PUR,fs=6.8)
    arrow(ax,(81,y2+6),(80,y2+6.8),color=PUR,ls="--")
    # 变体③ 注
    ax.text(50,23.1,L["variantC"],fontsize=7.2,ha="center",color=GREY,style="italic")
    # —— 公共注:TCP/ISO + 观测 + 部署 ——
    ax.text(33,46.3,L["tcp"],fontsize=8,ha="center",color=INK)
    box(ax,1,13.5,72,5,L["obs"],fc="#f4f6f8",ec=GREY,fs=7.6)
    arrow(ax,(25,21),(25,18.5),color=GREY,ls="--"); arrow(ax,(55,21),(55,18.5),color=GREY,ls="--")
    box(ax,74,11.2,25,7.6,L["deploy"],fc="#fffbe8",ec=ORANGE,fs=6.2)
    save(fig,outdir,"fig1_testbed")

# ============================== 图2 时序 ==============================
def fig2(L, outdir):
    fig,ax=plt.subplots(figsize=(9.6,8.0)); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")
    # 标题不入图:图题由论文正文图注(图下)给出
    X=[10,37,63,88]
    for x,t in zip(X,L["ln"]):
        box(ax,x-9,92,18,4.6,t,fs=8.5,bold=True)
        ax.plot([x,x],[8,92],color="#9aa7bd",lw=1.0,ls="--",zorder=0)
    def msg(y,i,j,txt,color="#33415f",ls="-",fs=7.4,dy=1.2):
        arrow(ax,(X[i],y),(X[j],y),color=color,ls=ls)
        ax.text((X[i]+X[j])/2,y+dy,txt,ha="center",fontsize=fs,color=color)
    def selfnote(y,i,txt,color=INK,fc="#f4f6f8",w=15,h=4.6,fs=7):
        box(ax,X[i]-w/2,y-h/2,w,h,txt,fc=fc,ec=GREY,fs=fs)
    msg(88.5,0,1,L["m_submit"])
    msg(83.5,1,2,L["m_s1"],color=BLUE)
    msg(78.5,2,3,L["m_s2"],color=PUR)
    selfnote(73.5,3,L["m_pend"],fc="#fff7e6")
    msg(68,3,0,L["m_prov"],color=ORANGE,ls="--")
    # S3 自循环(PQC-SVS)
    box(ax,X[2]-21,58.2,42,6.4,L["m_s3"],fc="#f3effc",ec=PUR,fs=6.4)
    arrow(ax,(X[2],66.8),(X[2],64.9),color=PUR)
    # alt 框
    ax.add_patch(Rectangle((3,10),94,44,fc="none",ec=GREY,lw=1.2))
    ax.text(4.5,52.0,"alt",fontsize=8,color=GREY,fontweight="bold")
    ax.text(8,49.6,L["alt_a"],fontsize=8,color=GREEN,fontweight="bold")
    msg(45.5,2,3,L["m_s4a"],color=GREEN)
    selfnote(40.5,3,L["m_commit"],fc="#eefaf0")
    msg(35,3,0,L["m_fin_a"],color=GREEN,ls="--")
    ax.plot([3,97],[31,31],color=GREY,lw=1.0,ls=":")
    ax.text(8,28.6,L["alt_b"],fontsize=8,color=RED,fontweight="bold")
    msg(24.5,2,3,L["m_s4b"],color=RED)
    selfnote(19.5,3,L["m_roll"],fc="#fdeeee")
    msg(14,3,0,L["m_fin_b"],color=RED,ls="--")
    save(fig,outdir,"fig2_s1s4b")

if __name__=="__main__":
    for lang,sub in (("en","fig"),("cn","fig_cn")):
        out=os.path.join(HERE,sub)
        print(f"[{lang}] -> {sub}/")
        fig1(T[lang],out); fig2(T[lang],out)
    print("done")
