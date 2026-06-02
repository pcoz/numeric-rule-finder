"""
Closing the March books at Northwind Retail
============================================

Maya is a finance-ops business analyst. It's month-end. She has the general
ledger, a stockroom export, a warehouse physical count, and three regional
controllers' sign-offs. She runs five checks; each ends with an ACTION she can
take today. Everything below is plain English -- she never sees a matrix, and
never needs to. (The same answers are produced by deep mathematics, but it
doesn't have to surface, and here it doesn't.)

Run:  python close_the_books.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break          # find the library (flat modules)
DATA = HERE / "data"

from numeric_rule_finder.analyst import Reconciler, cross_check, account_for_movement


def check(n, question):
    print("\n" + "-" * 72)
    print(f"CHECK {n}.  {question}")
    print("-" * 72)


def main():
    print("NORTHWIND RETAIL -- closing the March books.")
    gl = Reconciler.from_csv(DATA / "gl.csv")

    # 1. Does the ledger balance?
    check(1, "Do all the journal entries balance?")
    print(gl.balance_check(group="journal", amount="amount").summary())
    print("ACTION: chase the journal(s) flagged above before anything else.")

    # 2. Is it really one ledger?
    check(2, "Am I even looking at one set of books?")
    print(gl.what_balances(account="account", group="journal", amount="amount").summary())
    print("ACTION: reconcile the operating book and the intercompany book")
    print("        SEPARATELY -- an entry in one can never fix the other.")

    # 3. Is each flagged break real, or just mis-booked?
    check(3, "For the breaks: real money missing, or just booked oddly?")
    print(gl.diagnose_breaks(group="journal", amount="amount", account="account").summary())

    # 4. The stockroom feed won't tie out to the unit.
    check(4, "The stockroom never balances to the unit -- is the data junk?")
    print(Reconciler.from_csv(DATA / "stock.csv")
          .what_balances(account="bin", group="move", amount="units").summary())
    print("ACTION: don't chase single units -- reconcile at the CASE (12) level;")
    print("        any count that isn't a whole number of cases is the error.")

    # 5. The warehouse physical count vs the books.
    check(5, "Physical count vs books: did stock move, or go missing?")
    physical_net = {"DC": -200, "StoreA": 150, "StoreB": 30}
    print(f"  net change by location: {physical_net}")
    print("  " + account_for_movement(physical_net))
    print("ACTION: this is shrinkage, not a transfer -- open a loss investigation")
    print("        and write down the 20 units; do NOT keep hunting for a transfer.")

    # 6. Three regional sign-offs.
    check(6, "Three regions signed off pairwise -- can they all be right?")
    signoffs = {("North", "South"): 120, ("South", "East"): -50, ("East", "North"): -40}
    for (u, v), d in signoffs.items():
        print(f"  {u} vs {v}: differ by {d}")
    print("  " + cross_check(signoffs))
    print("ACTION: stop reconciling them pairwise -- send at least one region back")
    print("        to re-measure; no set of adjustments can make all three agree.")

    print("\n" + "=" * 72)
    print("Maya's close, in one pass: one real shortfall to journal, two books to")
    print("split, a stockroom to reconcile by the case, 20 units of genuine shrink")
    print("to write down, and three regional sign-offs that are mutually impossible.")
    print("No maths on screen -- just decisions.")
    print("=" * 72)


if __name__ == "__main__":
    main()
