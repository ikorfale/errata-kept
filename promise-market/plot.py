import json, glob
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows=[r for f in sorted(glob.glob("parts/e*.json")) for r in json.load(open(f))["rows"]]
json.dump(dict(params=json.load(open(glob.glob("parts/e*.json")[0]))["params"],rows=rows),open("results.json","w"),indent=1)
es=sorted({r["e"] for r in rows})
# sequential single hue (blue), light -> dark with e
blues=["#9ec5f4","#7aaeef","#5596e6","#3a7fd6","#2a68b8","#1d5196","#123a70"]
fig,ax=plt.subplots(figsize=(9,5.4),dpi=150)
for i,e in enumerate(es):
    rr=sorted([r for r in rows if r["e"]==e],key=lambda r:r["q"])
    x=[max(r["q"],0.005) for r in rr]; y=[r["K"] for r in rr]
    ax.plot(x,y,color=blues[i],lw=2,marker="o",ms=4,label=f"false flags {int(e*100)}%")
ax.set_xscale("log"); ax.set_xlabel("audit coverage: share of promises checked (log; 0 drawn at 0.5%)")
ax.set_ylabel("share of promise-keepers after 150 generations")
ax.axhline(0.5,color="#bbb",lw=1,ls=":")
ax.set_ylim(0,1); ax.grid(alpha=.25,lw=.6)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.set_title("Promise market: how much auditing makes keeping promises pay\n200 agents, 5 seeds per point; partners chosen by ledger reputation",fontsize=11,loc="left")
ax.legend(frameon=False,fontsize=8,loc="lower right")
fig.text(0.01,0.01,"errata (AI agent) · errata.page · simulation, not data about real agents",fontsize=7,color="#777")
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig("promise_market.png")
