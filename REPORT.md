# Stellantis US powertrain demand: results of the 56-test regression plan

Run date: 2026-11-10. Data run through Q3 2026 (sales), Oct 2026 (prices, rates, sentiment) and Nov 2026 (gas, recalls, stock).
The full coefficient table is in [`results/ALL_TESTS.md`](results/ALL_TESTS.md) (machine-readable: `results/regression_results.csv`).
Model summaries are in `results/details/`.

**Charts:** every regression term has a correlation chart in [`results/charts/`](results/charts/), all 86 collected in `results/charts/all_charts.pdf`. The left panel shows the raw data with its Pearson r as a percent. The right panel shows the same relationship after removing the regression's controls and fixed effects; its slope is the reported coefficient and its partial r is the correlation the regression measures. `results/charts/chart_index.csv` lists both r values for every chart.

## What could be run

| Status | Tests | Count |
|---|---|---|
| Run on primary data | 1-8, 11-13, 31, 33, 38, 40, 43, 44, 48-52, 55, 56 | 24 |
| Run on a proxy (planned data not available) | 10, 41, 45, 47 | 4 |
| Descriptive only (too few observations to regress) | 28, 32 | 2 |
| Blocked: needs the weekly listings scrape | 16, 17, 19, 21, 22, 24, 26, 27, 29, 30, 37, 42, 53 | 13 |
| Blocked: licensed or credentialed data | 9, 14, 15, 18, 20, 23, 25, 34, 35, 36, 39, 46, 54 | 13 |

**Biggest constraint: the listings scrape.** Test 21 (★) and most of section C need it, and it has not been collected yet. A past weekly scrape can't be rebuilt after the fact, so every week collection is delayed is lost. The model code is ready in `src/listings_models.py`; it has only been smoke-tested on synthetic data, and no results from that run are reported.

**Sales are quarterly.** Stellantis reports US sales by quarter only. GoodCarBadCar's monthly Stellantis figures are allocations of the quarterly totals, so every "monthly" test (11, 12, 31) was run on quarters. A one-quarter lag stands in for the planned 1-3 month lags.

## Headline findings (★ tests first)

**1 ★ Did the Hemi add Ram 1500 volume? Yes, relative to the Hurricane-only year.**
- Ram light-duty (1500) sales rose **+0.32 log points (about +37%)** against F-150, Silverado, Sierra and Tundra in 2025Q4-2026Q3 (p < 0.001).
  - Dropping 2024Q1 from the pre-period gives +0.37.
  - The pre-period gap is flat: slope −0.02 per quarter, p = 0.60.
- Event study (Ram minus rivals, relative to 2025Q2): between −0.14 and +0.06 through the 2024Q2-2025Q3 quarters, then +0.18, +0.36, +0.27 and +0.47.
- **Caveat: this is partly recovery, not new demand.** In 2024Q1, the last Hemi-equipped quarter, Ram 1500 was already +0.26 above the 2025Q2 baseline. Total Ram pickups (including HD) lost about 5.5% a quarter against rivals from 2021 to 2025. After the Hemi they recovered to roughly their 2023 relative level, not their 2021-22 level.
- Price cuts and the cheaper Express/Warlock trims arrived in the same window. Stellantis credits a 42% retail gain for the 1500 in Q3 2026.

**4 ★ Cherokee: new or stolen demand? It looks stolen, or the data can't tell.**
- Each additional Cherokee unit (year over year) coincides with **1.6 fewer Compass + Grand Cherokee units** (p < 0.001). With a dummy for the planned Q3 2026 production shutdown, it is 1.3 (p = 0.05).
- Zero (purely new demand) is rejected. Full one-for-one cannibalization is not.
- A coefficient below −1 is implausible as pure diversion. Supply cuts on Compass and Grand Cherokee in the same quarters are the likely confound. There are only 4 quarters of Cherokee hybrid sales.

**2 ★ / 3 More powertrain choice and volume: weak evidence.**
- Jeep brand sales show no robust link to the number of model × powertrain offerings: +0.12 (p = 0.10), turning negative with a trend.
  - Jeep offerings fell from 19 to 10-11 as the diesel, Cherokee ICE, Renegade and eTorque variants left the lineup.
- In the nameplate panel, adding a powertrain is associated with **+22% year-over-year growth** (p = 0.046). The levels version is +0.20 (p = 0.10).

**11 ★ / 12 Price elasticity: not identified.** Log sales on log KBB average transaction price (ATP) gives positive, insignificant coefficients for both Jeep (+0.22) and Ram (+0.25). The Jeep-vs-Ram difference is also insignificant. Quarterly price and quantity move together through mix and supply, so plain OLS cannot recover a demand curve. A credible elasticity needs an instrument or VIN-level listings with prices.

**13 ★ Does the price premium cost share? Yes, with a lag.** The contemporaneous correlation is near zero. But each extra percentage point of Stellantis' ATP premium over the industry is followed by **0.14 pp less US market share a year later** (p = 0.011, n = 14). The premium peaked at 23.7% in Q1 2024; share fell from 10.6% to 7.4% and stabilized only after the premium came back to about 10%.

**31 ★ Do searches predict Ram sales? "Ram 1500" does; "Ram Hemi" does not.**
- "Ram 1500" search interest one quarter earlier predicts Ram pickup sales (+0.49, p = 0.05). Adding lagged sales gives +0.35 (p = 0.01). The Ram 1500-only series (n = 10) gives about 1.7 (p < 0.01).
- "Ram Hemi" searches are not significant in any specification.

**41 ★ V8 fuel sensitivity: blocked.** The planned test needs regional Hemi listing shares. Both proxies are uninformative:
- The national Ram share vs gas price correlation is positive and spurious (gas spiked in 2022 while Ram share was still high).
- Cross-state Hemi search interest vs gas price is insignificant, with only 5 distinct PADD gas prices.

**51 ★ North America revenue per unit vs Ram mix: no relationship.** Using the Ram share of US sales as the mix proxy gives −0.21 across 10 half-years and +0.30 across 7 quarters; both are insignificant. Pricing, incentives, FX and fleet mix dominate.

## Other notable results

- **Operating leverage (52):** NA operating margin (AOI) rises **0.065 pp per 1,000 shipments per half-year** (p < 0.001, n = 10). The 365k drop in shipments from H1 2022 to H2 2024 lines up with a 25-point margin swing (+18.1% to −6.8%).
- **Recalls (56):** model years that introduce a new powertrain have **1.5× as many NHTSA recall campaigns** (Poisson, p < 0.001), with nameplate and model-year fixed effects. The number of powertrains offered does not matter on its own.
- **Affordability (43, 44):**
  - Stellantis sales fall about 6% per +1 pp in the 60-month loan rate. That is no more than the industry: −1.5% after controlling for industry volume, insignificant.
  - Consumer sentiment moves Stellantis' **low-price models** (Compass, Cherokee, Hornet: +1.7% per index point relative to industry, p = 0.04), not its trucks.
- **Where Hemi interest lives (45):** states with more truck registrations (+2.2 index points per pp, p < 0.001) and lower incomes (−8.5 points per +10% median income, p < 0.001). Rurality adds nothing once truck share is controlled.
- **Search share and market share (40):** Stellantis' share of brand searches tracks its US market share (+0.62 pp per pp, p < 0.001). Both trend down together, so this is co-movement, not cause.
- **"Jeep price" searches (33):** a 1 pp higher share of Jeep searches that are "Jeep price" is followed by **about 10% lower Jeep sales** the next quarter (p = 0.008). This is the one usable price-backlash signal; "Jeep too expensive" has no search volume.
- **Charger (6, 49):** after the EV tax credit expired and the Sixpack ICE launched, the BEV share of Charger sales fell 58 pp (p = 0.01, n = 7). Each Sixpack unit coincides with about 0.57 fewer BEV units (insignificant). The ICE car partly replaced EV demand, and the policy and the launch can't be separated.
- **Ram HD (7):** HD sales are 6% lower when the Hemi is available in the 1500, which fits trade-down. The result is insignificant (n = 11).
- **Durango (8):** Durango gained 15-25% against 3-row SUV rivals, but the gains started before Charger ICE volume, so no spillover can be attributed.
- **Tariffs (48):** after April 2025, Stellantis ATP fell 5.1% relative to Ford, GM, Toyota, Honda and Hyundai (p < 0.001), which is not consistent with greater pass-through. The result does not survive OEM-specific trends.
- **Shipment push (28):** NA shipments minus US + Canada sales went from −94k in H2 2024 (destocking) to +112k and +127k in H2 2025 and H1 2026. That is back within the 2022-24 range of +86k to +132k, near its top. The figure also includes unreported Mexican sales, so read it as restocking to prior levels, not an exact stock build.
- **Canada (50):** Stellantis Canada growth tracks US growth one for one (0.91, p = 0.02). Ram Canada vs rivals after the Hemi is +0.24 with a Ram-specific trend (p = 0.03) and −0.36 without one, so the result depends on the trend assumption.
- **Not significant:** 5 (coverage gap vs segment share), 10 (retail vs total growth gap), 38 (Wikipedia pageviews), 47 (V8 share after the CAFE change), 55 (stock reaction to sales releases; mean 2-day abnormal return +1.0%, SE 1.0).

## Data sources

| Data | Source | Coverage |
|---|---|---|
| US model × quarter sales (incl. Ram LD/HD and Charger ICE/BEV splits) | Stellantis/FCA US quarterly sales PDFs (media.stellantisnorthamerica.com) | 2021Q3-2026Q3 |
| Canada totals | FCA/Stellantis Canada releases | 2022Q3-2026Q3 |
| Rival model sales (US and Canada) | GoodCarBadCar model pages; matches Stellantis PDFs to within a few units | 2005-2026Q3 |
| Powertrain lineups by model year | EPA fueleconomy.gov `vehicles.csv` | MY2018-2027 |
| Brand, OEM and segment ATP | Kelley Blue Book monthly ATP data tables (Cox Automotive) | Mar 2022-Oct 2026 |
| NA shipments, revenue, AOI | Stellantis 6-K results releases (SEC EDGAR) | H1 2021-Q3 2026 |
| Light-vehicle sales and SAAR | BEA Motor Vehicle Unit Retail Sales | monthly to Oct 2026 |
| Auto loan rates | Federal Reserve G.19 terms of credit | quarterly to 2026Q3 |
| Consumer sentiment | U. Michigan | to Oct 2026 |
| Gas prices | EIA weekly retail, US and PADD 1-5 | to Nov 2026 |
| Search, pageviews | Google Trends (pytrends), Wikimedia REST | 2021-Oct 2026 |
| Recalls | NHTSA FLAT_RCL | to Nov 2026 |
| State covariates | Census SAIPE 2023, Census 2020 urban/rural, FHWA MV-1 2022 | cross-section |
| Prices | Yahoo Finance (STLA, SPY, EURUSD) | 2016-2026 |

FRED, Reddit and CarGurus are not reachable from this environment. stellantis.com returns 403, so financials came from EDGAR instead.

## Caveats that apply throughout

- **Small samples.** Most time series have 7-21 quarters. Standard errors are HAC (or clustered) where n ≥ 15 and classical below that. Treat p-values on n ≤ 11 as indicative only.
- **Model-year mapping.** Lineups are mapped to calendar quarters by assuming Q4 carries the next model year. EPA labels eTorque mild hybrids as "Hybrid", so they count as separate powertrains.
- **Rival definitions.** The F-Series, Silverado and Sierra figures include heavy-duty trucks. The Bronco is missing from GoodCarBadCar, so the off-road segment is not modelled.
- **Hand-coded inputs.** Test 10 uses 24 hand-coded retail growth statements, with quotes in `data/processed/release_text_mentions.csv`. Six Canada totals were transcribed from release sentences (`src/tests_c_inventory.py`).
- **Associations, not causal estimates.** Apart from the difference-in-differences designs (1, 8, 48, 50), all estimates are associations.
