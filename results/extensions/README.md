# Extensions: cost quality, fleet mix, Hemi pricing power and alternative datasets

Run date 2026-11-11. Each item has its own page with tables, method and caveats; the scripts are `src/ext*.py`.

| # | Question | Answer in one line | Page |
|---|---|---|---|
| 4 | How much of the €1.33bn NA "Industrial" gain is repeatable? | **About €0.2-0.7bn (18-55%).** About €0.6bn is the CAFE-penalty elimination (policy; the YoY gain ends after mid-2026) and €0.4-0.9bn is one-time (IEEPA refund, warranty base effect). | [04_na_bridge.md](04_na_bridge.md) |
| 5 | Is Ram 1500 growth fleet-driven? | **Partly.** Retail supplied only 40-52% of the Q3 2026 added units nationally. In NY, rental fleets buy the six-cylinder (8.2% of registrations) and almost never the Hemi (0.5%); 91% of Hemis are retail-plated. | [05_fleet.md](05_fleet.md) |
| 1 | Does the Hemi need smaller discounts? | **Yes, modestly.** Within the same dealer, Hemi trucks are discounted 1.6-1.8 pp less (about $1,000; p≈0.02-0.04). The gap comes from aged MY2026 stock; on fresh MY2027 stock it is zero (both about 9%). | [01_listings.md](01_listings.md) |
| 10 | Ram vs Ford/GM discounts | **Ram discounts more.** Dallas: Ram six-cyl 25%, Ram Hemi 16%, Silverado 18%, F-150 13% off MSRP. Ram is +5 pp vs rivals at equal MSRP. Ram's MY2026 is already prior-year stock. | [01_listings.md](01_listings.md) |
| 11 | Prior-year inventory | **Most listed Ram stock is prior model year** (71% of Hemi, 80% of six-cyl listings; 98% in Phoenix). It carries 10-12 pp deeper discounts than MY2027. | [01_listings.md](01_listings.md) |
| 12 | Where is Hemi demand strongest? | Hemi is 29% of inventory in Phoenix and 47% in New York. In NY retail registrations it is 54% in NYC and suburbs vs 47% upstate, so not the "rural truck" pattern. NY sales share (46-48%) is about equal to NYC-area inventory share (47%), so there is no sign of faster sell-through. | [01_listings.md](01_listings.md) |
| 13 | Are shipments running ahead of sales? | **Yes, through Q2 2026.** NA shipments − US/Canada/Mexico sales = +145k from Q3 2025 to Q2 2026, then −22k in Q3 (planned shutdown). Mexico exports +42% in Q2-Q3 2026 (INEGI), partly new Saltillo Ram 1500 and Toluca Cherokee output. | [13_inventory_identity.md](13_inventory_identity.md) |
| 14 | Demand or push: market signals and analogs | Cox **retail** days' supply: Jeep 169, Ram 152, Ram 1500 142 vs industry 82 (Sep 2026), up from Ram 115 / Jeep 130 in Dec 2025. Stellantis's own 84 days uses total sales including fleet. Management's year-end stock target implies 2026 shipments of 1,517-1,547k vs the AI 1,623k. Analogs: GM 2005, Chrysler 2007, FCA 2012-16, Nissan 2016-18, GM's 2015-17 rental cut. | [14_market_signals.md](14_market_signals.md) |
| 8 | Do new powertrains raise warranty risk? | **No sign yet.** MY2026 (Hemi returns) had 2.9 complaints per 10k first-year sales vs 4.5 for MY2025 (Hurricane-only). Powertrain complaints were 0.3 vs 1.7 per 10k, and there have been no MY2025-26 powertrain recalls. The 2025 warranty re-estimate (€3.25bn NA) is the bigger risk signal. | [08_warranty_risk.md](08_warranty_risk.md) |
| 9 | Used resale values | **Hemi holds a small premium:** +2.7% (about $900, p=0.15) on used MY2023 trucks in Dallas, controlling for trim and mileage. | [09_resale.md](09_resale.md) |
| 6-7 | Plant downtime / productivity | Descriptive only. 2025 Hemi orders (about 50k) exceeded engine output (about 30k), and SHAP ran seven-day schedules in 2026. About 45 US trucks per SHAP worker annualized in 2026. | [06_07_plants.md](06_07_plants.md) |

## New data built

| File | What | Source |
|---|---|---|
| `data/processed/na_aoi_bridges.csv` | 14 NA AOI waterfalls FY2021-9M 2026 (vol/mix, price, industrial, SG&A, R&D, FX) | Values read off the MD&A chart images in the 20-F / interim reports (SEC EDGAR); every bridge sums to the reported AOI |
| `results/extensions/04_industrial_decomposition.csv` | 9M/Q3 2026 Industrial split into CAFE, warranty, tariffs, residual | 6-K interim "Cost of revenues" notes and results-release tariff guidance |
| `data/raw/ny_dmv/ny_pickup_registrations.csv.gz` (not committed: VIN/ZIP level; rebuild with `src/collect_ny_registrations.py`) | 338k NY full-size pickup VINs MY2023+, decoded (model, engine, trim) | data.ny.gov DMV registrations (snapshot 2026-11-03) + NHTSA vPIC |
| `data/processed/ny_new_pickup_registrations.csv.gz` | De-identified new-vehicle subset (no VIN/ZIP) with channel (retail/commercial/rental/government), engine, county | derived |
| `data/processed/listings_ram1500_2026-11-11.csv` | 432 cleaned Ram 1500 listings (MSRP, price, trim, MY, engine, dealer, market) | KBB/Autotrader search pages, 5 metros; raw pulls in `data/raw/listings/` |
| `data/raw/listings/kbb_rivals_2026-11-11.csv` | 84 F-150 / Silverado 1500 listings, Dallas | KBB |
| `data/raw/listings/kbb_used_ram1500_my2023_dallas_2026-11-11.csv` | 69 used Ram 1500 listings | KBB |
| `data/processed/nhtsa_complaints_ram1500.csv.gz` | 4,245 owner complaints, Ram 1500 MY2019-2026 | api.nhtsa.gov |

| `data/processed/inegi_stellantis_mexico_monthly.csv` | Stellantis Mexico production, exports, domestic sales by month 2024-2026 | INEGI RAIAVL monthly summaries (`src/parse_inegi.py`) |
| `data/processed/cox_brand_days_supply.csv` | Brand retail days' supply, hand-collected with URLs | Cox Automotive monthly inventory articles |

## Caveats that matter

* **Listings are a one-day cross-section, not a panel.** "Days listed" is not shown on KBB, so the sequential listing ID is
  used as a relative-age proxy (no Hemi difference, p=0.33). Advertised prices are not transaction prices, and they include
  about $314 of dealer fees. Values were extracted from rendered search pages by a fetch tool and spot-checked against two
  detail pages (both matched). Each page shows only its first ~45 results in KBB's default order, so the sample leans
  toward a few large dealers. Dealer fixed effects absorb this. Sites that block automated access (Cars.com, CarGurus,
  Edmunds, TrueCar) were not scraped.
* **To turn item 1 into the planned 100-200-truck panel with days-on-lot,** re-run the same KBB pulls weekly (same URLs, in
  `src/ext01_listings.py` docstring) and feed `src/listings_models.py`.
* **The NY registration file is a survival snapshot.** It understates 2025 counts, especially rental. Use levels and
  Ram-vs-rival gaps, not raw YoY.
* **Stellantis does not split "Industrial" into purchasing/manufacturing/warranty/tariffs.** Item 4 combines group-level
  warranty figures with NA-specific regulatory and tariff text. The warranty range is an upper bound for NA.
