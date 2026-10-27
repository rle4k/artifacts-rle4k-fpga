"""Re-verify the aggregate background numbers cited by the paper (JM^3, RLE4K column).
Run: python verify.py  (requires the CSV next to it). Expected: 64, 203.4, 70.3, 78.3."""
import csv, statistics as st
def thr(tis,t): return (tis/1e6)*8/t   # JM^3-locked speed formula (TIS bytes, WED/WDD ms)
rows=list(csv.DictReader(open("rle4k_cpu_background_64files_n32_pw0p5_rt4.csv",encoding="utf-8")))
rho=[float(r["rho"]) for r in rows]; E=[float(r["E_gbps"]) for r in rows]; D=[float(r["D_gbps"]) for r in rows]
print(len(rows), f"{st.mean(rho):.1f} +/- {st.stdev(rho):.1f}", f"{st.mean(E):.1f} +/- {st.stdev(E):.1f}", f"{st.mean(D):.1f} +/- {st.stdev(D):.1f}")
