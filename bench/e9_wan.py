#!/usr/bin/env python3
# E9 WAN 外部效度:对 12 容器 Tier3 的节点容器注入 tc netem 逐级延迟,
# 用 Python 直接读 SSE(逐行,免缓冲丢失),测决策延迟 vs 每跳延迟 + 跨容器正确性。
import json, re, subprocess, threading, time, urllib.request, os, statistics as st
from collections import defaultdict

BASE = "http://localhost:8080"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "out")
NODES = ["sidelane-part-a","sidelane-nsp-a","sidelane-esmig-a","sidelane-rtgs-a",
         "sidelane-part-b","sidelane-nsp-b","sidelane-new-nsp-b","sidelane-new-esmig-b","sidelane-esmig-b","sidelane-svs-b","sidelane-rtgs-b"]
DELAYS = [0, 5, 10, 20]

cur = {"level": None}
dec = defaultdict(lambda: defaultdict(list))   # level -> mode -> [ms]
finals = []                                     # (level, node, status)
stop = threading.Event()

def sse_reader():
    while not stop.is_set():
        try:
            with urllib.request.urlopen(BASE + "/events", timeout=5) as r:
                for raw in r:
                    if stop.is_set(): break
                    line = raw.decode("utf-8", "ignore").strip()
                    if not line.startswith("data:"): continue
                    try: e = json.loads(line[5:].strip())
                    except Exception: continue
                    lv = cur["level"]
                    if lv is None: continue
                    if e.get("kind") == "metric":
                        m = re.match(r"([AB])\|decision\|([0-9.]+)", e.get("detail",""))
                        if m: dec[lv][m.group(1)].append(float(m.group(2)))
                    elif e.get("kind") == "final":
                        d = e.get("detail",""); node = e.get("node","")
                        for s in ("SETTLED","PARTITIONED","ROLLED_BACK","FAILED"):
                            if s in d: finals.append((lv, node, s)); break
        except Exception:
            time.sleep(0.3)

def http(path):
    try: urllib.request.urlopen(BASE + path, timeout=10).read()
    except Exception as ex: print("  http err", path, ex)

def netem(ms):
    for c in NODES:
        if ms <= 0:
            subprocess.run(["docker","exec",c,"tc","qdisc","del","dev","eth0","root"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["docker","exec",c,"tc","qdisc","replace","dev","eth0","root","netem","delay",f"{ms}ms"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    t = threading.Thread(target=sse_reader, daemon=True); t.start()
    http("/config?verifyDelayMs=0")
    time.sleep(1)
    for d in DELAYS:
        print(f"=== NET_DELAY={d}ms ===")
        netem(d); time.sleep(2)
        cur["level"] = d
        for i in range(15):
            http("/scenario?s=S1"); time.sleep(0.9)
        time.sleep(2)
        http("/scenario?s=S4"); time.sleep(3)     # 正确性:两线应拒绝
        http("/scenario?s=S1"); time.sleep(3)
        print(f"  A={len(dec[d]['A'])} B={len(dec[d]['B'])} samples")
    cur["level"] = None
    netem(0)
    stop.set(); time.sleep(0.5)

    # 写 CSV
    with open(os.path.join(OUT,"E9_wan.csv"),"w",encoding="utf-8") as f:
        f.write("net_delay_ms,mode,sample,decision_ms\n")
        for d in DELAYS:
            for mode in ("A","B"):
                for i,v in enumerate(dec[d][mode]): f.write(f"{d},{mode},{i},{v}\n")
    # 摘要
    print("\nnet_delay  A_med(n)        B_med(n)")
    for d in DELAYS:
        a,b = dec[d]["A"], dec[d]["B"]
        am = f"{st.median(a):.2f}({len(a)})" if a else "-"
        bm = f"{st.median(b):.2f}({len(b)})" if b else "-"
        print(f"{d:9}  {am:14}  {bm}")
    # 正确性摘要(取每级最后一次 S1 与 S4)
    with open(os.path.join(OUT,"E9_correctness.csv"),"w",encoding="utf-8") as f:
        f.write("net_delay_ms,node,status,count\n")
        cnt = defaultdict(int)
        for lv,node,s in finals: cnt[(lv,node,s)] += 1
        for (lv,node,s),c in sorted(cnt.items()): f.write(f"{lv},{node},{s},{c}\n")
    print("E9 done -> out/E9_wan.csv, E9_correctness.csv")

if __name__ == "__main__":
    main()
