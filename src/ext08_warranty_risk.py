"""Extension 8: do the new/returning powertrains carry warranty risk?  NHTSA recalls (FLAT_RCL) and owner complaints
(api.nhtsa.gov) for Ram 1500 MY2019-2027, normalized by US Ram light-duty sales in each model year's first 12 months."""
import pathlib, re, numpy as np, pandas as pd
from ext_common import md_table
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; OUT = ROOT / "results/extensions"

sales = pd.read_csv(P / "stellantis_us_quarterly_sales.csv").query("model == 'Ram LD PU'").set_index("quarter").units
def first_year_sales(my):            # MY launches ~Q3 of the prior calendar year: Q3(MY-1) .. Q2(MY)
    qs = [f"{my-1}Q3", f"{my-1}Q4", f"{my}Q1", f"{my}Q2"]
    return sales.reindex(qs).sum(min_count=4)

# ---------- complaints in the first 12 months of each model year
c = pd.read_csv(P / "nhtsa_complaints_ram1500.csv.gz")
c["date"] = pd.to_datetime(c.date_received, format="%m/%d/%Y", errors="coerce")
c["start"] = pd.to_datetime((c.model_year - 1).astype(str) + "-08-01")
c["months"] = (c.date - c.start).dt.days / 30.44
ptc = c.components.fillna("").str.contains("ENGINE|POWER TRAIN|FUEL/PROPULSION|FUEL SYSTEM")
txt = c.summary.fillna("").str.upper()
c["mentions_hurricane"] = txt.str.contains(r"HURRICANE|3\.0|TWIN[- ]?TURBO|\bI-?6\b|INLINE", regex=True) & ~txt.str.contains("DIESEL")
c["mentions_hemi"] = txt.str.contains(r"HEMI|5\.7|\bV-?8\b", regex=True)
c["powertrain"] = ptc
w = c[c.months.between(0, 12)]
rows = []
for my, g in w.groupby("model_year"):
    s = first_year_sales(my)
    rows.append(dict(model_year=my, complaints_12m=len(g), powertrain_complaints_12m=int(g.powertrain.sum()),
                     us_ld_sales_first_year=s,
                     per_10k=round(1e4 * len(g) / s, 2) if s == s else np.nan,
                     powertrain_per_10k=round(1e4 * g.powertrain.sum() / s, 2) if s == s else np.nan,
                     pt_mention_hurricane=int((g.powertrain & g.mentions_hurricane).sum()), pt_mention_hemi=int((g.powertrain & g.mentions_hemi).sum())))
C = pd.DataFrame(rows); C.to_csv(OUT / "08_complaints_first12m.csv", index=False)
# MY2026 (both engines offered): engine mentions among powertrain complaints vs NY registration mix
ny = pd.read_csv(P / "ny_new_pickup_registrations.csv.gz", low_memory=False)
mix26 = ny[(ny.nameplate == "Ram 1500") & (ny.my == 2026) & ny.engine.isin(["Hemi V8", "6-cyl"])].engine.value_counts(normalize=True)
pt26 = c[(c.model_year == 2026) & c.powertrain]
pt25 = c[(c.model_year == 2025) & c.powertrain]

# ---------- recalls
r = pd.read_csv(P / "nhtsa_vehicle_recalls_post2010.csv.gz", low_memory=False)
r = r[(r.MAKETXT == "RAM") & r.MODELTXT.astype(str).str.fullmatch(r"1500") & r.YEARTXT.between(2019, 2027)]
camp = r.groupby(["YEARTXT", "CAMPNO"]).agg(comp=("COMPNAME", "first"), potaff=("POTAFF", "max"), desc=("DESC_DEFECT", "first"),
                                            date=("ODATE", "first")).reset_index()
camp["powertrain"] = camp.comp.str.contains("ENGINE|POWER TRAIN|FUEL")
camp["hurricane"] = camp.desc.str.upper().str.contains(r"3\.0|HURRICANE|TWIN TURBO", regex=True) & ~camp.desc.str.upper().str.contains("DIESEL")
camp["diesel"] = camp.desc.str.upper().str.contains("DIESEL")
camp["hemi"] = camp.desc.str.upper().str.contains(r"5\.7|HEMI", regex=True)
R = camp.groupby("YEARTXT").agg(campaigns=("CAMPNO", "nunique"), powertrain_campaigns=("powertrain", "sum"),
                                hurricane_campaigns=("hurricane", "sum"), hemi_campaigns=("hemi", "sum"), ecodiesel_campaigns=("diesel", "sum")).reset_index()
R.to_csv(OUT / "08_recalls_by_my.csv", index=False)
hur = camp[camp.hurricane | camp.hemi | (camp.YEARTXT >= 2025) & camp.powertrain][["YEARTXT", "CAMPNO", "comp", "potaff", "desc"]]
hur = hur.assign(desc=hur.desc.str[:160]).drop_duplicates("CAMPNO")

md = ["# 8. Warranty-risk tracker: Ram 1500 recalls and complaints", "",
      "Complaints are owner complaints filed with NHTSA within 12 months of each model year's launch (taken as 1 Aug of the "
      "prior year), per 10,000 US Ram light-duty sales over that year. MY2026's window closes Jul 2026, so it is complete. "
      "MY2027's window is still open and is excluded. The quarterly Ram light-duty series starts in 2024, so pre-2025 rates cannot be normalized.", "", md_table(C, index=False, fmt="{:.4g}"), "",
      f"MY2026 is the first year with both engines on sale. NY registration mix: Hemi {mix26.get('Hemi V8', 0):.0%}, six-cylinder "
      f"{mix26.get('6-cyl', 0):.0%}. Of {len(pt26)} MY2026 powertrain complaints (all dates), {int(pt26.mentions_hurricane.sum())} mention the "
      f"Hurricane/3.0/twin-turbo and {int(pt26.mentions_hemi.sum())} mention the Hemi/5.7/V8. MY2025 (Hurricane-only) had {len(pt25)} "
      "powertrain complaints.", "",
      "## Recall campaigns by model year", "", md_table(R, index=False), "",
      "Campaigns that mention the gasoline Hurricane or the Hemi, or MY2025+ powertrain campaigns:", "", md_table(hur, index=False, fmt="{:.0f}"), ""]
(OUT / "08_warranty_risk.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
