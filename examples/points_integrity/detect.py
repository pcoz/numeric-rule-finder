"""
Rules-free integrity monitoring of a points / rewards economy
=============================================================

THE OLD WAY: fight points-duplication fraud and economy bugs by hand-writing
anomaly rules ("alert if a member gains > X per hour"). Brittle, and blind to
any exploit you didn't think of in advance.

THE NEW WAY (unlocked here): a points economy has exactly one law -- points are
*conserved* (every legitimate event just MOVES points between buckets: a mint
authority, members, a burn/redemption sink). Nobody has to write that law down.
This library **discovers it from the normal event log**, and then ANY event that
violates it is, by definition, points created or destroyed off-spec -- an
exploit or a bug -- caught with **zero rules written**, including exploits never
anticipated. The cohomology then *types* each violation: genuinely minted from
nothing (a duplication exploit) vs. merely a legitimate transfer.

Run:  python detect.py
"""

import sys
from pathlib import Path
from fractions import Fraction
from functools import reduce
from math import gcd
from collections import defaultdict

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break
DATA = HERE / "data"

from numeric_rule_finder.analyst import Reconciler, cross_check
from numeric_rule_finder.cohomology import ConservationComplex
from numeric_rule_finder.integer_invariants import integer_conservation


def step(n, title):
    print("\n" + "=" * 74)
    print(f"STEP {n}.  {title}")
    print("=" * 74)


def net_of_event(rows, event_col, event, bucket_col, points_col):
    net = defaultdict(Fraction)
    for r in rows:
        if r[event_col] == event:
            net[r[bucket_col]] += Fraction(str(r[points_col]))
    return dict(net)


def main():
    print("POINTS ECONOMY INTEGRITY -- no fraud rules are written anywhere below.")
    clean = Reconciler.from_csv(DATA / "clean_log.csv")

    # ---- STEP 1: LEARN the law nobody wrote -----------------------------
    step(1, "Learn the economy's law from the normal log  (what_balances)")
    wb = clean.what_balances(account="bucket", group="event", amount="points")
    print(wb.summary())
    print("\n  LEARNED, with no rule authored: each set above is a CLOSED economy")
    print("  whose total points are conserved -- points only ever move between")
    print("  buckets, never appear or vanish. (Also: NA and EU never mix.)")

    # ---- STEP 2: MONITOR new events against the learned law -------------
    step(2, "Screen a new batch -- which events break conservation?  (balance_check)")
    batch = Reconciler.from_csv(DATA / "monitor_batch.csv")
    bc = batch.balance_check(group="event", amount="points")
    print(bc.summary())
    print("\n  No rule said 'member_ben can't gain 200'. The LAW says points can't")
    print("  appear from nowhere -- and this event breaks it.")

    # ---- STEP 3: TYPE the violation -- exploit, or just a transfer? -----
    step(3, "Is it minted-from-nothing, or a legitimate transfer?  (coker S)")
    cx = ConservationComplex.from_records(clean.rows, "bucket", "event", "points")
    suspect = max(bc.breaks, key=lambda b: abs(b.off_by)).group
    suspect_net = net_of_event(batch.rows, "event", suspect, "bucket", "points")
    print(f"  event {suspect!r} net = {suspect_net}")
    typed = cx.type_observation(suspect_net)
    if not typed.is_coboundary:
        amt = typed.obstruction[0][1]
        print(f"  VERDICT: DUPLICATION EXPLOIT -- {amt} points were created from nothing")
        print("           (no transfer reproduces this). Not a re-attribution.")
    # contrast: a real transfer types as harmless
    print("  control -- a genuine transfer {member_amy:-25, member_ben:+25}:")
    benign = cx.type_observation({"member_amy": -25, "member_ben": 25})
    print(f"           is_coboundary={benign.is_coboundary} -> "
          f"{'harmless transfer, no points created' if benign.is_coboundary else 'flag'}")

    # ---- STEP 4: LEARN the grant granularity, flag odd grants ----------
    step(4, "Learn the award granularity, flag off-tier grants  (integer/modular)")
    tier_rows = Reconciler.from_csv(DATA / "tier_bonuses.csv").rows
    idisc = integer_conservation(tier_rows, "bucket", "grant", "points")
    moduli = [ml.modulus for ml in idisc.modular_laws]
    grain = reduce(gcd, moduli) if moduli else 0
    print(f"  learned (no rule): awards are issued only in multiples of {grain} "
          f"(per-member moduli {sorted(moduli)}).")
    for candidate in (200, 30):
        ok = grain and candidate % grain == 0
        print(f"    a proposed grant of {candidate}: "
              f"{'valid (on-tier)' if ok else 'ANOMALOUS -- not a whole tier; reject/review'}")

    # ---- STEP 5: are the partner statements even mutually possible? ----
    step(5, "Three program partners reconcile pairwise -- can all be right?  (H^1)")
    # airline<->hotel<->card reported net point transfers:
    partners = {("Airline", "Hotel"): 120, ("Hotel", "Card"): -50, ("Card", "Airline"): -40}
    for (u, v), d in partners.items():
        print(f"    {u} vs {v}: net transferred differs by {d}")
    print("  " + cross_check(partners))

    print("\n" + "=" * 74)
    print("PAYOFF: not one fraud rule was written. The conservation law was LEARNED")
    print("  from normal activity; every problem then fell out of it -- a dup exploit")
    print("  typed as genuine minting, an off-tier grant caught by the learned")
    print("  granularity, and a set of partner statements proven mutually impossible.")
    print("  New exploits need no new rules: if they create or destroy points, the")
    print("  law catches them.")
    print("=" * 74)


if __name__ == "__main__":
    main()
