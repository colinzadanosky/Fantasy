"""Extension 14: demand vs push - market signals and historical analogs.
Inputs: data/processed/cox_brand_days_supply.csv (hand-collected from Cox Automotive monthly inventory articles, URLs in file),
        data/processed/kbb_atp_monthly.csv (KBB brand ATP), results/extensions/13_na_stock_identity.csv."""
import pathlib, pandas as pd
from ext_common import md_table
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; OUT = ROOT / "results/extensions"
cox = pd.read_csv(P / "cox_brand_days_supply.csv")
cx = cox[cox.entity.isin(["Industry", "Ram", "Jeep", "Ford", "Toyota", "Dodge", "GMC", "Ram 1500"])].pivot_table(
    index="entity", columns="month", values="days_supply")
ind = cox[cox.entity == "Industry"].set_index("month").days_supply
rel = cox[cox.entity.isin(["Ram", "Jeep", "Ford", "Toyota"])].assign(
    x_industry=lambda d: (d.days_supply / d.month.map(ind)).round(2)).dropna(subset=["x_industry"])

k = pd.read_csv(P / "kbb_atp_monthly.csv")
mk = k[k.table == "make"].pivot_table(index="month", columns="entity", values="atp")
mf = k[k.table == "manufacturer"].pivot_table(index="month", columns="entity", values="atp")
br = ["Ram", "Ford", "Chevrolet", "GMC", "Toyota", "Jeep"]
atp = pd.DataFrame({"Oct 2025": mk.loc["2025-10", br], "Oct 2026": mk.loc["2026-10", br]})
atp["yoy_pct"] = (100 * (atp["Oct 2026"] / atp["Oct 2025"] - 1)).round(1)
seg = k[(k.table == "segment") & (k.entity == "Full-size Pickup Truck")].set_index("month").atp
atp.loc["Full-size pickup segment"] = [seg["2025-10"], seg["2026-10"], round(100 * (seg["2026-10"] / seg["2025-10"] - 1), 1)]
st = mf.get("Stellantis"); ia = mf.get("Industry Average")
prem = (100 * (st / ia - 1)).dropna().round(1)

md = ["# 14. Genuine demand or a push? Market signals and historical analogs", "",
      "## A. Retail days' supply (Cox Automotive / vAuto, retail sales basis)", "",
      md_table(cx, fmt="{:.0f}"), "", "Multiple of industry days' supply:", "",
      md_table(rel[["month", "entity", "days_supply", "x_industry"]], index=False, fmt="{:.2f}"), "",
      "Stellantis reports 368k US dealer units, 84 days' supply, at end-September 2026 (+23% YoY; year-end target 320-350k). "
      "Its 84 days divides by total sales including fleet. Cox's 152-169 days divides by retail sales only. **The gap between the "
      "two is itself the fleet effect:** inventory looks normal against total sales and about 2x industry against retail demand.", "",
      "## B. Transaction prices (KBB ATP, after dealer discounts)", "", md_table(atp, fmt="{:,.1f}"), "",
      f"Stellantis manufacturer ATP premium over industry average: {prem.index[-13]} {prem.iloc[-13]:+.1f}% -> {prem.index[-1]} {prem.iloc[-1]:+.1f}% "
      f"(peak {prem.max():+.1f}% in {prem.idxmax()}).", "",
      "ATP mixes price and trim/powertrain mix: Hemi, TRX and Rumble Bee push Ram's average up without any like-for-like price increase.", "",
      "## C. Historical analogs: what happened after volume was bought", "",
      "| Episode | What was done | Signal at the time | What followed | Source |",
      "|---|---|---|---|---|",
      "| GM employee pricing, Jun-Sep 2005 | Employee discount for all buyers | June sales +41% YoY (best since 1986), inventory -26% to 980k | Pulled-forward demand; empty showrooms in early 2006; NBER study finds the 'discount' prices were often higher than before the program | [CBS](https://www.cbsnews.com/news/gm-uncorks-employee-pricing-forget-all-that-stuff-about-restraint/), [NBER w13140](http://www.nber.org/papers/w13140.pdf) |",
      "| Chrysler (Cerberus), 2007 | Cut production rather than discount; pressure on dealers | 71-84 days' supply mid-2007 | Sales -3% in 2007; bankruptcy 2009 | [Chrysler Oct 2007 release](https://media.stellantisnorthamerica.com/newsrelease.do?fIId=7455&id=6534&mid=), [Forbes](https://www.forbes.com/forbes/2007/1126/168/) |",
      "| FCA US, 2012-2016 'sales streak' | Monthly YoY growth claims sustained by paying dealers to report sales, 'cookie jar' of unreported sales | Uninterrupted growth headline | SEC $40m settlement (2019); streak had been broken in Sept 2013 | [SEC 2019-196](https://www.sec.gov/newsroom/press-releases/2019-196) |",
      "| Nissan US, 2016-2018 | Share target (~10%) via fleet and incentives | Share 9.2% H1 2016; incentives +6% to ~$3,400 | Fleet pulled back from 2018; share 8.4% (2018) -> 7.7% (2019) -> 6.0% (2020); volume -15% 2017-19; NA profit rose only as incentives fell | [TTAC](https://www.thetruthaboutcars.com/2016/08/nissans-push-greater-market-share-comes-big-cost/), [Autonews](https://europe.autonews.com/article/20181108/ANE/181109790/nissan-earnings-fall-21-as-u-s-turnaround-stalls), [Stellantis 20-F FY2020](https://www.sec.gov/Archives/edgar/data/1605484/000160548421000032/stellantis-20201231.htm) |",
      "| GM, 2015-2017 (the reverse) | Deliberately cut daily-rental sales: 400k -> 327k -> 282k | Headline sales down | ATP ~$4.4k above industry; incentives 1pp below industry; better residuals | [GM 10-K 2017](https://www.sec.gov/Archives/edgar/data/1467858/000146785818000022/gm201710k.htm), [GM Authority](http://gmauthority.com/blog/2016/07/general-motors-june-2016-sales-figures-numbers-results-united-states/) |",
      "| Stellantis US, 2022-2024 (own history) | Held price premium (about +24% over industry ATP, late 2023-early 2024) | Share 10.6% -> 7.4% | 2024 H2 destock: shipments 139k below sales; AOI swung to losses; 2025 incentives | test 13 / test 28 in REPORT.md; 13_na_stock_identity.csv |", "",
      "**Pattern across the analogs.** Volume bought through fleet, incentives or channel loading shows up first as (1) retail "
      "days' supply far above peers, (2) a gap between total and retail growth, and (3) shipments running ahead of sales. "
      "It reverses within 1-3 years as either a destock, which cuts production and AOI, or an incentive step-up. Nissan's profit "
      "recovered only after it accepted lower volume. GM's rental cut lowered volume but raised ATP and residuals.", ""]
# ---------- D. what the signals imply for 2026-27
ship9m = 379 + 445 + 357; q4_25_sales = 384.2      # 000s; Q4 2025 US+CA+MX sales from 13_na_stock_identity.csv
ai_ship_2026 = 1623; ai_q4 = ai_ship_2026 - ship9m
dest_lo, dest_hi = 368 - 350, 368 - 320            # Q4 US dealer-stock reduction implied by management's year-end target
q4_lo, q4_hi = q4_25_sales - dest_hi, q4_25_sales - dest_lo
prem_chg = prem.iloc[-1] - prem.iloc[-13]
md += ["## D. What the signals imply", "",
       f"* **Q4 2026 shipments.** The AI forecast's 1,623k 2026 wholesale implies Q4 shipments of {ai_q4}k against 9M actual {ship9m}k. "
       f"Management targets US dealer stock of 320-350k at year-end, from 368k, which is a {dest_lo}-{dest_hi}k reduction. If Q4 sales "
       f"match Q4 2025 (~{q4_25_sales:.0f}k US+CA+MX), shipments must be about {q4_lo:.0f}-{q4_hi:.0f}k. That puts 2026 at "
       f"**{ship9m+q4_lo:,.0f}-{ship9m+q4_hi:,.0f}k**, {ai_ship_2026-(ship9m+q4_hi):.0f}-{ai_ship_2026-(ship9m+q4_lo):.0f}k below the AI forecast. "
       f"The AI number needs either Q4 sales about {100*(ai_q4/q4_25_sales-1):.0f}% above Q4 2025 or another stock build. (The stock target is US-only; Canada and Mexico dealer stock is ignored.)",
       f"* **Price premium is climbing back toward 2023 levels.** Stellantis's ATP premium over industry rose {prem_chg:+.1f} pp in 12 months. "
       f"Test 13 found each pp of premium is followed by about 0.14 pp lower US share a year later, which implies about "
       f"{-0.14*prem_chg:.1f} pp of share at risk into 2027 (from about 7.8%). Part of the rise is Hemi/TRX mix, which test 13 cannot separate.",
       "* **Retail inventory is the tell.** Ram rose from 1.5x to 1.85x and Jeep from 1.7x to 2.1x industry retail days' supply "
       "between Dec 2025 and Sep 2026, while total sales grew and Stellantis's own total-sales days' supply looked normal.", ""]
(OUT / "14_market_signals.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
