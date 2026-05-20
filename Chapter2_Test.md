# Test: Chapter 2, Sections 2.1–2.2.3 (A Basic Description Logic)

## Instructions
Answer all questions. No notes. Try to do it in 45 minutes. Answers are at the bottom — don't peek until you're done.

---

## Part A: Definitions (2 points each)

**A1.** What is a concept name? Give two examples.

**A2.** What is a role name? Give two examples.

**A3.** Define "interpretation" precisely. What are its two components?

**A4.** What does it mean for an interpretation I to be a **model** of a TBox T?

**A5.** What is the difference between a TBox and an ABox?

---

## Part B: Constructors (3 points each)

For each constructor, write (i) its syntax, (ii) its semantic definition (what set it denotes in an interpretation I), and (iii) a one-sentence English reading.

**B1.** Conjunction

**B2.** Existential restriction

**B3.** Negation

**B4.** Value restriction (universal restriction)

**B5.** Top (⊤)

**B6.** Bottom (⊥)

---

## Part C: Translate to DL syntax (3 points each)

Write a concept description in DL notation for each English phrase. Use concept names and role names of your choice.

**C1.** "A person who has at least one child that is a doctor."

**C2.** "Something that is both a student and an employee."

**C3.** "Something that is NOT a mammal."

**C4.** "A course that is taught by at least one professor."

**C5.** "Something where all its parts are metal." (Use role `hasPart` and concept `Metal`.)

---

## Part D: Compute the semantics (4 points each)

Given interpretation I with:
```
Domain:  Δ^I = {a, b, c, d}

Concept names:
  Student^I = {a, b}
  Employee^I = {b, c}
  Course^I = {d}

Role names:
  attends^I = {(a, d), (b, d)}
  supervises^I = {(c, a), (c, b)}
```

Compute the set of domain elements in each of the following:

**D1.** `(Student ⊓ Employee)^I` = ?

**D2.** `(¬Student)^I` = ?

**D3.** `(∃attends.Course)^I` = ?

**D4.** `(∃supervises.Student)^I` = ?

**D5.** `(∀supervises.Student)^I` = ?

**D6.** `(Student ⊓ ∃attends.⊤)^I` = ?

**D7.** `(∃supervises.Employee)^I` = ?

**D8.** `⊥^I` = ?

---

## Part E: TBox reasoning (4 points each)

Given TBox T:
```
T = { Cat ⊑ Mammal,
      Mammal ⊑ Animal,
      Dog ⊑ Mammal,
      Fish ⊑ Animal,
      Animal ⊑ ∃hasHabitat.⊤ }
```

**E1.** Does `Cat ⊑ Animal` follow from T? Justify informally.

**E2.** Does `Dog ⊑ Animal` follow from T? Justify informally.

**E3.** Does `Fish ⊑ Mammal` follow from T? Justify (give a counterexample interpretation if not).

**E4.** Does `Cat ⊑ ∃hasHabitat.⊤` follow from T? Justify.

**E5.** Is the concept `Cat ⊓ ¬Animal` satisfiable with respect to T? Explain.

---

## Part F: ABox reasoning (3 points each)

Given TBox T and ABox A:
```
T = { Student ⊑ Person,
      Professor ⊑ Person,
      ∃teaches.⊤ ⊑ Professor }

A = { Student(alice),
      Professor(bob),
      teaches(alice, cs101),
      Course(cs101) }
```

**F1.** List everything you can infer about `alice` from T and A. (What concepts must alice be in?)

**F2.** Is this KB consistent? (Is there a model that satisfies both T and A?)

**F3.** Is `Person(alice)` entailed by the KB? Why?

**F4.** Is `Professor(alice)` entailed by the KB? Why?

**F5.** Can you infer `Student(bob)`? Why or why not?

---

## Part G: True or False (2 points each)

**G1.** Every concept name is a concept description.

**G2.** Every concept description is a concept name.

**G3.** If I is a model of TBox T, and T contains `A ⊑ B`, then `A^I ⊆ B^I`.

**G4.** If `C ⊑ D` follows from T, then in some model of T we have `C^I ⊆ D^I`.

**G5.** If `C ⊑ D` follows from T, then in EVERY model of T we have `C^I ⊆ D^I`.

**G6.** An ABox can contain a statement like `(∃r.C)(a)`.

**G7.** A TBox can contain a statement like `Person(alice)`.

**G8.** `(C ⊓ D)^I` is always a subset of `C^I`.

**G9.** `C^I` is always a subset of `(C ⊔ D)^I`.

**G10.** An empty TBox (no axioms) has no models.

---

## Part H: Short answer (5 points each)

**H1.** Explain in 2–3 sentences why the interpretation function is defined RECURSIVELY on the structure of concept descriptions. Why can't you just assign a set to every concept description directly?

**H2.** What is the difference between `C ⊑ D` holding in a SPECIFIC interpretation I, versus `C ⊑ D` being ENTAILED by a TBox T? Give a tiny example.

**H3.** Give an example of a TBox that is INCONSISTENT (has no model). Explain why no model exists.

---

---

---

# ANSWERS

*(Stop here until you've attempted all questions.)*

---

## Part A Answers

**A1.** A concept name is an atomic (primitive) class — a single symbol representing a set of individuals, with no internal structure. Examples: `Person`, `Cat`.

**A2.** A role name is an atomic binary relation — a single symbol representing pairs of individuals. Examples: `hasParent`, `teaches`.

**A3.** An interpretation I = (Δ^I, ·^I) consists of:
- Δ^I: a non-empty set called the **domain** (the "universe of objects")
- ·^I: an **interpretation function** that maps each concept name A to a set A^I ⊆ Δ^I, and each role name r to a relation r^I ⊆ Δ^I × Δ^I

**A4.** I is a model of T iff for EVERY axiom `C ⊑ D` in T, we have `C^I ⊆ D^I`. (Every axiom is satisfied simultaneously.)

**A5.** A TBox contains **terminological axioms** — general statements about classes (e.g., `Cat ⊑ Animal`). An ABox contains **assertions** about specific named individuals (e.g., `Cat(rex)`, `hasOwner(rex, alice)`).

---

## Part B Answers

**B1.** Conjunction: `C ⊓ D`. Semantics: `(C ⊓ D)^I = C^I ∩ D^I`. English: "things that are in both C and D."

**B2.** Existential restriction: `∃r.C`. Semantics: `(∃r.C)^I = {d ∈ Δ^I | there exists e ∈ Δ^I such that (d,e) ∈ r^I and e ∈ C^I}`. English: "things that have at least one r-link to something in C."

**B3.** Negation: `¬C`. Semantics: `(¬C)^I = Δ^I \ C^I`. English: "everything that is NOT in C."

**B4.** Value restriction: `∀r.C`. Semantics: `(∀r.C)^I = {d ∈ Δ^I | for all e, if (d,e) ∈ r^I then e ∈ C^I}`. English: "things where ALL their r-links lead to something in C."

**B5.** Top: `⊤`. Semantics: `⊤^I = Δ^I`. English: "everything in the domain."

**B6.** Bottom: `⊥`. Semantics: `⊥^I = ∅`. English: "nothing — the empty class."

---

## Part C Answers

**C1.** `Person ⊓ ∃hasChild.Doctor`

**C2.** `Student ⊓ Employee`

**C3.** `¬Mammal`

**C4.** `Course ⊓ ∃taughtBy.Professor`

**C5.** `∀hasPart.Metal`

---

## Part D Answers

**D1.** `(Student ⊓ Employee)^I = {a,b} ∩ {b,c} = {b}`

**D2.** `(¬Student)^I = {a,b,c,d} \ {a,b} = {c, d}`

**D3.** `(∃attends.Course)^I`: who has an attends-link to something in Course^I={d}? a→d ✓, b→d ✓. Answer: **{a, b}**

**D4.** `(∃supervises.Student)^I`: who has a supervises-link to something in Student^I={a,b}? c→a ✓, c→b ✓. Answer: **{c}**

**D5.** `(∀supervises.Student)^I`: who has ALL their supervises-links going to students?
- a: no supervises-links at all → vacuously true ✓
- b: no supervises-links → vacuously true ✓
- c: supervises a (student ✓), supervises b (student ✓) → true ✓
- d: no supervises-links → vacuously true ✓

Answer: **{a, b, c, d}**

**D6.** `(Student ⊓ ∃attends.⊤)^I`: Student AND has at least one attends-link to anything.
- Student^I = {a,b}
- ∃attends.⊤: who has any attends-link? a→d ✓, b→d ✓. = {a,b}
- Intersection: **{a, b}**

**D7.** `(∃supervises.Employee)^I`: who supervises something in Employee^I={b,c}? c→b ✓ (b is in Employee). Answer: **{c}**

**D8.** `⊥^I = ∅`

---

## Part E Answers

**E1.** **Yes.** Cat ⊑ Mammal and Mammal ⊑ Animal. In any model: Cat^I ⊆ Mammal^I ⊆ Animal^I. So Cat^I ⊆ Animal^I.

**E2.** **Yes.** Same reasoning: Dog ⊑ Mammal ⊑ Animal.

**E3.** **No.** Counterexample: let Δ={x}, Fish^I={x}, Animal^I={x}, Mammal^I=∅, Cat^I=∅, Dog^I=∅, hasHabitat^I={(x,x)}. All axioms satisfied, but Fish^I ⊄ Mammal^I.

**E4.** **Yes.** Cat ⊑ Mammal ⊑ Animal ⊑ ∃hasHabitat.⊤. Chain of inclusions.

**E5.** **Not satisfiable w.r.t. T.** In any model of T, Cat^I ⊆ Animal^I. So Cat^I ∩ (Δ\Animal^I) = ∅. No model of T can have anything in `Cat ⊓ ¬Animal`.

---

## Part F Answers

**F1.**
- alice ∈ Student^I (directly from ABox)
- alice ∈ Person^I (from Student ⊑ Person)
- (alice, cs101) ∈ teaches^I (from ABox)
- alice ∈ (∃teaches.⊤)^I (she teaches something)
- alice ∈ Professor^I (from ∃teaches.⊤ ⊑ Professor)

So alice is: **Student, Person, Professor** (and teaches cs101).

**F2.** **Yes, it's consistent.** A model exists: Δ = {alice, bob, cs101}, with the expected assignments. The fact that alice is both Student and Professor isn't contradictory — nothing forbids it.

**F3.** **Yes.** alice ∈ Student^I, and Student ⊑ Person, so alice ∈ Person^I.

**F4.** **Yes.** alice teaches cs101, so alice ∈ (∃teaches.⊤)^I. The TBox says ∃teaches.⊤ ⊑ Professor. So alice ∈ Professor^I.

**F5.** **No.** Nothing in T or A implies bob is a student. We only know Professor(bob). There might be a model where bob ∈ Student^I and one where bob ∉ Student^I. Since it's not true in ALL models, it's not entailed.

---

## Part G Answers

**G1.** **True.** Every concept name is the simplest possible concept description (a leaf).

**G2.** **False.** `Person ⊓ ∃teaches.Course` is a concept description but not a concept name.

**G3.** **True.** That's exactly what "I is a model of T" means.

**G4.** **True** (but misleadingly weak). If C ⊑ D follows from T, it holds in EVERY model, so certainly in SOME model. The statement is true but the word "some" undersells it.

**G5.** **True.** This is the definition of entailment: `T ⊨ C ⊑ D` means for all models I of T, `C^I ⊆ D^I`.

**G6.** **True.** ABox assertions can use complex concept descriptions as long as the DL allows it. `(∃r.C)(a)` means "a has an r-link to something in C."

**G7.** **False.** `Person(alice)` is an ABox assertion, not a TBox axiom. TBoxes contain only concept/role inclusions.

**G8.** **True.** `(C ⊓ D)^I = C^I ∩ D^I ⊆ C^I` always.

**G9.** **True.** `C^I ⊆ C^I ∪ D^I = (C ⊔ D)^I` always.

**G10.** **False.** An empty TBox has NO constraints. EVERY interpretation is a model of it. (There's nothing to violate.)

---

## Part H Answers

**H1.** There are infinitely many possible concept descriptions (you can nest constructors forever: ∃r.∃r.∃r.A...). You can't assign a set to each one independently — that would require infinite arbitrary choices with no coherence. Instead, you fix interpretations of the atomic names (finite choices), and the semantics of complex concepts are DETERMINED by the recursion. This ensures consistency: `(A ⊓ B)^I` is always `A^I ∩ B^I`, never something random.

**H2.** "C ⊑ D holds in I" means: in THIS PARTICULAR interpretation, C^I ⊆ D^I. It might not hold in other interpretations. "C ⊑ D is entailed by T" means: in EVERY model of T, C^I ⊆ D^I. Example: Let T = ∅ (empty). Take I where Cat^I = Dog^I. Then Cat ⊑ Dog holds in I. But Cat ⊑ Dog is NOT entailed by T, because there's another model J where Cat^J ⊄ Dog^J.

**H3.** T = { A ⊑ B, A ⊑ ¬B, ⊤ ⊑ A }. In any model: everything is in A (from ⊤ ⊑ A), everything in A is in B (from A ⊑ B), and everything in A is NOT in B (from A ⊑ ¬B). Contradiction: B^I and (Δ\B^I) would both have to contain everything. Impossible since the domain must be non-empty. No model exists.

---

## Scoring

| Part | Points |
|------|--------|
| A (5 questions × 2) | 10 |
| B (6 questions × 3) | 18 |
| C (5 questions × 3) | 15 |
| D (8 questions × 4) | 32 |
| E (5 questions × 4) | 20 |
| F (5 questions × 3) | 15 |
| G (10 questions × 2) | 20 |
| H (3 questions × 5) | 15 |
| **Total** | **145** |

**Passing: 100/145 (69%).** If you're below that, re-read sections 2.1 and 2.2 one more time before moving to Chapter 7.
