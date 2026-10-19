#!/usr/bin/env python3
# I-485 approval-date Monte Carlo (field-office queue-frontier model).
# Community edition for the SFV group chat. Estimates, not statistics.
#
# Usage:
#   python3 aos_model.py i485-tracker.md                     # today's date
#   python3 aos_model.py i485-tracker.md 2026-10-19          # explicit date
#   python3 aos_model.py i485-tracker.md 2026-10-19 out.png  # also write the weekly chart
# Reads parameters from the first ```json block in i485-tracker.md (or from a .json file).
#
# Model, per simulated future:
#  1. Queue frontier: the FO clears cases roughly in transfer-date order (batches).
#     Today's frontier F (latest transfer date being cleared in your category) ~ Uniform(frontier_lo, frontier_hi).
#  2. Frontier speed v (transfer-days cleared per calendar day) ~ LogNormal(v_med, v_sig).
#     Days until your transfer date is reached = (transfer_date - F) / v  (0 if the frontier is already past it).
#  3. Within-batch spread: + LogNormal(jit_med days, jit_sig).
#  4. Out-of-order approval: competing exponential clock, hazard ~ Gamma(0.5 + ooo_events, rate batch_size x days since transfer)
#     (Jeffreys posterior from approvals seen so far in your transfer batch). Approval = min(queue time, out-of-order time).
#  5. Tail delays, independent: interview, RFE, visa pause, retrogression, batch straggler; each adds Uniform days.
import sys, re, json, datetime as dt
import numpy as np

DEFAULTS = dict(
    pd_current=True, transfer_date=None,
    frontier_lo="2026-08-12", frontier_hi="2026-08-21",
    v_med=1.8, v_sig=0.45, jit_med=5, jit_sig=0.9,
    ooo_events=0, batch_size=10,
    p_int=0.14, int_days=[60, 180],
    p_rfe=0.10, rfe_days=[45, 90],
    p_stall=0.10, stall_days=[30, 90],
    p_retro=0.07, retro_days=[90, 300],
    p_strag=0.10, strag_days=[30, 120],
    seed=42, n=200_000,
)

def load(path):
    txt = open(path, encoding="utf-8").read()
    if not path.lower().endswith(".json"):
        m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
        if not m:
            sys.exit(f"No ```json parameter block found in {path}")
        txt = m.group(1)
    p = dict(DEFAULTS); p.update(json.loads(txt)); return p

args = sys.argv[1:]
if not args:
    sys.exit(__doc__ or "usage: aos_model.py outlook.md [YYYY-MM-DD] [chart.png]")
P = load(args[0])
TODAY = dt.date.today(); CHART = None
for a in args[1:]:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a): TODAY = dt.date.fromisoformat(a)
    else: CHART = a

if not P["pd_current"]:
    print("NOT MODELED: priority date is not current for your category/chargeability.")
    print("Approval is gated by the Visa Bulletin Final Action Date, not by the field office queue.")
    sys.exit(0)
if not P["transfer_date"]:
    print("NOT MODELED: no field office transfer date yet. The model starts at FO transfer.")
    sys.exit(0)

d = dt.date.fromisoformat
T, lo, hi = d(P["transfer_date"]), d(P["frontier_lo"]), d(P["frontier_hi"])
if hi < lo: lo, hi = hi, lo
rng = np.random.default_rng(P["seed"]); N = int(P["n"])

F = rng.uniform((lo - TODAY).days, (hi - TODAY).days + 1e-9, N)   # frontier offset from today (days, usually negative)
D = np.maximum((T - TODAY).days - F, 0)                           # transfer-days still to clear before your batch
v = rng.lognormal(np.log(P["v_med"]), P["v_sig"], N)
t = D / v + rng.lognormal(np.log(P["jit_med"]), P["jit_sig"], N)
case_days = max(P["batch_size"] * max((TODAY - T).days, 1), 1)
h = rng.gamma(0.5 + P["ooo_events"], 1 / case_days, N)
t = np.minimum(t, rng.exponential(1 / h))
anyhit = np.zeros(N, bool)
for k in ("int", "rfe", "stall", "retro", "strag"):
    lo_d, hi_d = P[f"{k}_days"]
    hit = rng.random(N) < P[f"p_{k}"]
    t += hit * rng.uniform(lo_d, hi_d, N); anyhit |= hit
t = np.maximum(t, 1)

day = lambda x: TODAY + dt.timedelta(days=float(x))
fmt = lambda x: day(x).strftime("%b %d")
q = np.percentile(t, [10, 25, 50, 75, 90])
clean_med = np.median(t[~anyhit]) if (~anyhit).any() else float("nan")
print(f"Run date: {TODAY}  (transfer {T}, frontier {lo} to {hi})")
print("Median (estimated date):", fmt(q[2]))
print("If no interview/RFE/pause/retrogression/straggling:", fmt(clean_med))
print("50% interval:", fmt(q[1]), "to", fmt(q[3]))
print("80% interval:", fmt(q[0]), "to", fmt(q[4]))

# checkpoints: next 6 mid-months and month-ends after today
cps, y, m = [], TODAY.year, TODAY.month
while len(cps) < 6:
    nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
    for c in (dt.date(y, m, 15), nxt - dt.timedelta(days=1)):
        if c > TODAY and len(cps) < 6: cps.append(c)
    y, m = nxt.year, nxt.month
res = {}
for c in cps:
    pr = float(np.mean(t <= (c - TODAY).days)); res[c.strftime("%b %d")] = round(pr, 3)
    print(f"P(approved by {c:%b %d}) = {pr:.0%}")
for vm in (P["v_med"] * 0.67, P["v_med"], P["v_med"] * 1.4):
    tt = D / rng.lognormal(np.log(vm), P["v_sig"], N) + rng.lognormal(np.log(P["jit_med"]), P["jit_sig"], N)
    print(f"Sensitivity, no-tail median at v_med={vm:.1f}: {fmt(np.median(tt))}")
print("RESULT_JSON", json.dumps(dict(median=str(day(q[2])), no_tail_median=str(day(clean_med)),
      p25=str(day(q[1])), p75=str(day(q[3])), p10=str(day(q[0])), p90=str(day(q[4])), cumulative=res)))

if CHART:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt, matplotlib.dates as mdates, matplotlib.lines, matplotlib.ticker
    from matplotlib.patches import Patch
    W, NW = 7, 22; edges = np.arange(0, (NW + 1) * W, W)
    clean = np.histogram(t[~anyhit], edges)[0] / N * 100; tail = np.histogram(t[anyhit], edges)[0] / N * 100
    later = np.mean(t >= edges[-1]) * 100
    x = mdates.date2num([TODAY + dt.timedelta(days=int(e)) for e in edges[:-1]])
    INK, MUTED, RULE, BG = "#18232b", "#5b6a74", "#d8e0e4", "#ffffff"; SIM, TAIL, SOFT = "#0b78a8", "#c46f1f", "#dcecf3"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, ax = plt.subplots(figsize=(7, 3.7), dpi=200); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    q1, med, q3 = [mdates.date2num(day(v_)) for v_ in np.percentile(t, [25, 50, 75])]
    ax.axvspan(q1, min(q3, x[-1] + W), color=SOFT, zorder=0, lw=0)
    ax.bar(x, clean, width=W - 1.2, align="edge", color=SIM, zorder=2)
    ax.bar(x, tail, width=W - 1.2, align="edge", bottom=clean, color=TAIL, zorder=2, edgecolor=BG, linewidth=0.8)
    ax.axvline(med, color=INK, lw=1.6, zorder=3)
    daily = np.histogram(t, np.arange(0, edges[-1] + 1))[0]; mode_d = int(np.argmax(np.convolve(daily, np.ones(7) / 7, mode="same")))
    mode = mdates.date2num(day(mode_d)); ax.axvline(mode, color=INK, lw=1.4, ls=(0, (4, 3)), zorder=3)
    print("Most likely date (peak):", fmt(mode_d))
    top = max(clean + tail) * 1.18; ax.set_ylim(0, top)
    ax.text(med + 1, top * 0.93, "median " + day(np.median(t)).strftime("%b %-d") + "\n(estimate)", color=INK, fontsize=9, fontweight="bold", va="top")
    ax.text(mode - 2.5, top * 0.93, "most likely\n" + day(mode_d).strftime("%b %-d"), color=INK, fontsize=9, ha="right", va="top")
    ax.text(x[-1] + W, top * 0.93, f"{later:.0f}% later\n(not shown)", color=MUTED, fontsize=8, ha="right", va="top")
    ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_xlim(x[0], x[-1] + W)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v_, _: f"{v_:.0f}%"))
    ax.set_ylabel("Chance of approval\nin that week", color=MUTED)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"): ax.spines[sp].set_color(RULE)
    ax.tick_params(colors=MUTED); ax.grid(axis="y", color=RULE, lw=0.6, zorder=0)
    ax.legend(handles=[Patch(color=SIM, label="No delay"), Patch(color=TAIL, label="Hit a delay"), Patch(color=SOFT, label="Middle 50%"),
                       matplotlib.lines.Line2D([], [], color=INK, lw=1.6, label="Median"),
                       matplotlib.lines.Line2D([], [], color=INK, lw=1.4, ls=(0, (4, 3)), label="Most likely")],
              frameon=False, loc="upper right", bbox_to_anchor=(1, 0.8), fontsize=8, labelcolor=INK)
    ax.set_title(f"Simulated approval dates, {N:,} futures (run {TODAY:%b %-d})", loc="left", color=INK, fontsize=10, fontweight="bold")
    fig.text(0.01, 0.01, "Model estimates from community-reported cases, not USCIS statistics.", color=MUTED, fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(CHART, facecolor=BG); print("chart:", CHART)
