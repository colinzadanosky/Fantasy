"""Extension 5: is Ram 1500 growth coming from fleet?
(a) Stellantis US sales releases: total vs retail growth -> implied non-retail growth under a range of base retail shares.
(b) New York DMV registrations (VIN level, decoded): plate class splits retail (passenger) from commercial, rental
    and government registrations, by quarter, for Ram 1500 vs F-150 / Silverado 1500 / Sierra 1500 / Tundra."""
import pathlib, numpy as np, pandas as pd
from ext_common import md_table
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; OUT = ROOT / "results/extensions"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- (a) release statements: Ram light-duty pickup (1500) total vs retail YoY, %
REL = [("2025Q1", -11.2, 14), ("2025Q4", 23.4, 27), ("2026Q2", 26.7, 9), ("2026Q3", 72.8, 42)]
rows = []
for q, tot, ret in REL:
    for s in (0.70, 0.80, 0.90):                        # retail share of the year-earlier quarter
        T1, R1 = 1 + tot / 100, s * (1 + ret / 100)
        F1, F0 = T1 - R1, 1 - s
        inc = T1 - 1
        rows.append(dict(quarter=q, total_yoy=tot, retail_yoy=ret, base_retail_share=s,
                         implied_fleet_yoy=round(100 * (F1 / F0 - 1), 1),
                         retail_share_of_increment=round((R1 - s) / inc, 2) if inc > 0 else np.nan,
                         retail_share_now=round(R1 / T1, 3)))
rel = pd.DataFrame(rows); rel.to_csv(OUT / "05_release_retail_fleet_sensitivity.csv", index=False)

# ---------- (b) NY registrations
d = pd.read_csv(ROOT / "data/raw/ny_dmv/ny_pickup_registrations.csv.gz", dtype=str, low_memory=False)
FS = {("RAM", "1500"): "Ram 1500", ("FORD", "F-150"): "F-150", ("CHEVR", "Silverado"): "Silverado 1500",
      ("GMC", "Sierra"): "Sierra 1500", ("TOYOT", "Tundra"): "Tundra"}
d["nameplate"] = [FS.get((a, b)) for a, b in zip(d.make, d.Model)]
d = d[d.nameplate.notna()].copy()
d["reg_date"] = pd.to_datetime(d.reg_valid_date, errors="coerce")
d["my"] = pd.to_numeric(d.model_year, errors="coerce")
d["q"] = d.reg_date.dt.to_period("Q")
# 'new' proxy: model year within one year of the registration year (renewals happen every 2 years, so a MY>=year-1
# vehicle registered in that window is almost always on its first registration; used resales are a residual risk)
d = d[(d.my >= d.reg_date.dt.year - 1) & (d.reg_date >= "2024-07-01") & (d.reg_date <= "2026-10-31")]
CLS = {"PAS": "retail", "SRF": "retail", "SPO": "retail", "ORG": "retail", "RGL": "retail", "VAS": "retail", "MED": "retail",
       "HAM": "retail", "AGR": "retail", "FAR": "retail", "SRN": "retail",
       "COM": "commercial", "ORC": "commercial", "RGC": "commercial", "CSP": "commercial", "HAC": "commercial",
       "TOW": "commercial", "IRP": "commercial", "OMS": "rental", "OMR": "rental", "OMT": "rental",
       "STA": "government", "PSD": "government"}
d["channel"] = d.registration_class.map(CLS).fillna("other")
d["engine"] = np.where(d.nameplate.eq("Ram 1500") & d.vin.str[7].eq("T"), "Hemi V8",
               np.where(d.nameplate.eq("Ram 1500") & d.vin.str[7].isin(["G", "P"]), "6-cyl", "n/a"))
d.loc[d.nameplate.eq("Ram 1500") & d.vin.str[7].eq("9"), "engine"] = "6.2 SC (TRX)"
keep = ["nameplate", "my", "registration_class", "channel", "county", "reg_date", "engine", "Trim", "DisplacementL"]   # no VIN/ZIP
d[keep].to_csv(P / "ny_new_pickup_registrations.csv.gz", index=False)

q = d.groupby(["nameplate", "q", "channel"]).size().unstack(fill_value=0)
q["total"] = q.sum(axis=1)
for c in ["retail", "commercial", "rental", "government"]:
    q[c + "_share"] = (q[c] / q.total).round(3)
q = q.reset_index(); q["q"] = q.q.astype(str); q.to_csv(OUT / "05_ny_registrations_by_channel.csv", index=False)

def yoy(np_, qa, qb):
    a = q[(q.nameplate == np_) & (q.q == qa)].iloc[0]; b = q[(q.nameplate == np_) & (q.q == qb)].iloc[0]
    out = {"nameplate": np_, "period": f"{qa} vs {qb}"}
    for c in ["total", "retail", "commercial", "rental", "government"]:
        out[c + "_yoy_pct"] = round(100 * (a[c] / b[c] - 1), 1) if b[c] > 0 else np.nan
        out[c + "_units"] = int(a[c])
    inc = a.total - b.total
    out["retail_share_of_increment"] = round((a.retail - b.retail) / inc, 2) if inc > 0 else np.nan
    return out
Y = pd.DataFrame([yoy(n, qa, qb) for n in FS.values() for qa, qb in [("2026Q1", "2025Q1"), ("2026Q2", "2025Q2"), ("2026Q3", "2025Q3")]])
Y.to_csv(OUT / "05_ny_yoy.csv", index=False)

# Ram 1500 by engine x channel, MY2026+ (both engines on sale)
r = d[(d.nameplate == "Ram 1500") & (d.my >= 2026) & d.engine.isin(["Hemi V8", "6-cyl"])]
eng = pd.crosstab(r.engine, r.channel, normalize="index").round(3)
eng["n"] = r.engine.value_counts()
eng.to_csv(OUT / "05_ny_ram1500_engine_by_channel.csv")

# ---------- write-up
f = lambda x: "n/a" if pd.isna(x) else f"{x:+.0f}%"
md = ["# 5. Is Ram 1500 growth coming from fleet?", "",
      "## (a) What the sales releases imply", "",
      "Stellantis gives retail growth for the Ram 1500 in some quarters, but never fleet units. The table backs out non-retail "
      "growth for a range of year-earlier retail shares (70-90% brackets typical full-size pickup retail mix).", "",
      "| Quarter | Total YoY | Retail YoY | Base retail share | Implied non-retail YoY | Retail share of added units |", "|---|---:|---:|---:|---:|---:|"]
for x in rel.itertuples():
    md.append(f"| {x.quarter} | {x.total_yoy:+.1f}% | {x.retail_yoy:+.0f}% | {x.base_retail_share:.0%} | {x.implied_fleet_yoy:+.0f}% | "
              + ("n/a" if pd.isna(x.retail_share_of_increment) else f"{x.retail_share_of_increment:.0%}") + " |")
q3 = rel[(rel.quarter == "2026Q3")]
md += ["", f"**Q3 2026:** whatever the base mix, retail supplied only **{q3.retail_share_of_increment.min():.0%}-{q3.retail_share_of_increment.max():.0%}** "
       f"of the added units. Non-retail volume grew roughly {q3.implied_fleet_yoy.min():.0f}-{q3.implied_fleet_yoy.max():.0f}%. In Q2 2026 retail "
       "(+9%) explains even less of the +27%. In Q4 2025, the first Hemi quarter, it was the other way round: retail (+27%) "
       "outgrew total (+23%).", "",
      "## (b) New York registrations (VIN-level, plate class)", "",
      "Source: NY DMV registration file (data.ny.gov, snapshot 2026-11-03), VINs decoded with NHTSA vPIC. Retail = passenger-type "
      "plates; commercial = COM/ORC/RGC etc.; rental = OMS (omnibus private rental); government = STA/PSD. A new vehicle "
      "is MY >= registration year - 1.", "",
      "**Read the levels and the Ram-vs-rival gaps, not raw YoY.** The file is a snapshot of current registrations. A 2025 "
      "truck that has since been resold, defleeted or moved out of state shows its newer record or disappears. Every nameplate's "
      "2025 count is therefore understated (all show +30-130% YoY), and 2025 rental registrations are zero for every "
      "nameplate because rental trucks are sold within about 12 months.", "",
      "| Nameplate | Period | Total YoY (units) | Retail YoY | Commercial YoY | Rental units | Retail share of added units |", "|---|---|---:|---:|---:|---:|---:|"]
for x in Y.itertuples():
    md.append(f"| {x.nameplate} | {x.period} | {f(x.total_yoy_pct)} ({x.total_units:,}) | {f(x.retail_yoy_pct)} | {f(x.commercial_yoy_pct)} | "
              f"{x.rental_units} | " + ("n/a" if pd.isna(x.retail_share_of_increment) else f"{x.retail_share_of_increment:.0%}") + " |")
rs = q.pivot(index="q", columns="nameplate", values="retail_share").loc[["2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2", "2026Q3"]]
md += ["", "Retail-plate share of new registrations by quarter:", "", md_table(rs, fmt="{:.0%}"), "",
       "Ram 1500 MY2026+ registrations by engine and channel (row shares):", "", md_table(eng, fmt="{:.1%}"), "",
       "## Answer", "",
       "* **Nationally, roughly half of the Q3 2026 Ram 1500 jump was non-retail.** Retail +42% against total +73% means retail "
       "supplied 40-52% of the added units for any plausible base mix. In Q2 2026 it was about a quarter. Q4 2025, the Hemi "
       "launch quarter, was retail-led.",
       "* **The Hemi is a retail engine; the fleet volume is six-cylinder.** In NY, 91% of MY2026+ Hemi registrations carry "
       "retail plates vs 82% for the six-cylinder. Rental registrations are 8.2% of six-cylinder trucks but 0.5% of Hemis "
       "(19 of 5,236). Fleet growth therefore does not undercut the Hemi pricing-power argument, but it does mean headline "
       "Ram 1500 growth overstates individual-buyer demand for the truck overall.",
       "* **In NY, Ram's retail registrations grew about as fast as its total** (+103% to +128% vs +112% to +133%). That is "
       "well ahead of F-150, Silverado, Sierra and Tundra, which face the same snapshot bias. Ram's retail share slipped from "
       "about 89% (2025) to 85-88% (2026) while rivals were flat at about 79-81%. NY is one state, and national fleet buyers "
       "(rental, utilities) often register out of state, so NY understates fleet.",
       "* **Not available:** S&P Global Mobility / Experian national registrations by model and channel are licensed. "
       "Stellantis discloses fleet only as a share of total sales in some quarters (none for the Ram 1500 alone)."]
(OUT / "05_fleet.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
