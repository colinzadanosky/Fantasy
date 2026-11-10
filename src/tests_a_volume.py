"""Section A - does powertrain choice create new sales? Tests 1-10."""
import numpy as np, pandas as pd
from common import *

W = stla_wide(); IND = industry_q(); PT = powertrains(); G = gcbc_q("US")
gq = G.pivot_table(index="quarter", columns="model", values="units", aggfunc="sum")
QS = [q for q in W.index if "2021Q3" <= q <= "2026Q3"]


def lineup(model, q):
    my = quarter_to_my(q); r = PT[(PT.model == model) & (PT.model_year == my)]
    return r.iloc[0] if len(r) else None


# ---------------------------------------------------------------- 1 Ram Hemi DiD / event study
def test1():
    ctrl = ["Ford F-Series", "Chevrolet Silverado", "GMC Sierra", "Toyota Tundra"]
    for label, ram, start in [("Ram LD (1500) vs F-150/Silverado/Sierra/Tundra", "Ram LD PU", "2024Q1"),
                              ("Ram pickups total vs same controls (longer pre-period)", "Ram PU (total)", "2021Q3")]:
        rows = []
        for q in QS:
            if q < start: continue
            rows.append(dict(unit="Ram", quarter=q, units=W.loc[q, ram]))
            for c in ctrl: rows.append(dict(unit=c, quarter=q, units=gq.loc[q, c]))
        d = add_time(pd.DataFrame(rows).dropna())
        d["ly"] = np.log(d.units); d["ram"] = (d.unit == "Ram").astype(int)
        d["post"] = (d.quarter >= "2025Q4").astype(int); d["partial"] = (d.quarter == "2025Q3").astype(int)
        d["ram_post"] = d.ram * d.post; d["ram_partial"] = d.ram * d.partial
        m = ols("ly ~ ram_post + ram_partial + C(unit) + C(quarter)", d, cluster=None)
        record(1, f"Hemi return DiD: {label}", "RUN", m, ["ram_post", "ram_partial"],
               spec="log(units) ~ Ram x Post(>=2025Q4) + Ram x 2025Q3 + unit FE + quarter FE; HC1 SE",
               data="Stellantis quarterly sales PDFs; GoodCarBadCar (GCBC) quarterly rivals",
               note="Control pickups include HD (F-Series, Silverado, Sierra). Pre-period includes MY2025 (no-Hemi) quarters, "
                    "so the estimate is the Hemi-return effect relative to the Hurricane-only year.")
        # event study coefficients relative to 2025Q2
        for q in sorted(d.quarter.unique()):
            if q != "2025Q2": d[f"ev_{q}"] = d.ram * (d.quarter == q).astype(int)
        evs = [c for c in d.columns if c.startswith("ev_")]
        me = ols("ly ~ " + " + ".join(evs) + " + C(unit) + C(quarter)", d)
        pd.DataFrame({"coef": me.params[evs], "se": me.bse[evs]}).rename(index=lambda s: s[3:]).to_csv(
            OUT / f"details/test_01_event_study_{ram.replace(' ', '_').replace('(', '').replace(')', '')}.csv")
        # pre-trend check: slope of the Ram-minus-control log gap over the pre-period
        gap = d.groupby(["quarter", "ram"]).ly.mean().unstack(); gap = (gap[1] - gap[0]).rename("gap").reset_index()
        gap = add_time(gap); pre_df = gap[gap.quarter <= "2025Q2"]
        mp = ols("gap ~ t", pre_df, hac=1)
        record(1, f"Pre-trend: slope of Ram-vs-control log gap before 2025Q3 ({label})", "RUN", mp, ["t"],
               spec="gap_t = log(Ram) - mean log(controls); gap ~ t over pre-period; HAC(1)")
        if ram == "Ram PU (total)":
            d["ram_t"] = d.ram * d.t
            m3 = ols("ly ~ ram_post + ram_partial + ram_t + C(unit) + C(quarter)", d)
            record(1, "Robustness: Ram pickups total DiD with Ram-specific linear trend", "RUN", m3, ["ram_post", "ram_t"],
                   spec="+ Ram x linear trend (pre-period share loss of -5.5%/qtr)")
        if ram == "Ram LD PU":
            d2 = d[d.quarter >= "2024Q2"]
            m2 = ols("ly ~ ram_post + ram_partial + C(unit) + C(quarter)", d2)
            record(1, "Robustness: Ram LD DiD, pre-period 2024Q2-2025Q2 (Hurricane-transition quarters only)", "RUN", m2, ["ram_post"],
                   spec="as above, dropping 2024Q1")


# ---------------------------------------------------------------- 2 Jeep sales ~ powertrain count
JEEP = ["Wrangler", "Gladiator", "Grand Cherokee", "Cherokee", "Compass", "Renegade", "Wagoneer family", "Wagoneer S", "Recon"]
STLA_MODELS = JEEP + ["Ram LD PU", "Durango", "Hornet", "Charger ICE", "Charger BEV", "Challenger", "Pacifica", "Voyager",
                      "300", "Giulia", "Stelvio", "Tonale", "500X", "500e"]


def brand_pt_count(models, q, min_units=500):
    n, types = 0, set()
    for m in models:
        if m not in W.columns or pd.isna(W.loc[q, m]) or W.loc[q, m] < min_units: continue
        r = lineup(m, q)
        if r is None: continue
        n += r.n_powertrains; types |= set(r.powertrains.split(";"))
    return n, len(types)


def test2():
    rows = []
    for q in QS:
        n, nt = brand_pt_count(JEEP, q)
        rows.append(dict(quarter=q, jeep=W.loc[q, "Jeep"], pt=n, pt_distinct=nt, ind=IND.lv_nsa_k.get(q)))
    d = add_time(pd.DataFrame(rows).dropna())
    d.to_csv(OUT / "details/test_02_data.csv", index=False)
    d["ly"], d["lpt"], d["lind"] = np.log(d.jeep), np.log(d.pt), np.log(d.ind)
    m = ols("ly ~ lpt + lind + C(qtr)", d, hac=2)
    record(2, "Jeep brand sales ~ # powertrain offerings (model x powertrain)", "RUN", m, ["lpt"],
           spec="log(Jeep units) ~ log(powertrain offerings) + log(US light-vehicle sales) + quarter-of-year; HAC(2)",
           data="Stellantis sales PDFs; EPA fueleconomy.gov lineups; BEA", note="Offerings = sum over nameplates selling >=500 units of distinct EPA powertrains.")
    m2 = ols("ly ~ lpt + lind + t + C(qtr)", d, hac=2)
    record(2, "Same, with linear trend", "RUN", m2, ["lpt"], spec="+ linear trend; HAC(2)")
    d = d.sort_values("quarter"); d["dly"] = d.ly.diff(4); d["dlpt"] = d.lpt.diff(4); d["dlind"] = d.lind.diff(4)
    m3 = ols("dly ~ dlpt + dlind", d.dropna(), hac=2)
    record(2, "YoY growth version", "RUN", m3, ["dlpt"], spec="d4 log(Jeep) ~ d4 log(offerings) + d4 log(industry); HAC(2)")


# ---------------------------------------------------------------- 3 panel model sales ~ powertrain count
def model_panel(models=STLA_MODELS, min_units=500):
    rows = []
    for m in models:
        if m not in W.columns: continue
        for q in QS:
            u = W.loc[q, m]; r = lineup(m, q)
            if pd.isna(u) or u < min_units or r is None: continue
            rows.append(dict(model=m, quarter=q, units=u, n_pt=r.n_powertrains, hev=r.has_hev, phev=r.has_phev,
                             ev=r.has_ev, v8=r.has_v8, diesel=r.has_diesel))
    return add_time(pd.DataFrame(rows))


def test3():
    d = model_panel(); d["ly"] = np.log(d.units)
    d.to_csv(OUT / "details/test_03_panel.csv", index=False)
    m = ols("ly ~ n_pt + C(model) + C(quarter)", d, cluster="model")
    record(3, "Model sales ~ powertrain count (Stellantis nameplate panel)", "RUN", m, ["n_pt"],
           spec="log(units) ~ n_powertrains + model FE + quarter FE; SE clustered by model",
           data="Stellantis sales PDFs; EPA lineups", note=f"{d.model.nunique()} nameplates; quarters with <500 units dropped")
    d = d.sort_values(["model", "quarter"])
    d["g"] = d.groupby("model").ly.diff(4); d["dpt"] = d.groupby("model").n_pt.diff(4)
    m2 = ols("g ~ dpt + C(quarter)", d.dropna(subset=["g", "dpt"]), cluster="model")
    record(3, "YoY growth ~ change in powertrain count", "RUN", m2, ["dpt"],
           spec="d4 log(units) ~ d4 n_powertrains + quarter FE; cluster model")


# ---------------------------------------------------------------- 4 cannibalization
def test4():
    seg = ["Toyota RAV4", "Honda CR-V", "Nissan Rogue", "Ford Escape", "Chevrolet Equinox", "Hyundai Tucson", "Kia Sportage",
           "Subaru Forester", "Mazda CX-5", "Ford Explorer", "Toyota Highlander", "Toyota Grand Highlander", "Chevrolet Traverse",
           "Kia Telluride", "Hyundai Palisade", "Honda Pilot"]
    d = pd.DataFrame({"cg": W["Compass"] + W["Grand Cherokee"], "ch": W["Cherokee"],
                      "seg": gq[seg].sum(axis=1, min_count=len(seg) - 2)}).loc[QS].dropna()
    d = d.reset_index().rename(columns={"index": "quarter"})
    d["d_cg"], d["d_ch"], d["d_seg"] = d.cg.diff(4), d.ch.diff(4), d.seg.diff(4)
    d["shut"] = (d.quarter == "2026Q3").astype(int)
    d.to_csv(OUT / "details/test_04_data.csv", index=False)
    m = ols("d_cg ~ d_ch + d_seg", d.dropna(), hac=2)
    record(4, "Cannibalization: YoY change Compass+Grand Cherokee units ~ YoY change Cherokee units", "RUN", m, ["d_ch"],
           spec="d4 (Compass+GC) ~ d4 Cherokee + d4 rival compact/midsize SUV units; HAC(2). Coef -1 = full cannibalization, 0 = new demand",
           data="Stellantis sales PDFs; GCBC rivals",
           note="Cherokee hybrid volume exists only 2025Q4-2026Q3; earlier Cherokee changes are the old ICE model winding down. "
                "Q3 2026 Compass/GC drop coincides with a planned production shutdown (Stellantis Q3 2026 release).")
    m2 = ols("d_cg ~ d_ch + d_seg + shut", d.dropna(), hac=2)
    record(4, "Same, controlling for Q3-2026 production shutdown", "RUN", m2, ["d_ch"], spec="+ dummy 2026Q3")


# ---------------------------------------------------------------- 5 segment share ~ coverage gap
SEGS = {"fullsize_pickup": ["Ram PU (total)"], "midsize_pickup": ["Gladiator"], "compact_suv": ["Compass", "Cherokee", "Hornet"],
        "midsize_suv": ["Grand Cherokee", "Durango"], "large_suv": ["Wagoneer family"], "minivan": ["Pacifica", "Voyager"],
        "muscle_car": ["Charger ICE", "Charger BEV", "Challenger"]}
PT_NAME = {"Ram PU (total)": "Ram LD PU"}


def flags(models, q):
    out = {k: 0 for k in ["has_hev", "has_phev", "has_ev", "has_v8", "has_diesel"]}
    for m in models:
        r = PT[(PT.model == PT_NAME.get(m, m)) & (PT.model_year == quarter_to_my(q))]
        if len(r):
            for k in out: out[k] = max(out[k], int(r.iloc[0][k]))
    return out


def test5():
    G2 = G.copy(); rows = []
    for seg, smods in SEGS.items():
        rivals = [m for m in G2[G2.segment == seg].model.unique() if not m.startswith(("Jeep", "Dodge", "Chrysler", "Ram"))]
        for q in QS:
            s_units = sum(W.loc[q, m] if m in W.columns and not pd.isna(W.loc[q, m]) else 0 for m in smods)
            r_units = gq.loc[q, rivals].fillna(0).sum() if q in gq.index else np.nan
            live_s = [m for m in smods if m in W.columns and W.loc[q, m] > 500]
            live_r = [m for m in rivals if q in gq.index and gq.loc[q, m] > 500]
            fs, fr = flags(live_s, q), flags(live_r, q)
            gap = sum(int(fr[k] == 1 and fs[k] == 0) for k in fs)
            rows.append(dict(segment=seg, quarter=q, share=s_units / (s_units + r_units), gap=gap,
                             miss_hybrid=int((fr["has_hev"] or fr["has_phev"]) and not (fs["has_hev"] or fs["has_phev"])),
                             miss_ev=int(fr["has_ev"] and not fs["has_ev"])))
    d = pd.DataFrame(rows).dropna(); d.to_csv(OUT / "details/test_05_panel.csv", index=False)
    m = ols("share ~ gap + C(segment) + C(quarter)", d, cluster="segment")
    record(5, "Stellantis segment share ~ powertrain coverage gap vs rivals", "RUN", m, ["gap"],
           spec="share ~ #types (HEV/PHEV/EV/V8/diesel) offered by a rival but not Stellantis + segment FE + quarter FE; cluster segment",
           data="Stellantis PDFs; GCBC rivals; EPA lineups", note="7 segments; Wrangler excluded (no Bronco data). eTorque counted as hybrid by EPA.")
    m2 = ols("share ~ miss_hybrid + miss_ev + C(segment) + C(quarter)", d, cluster="segment")
    record(5, "Same, by missing type", "RUN", m2, ["miss_hybrid", "miss_ev"], spec="share ~ missing hybrid + missing EV + FE")


# ---------------------------------------------------------------- 6 Charger ICE vs EV
def test6():
    d = W.loc["2024Q1":"2026Q3", ["Charger ICE", "Charger BEV"]].fillna(0).reset_index()
    d.columns = ["quarter", "ice", "bev"]; d["total"] = d.ice + d.bev
    d.to_csv(OUT / "details/test_06_data.csv", index=False)
    s = d[d.quarter >= "2025Q1"]  # new-generation era (old LD Charger ended Dec 2023, tail through 2024)
    m = ols("bev ~ ice", s, hac=1)
    record(6, "Charger BEV units ~ Charger ICE (Sixpack) units, 2025Q1-2026Q3", "RUN", m, ["ice"],
           spec="BEV_t ~ ICE_t; HAC(1). Negative = ICE replaced EV demand", data="Stellantis sales PDFs",
           note="n=7; EV tax-credit expiry (Sept 2025) coincides with ICE ramp, so substitution and policy are confounded.")
    m2 = ols("total ~ ice", s, hac=1)
    record(6, "Total Charger units ~ ICE units (coef 1 = purely additive)", "RUN", m2, ["ice"], spec="total_t ~ ICE_t; HAC(1)")


# ---------------------------------------------------------------- 7 Ram HD ~ Hemi availability
def test7():
    d = pd.DataFrame({"hd": W["Ram HD PU"], "ld": W["Ram LD PU"],
                      "rivals": gq[["Ford F-Series", "Chevrolet Silverado", "GMC Sierra"]].sum(axis=1)}).loc["2024Q1":"2026Q3"].reset_index()
    d.columns = ["quarter", "hd", "ld", "rivals"]
    d["hemi"] = d.quarter.map(lambda q: int(lineup("Ram LD PU", q).has_v8 and "5.7" in lineup("Ram LD PU", q).powertrains))
    d = add_time(d); d["lhd"] = np.log(d.hd); d["lriv"] = np.log(d.rivals); d["hd_share"] = d.hd / (d.hd + d.ld)
    d.to_csv(OUT / "details/test_07_data.csv", index=False)
    m = ols("lhd ~ hemi + lriv + C(qtr)", d, hac=1)
    record(7, "Ram HD units ~ Hemi available in Ram 1500", "RUN", m, ["hemi"],
           spec="log(HD) ~ Hemi-available dummy (MY lineup) + log(F/Silverado/Sierra units) + quarter-of-year; HAC(1)",
           data="Stellantis PDFs (LD/HD split from 2024); EPA lineups", note="n=11; Hemi absent for MY2025 (2024Q4-2025Q3). Negative = buyers trade down to Hemi 1500.")
    m2 = ols("hd_share ~ hemi + C(qtr)", d, hac=1)
    record(7, "HD share of Ram pickups ~ Hemi availability", "RUN", m2, ["hemi"], spec="HD/(HD+LD) ~ Hemi + quarter-of-year; HAC(1)")


# ---------------------------------------------------------------- 8 Durango ~ Charger ICE launch
def test8():
    riv = ["Ford Explorer", "Toyota Highlander", "Chevrolet Traverse", "Kia Telluride", "Hyundai Palisade", "Honda Pilot", "Toyota 4Runner"]
    rows = []
    for q in QS:
        rows.append(dict(unit="Durango", quarter=q, units=W.loc[q, "Durango"]))
        for r in riv: rows.append(dict(unit=r, quarter=q, units=gq.loc[q, r]))
    d = add_time(pd.DataFrame(rows).dropna()); d["ly"] = np.log(d.units)
    for lbl, start in [("2026Q1 (first quarter Charger ICE >1,000 units)", "2026Q1"), ("2025Q4", "2025Q4")]:
        d["tp"] = ((d.unit == "Durango") & (d.quarter >= start)).astype(int)
        m = ols("ly ~ tp + C(unit) + C(quarter)", d)
        record(8, f"Durango vs 3-row SUV rivals after Charger ICE launch, post from {lbl}", "RUN", m, ["tp"],
               spec="log(units) ~ Durango x Post + unit FE + quarter FE; HC1", data="Stellantis PDFs; GCBC",
               note="Durango had its own MY2026 changes (6.4L V8 back in lineup per EPA), so this is not a clean spillover test.")


# ---------------------------------------------------------------- 9 conquest
def test9():
    record(9, "Conquest share ~ new powertrain launches", "BLOCKED", note="No conquest figures in any 2022-2026 Stellantis US sales "
           "release (searched); J.D. Power / S&P conquest data are not public. Needs licensed S&P Global Mobility data or press excerpts.")


# ---------------------------------------------------------------- 10 fleet vs retail
# Retail YoY growth stated in Stellantis US quarterly releases (exact phrases in data/processed/release_text_mentions.csv);
# total YoY computed from the release PDFs. launch = nameplate had a new powertrain on sale within the prior 4 quarters.
RETAIL = [("2022Q3", "Compass", 225, 0), ("2022Q3", "Cherokee", 1, 0), ("2024Q4", "Ram", 2, 0), ("2024Q4", "Durango", 40, 0),
          ("2024Q4", "Grand Cherokee", 17, 0), ("2025Q1", "Ram", 16, 1), ("2025Q1", "Ram LD PU", 14, 1), ("2025Q1", "Ram HD PU", 18, 0),
          ("2025Q1", "Jeep", 2, 0), ("2025Q1", "Grand Cherokee", 14, 0), ("2025Q1", "Stellantis", 0, 0), ("2025Q2", "Durango", 36, 0),
          ("2025Q3", "Ram", 26, 1), ("2025Q4", "Ram LD PU", 27, 1), ("2025Q4", "Ram HD PU", 7, 0), ("2025Q4", "ProMaster Van", 9, 0),
          ("2026Q2", "Ram LD PU", 9, 1), ("2026Q2", "Durango", 9, 1), ("2026Q2", "Pacifica", 7, 0), ("2026Q2", "ProMaster Van", 6, 0),
          ("2026Q3", "Ram LD PU", 42, 1), ("2026Q3", "Durango", 18, 1), ("2026Q3", "Pacifica", 7, 0), ("2026Q3", "Charger", 22, 1)]


def test10():
    rows = []
    for q, ent, rg, launch in RETAIL:
        py = f"{int(q[:4]) - 1}{q[4:]}"
        if ent == "Charger": cur, prv = W.loc[q, ["Charger ICE", "Charger BEV"]].sum(), W.loc[py, ["Charger ICE", "Charger BEV"]].sum()
        else: cur, prv = W.loc[q, ent], W.loc[py, ent]
        tg = 100 * (cur / prv - 1)
        rows.append(dict(quarter=q, entity=ent, retail_yoy=rg, total_yoy=round(tg, 1), gap=tg - rg, launch=launch))
    d = pd.DataFrame(rows); d.to_csv(OUT / "details/test_10_retail_vs_total.csv", index=False)
    m = ols("gap ~ launch", d)
    record(10, "Total-minus-retail YoY growth gap ~ new powertrain launch", "RUN (proxy)", m, ["launch"],
           spec="(total YoY % - retail YoY %) ~ launch dummy; HC1. Positive gap = non-retail (fleet) growing faster",
           data="Retail growth quoted in Stellantis releases; totals from release PDFs",
           note=f"n={len(d)} hand-coded release statements; releases give retail % but no fleet units.")


if __name__ == "__main__":
    for f in [test1, test2, test3, test4, test5, test6, test7, test8, test9, test10]:
        f()
    print(pd.DataFrame(RESULTS)[["test", "title", "term", "coef", "se", "p", "n"]].to_string())
    pd.DataFrame(RESULTS).to_csv(OUT / "results_A.csv", index=False)
