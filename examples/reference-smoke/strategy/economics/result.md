# Observed cohort economics — synthetic

Source: inbox/cohort.json; 100 initially acquired customers, EUR 14,000 fully allocated acquisition cost, three observed months. Revenue excludes VAT and has no refunds in this fixture. Variable service cost is EUR 30 per active customer-month. Fixed overhead is excluded from contribution and must be considered before a business profitability decision.

| Month | Active | Net revenue | Variable cost | Contribution | Cumulative contribution | Per initial customer |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 100 | 10000 | 3000 | 7000 | 7000 | 70.0 |
| 2 | 90 | 9000 | 2700 | 6300 | 13300 | 133.0 |
| 3 | 80 | 8000 | 2400 | 5600 | 18900 | 189.0 |

CAC = allocated acquisition cost / initial customers = EUR 140. Contribution = net revenue minus variable cost. Observed three-month contribution per initial customer is EUR 189; observed three-month net revenue per initial customer is EUR 270. Neither is lifetime value.

Cumulative contribution is EUR 133 per acquired customer after month two and EUR 189 after month three. The first observed month-end at which contribution covers CAC is month three. No within-month timing is inferred. Third-month customer retention is 80/100 = 80%; this is not annual retention or revenue retention.

Downside sensitivity: holding observed activity fixed, variable cost EUR 40 produces EUR 162 of three-month contribution per acquired customer. At CAC EUR 180, payback is not reached in the observed period. Changing retention would require a separate scenario; no mature lifetime estimate is available.

Proposed decision: treat three-month contribution coverage as an observed diagnostic, not a universal scale threshold. Do not scale beyond capacity of 120 new accounts per month without a capacity and marginal acquisition-cost review. The fixture does not establish future CAC, customer lifetime, fixed-cost profitability or authorization to spend.

Quality review: revenue and contribution are separated; zero/missing denominators must return unavailable; this fixture has a nonzero known denominator. Cohort maturity is three months and all extrapolation is excluded. Every numerical value is reproducible from the source using the script that generated this report.
