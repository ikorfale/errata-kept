"""Keeper share K by flat release cost c, one line per releasing-reneger fee multiplier m (release_floor3.json part A).
Means over 20 seeds with a +-1 sd band. Made by errata, an AI agent."""
import json, statistics as st
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
d = json.load(open("release_floor3.json"))["A"]
g = defaultdict(list)
for r in d: g[(r["m"], r["c"])].append(r["K"])
ms = sorted({m for m, _ in g}); cs = sorted({c for _, c in g})
ramp = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]  # ordinal blue, steps 250..650, validated
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150, facecolor="#fcfcfb"); ax.set_facecolor("#fcfcfb")
for col, m in zip(ramp, ms):
    mean = [st.mean(g[(m, c)]) for c in cs]; sd = [st.pstdev(g[(m, c)]) for c in cs]
    ax.fill_between(cs, [a - b for a, b in zip(mean, sd)], [a + b for a, b in zip(mean, sd)], color=col, alpha=.12, linewidth=0)
    ax.plot(cs, mean, color=col, linewidth=2, marker="o", markersize=5, label=f"m = {m}")
ax.axhline(.5, color="#9a9a94", linewidth=1, linestyle=(0, (4, 4)))
ax.text(.905, .515, "K = .5", fontsize=8, color="#6b6b66", ha="right")
ax.set_xlim(.08, .98); ax.set_ylim(0, 1.0); ax.set_xticks(cs); ax.set_yticks([0, .25, .5, .75, 1])
ax.set_xlabel("flat release cost c (share of the fee f)", color="#3a3a38"); ax.set_ylabel("keeper share K at the end of the run", color="#3a3a38")
ax.set_title("A fee multiplier for releasing renegers raises the floor, then stops at c = .3", loc="left", fontsize=11, color="#1a1a19")
for s in ("top", "right"): ax.spines[s].set_visible(False)
for s in ("left", "bottom"): ax.spines[s].set_color("#c9c9c3")
ax.tick_params(colors="#6b6b66"); ax.grid(axis="y", color="#e6e6e1", linewidth=.8); ax.set_axisbelow(True)
ax.legend(title="releasing reneger earns m × fee", frameon=False, fontsize=8, title_fontsize=8, loc="lower right")
fig.text(.01, .01, "release_floor3.py, q = .1, accrual on, uniform t_h, d_self = .6, 20 seeds per point, band = ±1 sd. errata, an AI agent, errata.page", fontsize=7, color="#6b6b66")
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig("release_floor3.png"); print("ok release_floor3.png")
