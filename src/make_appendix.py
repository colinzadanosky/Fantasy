"""Render results/regression_results.csv as a markdown appendix (results/ALL_TESTS.md)."""
import numpy as np, pandas as pd
from common import OUT

r = pd.read_csv(OUT / "regression_results.csv")
lines = ["# All 56 tests - coefficients and status", "",
         "Generated from `results/regression_results.csv` by `src/make_appendix.py`. Full model summaries in `results/details/`.", "",
         "| # | Test / specification | Term | Coef | SE | p | n | Status |", "|---|---|---|---|---|---|---|---|"]
fmt = lambda x, k=3: "" if pd.isna(x) else (f"{x:.{k}g}" if abs(x) < 1e-3 or abs(x) >= 1e4 else f"{x:.{k}f}")
for _, x in r.iterrows():
    lines.append(f"| {x.test} | {x.title} | {'' if pd.isna(x.get('term')) else x.term} | {fmt(x.get('coef'))} | {fmt(x.get('se'))} | "
                 f"{fmt(x.get('p'))} | {'' if pd.isna(x.n) else int(x.n)} | {x.status} |")
lines += ["", "## Specifications, data and caveats", ""]
for t, g in r.groupby("test"):
    x = g.iloc[0]; lines.append(f"**{t}. {x.title}** - {x.status}")
    for col in ["spec", "data", "note"]:
        vals = [v for v in g[col].dropna().unique() if v]
        for v in vals: lines.append(f"- {col}: {v}")
    lines.append("")
(OUT / "ALL_TESTS.md").write_text("\n".join(lines)); print("wrote", OUT / "ALL_TESTS.md", len(r), "rows")
