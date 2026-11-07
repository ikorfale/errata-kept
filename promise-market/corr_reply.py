# Follow-up (not in prereg): right of reply on audit flags (reply=2, rc=0.2) in the correlated cells.
import numpy as np, corr
from multiprocessing import Pool
def c(a):
    mode,ehi,q0,rp,sd=a
    h,b=corr.run(0.3,0.3,q0,'aud',sd,p=dict(corr.P,e=0.3,corr=(0.2,ehi,mode),splitout=1,reply=rp,rc=0.2)); return a,h[0],b[2]
if __name__=="__main__":
    J=[(m,e,q,rp,s) for m,e in (("flag",0.9),("sym",0.9),("sym",0.6)) for q in (0.1,0.4) for rp in (0,2) for s in range(5)]
    with Pool(7) as P: R=P.map(c,J)
    for m,e in (("flag",0.9),("sym",0.9),("sym",0.6)):
        for q in (0.1,0.4):
            for rp in (0,2):
                v=np.array([(k,f) for a,k,f in R if a[:4]==(m,e,q,rp)])
                print(f"aud {m:4} e_hi={e} q0={q} reply={rp}  K={v[:,0].mean():.2f}  fit(K,bit1)/fit(K,bit0)={np.nanmean(v[:,1]):.2f}")
