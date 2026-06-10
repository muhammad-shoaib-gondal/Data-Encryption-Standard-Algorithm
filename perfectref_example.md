# PerfectRef — A Worked Example with 5 Axioms

`PerfectRef` is the query‑rewriting algorithm for the **DL‑Lite** family of
Description Logics introduced by Calvanese, De Giacomo, Lembo, Lenzerini and
Rosati in
*"Tractable Reasoning and Efficient Query Answering in Description Logics:
The DL‑Lite Family"* (JAR, 2007).

Given

* a TBox **T** (a set of *positive inclusion axioms*, PIs), and
* a *conjunctive query* (CQ) **q**,

`PerfectRef` returns a *union of conjunctive queries* (UCQ) **q'** such that,
for **every** ABox **A**, evaluating **q'** directly on **A** as a plain
relational database yields exactly the certain answers of **q** over the
ontology *(T, A)*.

This document walks through the algorithm on an explicit TBox containing
**5 axioms** — one of each of the structural shapes that DL‑Lite allows.

---

## 1.  The TBox  *T*  (5 axioms)

We use a small university ontology.

| #   | Axiom                              | Shape                                | Intuition                                              |
| --- | ---------------------------------- | ------------------------------------ | ------------------------------------------------------ |
| A1  | `Professor ⊑ Person`               | concept ⊑ concept                    | every professor is a person                            |
| A2  | `Student   ⊑ Person`               | concept ⊑ concept                    | every student is a person                              |
| A3  | `Professor ⊑ ∃teaches`             | concept ⊑ ∃ role  (mandatory part.)  | every professor teaches something                      |
| A4  | `∃teaches⁻ ⊑ Course`               | ∃ inverse role ⊑ concept             | anything that is taught is a course                    |
| A5  | `teaches   ⊑ involvedIn`           | role ⊑ role                          | teaching is a special form of being involved with sth. |

These five axioms cover every DL‑Lite_R PI shape that PerfectRef needs to
handle, except for the inverse‑role variants of A3 and A5 (which behave
symmetrically).

---

## 2.  The Query  *q*

```
q(x)  ←  Person(x), involvedIn(x, y)
```

*"Return every person that is involved in something."*

Here `x` is a **distinguished** (answer) variable and `y` is an **existential**
(non‑distinguished) variable.  In PerfectRef terminology `y` is *unbound*
because it appears in exactly one atom and is not in the head.

---

## 3.  The Algorithm in One Slide

```
PerfectRef(q, T):
    PR := { q }
    repeat
        PR' := PR
        for each q' ∈ PR':
            -- (1) REWRITE STEP
            for each atom g in q':
                for each PI  I ∈ T applicable to g:
                    add  q'[g / gr(g, I)]  to PR
            -- (2) REDUCE STEP (unification)
            for each pair of atoms g1, g2 in q':
                if g1 and g2 unify with mgu σ:
                    add  τ(σ(q'))  to PR
        eliminate from PR every CQ that is subsumed by another CQ in PR
    until PR = PR'
    return PR
```

* **Applicability** of a PI `α ⊑ β` to an atom `g`:
  * `g = A(x)`            and `β = A`
  * `g = R(x, _)` (2nd arg *unbound*)  and `β = ∃R`
  * `g = R(_, x)` (1st arg *unbound*)  and `β = ∃R⁻`
  * `g = R(x, y)`         and the PI is a role inclusion `S ⊑ R` (or `S⁻ ⊑ R`)
* **`gr(g, I)`** is the corresponding rewriting (e.g. `gr(Person(x), Professor⊑Person) = Professor(x)`, `gr(teaches(x, _), Professor⊑∃teaches) = Professor(x)`).
* **Subsumption** is the usual CQ‑containment check: `q1` is subsumed by `q2`
  iff there is a homomorphism from `q2` to `q1`.

---

## 4.  Full Trace

We label rewritten queries `q0, q1, …` in the order they are first derived.

### Round 0

```
PR = { q0 : q(x) ← Person(x), involvedIn(x, y) }
```

### Round 1 — rewrite step on q0

| atom of q0          | applicable PI            | resulting atom    | new CQ                                                        |
| ------------------- | ------------------------ | ----------------- | ------------------------------------------------------------- |
| `Person(x)`         | A1  `Professor ⊑ Person` | `Professor(x)`    | **q1**  `q(x) ← Professor(x), involvedIn(x, y)`               |
| `Person(x)`         | A2  `Student ⊑ Person`   | `Student(x)`      | **q2**  `q(x) ← Student(x), involvedIn(x, y)`                 |
| `involvedIn(x, y)`  | A5  `teaches ⊑ involvedIn` | `teaches(x, y)` | **q3**  `q(x) ← Person(x), teaches(x, y)`                     |

```
PR = { q0, q1, q2, q3 }
```

### Round 2 — rewrite step on q1, q2, q3

* **q1**  `q(x) ← Professor(x), involvedIn(x, y)`
  * A5 on `involvedIn(x, y)` →  **q4**  `q(x) ← Professor(x), teaches(x, y)`
* **q2**  `q(x) ← Student(x), involvedIn(x, y)`
  * A5 on `involvedIn(x, y)` →  **q5**  `q(x) ← Student(x), teaches(x, y)`
* **q3**  `q(x) ← Person(x), teaches(x, y)`
  * A1 on `Person(x)` →  q4   *(already generated)*
  * A2 on `Person(x)` →  q5   *(already generated)*
  * A3 `Professor ⊑ ∃teaches` is applicable to `teaches(x, y)` because
    `y` is **unbound** (appears only in this atom and not in the head).
    `gr(teaches(x, _), A3) = Professor(x)`, giving
    **q6**  `q(x) ← Person(x), Professor(x)`

```
PR = { q0, q1, q2, q3, q4, q5, q6 }
```

### Round 3 — rewrite step on q4, q5, q6

* **q4**  `q(x) ← Professor(x), teaches(x, y)`
  * A3 on `teaches(x, y)` (y unbound) →
    `q(x) ← Professor(x), Professor(x)`  ≡  **q7**  `q(x) ← Professor(x)`
* **q5**  `q(x) ← Student(x), teaches(x, y)`
  * A3 on `teaches(x, y)` →  **q8**  `q(x) ← Student(x), Professor(x)`
* **q6**  `q(x) ← Person(x), Professor(x)`
  * A1 on `Person(x)` →  `q(x) ← Professor(x), Professor(x)`  ≡ q7
  * A2 on `Person(x)` →  q8

```
PR = { q0, q1, q2, q3, q4, q5, q6, q7, q8 }
```

### Round 4

No new CQs can be derived from `q7` or `q8` (no PI rewrites the lone
`Professor` atom, and the two atoms of `q8` have different predicates so do
not unify).  The fixpoint is reached.

### Reduce / subsumption clean‑up

```
q7 :  q(x) ← Professor(x)
```

subsumes every CQ that contains `Professor(x)`, namely **q1, q4, q6, q8**.
Those four CQs are removed.

(For instance, the answers of `q1` are precisely the `x`'s for which the ABox
contains both `Professor(x)` *and* some `involvedIn(x, _)`, which is a subset
of the `x`'s for which the ABox contains `Professor(x)`.)

---

## 5.  Final UCQ (the perfect reformulation)

```
q(x) ← Person(x),     involvedIn(x, y)        -- q0
q(x) ← Student(x),    involvedIn(x, y)        -- q2
q(x) ← Person(x),     teaches(x, y)            -- q3
q(x) ← Student(x),    teaches(x, y)            -- q5
q(x) ← Professor(x)                            -- q7
```

Five CQs — one per "way" an individual can end up being a *person involved
in something* given the implicit knowledge in the TBox:

* explicit `Person` + explicit `involvedIn`             (q0)
* explicit `Student` (→ Person by A2) + explicit `involvedIn`   (q2)
* explicit `Person` + explicit `teaches` (→ involvedIn by A5)   (q3)
* explicit `Student` (→ Person) + explicit `teaches` (→ involvedIn)  (q5)
* explicit `Professor` (→ Person by A1, → ∃teaches by A3,
                          → ∃involvedIn by A5)                  (q7)

Evaluating this UCQ on **any** ABox returns exactly the certain answers of
the original query over the ontology — without any reasoning at query time.

---

## 6.  Running it yourself

A small, self‑contained Python script that performs exactly the trace above
is provided in [`perfectref_example.py`](./perfectref_example.py).  Just run

```bash
python3 perfectref_example.py
```

to see the rewriting unfold and the final UCQ printed.
