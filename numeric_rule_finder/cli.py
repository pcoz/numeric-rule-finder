"""
cli.py — command-line reconciliation for non-programmers
========================================================

Examples:

    python -m numeric_rule_finder.cli report   examples/quickstart/sample_ledger.csv --group txn_id --amount amount --account account
    python -m numeric_rule_finder.cli check    examples/quickstart/sample_ledger_broken.csv --group txn_id --amount amount
    python -m numeric_rule_finder.cli books    examples/quickstart/sample_ledger.csv --group txn_id --amount amount --account account
    python -m numeric_rule_finder.cli groups   examples/quickstart/sample_ledger.csv --group txn_id --account account
    python -m numeric_rule_finder.cli compare  a.csv b.csv --group txn_id --amount amount

Nothing here needs any mathematics. Feed it a CSV; read the plain-English answer.
"""

import argparse
import sys

from .analyst import Reconciler


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="reconcile",
        description="Plain-language reconciliation: does it balance, what stays "
                    "balanced, and do two systems agree?")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, account=False):
        sp.add_argument("csv", help="path to a CSV file")
        sp.add_argument("--group", required=True, help="column that groups line items (e.g. txn_id)")
        sp.add_argument("--amount", required=True, help="signed amount column")
        if account:
            sp.add_argument("--account", help="account / category column")

    common(sub.add_parser("check", help="does each group balance?"))
    common(sub.add_parser("books", help="find hidden separate books / what stays balanced"), account=True)
    common(sub.add_parser("report", help="full plain-language report"), account=True)

    grp = sub.add_parser("groups", help="find the exact independent groups (fast; no maths, no amount needed)")
    grp.add_argument("csv", help="path to a CSV file")
    grp.add_argument("--group", required=True, help="column that links items together (e.g. txn_id)")
    grp.add_argument("--account", required=True, help="account / entity column")

    cmp_ = sub.add_parser("compare", help="do two CSVs agree?")
    cmp_.add_argument("csv_a")
    cmp_.add_argument("csv_b")
    cmp_.add_argument("--group", required=True)
    cmp_.add_argument("--amount", required=True)

    args = p.parse_args(argv)

    if args.cmd == "check":
        r = Reconciler.from_csv(args.csv)
        print(r.balance_check(group=args.group, amount=args.amount).summary())
    elif args.cmd == "books":
        r = Reconciler.from_csv(args.csv)
        print(r.what_balances(account=args.account, group=args.group, amount=args.amount).summary())
    elif args.cmd == "report":
        r = Reconciler.from_csv(args.csv)
        print(r.report(group=args.group, amount=args.amount, account=args.account))
    elif args.cmd == "groups":
        r = Reconciler.from_csv(args.csv)
        comps = r.independent_groups(account=args.account, group=args.group)
        total = sum(len(c) for c in comps)
        if len(comps) <= 1:
            print(f"All {total} accounts form a single connected group "
                  f"-- no separate sub-systems.")
        else:
            print(f"Found {len(comps)} independent groups among {total} accounts "
                  f"(each a set linked, directly or transitively, through shared "
                  f"{args.group!r}):")
            for i, c in enumerate(comps, 1):
                shown = ", ".join(map(str, c[:8]))
                more = f", ... (+{len(c) - 8} more)" if len(c) > 8 else ""
                print(f"  group {i}: {len(c)} accounts  [{shown}{more}]")
    elif args.cmd == "compare":
        a = Reconciler.from_csv(args.csv_a)
        b = Reconciler.from_csv(args.csv_b)
        diffs = a.compare(b, group=args.group, amount=args.amount)
        if not diffs:
            print("The two systems agree on every group total.")
        else:
            print(f"{len(diffs)} difference(s):")
            for d in diffs:
                print(f"  - {d}")


if __name__ == "__main__":
    main(sys.argv[1:])
