# I-485 tracker state
Personalized: yes (EXAMPLE: invented case for illustration. Not a real applicant.)
Last run: 2026-10-19T12:20-07:00
Cadence: once daily, 7:56 America/Los_Angeles
Reddit: unreachable

## My case
- Sheet username / tracker ID (skip my own rows): ExampleUser / none
- Category / chargeability / PD: EB-2 PERM / ROW / 2024-09-10
- 75 COC (country of concern list): no
- I-485 receipt date / receipt block / concurrent with I-140 / I-485J filed: 2026-05-18 / IOE09xxx / yes / yes
- Biometrics: 2026-06-25
- FO / local or non-local / transfer date (source): San Fernando Valley / non-local / 2026-09-24 (Emma)
- Interview waiver stated (date, source) / re-confirmed after transfer: stated 2026-07-14 by Emma tier 2 / no
- FTA0 dates / FTA1 dates / silent updates / RFEs / other: FTA0 2026-06-25 (biometrics, mass) / none / 2026-07-02, 2026-09-24 / none / none

## Model parameters
```json
{"pd_current": true, "transfer_date": "2026-09-24",
 "frontier_lo": "2026-08-12", "frontier_hi": "2026-08-21",
 "v_med": 1.9, "v_sig": 0.45, "jit_med": 5, "jit_sig": 0.9,
 "ooo_events": 0, "batch_size": 11,
 "p_int": 0.14, "p_rfe": 0.10, "p_stall": 0.10, "p_retro": 0.07, "p_strag": 0.10}
```

## Parameter basis (one line per parameter)
- pd_current: Oct 2026 VB EB-2 ROW FAD 01JAN25; PD 10SEP24 is current.
- frontier_hi 2026-08-21: latest transfer date with an approved current-PD EB-2 pool case at SFV.
- frontier_lo 2026-08-12: oldest transfer date with a pending current-PD EB-2 case (75 COC excluded).
- v_med 1.9: frontier moved 23 transfer-days in 12 calendar days. Few data points.
- p_int 0.14: waiver stated, not re-confirmed after transfer.

## Frontier data (my category at my FO: case, transfer, approved, gap wk)
## Batch watch (same FO, transferred within 3 days of me: case, category, status)
## Already counted (dedupe: one line per case, label = source ids)
## Visa Bulletin last reported (month, FAD, DFF)
- Oct 2026: EB-2 ROW FAD 01JAN25, DFF 15MAR26.

## Change log (newest first, one line per revision)
- 2026-10-19: Setup.
