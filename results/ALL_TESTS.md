# All 56 tests - coefficients and status

Generated from `results/regression_results.csv` by `src/make_appendix.py`. Full model summaries in `results/details/`.

| # | Test / specification | Term | Coef | SE | p | n | Status |
|---|---|---|---|---|---|---|---|
| 1 | Hemi return DiD: Ram LD (1500) vs F-150/Silverado/Sierra/Tundra | ram_post | 0.316 | 0.076 | 3.06e-05 | 55 | RUN |
| 1 | Hemi return DiD: Ram LD (1500) vs F-150/Silverado/Sierra/Tundra | ram_partial | -0.087 | 0.060 | 0.147 | 55 | RUN |
| 1 | Pre-trend: slope of Ram-vs-control log gap before 2025Q3 (Ram LD (1500) vs F-150/Silverado/Sierra/Tundra) | t | -0.021 | 0.037 | 0.603 | 6 | RUN |
| 1 | Robustness: Ram LD DiD, pre-period 2024Q2-2025Q2 (Hurricane-transition quarters only) | ram_post | 0.368 | 0.064 | 7.28e-09 | 50 | RUN |
| 1 | Hemi return DiD: Ram pickups total vs same controls (longer pre-period) | ram_post | -0.108 | 0.071 | 0.129 | 105 | RUN |
| 1 | Hemi return DiD: Ram pickups total vs same controls (longer pre-period) | ram_partial | -0.335 | 0.070 | 1.54e-06 | 105 | RUN |
| 1 | Pre-trend: slope of Ram-vs-control log gap before 2025Q3 (Ram pickups total vs same controls (longer pre-period)) | t | -0.055 | 0.004 | 1.74e-40 | 16 | RUN |
| 1 | Robustness: Ram pickups total DiD with Ram-specific linear trend | ram_post | 0.483 | 0.075 | 1.11e-10 | 105 | RUN |
| 1 | Robustness: Ram pickups total DiD with Ram-specific linear trend | ram_t | -0.054 | 0.006 | 3.18e-22 | 105 | RUN |
| 2 | Jeep brand sales ~ # powertrain offerings (model x powertrain) | lpt | 0.116 | 0.071 | 0.102 | 21 | RUN |
| 2 | Same, with linear trend | lpt | -0.058 | 0.096 | 0.546 | 21 | RUN |
| 2 | YoY growth version | dlpt | -0.058 | 0.110 | 0.601 | 17 | RUN |
| 3 | Model sales ~ powertrain count (Stellantis nameplate panel) | n_pt | 0.201 | 0.123 | 0.102 | 265 | RUN |
| 3 | YoY growth ~ change in powertrain count | dpt | 0.222 | 0.112 | 0.046 | 187 | RUN |
| 4 | Cannibalization: YoY change Compass+Grand Cherokee units ~ YoY change Cherokee units | d_ch | -1.616 | 0.464 | 0.00049 | 17 | RUN |
| 4 | Same, controlling for Q3-2026 production shutdown | d_ch | -1.327 | 0.681 | 0.051 | 17 | RUN |
| 5 | Stellantis segment share ~ powertrain coverage gap vs rivals | gap | 0.000363 | 0.020 | 0.986 | 147 | RUN |
| 5 | Same, by missing type | miss_hybrid | 0.077 | 0.065 | 0.238 | 147 | RUN |
| 5 | Same, by missing type | miss_ev | 0.119 | 0.109 | 0.273 | 147 | RUN |
| 6 | Charger BEV units ~ Charger ICE (Sixpack) units, 2025Q1-2026Q3 | ice | -0.571 | 0.302 | 0.117 | 7 | RUN |
| 6 | Total Charger units ~ ICE units (coef 1 = purely additive) | ice | 0.429 | 0.302 | 0.214 | 7 | RUN |
| 7 | Ram HD units ~ Hemi available in Ram 1500 | hemi | -0.062 | 0.047 | 0.248 | 11 | RUN |
| 7 | HD share of Ram pickups ~ Hemi availability | hemi | -0.029 | 0.043 | 0.521 | 11 | RUN |
| 8 | Durango vs 3-row SUV rivals after Charger ICE launch, post from 2026Q1 (first quarter Charger ICE >1,000 units) | tp | 0.147 | 0.133 | 0.270 | 167 | RUN |
| 8 | Durango vs 3-row SUV rivals after Charger ICE launch, post from 2025Q4 | tp | 0.255 | 0.134 | 0.057 | 167 | RUN |
| 9 | Conquest share ~ new powertrain launches |  |  |  |  |  | BLOCKED |
| 10 | Total-minus-retail YoY growth gap ~ new powertrain launch | launch | 19.309 | 20.078 | 0.336 | 24 | RUN (proxy) |
| 11 | Jeep quarterly sales ~ Jeep KBB ATP (log-log) | lp | 0.222 | 0.448 | 0.621 | 18 | RUN |
| 11 | Jeep sales ~ Jeep ATP relative to industry ATP | lrp | 0.455 | 0.374 | 0.224 | 18 | RUN |
| 12 | Ram quarterly sales ~ Ram KBB ATP (log-log) | lp | 0.254 | 0.674 | 0.706 | 18 | RUN |
| 12 | Ram sales ~ Ram ATP relative to industry ATP | lrp | 0.006 | 0.635 | 0.992 | 18 | RUN |
| 12 | Difference in relative-price coefficient, Ram minus Jeep | lrp_ram | -0.449 | 0.737 | 0.542 | 36 | RUN |
| 13 | Stellantis US market share (%) ~ Stellantis ATP premium over industry (%) | prem | 0.087 | 0.059 | 0.142 | 18 | RUN |
| 13 | Same, premium lagged one quarter | prem_l1 | 0.045 | 0.050 | 0.366 | 17 | RUN |
| 13 | Dynamic: YoY change in share (pp) ~ premium four quarters earlier | prem_l4 | -0.140 | 0.046 | 0.011 | 14 | RUN |
| 14 | Model sales ~ (MSRP - segment ATP) |  |  |  |  |  | BLOCKED |
| 15 | Hemi option price ~ Hemi share of Ram sales |  |  |  |  |  | BLOCKED |
| 16 | Listing discount % ~ powertrain |  |  |  |  |  | BLOCKED |
| 17 | Discount % ~ model year, by powertrain |  |  |  |  |  | BLOCKED |
| 18 | Stellantis incentive % ~ days' supply |  |  |  |  |  | BLOCKED |
| 19 | Dealer discount minus OEM incentive ~ days listed |  |  |  |  |  | BLOCKED |
| 20 | Forum price-paid reports ~ MSRP, by powertrain |  |  |  |  |  | BLOCKED |
| 21 | VIN exit-rate hazard model ~ powertrain + price band + metro |  |  |  |  |  | BLOCKED |
| 22 | Days listed ~ powertrain | trim, price |  |  |  |  |  | BLOCKED |
| 23 | Days' supply by model ~ # powertrain variants |  |  |  |  |  | BLOCKED |
| 24 | Dealer inventory depth ~ powertrain mix |  |  |  |  |  | BLOCKED |
| 25 | Brand days' supply ~ production cuts |  |  |  |  |  | BLOCKED |
| 26 | Prior-model-year share ~ powertrain |  |  |  |  |  | BLOCKED |
| 27 | Exit rate ~ price band, Stellantis vs Ford |  |  |  |  |  | BLOCKED |
| 28 | NA shipments minus US+Canada retail-reported sales, by half-year |  |  |  |  | 11 | DESCRIPTIVE |
| 29 | Exit rate ~ distance from metro center |  |  |  |  |  | BLOCKED |
| 30 | Exit rate ~ color/package, same powertrain |  |  |  |  |  | BLOCKED |
| 31 | Trends "Ram Hemi" ~ Ram pickups sales (current + 1-quarter lag) | ltr0 | 0.436 | 0.268 | 0.103 | 20 | RUN |
| 31 | Trends "Ram Hemi" ~ Ram pickups sales (current + 1-quarter lag) | ltr1 | -0.309 | 0.284 | 0.275 | 20 | RUN |
| 31 | Granger-style: Ram pickups sales ~ own lag + Trends "Ram Hemi" lag | ltr1 | 0.103 | 0.091 | 0.254 | 20 | RUN |
| 31 | Trends "Ram Hemi" ~ Ram 1500 sales (current + 1-quarter lag) | ltr0 | -0.237 | 0.908 | 0.811 | 10 | RUN |
| 31 | Trends "Ram Hemi" ~ Ram 1500 sales (current + 1-quarter lag) | ltr1 | 1.179 | 0.960 | 0.307 | 10 | RUN |
| 31 | Granger-style: Ram 1500 sales ~ own lag + Trends "Ram Hemi" lag | ltr1 | 0.759 | 0.460 | 0.198 | 10 | RUN |
| 31 | Trends "Ram 1500" ~ Ram pickups sales (current + 1-quarter lag) | ltr0 | -0.043 | 0.198 | 0.828 | 20 | RUN |
| 31 | Trends "Ram 1500" ~ Ram pickups sales (current + 1-quarter lag) | ltr1 | 0.486 | 0.250 | 0.052 | 20 | RUN |
| 31 | Granger-style: Ram pickups sales ~ own lag + Trends "Ram 1500" lag | ltr1 | 0.354 | 0.139 | 0.011 | 20 | RUN |
| 31 | Trends "Ram 1500" ~ Ram 1500 sales (current + 1-quarter lag) | ltr0 | -0.194 | 0.233 | 0.466 | 10 | RUN |
| 31 | Trends "Ram 1500" ~ Ram 1500 sales (current + 1-quarter lag) | ltr1 | 1.653 | 0.246 | 0.007 | 10 | RUN |
| 31 | Granger-style: Ram 1500 sales ~ own lag + Trends "Ram 1500" lag | ltr1 | 1.716 | 0.250 | 0.006 | 10 | RUN |
| 32 | Cherokee/RAV4 sales ratio vs "Cherokee hybrid"/"RAV4 hybrid" search ratio | corr | -0.940 |  |  | 4 | DESCRIPTIVE |
| 33 | Jeep sales ~ "Jeep price" search share (% of "Jeep" searches) | ps0 | 0.022 | 0.039 | 0.568 | 20 | RUN |
| 33 | Jeep sales ~ "Jeep price" search share (% of "Jeep" searches) | ps_l1 | -0.103 | 0.039 | 0.008 | 20 | RUN |
| 34 | Reddit price-complaint share ~ brand ATP |  |  |  |  |  | BLOCKED |
| 35 | Reddit Hemi sentiment ~ Ram retail growth |  |  |  |  |  | BLOCKED |
| 36 | YouTube review views ~ launch-quarter sales |  |  |  |  |  | BLOCKED |
| 37 | CarGurus deal-rating mix ~ exit rate |  |  |  |  |  | BLOCKED |
| 38 | Model sales ~ Wikipedia pageviews (model panel) | lv | -0.100 | 0.256 | 0.694 | 301 | RUN |
| 38 | Same, pageviews lagged one quarter | lv_l1 | -0.178 | 0.200 | 0.372 | 288 | RUN |
| 39 | Dealer review sentiment ~ inventory turn |  |  |  |  |  | BLOCKED |
| 40 | Stellantis US share ~ Stellantis brands' search share vs Ford+Toyota | ss | 0.621 | 0.135 | 3.94e-06 | 21 | RUN |
| 40 | Same, search share lagged one quarter | ss_l1 | 0.618 | 0.159 | 9.78e-05 | 20 | RUN |
| 41 | PROXY: Ram share of full-size pickups ~ US gasoline price | lgas | 0.861 | 0.262 | 0.001 | 21 | RUN (proxy) |
| 41 | Cross-state: "Hemi" search intensity ~ regional (PADD) gas price | np.log(gas) | 11.384 | 12.706 | 0.370 | 50 | RUN (proxy) |
| 42 | Cherokee hybrid exit rate ~ gas prices |  |  |  |  |  | BLOCKED |
| 43 | Stellantis sales ~ 60-month new-car loan rate | r60 | -0.060 | 0.012 | 2.1e-07 | 21 | RUN |
| 43 | Stellantis sales ~ loan rate, controlling for industry volume (excess sensitivity) | r60 | -0.015 | 0.026 | 0.557 | 21 | RUN |
| 43 | Ram sales ~ 60-month new-car loan rate | r60 | -0.064 | 0.012 | 1.12e-07 | 21 | RUN |
| 43 | Ram sales ~ loan rate, controlling for industry volume (excess sensitivity) | r60 | -0.049 | 0.036 | 0.173 | 21 | RUN |
| 43 | Jeep sales ~ 60-month new-car loan rate | r60 | -0.064 | 0.011 | 1.65e-08 | 21 | RUN |
| 43 | Jeep sales ~ loan rate, controlling for industry volume (excess sensitivity) | r60 | -0.034 | 0.027 | 0.215 | 21 | RUN |
| 44 | Stellantis sales by price band ~ U. Michigan sentiment | sent:C(band)[high] | -0.002 | 0.002 | 0.269 | 63 | RUN |
| 44 | Stellantis sales by price band ~ U. Michigan sentiment | sent:C(band)[mid] | 0.006 | 0.004 | 0.121 | 63 | RUN |
| 44 | Stellantis sales by price band ~ U. Michigan sentiment | sent:C(band)[low] | 0.015 | 0.006 | 0.015 | 63 | RUN |
| 44 | Band sales relative to industry ~ sentiment (does Stellantis feel shocks more than the market?) | sent:C(band)[high] | -0.001 | 0.004 | 0.809 | 63 | RUN |
| 44 | Band sales relative to industry ~ sentiment (does Stellantis feel shocks more than the market?) | sent:C(band)[mid] | 0.007 | 0.006 | 0.219 | 63 | RUN |
| 44 | Band sales relative to industry ~ sentiment (does Stellantis feel shocks more than the market?) | sent:C(band)[low] | 0.017 | 0.008 | 0.042 | 63 | RUN |
| 45 | State "Hemi" search intensity ~ income, rurality, truck share | np.log(med_income) | -89.358 | 10.578 | 2.97e-17 | 50 | RUN (proxy) |
| 45 | State "Hemi" search intensity ~ income, rurality, truck share | rural_share | -0.257 | 0.153 | 0.093 | 50 | RUN (proxy) |
| 45 | State "Hemi" search intensity ~ income, rurality, truck share | truck_share | 2.193 | 0.257 | 1.37e-17 | 50 | RUN (proxy) |
| 46 | Stellantis share ~ Texas/Southeast vs coastal states |  |  |  |  |  | BLOCKED |
| 47 | Event study: share of Stellantis sales from V8-offering nameplates ~ post CAFE-penalty zeroing (Jul 2025) | post | 7.217 | 8.654 | 0.404 | 21 | RUN (proxy) |
| 48 | Tariffs: Stellantis ATP vs peer OEMs after April 2025 auto tariffs | sp | -0.051 | 0.009 | 7.75e-08 | 336 | RUN |
| 48 | Same, with OEM-specific linear trends | sp | -0.028 | 0.023 | 0.226 | 336 | RUN |
| 49 | Charger BEV share of Charger sales ~ post EV-credit expiry (Sep 30 2025) | post | -58.138 | 15.336 | 0.013 | 7 | RUN |
| 49 | Stellantis BEV share (Charger BEV + Wagoneer S + 500e) ~ post credit expiry | post | -1.817 | 0.131 | 3.54e-05 | 7 | RUN |
| 50 | Canada: Ram pickups vs Canadian full-size rivals after US Hemi return | tp | -0.365 | 0.089 | 4.48e-05 | 105 | RUN |
| 50 | Same, with Ram-specific trend | tp | 0.245 | 0.111 | 0.027 | 105 | RUN |
| 50 | Stellantis Canada YoY growth ~ US YoY growth | gus | 0.907 | 0.318 | 0.016 | 13 | RUN |
| 51 | NA revenue per unit (USD k) ~ Ram share of US sales (half-years 2021-2026) | ram_share_us | -0.207 | 0.198 | 0.328 | 10 | RUN |
| 51 | NA revenue per unit (USD k) ~ Ram share of US sales (quarters 2025Q1-2026Q3) | ram_share_us | 0.305 | 0.168 | 0.129 | 7 | RUN |
| 52 | NA AOI margin (%) ~ NA shipments (000s) (half-years 2021-2026) | ship | 0.065 | 0.011 | 0.000447 | 10 | RUN |
| 52 | NA AOI margin (%) ~ NA shipments (000s) (quarters 2025Q1-2026Q3) | ship | 0.021 | 0.021 | 0.345 | 7 | RUN |
| 53 | Used values: Hemi vs Hurricane Ram 1500 |  |  |  |  |  | BLOCKED |
| 54 | Used Jeep prices ~ new Jeep incentives |  |  |  |  |  | BLOCKED |
| 55 | STLA abnormal return on US sales-release days ~ sales growth vs industry | surprise | 0.062 | 0.119 | 0.604 | 16 | RUN |
| 55 | Mean CAR[0,+1] on sales-release days | mean_car_pct | 0.968 | 0.956 |  | 16 | DESCRIPTIVE |
| 56 | NHTSA recall campaigns per nameplate-model-year ~ new powertrain introduced that MY | any_new | 0.406 | 0.114 | 0.000375 | 80 | RUN |
| 56 | NHTSA recall campaigns per nameplate-model-year ~ new powertrain introduced that MY | n_pt | 0.016 | 0.159 | 0.920 | 80 | RUN |

## Specifications, data and caveats

**1. Hemi return DiD: Ram LD (1500) vs F-150/Silverado/Sierra/Tundra** - RUN
- spec: log(units) ~ Ram x Post(>=2025Q4) + Ram x 2025Q3 + unit FE + quarter FE; HC1 SE
- spec: gap_t = log(Ram) - mean log(controls); gap ~ t over pre-period; HAC(1)
- spec: as above, dropping 2024Q1
- spec: + Ram x linear trend (pre-period share loss of -5.5%/qtr)
- data: Stellantis quarterly sales PDFs; GoodCarBadCar (GCBC) quarterly rivals
- note: Control pickups include HD (F-Series, Silverado, Sierra). Pre-period includes MY2025 (no-Hemi) quarters, so the estimate is the Hemi-return effect relative to the Hurricane-only year.

**2. Jeep brand sales ~ # powertrain offerings (model x powertrain)** - RUN
- spec: log(Jeep units) ~ log(powertrain offerings) + log(US light-vehicle sales) + quarter-of-year; HAC(2)
- spec: + linear trend; HAC(2)
- spec: d4 log(Jeep) ~ d4 log(offerings) + d4 log(industry); HAC(2)
- data: Stellantis sales PDFs; EPA fueleconomy.gov lineups; BEA
- note: Offerings = sum over nameplates selling >=500 units of distinct EPA powertrains.

**3. Model sales ~ powertrain count (Stellantis nameplate panel)** - RUN
- spec: log(units) ~ n_powertrains + model FE + quarter FE; SE clustered by model
- spec: d4 log(units) ~ d4 n_powertrains + quarter FE; cluster model
- data: Stellantis sales PDFs; EPA lineups
- note: 20 nameplates; quarters with <500 units dropped

**4. Cannibalization: YoY change Compass+Grand Cherokee units ~ YoY change Cherokee units** - RUN
- spec: d4 (Compass+GC) ~ d4 Cherokee + d4 rival compact/midsize SUV units; HAC(2). Coef -1 = full cannibalization, 0 = new demand
- spec: + dummy 2026Q3
- data: Stellantis sales PDFs; GCBC rivals
- note: Cherokee hybrid volume exists only 2025Q4-2026Q3; earlier Cherokee changes are the old ICE model winding down. Q3 2026 Compass/GC drop coincides with a planned production shutdown (Stellantis Q3 2026 release).

**5. Stellantis segment share ~ powertrain coverage gap vs rivals** - RUN
- spec: share ~ #types (HEV/PHEV/EV/V8/diesel) offered by a rival but not Stellantis + segment FE + quarter FE; cluster segment
- spec: share ~ missing hybrid + missing EV + FE
- data: Stellantis PDFs; GCBC rivals; EPA lineups
- note: 7 segments; Wrangler excluded (no Bronco data). eTorque counted as hybrid by EPA.

**6. Charger BEV units ~ Charger ICE (Sixpack) units, 2025Q1-2026Q3** - RUN
- spec: BEV_t ~ ICE_t; HAC(1). Negative = ICE replaced EV demand
- spec: total_t ~ ICE_t; HAC(1)
- data: Stellantis sales PDFs
- note: n=7; EV tax-credit expiry (Sept 2025) coincides with ICE ramp, so substitution and policy are confounded.

**7. Ram HD units ~ Hemi available in Ram 1500** - RUN
- spec: log(HD) ~ Hemi-available dummy (MY lineup) + log(F/Silverado/Sierra units) + quarter-of-year; HAC(1)
- spec: HD/(HD+LD) ~ Hemi + quarter-of-year; HAC(1)
- data: Stellantis PDFs (LD/HD split from 2024); EPA lineups
- note: n=11; Hemi absent for MY2025 (2024Q4-2025Q3). Negative = buyers trade down to Hemi 1500.

**8. Durango vs 3-row SUV rivals after Charger ICE launch, post from 2026Q1 (first quarter Charger ICE >1,000 units)** - RUN
- spec: log(units) ~ Durango x Post + unit FE + quarter FE; HC1
- data: Stellantis PDFs; GCBC
- note: Durango had its own MY2026 changes (6.4L V8 back in lineup per EPA), so this is not a clean spillover test.

**9. Conquest share ~ new powertrain launches** - BLOCKED
- note: No conquest figures in any 2022-2026 Stellantis US sales release (searched); J.D. Power / S&P conquest data are not public. Needs licensed S&P Global Mobility data or press excerpts.

**10. Total-minus-retail YoY growth gap ~ new powertrain launch** - RUN (proxy)
- spec: (total YoY % - retail YoY %) ~ launch dummy; HC1. Positive gap = non-retail (fleet) growing faster
- data: Retail growth quoted in Stellantis releases; totals from release PDFs
- note: n=24 hand-coded release statements; releases give retail % but no fleet units.

**11. Jeep quarterly sales ~ Jeep KBB ATP (log-log)** - RUN
- spec: log(Jeep units) ~ log(Jeep ATP) + log(US light-vehicle sales, BEA) + quarter-of-year; HAC(2)
- spec: log(Jeep) ~ log(Jeep ATP / industry ATP) + log(industry units) + quarter-of-year; HAC(2)
- data: KBB ATP monthly tables (Cox) averaged to quarters; Stellantis sales PDFs; BEA
- note: Quarterly, not monthly: Stellantis reports sales only quarterly (GCBC monthly figures are allocations). OLS on equilibrium price/quantity, not an IV demand elasticity; ATP excludes incentives.

**12. Ram quarterly sales ~ Ram KBB ATP (log-log)** - RUN
- spec: log(Ram units) ~ log(Ram ATP) + log(US light-vehicle sales, BEA) + quarter-of-year; HAC(2)
- spec: log(Ram) ~ log(Ram ATP / industry ATP) + log(industry units) + quarter-of-year; HAC(2)
- spec: stacked Jeep+Ram; log(units) ~ rel. price + rel. price x Ram + brand-specific controls; HAC(2). Positive = Ram less price-sensitive
- data: KBB ATP monthly tables (Cox) averaged to quarters; Stellantis sales PDFs; BEA
- note: Quarterly, not monthly: Stellantis reports sales only quarterly (GCBC monthly figures are allocations). OLS on equilibrium price/quantity, not an IV demand elasticity; ATP excludes incentives.

**13. Stellantis US market share (%) ~ Stellantis ATP premium over industry (%)** - RUN
- spec: share_t ~ premium_t + quarter-of-year; HAC(2)
- spec: share_t ~ premium_{t-1}
- spec: share_t - share_{t-4} ~ premium_{t-4}; HAC(2) (n<15 -> classical SE). Negative = a high premium is followed by share loss
- data: KBB ATP manufacturer table; Stellantis PDFs; BEA (share = STLA / BEA light-vehicle sales)
- note: BEA total includes some medium-duty classes differently than OEM reports; level of share is approximate, changes are informative.

**14. Model sales ~ (MSRP - segment ATP)** - BLOCKED
- note: KBB segment ATP collected (data/processed/kbb_atp_monthly.csv), but model-level MSRP/transaction prices by quarter are not public; configurator MSRP history would need to be compiled.

**15. Hemi option price ~ Hemi share of Ram sales** - BLOCKED
- note: Stellantis does not disclose Hemi take rates; only two option-price points exist, so no regression is identifiable.

**16. Listing discount % ~ powertrain** - BLOCKED
- note: Requires the weekly dealer-listing scrape described in the project plan (not yet collected; CarGurus returns 406 here; check site terms).

**17. Discount % ~ model year, by powertrain** - BLOCKED
- note: Requires listing scrape.

**18. Stellantis incentive % ~ days' supply** - BLOCKED
- note: Cox publishes brand incentives / days' supply only inside paid vAuto/Cox data or press charts; the public KBB ATP PDFs carry no incentive or supply tables.

**19. Dealer discount minus OEM incentive ~ days listed** - BLOCKED
- note: Requires listing scrape plus a history of OEM offers.

**20. Forum price-paid reports ~ MSRP, by powertrain** - BLOCKED
- note: Needs manual/consented collection from Ram Forum and Jeep Garage threads; not collected.

**21. VIN exit-rate hazard model ~ powertrain + price band + metro** - BLOCKED
- note: Needs the weekly listings scrape (VIN, powertrain via NHTSA vPIC decode, price, dealer, first/last seen). Model code is ready in src/listings_models.py; it cannot be backfilled, so collection must start now. Check site terms before scraping.

**22. Days listed ~ powertrain | trim, price** - BLOCKED
- note: Needs the weekly listings scrape (VIN, powertrain via NHTSA vPIC decode, price, dealer, first/last seen). Model code is ready in src/listings_models.py; it cannot be backfilled, so collection must start now. Check site terms before scraping.

**23. Days' supply by model ~ # powertrain variants** - BLOCKED
- note: Cox model-level days' supply is not public (vAuto subscription).

**24. Dealer inventory depth ~ powertrain mix** - BLOCKED
- note: Needs the weekly listings scrape (VIN, powertrain via NHTSA vPIC decode, price, dealer, first/last seen). Model code is ready in src/listings_models.py; it cannot be backfilled, so collection must start now. Check site terms before scraping.

**25. Brand days' supply ~ production cuts** - BLOCKED
- note: No public brand days' supply series; production cuts appear only as text in releases.

**26. Prior-model-year share ~ powertrain** - BLOCKED
- note: Needs the weekly listings scrape (VIN, powertrain via NHTSA vPIC decode, price, dealer, first/last seen). Model code is ready in src/listings_models.py; it cannot be backfilled, so collection must start now. Check site terms before scraping.

**27. Exit rate ~ price band, Stellantis vs Ford** - BLOCKED
- note: Needs the weekly listings scrape (VIN, powertrain via NHTSA vPIC decode, price, dealer, first/last seen). Model code is ready in src/listings_models.py; it cannot be backfilled, so collection must start now. Check site terms before scraping.

**28. NA shipments minus US+Canada retail-reported sales, by half-year** - DESCRIPTIVE
- spec: ship - (US sales + Canada sales); residual also includes Mexico sales (not reported) and fleet timing
- data: Stellantis 6-K results (SEC EDGAR); US and Canada sales releases
- note: See details/test_28_shipments_vs_sales.csv. A rising residual = dealer stock build (shipment push); H2 2024 shows the drawdown Stellantis described ('dealer inventory reduced by over 50,000 units' in Q3 2024).

**29. Exit rate ~ distance from metro center** - BLOCKED
- note: Needs the weekly listings scrape (VIN, powertrain via NHTSA vPIC decode, price, dealer, first/last seen). Model code is ready in src/listings_models.py; it cannot be backfilled, so collection must start now. Check site terms before scraping.

**30. Exit rate ~ color/package, same powertrain** - BLOCKED
- note: Needs the weekly listings scrape (VIN, powertrain via NHTSA vPIC decode, price, dealer, first/last seen). Model code is ready in src/listings_models.py; it cannot be backfilled, so collection must start now. Check site terms before scraping.

**31. Trends "Ram Hemi" ~ Ram pickups sales (current + 1-quarter lag)** - RUN
- spec: log(units) ~ log(Trends_t) + log(Trends_{t-1}) + log(industry) + quarter-of-year; HAC(2)
- spec: log(units_t) ~ log(units_{t-1}) + log(Trends_{t-1}) + log(industry) + quarter-of-year
- data: Google Trends (US, monthly averaged to quarter); Stellantis PDFs
- note: 1-3 month lags are not testable: Stellantis reports quarterly. Quarter lag ~ 1-3 months.

**32. Cherokee/RAV4 sales ratio vs "Cherokee hybrid"/"RAV4 hybrid" search ratio** - DESCRIPTIVE
- spec: correlation over quarters with Cherokee hybrid on sale (2025Q4-2026Q3)
- data: Google Trends; Stellantis PDFs; GCBC
- note: Only 4 quarters; RAV4 sales are not split hybrid/ICE in public data. Mean search ratio = 0.053, mean sales ratio = 0.058.

**33. Jeep sales ~ "Jeep price" search share (% of "Jeep" searches)** - RUN
- spec: log(Jeep) ~ price-search share_t + share_{t-1} + log(industry) + quarter-of-year; HAC(2)
- data: Google Trends
- note: "Jeep too expensive" and "Jeep deals" have ~zero Trends volume; "Jeep price" used.

**34. Reddit price-complaint share ~ brand ATP** - BLOCKED
- note: reddit.com returns 403 from this environment; needs Reddit API credentials (OAuth app).

**35. Reddit Hemi sentiment ~ Ram retail growth** - BLOCKED
- note: Same: Reddit API access required.

**36. YouTube review views ~ launch-quarter sales** - BLOCKED
- note: YouTube Data API v3 requires an API key; none configured.

**37. CarGurus deal-rating mix ~ exit rate** - BLOCKED
- note: Requires CarGurus listings scrape (site returns 406; check terms).

**38. Model sales ~ Wikipedia pageviews (model panel)** - RUN
- spec: log(units) ~ log(pageviews) + model FE + quarter FE; cluster model
- spec: log(units_t) ~ log(views_{t-1}) + FE
- data: Wikimedia REST API; Stellantis PDFs; GCBC
- note: 16 nameplates (13 Stellantis + 3 rivals), 2021Q3-2026Q3

**39. Dealer review sentiment ~ inventory turn** - BLOCKED
- note: Google Places API key required, plus dealer inventory turns from the listings scrape.

**40. Stellantis US share ~ Stellantis brands' search share vs Ford+Toyota** - RUN
- spec: share% ~ search share% (Jeep+Dodge+Chrysler)/(those+Ford+Toyota) + quarter-of-year; HAC(2)
- data: Google Trends (one payload, comparable scale); Stellantis PDFs; BEA
- note: Ram excluded from Trends (term 'Ram' ambiguous; 'Ram trucks' ~0 volume).

**41. PROXY: Ram share of full-size pickups ~ US gasoline price** - RUN (proxy)
- spec: log(Ram/(Ram+F-Series+Silverado)) ~ log(EIA retail regular) + quarter-of-year; HAC(2)
- spec: state Trends index ~ log PADD avg gas price (Jun 2025-Oct 2026) + state covariates; HC1
- data: EIA weekly gasoline; Stellantis PDFs; GCBC
- data: EIA PADD prices; Trends; Census; FHWA
- note: The planned test (Hemi share of listings by region ~ regional gas) needs the listings scrape; this national proxy cannot isolate the V8.
- note: Only 5 distinct gas prices (PADD level); weak identification.

**42. Cherokee hybrid exit rate ~ gas prices** - BLOCKED
- note: Needs listings scrape; national Cherokee hybrid sales exist for only 4 quarters.

**43. Stellantis sales ~ 60-month new-car loan rate** - RUN
- spec: log(units) ~ rate (pp) + quarter-of-year; HAC(2)
- spec: log(units) ~ rate + log(industry units) + quarter-of-year; HAC(2)
- data: Fed G.19 terms of credit (commercial banks, 60m new car); Stellantis PDFs

**44. Stellantis sales by price band ~ U. Michigan sentiment** - RUN
- spec: log(band units) ~ sentiment x band + band FE + band x quarter-of-year; HAC(2)
- spec: log(band units / industry units) ~ sentiment x band + FE
- data: U. Michigan ICS; Stellantis PDFs
- note: Bands by KBB segment ATP: high = full-size pickup/SUV (>$65k), mid = $45-60k, low = compact (<$40k).

**45. State "Hemi" search intensity ~ income, rurality, truck share** - RUN (proxy)
- spec: Trends state index (Jun 2025-Oct 2026) ~ log median HH income + rural % + truck registration %; HC1
- data: Google Trends by state; Census SAIPE 2023; Census 2020 urban/rural by county; FHWA MV-1 2022
- note: Search interest stands in for Hemi share of sales/listings (needs scrape). Trends index is relative within each state.

**46. Stellantis share ~ Texas/Southeast vs coastal states** - BLOCKED
- note: State new-vehicle registration data by make is licensed (S&P Global Mobility/Experian); no free state series found.

**47. Event study: share of Stellantis sales from V8-offering nameplates ~ post CAFE-penalty zeroing (Jul 2025)** - RUN (proxy)
- spec: V8-available sales share % ~ post(>=2025Q3) + trend + quarter-of-year; HAC(2)
- data: EPA lineups; Stellantis PDFs
- note: Production V8 share is not public; this uses nameplate V8 availability. Hemi-return decision (Jun 2025) predates the July 2025 law, so policy and demand are not separable. V8 powertrains offered by MY: {2018: np.int64(12), 2019: np.int64(13), 2020: np.int64(13), 2021: np.int64(16), 2022: np.int64(15), 2023: np.int64(16), 2024: np.int64(9), 2025: np.int64(3), 2026: np.int64(6), 2027: np.int64(7)}

**48. Tariffs: Stellantis ATP vs peer OEMs after April 2025 auto tariffs** - RUN
- spec: log(ATP) ~ Stellantis x Post(>=Apr 2025) + OEM FE + month FE; cluster month
- spec: + OEM x linear trend
- data: KBB ATP manufacturer table, Mar 2022-Oct 2026
- note: Peers: Ford, GM, Toyota, Honda, Hyundai. ATP reflects mix and excludes incentives; tariff pass-through and mix shift are not separable.

**49. Charger BEV share of Charger sales ~ post EV-credit expiry (Sep 30 2025)** - RUN
- spec: BEV share % ~ post(>=2025Q4); HAC(1); 2025Q1-2026Q3
- spec: BEV % of Stellantis US ~ post
- data: Stellantis PDFs
- note: n=7; Sixpack ICE ramp coincides with the credit expiry, so the effect is an upper bound on the policy effect.

**50. Canada: Ram pickups vs Canadian full-size rivals after US Hemi return** - RUN
- spec: log(units) ~ Ram x Post(>=2025Q4) + unit FE + quarter FE; HC1
- spec: + Ram x trend
- spec: d4 log(Canada total) ~ d4 log(US total); HAC(2)
- data: GCBC Canada tables (from OEM reports)
- data: Stellantis Canada releases (quarterly totals)
- note: Hemi return applied to Canada too, so this is a replication in a second market, not a spillover test. Mexico: no public model data.

**51. NA revenue per unit (USD k) ~ Ram share of US sales (half-years 2021-2026)** - RUN
- spec: NA net revenue x EURUSD / NA shipments ~ Ram % of Stellantis US sales; HC1
- data: Stellantis 6-K results (SEC EDGAR); Yahoo EURUSD; Stellantis US PDFs
- note: Ram share of shipments is not disclosed; Ram share of US sales is the proxy. Revenue includes pricing, incentives and fleet mix.

**52. NA AOI margin (%) ~ NA shipments (000s) (half-years 2021-2026)** - RUN
- spec: AOI margin ~ shipments; HC1
- data: Stellantis 6-K results
- note: 2024-25 margins include tariffs, warranty-estimate changes and incentive spend; fixed-cost leverage is not isolated.

**53. Used values: Hemi vs Hurricane Ram 1500** - BLOCKED
- note: Needs used-listing scrape (or Manheim/J.D. Power valuation data by engine); Manheim's public index is not split by engine.

**54. Used Jeep prices ~ new Jeep incentives** - BLOCKED
- note: No public Jeep incentive series (see #18) and no brand-level used price index.

**55. STLA abnormal return on US sales-release days ~ sales growth vs industry** - RUN
- spec: CAR[0,+1] (market model vs SPY, est. window t-130..t-10) ~ (STLA YoY - industry YoY) pp; HC1
- data: Yahoo Finance STLA, SPY; Stellantis PDFs; BEA
- note: Days' supply component blocked (no public Cox brand series). Q2-2024 release missing from the media archive; Q4 dates are early January.

**56. NHTSA recall campaigns per nameplate-model-year ~ new powertrain introduced that MY** - RUN
- spec: Poisson: campaigns ~ new-powertrain dummy + # powertrains + nameplate FE + MY FE; cluster nameplate (coef = log rate ratio)
- data: NHTSA FLAT_RCL recalls (through Nov 2026); EPA lineups
- note: Recent model years have had less time to accumulate recalls (absorbed by MY FE). Counts campaigns, not affected units.
