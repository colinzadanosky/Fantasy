# 1. Does the Hemi need smaller discounts? (one-day listing pull, 2026-11-11)

Listings: 451 Ram 1500 listings across Dallas, Detroit, Atlanta, Phoenix and New York (50-mile radius each), read from KBB/Autotrader search pages filtered by cylinder count (8 = 5.7 Hemi; 6 = 3.0 Hurricane). After dropping TRX/RHO, missing MSRP and 12 listings with an implausible MSRP (>1.25x the trim median; one Long Island dealer), **432 listings** remain from 43 dealers. Discount = 1 - advertised price / MSRP.

## Discount by model year and engine

| year | engine | n | mean_disc | median_disc | mean_disc_usd | mean_msrp |
|---|---|---|---|---|---|---|
| 2025 | 6-cyl | 2 | 11.2 | 11.2 | 5698.0 | 50877.5 |
| 2026 | 6-cyl | 176 | 21.8 | 23.8 | 13239.5 | 60924.9 |
| 2026 | Hemi V8 | 149 | 19.9 | 22.6 | 12961.0 | 65102.4 |
| 2027 | 6-cyl | 45 | 9.4 | 9.0 | 6676.6 | 69982.4 |
| 2027 | Hemi V8 | 60 | 9.6 | 9.0 | 6520.8 | 67906.9 |

## Regression: discount (pp of MSRP) on Hemi dummy, SEs clustered by dealer

| Spec | Hemi coef (pp) | SE | p | n |
|---|---:|---:|---:|---:|
| discount % ~ V8 (raw) | -2.23 | 1.73 | 0.199 | 432 |
| + trim, model year, market, log MSRP | -1.20 | 0.72 | 0.096 | 432 |
| + dealer FE (within-dealer) | -1.79 | 0.76 | 0.018 | 432 |
| MY2026 only, trim + market + dealer FE | -1.56 | 0.76 | 0.039 | 325 |
| MY2027 only, trim + market | -0.06 | 0.84 | 0.944 | 105 |
| Big Horn/Lone Star only, + year + dealer FE | -1.54 | 1.11 | 0.165 | 225 |
| listing-age proxy: ID percentile ~ V8 + trim + year + market | +0.03 | 0.03 | 0.328 | 432 |

## By trim

| trim | n_6-cyl | n_Hemi V8 | disc_6-cyl | disc_Hemi V8 |
|---|---|---|---|---|
| Big Horn | 88 | 96 | 16.4 | 16.3 |
| Express | 36 | 34 | 22.0 | 18.3 |
| Laramie | 44 | 28 | 17.2 | 18.8 |
| Lone Star | 29 | 12 | 25.9 | 19.5 |
| Rebel | 2 | 10 | 27.9 | 9.4 |
| Tradesman | 12 | 7 | 18.3 | 18.3 |
| Warlock | 8 | 17 | 24.6 | 18.0 |

## By market: inventory mix and discount gap (items 12)

| market | 6-cyl | Hemi V8 | v8_share_of_inventory | disc_gap_v8_minus_6cyl_pp |
|---|---|---|---|---|
| Atlanta GA | 738 | 498 | 0.403 | -0.2 |
| Dallas TX | 1069 | 602 | 0.36 | -9 |
| Detroit MI | 1348 | 692 | 0.339 | -4.3 |
| New York NY | 737 | 657 | 0.471 | 1.5 |
| Phoenix AZ | 643 | 257 | 0.286 | -0.7 |

## Sales-to-inventory check (NY registrations vs NYC-area listings)

Hemi share of NYC-area Ram 1500 inventory (KBB, excl. TRX/RHO not separable in totals): **47%**.

Hemi share of new NY Ram 1500 registrations (MY2026+, i.e. years where both engines are offered; excl. TRX/RHO):

| q | hemi_share_all | hemi_share_retail | n |
|---|---|---|---|
| 2025Q4 | 0.37 | 0.364 | 1014 |
| 2026Q1 | 0.459 | 0.5 | 2295 |
| 2026Q2 | 0.478 | 0.541 | 3087 |
| 2026Q3 | 0.457 | 0.47 | 3898 |
| 2026Q4 | 0.474 | 0.501 | 1129 |

Within New York, retail MY2026+ registrations:

| region | hemi_share_retail | n |
|---|---|---|
| NYC | 0.548 | 1094 |
| NYC suburbs | 0.542 | 3418 |
| Upstate | 0.47 | 4908 |

Counties with >=100 retail MY2026+ registrations, lowest to highest Hemi share:

| county | n | hemi |
|---|---|---|
| NIAGARA | 141 | 0.333 |
| JEFFERSON | 129 | 0.388 |
| ALBANY | 107 | 0.43 |
| MONROE | 258 | 0.43 |
| ONEIDA | 199 | 0.437 |
| ERIE | 487 | 0.437 |
| SARATOGA | 198 | 0.444 |
| ONONDAGA | 365 | 0.458 |
| BROOME | 102 | 0.461 |
| ST LAWRENCE | 163 | 0.472 |
| OSWEGO | 133 | 0.481 |
| WESTCHESTER | 490 | 0.494 |
| ROCKLAND | 166 | 0.512 |
| NASSAU | 1177 | 0.512 |
| QUEENS | 346 | 0.517 |
| ULSTER | 155 | 0.529 |
| KINGS | 145 | 0.531 |
| DUTCHESS | 209 | 0.574 |
| SUFFOLK | 1585 | 0.582 |
| RICHMOND | 488 | 0.59 |
| ORANGE | 286 | 0.647 |

## Prior-model-year inventory (item 11)

| engine | n | prior_my_share |
|---|---|---|
| 6-cyl | 223 | 0.798 |
| Hemi V8 | 209 | 0.713 |

| market | prior_my_share |
|---|---|
| Atlanta GA | 0.888 |
| Dallas TX | 0.773 |
| Detroit MI | 0.678 |
| New York NY | 0.429 |
| Phoenix AZ | 0.977 |

Extra discount on prior-MY vs MY2027 stock: 6-cyl +12.3 pp, Hemi +10.4 pp.

## Ram vs F-150 vs Silverado 1500 discounts, Dallas (item 10)

| model | n | mean_disc | median_disc | mean_msrp |
|---|---|---|---|---|
| Chevrolet Silverado 1500 | 42 | 17.9 | 18.5 | 64843.7 |
| Ford F-150 | 40 | 13.3 | 14.6 | 59872.1 |
| Ram 1500 (6-cyl) | 44 | 25.2 | 26.7 | 59437.5 |
| Ram 1500 (Hemi V8) | 44 | 16.2 | 18.6 | 67191.2 |

Ram minus rivals, controlling for log MSRP: +5.1 pp (SE 1.1, p=0.000, n=170).

