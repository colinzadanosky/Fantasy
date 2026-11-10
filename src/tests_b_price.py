"""Section B - demand or discounting? Tests 11-20."""
import numpy as np, pandas as pd
from common import *

W = stla_wide(); IND = industry_q()
ATP = atp_q(["Jeep", "Ram", "Dodge", "Chrysler", "Industry Average"], "make")
ATPM = atp_q(["Stellantis", "Industry Average"], "manufacturer")


def base():
    d = pd.DataFrame({"jeep": W["Jeep"], "ram": W["Ram"], "stla": W["Stellantis"]}).join(IND).join(ATP).dropna()
    d = d.join(ATPM[["Stellantis"]].rename(columns={"Stellantis": "atp_stla"}))
    d = add_time(d.reset_index().rename(columns={"index": "quarter"}))
    return d


def test11_12():
    d = base(); d.to_csv(OUT / "details/test_11_12_data.csv", index=False)
    d["lind"] = np.log(d.lv_nsa_k)
    for b, test in [("Jeep", 11), ("Ram", 12)]:
        d["ly"] = np.log(d[b.lower()]); d["lp"] = np.log(d[b]); d["lrp"] = np.log(d[b] / d["Industry Average"])
        m = ols("ly ~ lp + lind + C(qtr)", d, hac=2)
        record(test, f"{b} quarterly sales ~ {b} KBB ATP (log-log)", "RUN", m, ["lp"],
               spec=f"log({b} units) ~ log({b} ATP) + log(US light-vehicle sales, BEA) + quarter-of-year; HAC(2)",
               data="KBB ATP monthly tables (Cox) averaged to quarters; Stellantis sales PDFs; BEA",
               note="Quarterly, not monthly: Stellantis reports sales only quarterly (GCBC monthly figures are allocations). "
                    "OLS on equilibrium price/quantity, not an IV demand elasticity; ATP excludes incentives.")
        m2 = ols("ly ~ lrp + lind + C(qtr)", d, hac=2)
        record(test, f"{b} sales ~ {b} ATP relative to industry ATP", "RUN", m2, ["lrp"],
               spec=f"log({b}) ~ log({b} ATP / industry ATP) + log(industry units) + quarter-of-year; HAC(2)")
    # stacked comparison Jeep vs Ram (test 12)
    s = pd.concat([d.assign(brand="Jeep", ly=np.log(d.jeep), lrp=np.log(d.Jeep / d["Industry Average"])),
                   d.assign(brand="Ram", ly=np.log(d.ram), lrp=np.log(d.Ram / d["Industry Average"]))])
    s["ram"] = (s.brand == "Ram").astype(int); s["lrp_ram"] = s.lrp * s.ram
    m = ols("ly ~ lrp + lrp_ram + C(brand)*lind + C(brand):C(qtr)", s, hac=2)
    record(12, "Difference in relative-price coefficient, Ram minus Jeep", "RUN", m, ["lrp_ram"],
           spec="stacked Jeep+Ram; log(units) ~ rel. price + rel. price x Ram + brand-specific controls; HAC(2). "
                "Positive = Ram less price-sensitive")


def test13():
    d = base(); d["share"] = d.stla / (d.lv_nsa_k * 1000) * 100; d["prem"] = (d.atp_stla / d["Industry Average"] - 1) * 100
    d = d.sort_values("quarter"); d["prem_l1"] = d.prem.shift(1)
    d.to_csv(OUT / "details/test_13_data.csv", index=False)
    m = ols("share ~ prem + C(qtr)", d, hac=2)
    record(13, "Stellantis US market share (%) ~ Stellantis ATP premium over industry (%)", "RUN", m, ["prem"],
           spec="share_t ~ premium_t + quarter-of-year; HAC(2)", data="KBB ATP manufacturer table; Stellantis PDFs; BEA (share = STLA / BEA light-vehicle sales)",
           note="BEA total includes some medium-duty classes differently than OEM reports; level of share is approximate, changes are informative.")
    m2 = ols("share ~ prem_l1 + C(qtr)", d.dropna(subset=["prem_l1"]), hac=2)
    record(13, "Same, premium lagged one quarter", "RUN", m2, ["prem_l1"], spec="share_t ~ premium_{t-1}")
    d["d4share"] = d.share - d.share.shift(4); d["prem_l4"] = d.prem.shift(4)
    m3 = ols("d4share ~ prem_l4", d.dropna(subset=["d4share", "prem_l4"]), hac=2)
    record(13, "Dynamic: YoY change in share (pp) ~ premium four quarters earlier", "RUN", m3, ["prem_l4"],
           spec="share_t - share_{t-4} ~ premium_{t-4}; HAC(2) (n<15 -> classical SE). Negative = a high premium is followed by share loss")


def blocked():
    B = {14: ("Model sales ~ (MSRP - segment ATP)", "KBB segment ATP collected (data/processed/kbb_atp_monthly.csv), but model-level MSRP/"
              "transaction prices by quarter are not public; configurator MSRP history would need to be compiled."),
         15: ("Hemi option price ~ Hemi share of Ram sales", "Stellantis does not disclose Hemi take rates; only two option-price points exist, so no regression is identifiable."),
         16: ("Listing discount % ~ powertrain", "Requires the weekly dealer-listing scrape described in the project plan (not yet collected; CarGurus returns 406 here; check site terms)."),
         17: ("Discount % ~ model year, by powertrain", "Requires listing scrape."),
         18: ("Stellantis incentive % ~ days' supply", "Cox publishes brand incentives / days' supply only inside paid vAuto/Cox data or press charts; the public KBB ATP PDFs carry no incentive or supply tables."),
         19: ("Dealer discount minus OEM incentive ~ days listed", "Requires listing scrape plus a history of OEM offers."),
         20: ("Forum price-paid reports ~ MSRP, by powertrain", "Needs manual/consented collection from Ram Forum and Jeep Garage threads; not collected.")}
    for k, (t, why) in B.items(): record(k, t, "BLOCKED", note=why)


if __name__ == "__main__":
    test11_12(); test13(); blocked()
    r = pd.DataFrame(RESULTS); print(r[["test", "title", "term", "coef", "se", "p", "n"]].to_string())
    r.to_csv(OUT / "results_B.csv", index=False)
