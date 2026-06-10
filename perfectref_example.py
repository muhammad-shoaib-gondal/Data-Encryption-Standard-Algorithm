"""
A minimal, self-contained demonstration of the PerfectRef query-rewriting
algorithm for DL-Lite (Calvanese, De Giacomo, Lembo, Lenzerini, Rosati, 2007).

It runs the algorithm on the worked example documented in
``perfectref_example.md`` (a TBox of 5 axioms and one initial conjunctive
query) and prints the full rewriting trace plus the final UCQ.

The implementation is intentionally small and pedagogical, not optimised, and
covers exactly the DL-Lite_R axiom shapes used in the example:

    A ⊑ B          (concept inclusion)
    A ⊑ ∃R         (mandatory participation)
    ∃R⁻ ⊑ A        (inverse role typing)
    R ⊑ S          (role inclusion)

Run with:

    python3 perfectref_example.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import Iterable


# ---------------------------------------------------------------------------
#  Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Var:
    name: str

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return self.name


@dataclass(frozen=True)
class Atom:
    """A query atom: predicate name + tuple of arguments (all Vars here)."""

    pred: str
    args: tuple[Var, ...]

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.pred}({', '.join(map(repr, self.args))})"


@dataclass(frozen=True)
class CQ:
    """A conjunctive query  q(head_vars) :- body_atoms ."""

    head: tuple[Var, ...]
    body: frozenset[Atom]

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        head = f"q({', '.join(map(repr, self.head))})"
        body = ", ".join(map(repr, sorted(self.body, key=repr)))
        return f"{head} <- {body}"


# A TBox axiom is one of these tagged tuples:
#   ("concept_incl",  A,  B)              -- A ⊑ B
#   ("mand_part",     A,  R)              -- A ⊑ ∃R
#   ("mand_part_inv", A,  R)              -- A ⊑ ∃R⁻
#   ("inv_typing",    R,  A)              -- ∃R⁻ ⊑ A
#   ("dom_typing",    R,  A)              -- ∃R  ⊑ A
#   ("role_incl",     S,  R)              -- S  ⊑ R
Axiom = tuple


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------


_fresh = count()


def fresh_var(prefix: str = "z") -> Var:
    return Var(f"{prefix}{next(_fresh)}")


def is_unbound(v: Var, cq: CQ, in_atom: Atom) -> bool:
    """A variable is *unbound* in PerfectRef's sense iff it appears in
    exactly one body atom and not in the head."""
    if v in cq.head:
        return False
    occurrences = sum(1 for a in cq.body for arg in a.args if arg == v)
    return occurrences == 1 and v in in_atom.args


def replace_atom(cq: CQ, old: Atom, new: Atom) -> CQ:
    body = (cq.body - {old}) | {new}
    return CQ(cq.head, frozenset(body))


# ---------------------------------------------------------------------------
#  Rewrite step:  applicability and  gr(g, I)
# ---------------------------------------------------------------------------


def rewrite_atom(atom: Atom, axiom: Axiom, cq: CQ) -> Atom | None:
    """Return gr(atom, axiom) if `axiom` is applicable to `atom` in `cq`,
    else None."""

    kind = axiom[0]

    # A ⊑ B  matches  B(x)  ->  A(x)
    if kind == "concept_incl":
        _, A, B = axiom
        if atom.pred == B and len(atom.args) == 1:
            return Atom(A, atom.args)

    # ∃R⁻ ⊑ A  matches  A(x)  ->  R(_, x)
    elif kind == "inv_typing":
        _, R, A = axiom
        if atom.pred == A and len(atom.args) == 1:
            return Atom(R, (fresh_var(), atom.args[0]))

    # ∃R ⊑ A  matches  A(x)  ->  R(x, _)
    elif kind == "dom_typing":
        _, R, A = axiom
        if atom.pred == A and len(atom.args) == 1:
            return Atom(R, (atom.args[0], fresh_var()))

    # A ⊑ ∃R  matches  R(x, y) with y unbound  ->  A(x)
    elif kind == "mand_part":
        _, A, R = axiom
        if atom.pred == R and len(atom.args) == 2:
            x, y = atom.args
            if is_unbound(y, cq, atom):
                return Atom(A, (x,))

    # A ⊑ ∃R⁻  matches  R(x, y) with x unbound  ->  A(y)
    elif kind == "mand_part_inv":
        _, A, R = axiom
        if atom.pred == R and len(atom.args) == 2:
            x, y = atom.args
            if is_unbound(x, cq, atom):
                return Atom(A, (y,))

    # S ⊑ R  matches  R(x, y)  ->  S(x, y)
    elif kind == "role_incl":
        _, S, R = axiom
        if atom.pred == R and len(atom.args) == 2:
            return Atom(S, atom.args)

    return None


# ---------------------------------------------------------------------------
#  Reduce step (atom unification) — simplified: only unify identical atoms.
# ---------------------------------------------------------------------------


def reduce_cq(cq: CQ) -> CQ:
    """Collapse syntactically identical atoms.  (A full PerfectRef reduce
    step also tries non-trivial MGUs between body atoms; the example in
    this file only needs the identity case.)"""
    return CQ(cq.head, frozenset(cq.body))  # frozenset already dedups


# ---------------------------------------------------------------------------
#  CQ containment (subsumption) via homomorphism search
# ---------------------------------------------------------------------------


def _homomorphism(src_atoms: list[Atom], src_head: tuple[Var, ...],
                  tgt: CQ, mapping: dict[Var, Var]) -> bool:
    """Try to extend `mapping` into a homomorphism src -> tgt that fixes
    the head variables (mapping[h_i] = tgt.head[i])."""
    if not src_atoms:
        return True
    a, *rest = src_atoms
    for b in tgt.body:
        if b.pred != a.pred or len(b.args) != len(a.args):
            continue
        new_mapping = dict(mapping)
        ok = True
        for sa, ta in zip(a.args, b.args):
            if sa in new_mapping:
                if new_mapping[sa] != ta:
                    ok = False
                    break
            else:
                new_mapping[sa] = ta
        if ok and _homomorphism(rest, src_head, tgt, new_mapping):
            return True
    return False


def subsumes(q_general: CQ, q_specific: CQ) -> bool:
    """Return True iff every answer of `q_specific` is also an answer of
    `q_general` -- equivalently, iff there is a homomorphism from
    `q_general` to `q_specific` that maps head variables identically."""
    if len(q_general.head) != len(q_specific.head):
        return False
    init = dict(zip(q_general.head, q_specific.head))
    return _homomorphism(list(q_general.body), q_general.head,
                         q_specific, init)


def remove_subsumed(pr: set[CQ]) -> set[CQ]:
    """Drop every CQ that is strictly subsumed by another CQ in the set."""
    result = set(pr)
    for q in list(result):
        for other in result:
            if other is q or other == q:
                continue
            if subsumes(other, q):
                result.discard(q)
                break
    return result


# ---------------------------------------------------------------------------
#  PerfectRef main loop
# ---------------------------------------------------------------------------


def perfect_ref(q0: CQ, tbox: Iterable[Axiom],
                verbose: bool = True) -> set[CQ]:
    """Compute the perfect reformulation of `q0` under `tbox`.

    Implementation note: we keep two sets.

      * ``seen`` holds every CQ ever derived and is monotonically growing;
        it is what we test against to avoid re-adding work.
      * ``frontier`` holds the CQs that still need to have the rewrite step
        applied to them in the next round.

    Subsumption-based pruning is only done once, on the final result, so
    that a CQ which was subsumed in an early round cannot be re-derived
    (and thus cause non-termination) in a later round.
    """
    tbox = list(tbox)
    seen: set[CQ] = {q0}
    frontier: set[CQ] = {q0}
    round_no = 0
    if verbose:
        print(f"\n[round {round_no}]  initial PR =")
        for q in seen:
            print(f"    {q}")

    while frontier:
        round_no += 1
        next_frontier: set[CQ] = set()

        for q in frontier:
            for atom in q.body:
                for ax in tbox:
                    rewritten = rewrite_atom(atom, ax, q)
                    if rewritten is None:
                        continue
                    q_new = reduce_cq(replace_atom(q, atom, rewritten))
                    if q_new not in seen:
                        seen.add(q_new)
                        next_frontier.add(q_new)
                        if verbose:
                            print(f"    [+] via {axiom_label(ax)} on {atom}:  {q_new}")

        if verbose and next_frontier:
            print(f"\n[round {round_no}]  PR has {len(seen)} CQs total "
                  f"({len(next_frontier)} new this round)")
        frontier = next_frontier

    pruned = remove_subsumed(seen)
    if verbose:
        print(f"\n[after subsumption pruning]  {len(pruned)} CQ(s):")
        for q in sorted(pruned, key=repr):
            print(f"    {q}")
    return pruned


def axiom_label(ax: Axiom) -> str:
    kind = ax[0]
    if kind == "concept_incl":
        return f"{ax[1]} ⊑ {ax[2]}"
    if kind == "mand_part":
        return f"{ax[1]} ⊑ ∃{ax[2]}"
    if kind == "mand_part_inv":
        return f"{ax[1]} ⊑ ∃{ax[2]}⁻"
    if kind == "inv_typing":
        return f"∃{ax[1]}⁻ ⊑ {ax[2]}"
    if kind == "dom_typing":
        return f"∃{ax[1]} ⊑ {ax[2]}"
    if kind == "role_incl":
        return f"{ax[1]} ⊑ {ax[2]}"
    return str(ax)


# ---------------------------------------------------------------------------
#  The 5-axiom example
# ---------------------------------------------------------------------------


def main() -> None:
    # The TBox: five DL-Lite_R positive inclusion axioms.
    tbox = [
        ("concept_incl", "Professor", "Person"),       # A1
        ("concept_incl", "Student",   "Person"),       # A2
        ("mand_part",    "Professor", "teaches"),      # A3
        ("inv_typing",   "teaches",   "Course"),       # A4  (∃teaches⁻ ⊑ Course)
        ("role_incl",    "teaches",   "involvedIn"),   # A5
    ]

    print("TBox T:")
    for i, ax in enumerate(tbox, 1):
        print(f"  A{i}:  {axiom_label(ax)}")

    x, y = Var("x"), Var("y")
    q0 = CQ(
        head=(x,),
        body=frozenset({
            Atom("Person", (x,)),
            Atom("involvedIn", (x, y)),
        }),
    )

    print(f"\nInitial query q0:  {q0}")
    print("\n--- Running PerfectRef ---")

    result = perfect_ref(q0, tbox, verbose=True)

    print("\n=== Final UCQ (perfect reformulation) ===")
    for q in sorted(result, key=repr):
        print(f"  {q}")
    print(f"\n{len(result)} CQ(s) in total.")


if __name__ == "__main__":
    main()
