"""
datasets.py — synthesized test data for conservation-law discovery
==================================================================

Each dataset is a list of movement records (entity, event, signed qty) with a
known number of *independent* conservation laws, so the discovery engine can be
checked against ground truth. They deliberately span the cases that decide
whether "discover the laws" is more interesting than "check one declared law":

  * michaelis_menten   — a real reaction-network shape: 2 conserved moieties.
  * ledger_connected   — one fully-linked double-entry book: 1 law.
  * ledger_two_books   — two disjoint books: 2 laws (block structure NOBODY
                          declared — the headline "more than one law?" case).
  * inventory_two_skus — per-SKU stock conservation across locations: 2 laws.
  * no_structure       — non-balancing movements: 0 laws -> HONEST STOP.
"""

ENTITY, EVENT, QTY = "entity", "event", "qty"


def _rec(entity, event, qty):
    return {ENTITY: entity, EVENT: event, QTY: qty}


def michaelis_menten():
    """Enzyme kinetics  E + S <-> ES -> E + P.  Two conserved moieties:
    enzyme (E + ES) and substrate-matter (S + ES + P)."""
    recs = [
        _rec("E", "R1_bind", -1), _rec("S", "R1_bind", -1), _rec("ES", "R1_bind", +1),
        _rec("E", "R2_unbind", +1), _rec("S", "R2_unbind", +1), _rec("ES", "R2_unbind", -1),
        _rec("E", "R3_catalyse", +1), _rec("ES", "R3_catalyse", -1), _rec("P", "R3_catalyse", +1),
    ]
    return dict(name="michaelis_menten", records=recs, entity_key=ENTITY,
                event_key=EVENT, qty_key=QTY, expected_laws=2)


def ledger_connected():
    """Double-entry book, every transaction pivots on cash -> one law
    (every account's weight forced equal: the all-equal / nets-to-zero law)."""
    recs = [
        _rec("cash", "t1", 100), _rec("revenue", "t1", -100),
        _rec("cash", "t2", 250), _rec("expense", "t2", -250),
        _rec("cash", "t3", 75),  _rec("revenue", "t3", -75),
        _rec("cash", "t4", 40),  _rec("expense", "t4", -40),
    ]
    return dict(name="ledger_connected", records=recs, entity_key=ENTITY,
                event_key=EVENT, qty_key=QTY, expected_laws=1)


def ledger_two_books():
    """Two double-entry books that never exchange -> TWO independent laws,
    one per book. The block structure is discovered, not declared."""
    recs = [
        # book 1: cash / revenue / expense
        _rec("cash", "t1", 100), _rec("revenue", "t1", -100),
        _rec("cash", "t2", 250), _rec("expense", "t2", -250),
        _rec("cash", "t3", 40),  _rec("revenue", "t3", -40),
        # book 2: inventory / cogs  (disjoint from book 1)
        _rec("inventory", "u1", 60), _rec("cogs", "u1", -60),
        _rec("inventory", "u2", 30), _rec("cogs", "u2", -30),
    ]
    return dict(name="ledger_two_books", records=recs, entity_key=ENTITY,
                event_key=EVENT, qty_key=QTY, expected_laws=2)


def inventory_two_skus():
    """Stock transfers for two SKUs across locations. Each SKU's total stock
    is conserved across its locations -> two laws (one per SKU)."""
    recs = [
        _rec("A@w1", "m1", -5), _rec("A@w2", "m1", +5),
        _rec("A@w2", "m2", -3), _rec("A@store", "m2", +3),
        _rec("B@w1", "m3", -7), _rec("B@w2", "m3", +7),
        _rec("B@w2", "m4", -2), _rec("B@store", "m4", +2),
    ]
    return dict(name="inventory_two_skus", records=recs, entity_key=ENTITY,
                event_key=EVENT, qty_key=QTY, expected_laws=2)


def no_structure():
    """Pure sources: each event adds matter without balancing. The incidence
    has full column rank -> no conservation law -> HONEST STOP."""
    recs = [
        _rec("a", "e1", 1), _rec("b", "e1", 1),
        _rec("b", "e2", 1), _rec("c", "e2", 1),
        _rec("a", "e3", 1), _rec("c", "e3", 1),
    ]
    return dict(name="no_structure", records=recs, entity_key=ENTITY,
                event_key=EVENT, qty_key=QTY, expected_laws=0)


def parity_pairs():
    """Goods only ever move in cases of two. Bin counts grow without bound, so
    NOTHING is conserved over Q — yet the PARITY of each bin is conserved
    forever: two Z/2 laws that rational linear algebra cannot see."""
    recs = [
        _rec("bin_a", "case_to_a", 2),
        _rec("bin_b", "case_to_b", 2),
    ]
    return dict(name="parity_pairs", records=recs, entity_key=ENTITY,
                event_key=EVENT, qty_key=QTY, expected_laws=0)  # 0 over Q


def crt_mod6():
    """One event adds 2 to a, another adds 3 to b. Over Q: nothing. Over Z:
    a single Z/6 law — parity of a and the mod-3 residue of b fuse by CRT
    into one canonical modulus-6 invariant (the SNF normal form)."""
    recs = [
        _rec("a", "add2_a", 2),
        _rec("b", "add3_b", 3),
    ]
    return dict(name="crt_mod6", records=recs, entity_key=ENTITY,
                event_key=EVENT, qty_key=QTY, expected_laws=0)


ALL_DATASETS = [
    michaelis_menten,
    ledger_connected,
    ledger_two_books,
    inventory_two_skus,
    no_structure,
]

# Datasets whose structure is integer/modular — invisible over Q.
INTEGER_DATASETS = [parity_pairs, crt_mod6]
