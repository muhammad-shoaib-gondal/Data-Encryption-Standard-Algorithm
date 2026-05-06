# DL-Lite_A: Master's Thesis Plan & Summer Roadmap

A complete plan for contributing the DL-Lite_A formalization and verified reasoner to the FOWL (Formally Verified OWL2) project.

---

## Table of Contents

1. [Project Context](#1-project-context)
2. [What You're Building](#2-what-youre-building)
3. [Concepts to Learn (Layered)](#3-concepts-to-learn-layered)
4. [Reading List](#4-reading-list)
5. [Week-by-Week Summer Plan](#5-week-by-week-summer-plan)
6. [Thesis Year Plan](#6-thesis-year-plan)
7. [Mapping to Grant Tasks](#7-mapping-to-grant-tasks)
8. [Project Progress After Completion](#8-project-progress-after-completion)
9. [Publication Opportunities](#9-publication-opportunities)
10. [Files You'll Create](#10-files-youll-create)
11. [Files to Study in the Existing Codebase](#11-files-to-study-in-the-existing-codebase)

---

## 1. Project Context

The FOWL grant defines a 4-year project to build provably-correct reasoners for OWL2 ontologies. It has five tasks:

| # | Task | Scope |
|---|------|-------|
| 1 | Formalization of Description Logics | EL⁺⁺, DHL + def-Horn, DL-Lite_A in Coq |
| 2 | Implementation of Reasoners | Verified reasoners for the three logics above |
| 3 | Formalization of OWL2 | OWL2 syntax + direct semantics + profile predicates |
| 4 | OWL2 Parsers | Verified parsers for OWL2 EL/RL/QL profiles |
| 5 | Code Extraction & Deployment | Coq → OCaml extraction, benchmarks, Protégé plugin |

**Current state:** EL is done (~90% for Tasks 1–2). DL-Lite_A is at **0%**. Your work fills this gap entirely.

---

## 2. What You're Building

### The problem DL-Lite_A solves

You have a large database (millions of rows) plus a lightweight ontology (schema with subclass relationships). A user asks a query. Instead of materializing all inferences (expensive), you **rewrite the query** into a bigger SQL query that, when run directly on the raw database, gives the same answers as if you had done full reasoning.

### What you'll deliver

1. **Coq formalization** of DL-Lite_A syntax and semantics (`src/Logic/DLLiteA.v`)
2. **Verified reasoner** — the PerfectRef query rewriting algorithm implemented in Coq with machine-checked soundness and completeness proofs
3. **Extracted OCaml** — the verified reasoner automatically translated to runnable OCaml
4. **Benchmarks** — performance comparison against existing systems (Ontop, Rapid) on standard ontologies

### Example of what the reasoner does

```
Input:
  Ontology:  Manager ⊑ Employee
             hasReport ⊑ supervises
  Query:     "Find all (x) such that Employee(x)"

Output (rewritten UCQ):
  "Find all (x) such that Employee(x)"
  UNION
  "Find all (x) such that Manager(x)"

The rewritten query, run on raw data, gives complete answers.
```

---

## 3. Concepts to Learn (Layered)

Master each layer before moving to the next.

### Layer 0: Prerequisites (you likely have these)

- Sets, relations, functions
- First-order logic (∀, ∃, ∧, ∨, →)
- Directed graphs, reachability, DAGs
- Computational complexity (P, NP, PTIME, data complexity vs combined complexity)
- Basic databases (relations/tables, SQL, SELECT-FROM-WHERE, joins)

### Layer 1: Description Logics basics

| Concept | What it is |
|---------|------------|
| Concept (class) | A set of things. E.g., `Person`, `Cat`. |
| Role (property) | A binary relation. E.g., `hasParent`, `worksFor`. |
| Individual | A named specific thing. E.g., `Alice`, `Rex`. |
| Concept constructors | Operators building complex concepts: ⊓ (and), ∃r.C (exists), ⊤ (top), ⊥ (bottom). |
| TBox | The schema — concept/role inclusions. E.g., `{Cat ⊑ Mammal}`. |
| ABox | The data — assertions about individuals. E.g., `{Cat(Rex)}`. |
| Knowledge Base (KB) | TBox + ABox together. |
| Interpretation | A concrete "world" assigning sets to concepts and pairs to roles. |
| Model | An interpretation making all KB statements true. |
| Subsumption (⊑) | "Every member of A is also in B, in every model." |
| Soundness | If the reasoner says yes → it's really true. |
| Completeness | If it's really true → the reasoner says yes. |

### Layer 2: DL-Lite_A specifically

| Concept | What it is |
|---------|------------|
| Basic concept | Atomic concept `A`, or `∃r` (domain of r), or `∃r⁻` (range of r). Very restricted. |
| General concept | A basic concept, or its negation `¬B`. Only on right side of ⊑. |
| Positive inclusion | `B₁ ⊑ B₂` — every B₁ is a B₂. |
| Negative inclusion | `B₁ ⊑ ¬B₂` — B₁ and B₂ are disjoint (nothing is both). |
| Role inclusion | `r ⊑ s` — r is a sub-role of s. |
| Functionality | `(funct r)` — each thing has at most one r-value. |
| Why it's restricted | The severe syntax restrictions guarantee PTIME data complexity for query answering. |
| TBox reasoning | Concept satisfiability + subsumption — both PTIME in DL-Lite_A. |
| ABox consistency | Can be checked in PTIME via a closure algorithm. |

### Layer 3: Conjunctive queries

| Concept | What it is |
|---------|------------|
| Conjunctive query (CQ) | `∃y₁…yₖ. atom₁ ∧ atom₂ ∧ …` — like SELECT-FROM-WHERE with joins. |
| Union of CQs (UCQ) | Multiple CQs connected by UNION. |
| Certain answers | Tuples that satisfy the query in EVERY model of the KB. |
| Query answering problem | "Given KB and query, compute certain answers." |
| Why it's hard | Infinitely many models, finite computation needed. |

### Layer 4: The PerfectRef algorithm

| Concept | What it is |
|---------|------------|
| Key insight | Instead of reasoning over data, rewrite the QUERY so it's self-sufficient. |
| Rewriting step | Unify a query atom with a TBox axiom → produce a new query atom. |
| Reduction step | Handle role inclusions by replacing a role with its super-role. |
| Containment check | Remove redundant queries (one subsumed by another). |
| Fixed point | Repeat until no new queries are produced. |
| Termination | Finite because there are only finitely many possible query shapes over the TBox signature. |
| Correctness | The rewritten UCQ gives EXACTLY the certain answers over any ABox. |

### Layer 5: Optimizations

| Concept | What it is |
|---------|------------|
| Exponential blowup | Naïve PerfectRef can produce exponentially many CQs. |
| CQ subsumption | Remove any query that's logically contained in another. |
| Factorization | Merge variables to shrink queries. |
| Datalog reformulation | Instead of UCQ output, compile to a Datalog program (avoids some blowup). |
| Tree-witness approach | Structural analysis of the TBox to avoid unnecessary rewriting. |

### Layer 6: Coq and the FOWL connection

| Concept | What it is |
|---------|------------|
| Inductive type | Coq's way to define syntax (like an algebraic data type). |
| Fixpoint | Coq's recursive function — must provably terminate. |
| Theorem/Proof | A property stated and proved; machine-checked by Coq. |
| Extraction | Coq → OCaml automatic translation. Proofs erased; functions kept. |
| Logic_Primitives | The FOWL type class (in `ConcreteDomain.v`) your types will plug into. |
| Termination metric | A number that strictly decreases with each recursive call — needed to convince Coq the algorithm halts. |

---

## 4. Reading List

### Textbooks (start here)

1. **"An Introduction to Description Logic" — Baader, Horrocks, Lutz, Sattler (2017)**
   - Chapter 1: What are DLs
   - Chapter 4: The DL-Lite family
   - Free PDF available online

2. **Software Foundations, Volume 1: "Logical Foundations" — Pierce et al.**
   - Chapters 1–8: Basics, Induction, Lists, Poly, Tactics, Logic, IndProp, Maps
   - For Coq fluency. Do in parallel with the DL reading.
   - https://softwarefoundations.cis.upenn.edu/

### Papers (read in this order)

| # | Paper | What you get from it |
|---|-------|---------------------|
| 1 | Calvanese, De Giacomo, Lembo, Lenzerini, Rosati. **"Tractable Reasoning and Efficient Query Answering in Description Logics: The DL-Lite Family."** JAIR 2007. | THE foundational paper. Defines DL-Lite, PerfectRef, proves all complexity results. Read Sections 1–6 carefully. |
| 2 | Calvanese et al. **"Linking Data to Ontologies."** J. Data Semantics, 2009. | Extends to DL-Lite_A (adds attributes/datatypes). Shows the specific variant you're formalizing. |
| 3 | Pérez-Urbina, Motik, Horrocks. **"Tractable Query Answering and Rewriting under Description Logic Constraints."** J. Applied Logic, 2010. | The Datalog reformulation optimization. Your main optimization reference. |
| 4 | Kontchakov, Lutz, Wolter, Zakharyaschev. **"The Tree-Witness Approach."** 2014. | Advanced structural optimization. Read after you implement the basic version. |
| 5 | Rosati, Almatelli. **"Improving Query Answering over DL-Lite Ontologies."** KR 2010. | Practical optimizations (semantic query optimization). |
| 6 | Artale, Calvanese, Kontchakov, Zakharyaschev. **"The DL-Lite Family and Relations."** JAIR 2009. | Extended DL-Lite family relationships. Good for understanding variants. |

### For Coq proof work (thesis year)

| # | Paper | Why |
|---|-------|-----|
| 7 | The existing FOWL codebase (`src/Correctness/Correctness.v`) | See how soundness+completeness proofs are structured for EL. Follow the same pattern. |
| 8 | Sozeau. **"Program-ing Finger Trees in Coq."** ICFP 2007. | Shows how to use `Program Fixpoint` for complex termination arguments. |
| 9 | Chlipala. **"Certified Programming with Dependent Types."** | Advanced Coq techniques if you get stuck on proofs. |

### Benchmark ontologies

| Ontology | What it is | Where to get it |
|----------|-----------|-----------------|
| LUBM | University domain, standard DL-Lite benchmark | http://swat.cse.lehigh.edu/projects/lubm/ |
| UOBM | Extended university benchmark | Search "UOBM ontology benchmark" |
| Adolena | Small test ontology for DL-Lite | Included in Ontop test suite |
| NPD (Norwegian Petroleum Directorate) | Real-world DL-Lite_A ontology | https://github.com/ontop/npd-benchmark |

### Tools to compare against

| Tool | What it does |
|------|-------------|
| Ontop | The reference OMQA system for DL-Lite. Java. | 
| Rapid | Optimized query rewriting (Chortaras et al.) |
| Requiem | Older rewriting system (Pérez-Urbina et al.) |
| ELK | EL reasoner (for comparison on EL-fragment ontologies) |

---

## 5. Week-by-Week Summer Plan

### Weeks 1–2: Foundations

**Goal:** Understand DLs and DL-Lite_A conceptually. No code yet.

| Day | Activity |
|-----|----------|
| 1–2 | Read Baader et al. (2017) textbook, Chapter 1. Take notes: concept, role, interpretation, model, subsumption. |
| 3–4 | Read Chapter 4 (DL-Lite). Understand the syntax restrictions and WHY they exist (PTIME data complexity). |
| 5–6 | Read Calvanese et al. JAIR 2007, Sections 1–3. Understand DL-Lite_R and DL-Lite_A languages. |
| 7–8 | Read Calvanese 2007, Section 4. Understand TBox reasoning (satisfiability, subsumption — both PTIME). |
| 9–10 | Read Section 5 (query answering complexity) and Section 6 (PerfectRef). Trace Example 29 by hand on paper. |
| 11–14 | Start Software Foundations Ch 1–3 (Basics, Induction, Lists) in evenings. |

**Deliverable:** Can explain PerfectRef on a whiteboard. Can trace the algorithm by hand on a 5-axiom ontology.

---

### Weeks 3–4: First Implementation

**Goal:** Implement basic PerfectRef in OCaml. No optimizations yet.

| Day | Activity |
|-----|----------|
| 1–2 | Define OCaml types: `concept`, `role`, `tbox_axiom`, `conjunctive_query`, `ucq`. |
| 3–4 | Implement the core loop: pick a query atom, try to unify with each TBox axiom, produce new queries. |
| 5–6 | Implement the reduction step (role inclusions). |
| 7–8 | Implement basic containment check (syntactic duplicate elimination). |
| 9–10 | Test on examples from the Calvanese paper. Verify by hand that output is correct. |
| 11–14 | Continue Software Foundations Ch 4–6 (Poly, Tactics, Logic). |

**Deliverable:** Working PerfectRef on toy inputs. Given a 5-axiom TBox and a 2-atom CQ, outputs the correct UCQ rewriting.

---

### Weeks 5–6: Benchmarking Infrastructure

**Goal:** Run on real ontologies and compare to existing systems.

| Day | Activity |
|-----|----------|
| 1–3 | Download LUBM benchmark ontology (DL-Lite fragment). Parse it into your OCaml types (write a simple OWL parser or use an existing library). |
| 4–5 | Download 2–3 more benchmarks: NPD, UOBM, or Adolena. |
| 6–7 | Implement timing harness. Measure: rewriting time, output UCQ size (number of disjuncts), number of atoms per disjunct. |
| 8–10 | Install and run Ontop on the same inputs. Record its rewriting sizes for comparison. |
| 11–14 | Write up initial results table. Identify where naïve implementation produces huge UCQs. |

**Deliverable:** Benchmark table comparing your PerfectRef output size and time to Ontop on 3+ ontologies.

---

### Weeks 7–8: Optimization

**Goal:** Implement at least one optimization that measurably reduces output size or time.

| Day | Activity |
|-----|----------|
| 1–2 | Read Pérez-Urbina et al. 2010 (Datalog reformulation). |
| 3–4 | Read Rosati & Almatelli 2010 (semantic optimization). |
| 5–7 | Pick ONE optimization to implement: |
|     | (a) CQ subsumption — remove any query subsumed by another in the UCQ |
|     | (b) Factorization — merge queries differing only in variable naming |
|     | (c) Datalog compilation for the recursive TBox portion |
| 8–10 | Implement it. |
| 11–14 | Re-run benchmarks. Measure improvement. |

**Deliverable:** Optimized implementation with measurable improvement over naïve. Updated benchmark table.

---

### Weeks 9–10: Connect to FOWL Project

**Goal:** Define DL-Lite_A formally in Coq. Integrate with existing codebase.

| Day | Activity |
|-----|----------|
| 1–2 | Get the FOWL project building (`dune build`). Run existing EL benchmarks via `test-compile.sh`. |
| 3–4 | Read `src/Logic/EL.v` and `src/Logic/ConcreteDomain.v`. Understand `Logic_Primitives`. |
| 5–7 | Create `src/Logic/DLLiteA.v`: define `Inductive DLLiteA_Basic_Concept`, `DLLiteA_Axiom`, `DLLiteA_TBox`, etc. Model after EL.v. |
| 8–10 | Define DL-Lite_A model-theoretic semantics: interpretation record, satisfaction relation. |
| 11–14 | Verify it compiles (`dune build`). No proofs yet — just definitions. |

**Deliverable:** `src/Logic/DLLiteA.v` that compiles. Formal syntax and semantics of DL-Lite_A in Coq.

---

### Weeks 11–12: Write-Up and Thesis Proposal

**Goal:** Consolidate into documents.

| Day | Activity |
|-----|----------|
| 1–3 | Write summer report: problem statement, algorithm description, implementation details, benchmark results, optimization. |
| 4–5 | Draft thesis proposal: "Verified Query Rewriting for DL-Lite_A." |
| 6–7 | Clean up code. Push to repository. Ensure everything builds. |
| 8–10 | Meet with advisor. Present results. Get feedback on thesis direction. |
| 11–14 | Draft workshop paper (see Section 9). Buffer/catch-up. |

**Deliverable:** Summer report. Thesis proposal. Clean codebase. Working reasoner with benchmarks. Workshop paper draft.

---

## 6. Thesis Year Plan

### September–October: Coq Formalization of TBox Reasoning

- Formalize TBox consistency checking in Coq (closure-based algorithm from Calvanese 2007 Section 4)
- Formalize concept satisfiability algorithm (NNF-closure)
- Prove soundness: if algorithm says "satisfiable" → concept truly has a model
- Prove completeness: if concept has a model → algorithm says "satisfiable"
- Submit workshop paper (Paper 1) if not already done

### November–December: Formalize PerfectRef in Coq

- Define conjunctive queries as a Coq inductive type
- Implement PerfectRef as a Coq `Program Fixpoint`
- Prove termination (define a decreasing metric — the hard part)
- Begin soundness proof: if a tuple is in the rewriting's answers → it's a certain answer

### January–February: Correctness Proofs

- Complete soundness proof for PerfectRef
- Completeness proof: if a tuple is a certain answer → the rewriting finds it
- These are the hardest proofs. Budget two full months.
- Submit conference paper (Paper 2) to KR or CPP

### March: Extraction and End-to-End Benchmarks

- Extract verified Coq reasoner to OCaml via `Extraction.v`
- Run on the same benchmarks from summer
- Compare: verified reasoner vs. unverified summer implementation vs. Ontop
- Measure the "cost of verification" (performance overhead, if any)

### April–May: Write Thesis

- Chapter 1: Introduction and background
- Chapter 2: DL-Lite_A formalization (syntax, semantics, properties)
- Chapter 3: PerfectRef algorithm design and optimization
- Chapter 4: Correctness proofs (soundness and completeness)
- Chapter 5: Experimental evaluation (benchmarks, comparison)
- Chapter 6: Conclusion and future work
- Defend

---

## 7. Mapping to Grant Tasks

### Which tasks your work fulfills

| Grant Task | Your contribution | Portion completed |
|---|---|---|
| **Task 1: Formalization of DLs** | DL-Lite_A syntax + semantics in Coq | ~1/3 of Task 1 (the DL-Lite_A part) |
| **Task 2: Reasoners** | PerfectRef in Coq, proved sound + complete | ~1/3 of Task 2 (DL-Lite_A reasoner) |
| **Task 3: OWL2 formalization** | DL-Lite_A semantics reusable for OWL2 QL profile predicate | ~15–20% of Task 3 (indirect) |
| **Task 4: Parsers** | Not directly your work | 0% |
| **Task 5: Extraction & deployment** | Extract reasoner to OCaml + real ontology benchmarks | ~20% of Task 5 |

### How it fits structurally

Your DL-Lite_A formalization will:
- Reuse `Logic_Primitives` from `ConcreteDomain.v` (same concept/role/individual names)
- Follow the same pattern as `EL.v` (inductive types for syntax)
- Follow the same pattern as `Classification.v` (a fixpoint loop that saturates)
- Follow the same pattern as `Correctness.v` (soundness ↔ completeness theorem)
- Plug into `Extraction.v` for OCaml generation

---

## 8. Project Progress After Completion

### Before your work

| Task | Status | Done |
|------|--------|------|
| 1. DL formalizations | EL only | ~80% |
| 2. Reasoners | EL reasoner only | ~30% |
| 3. OWL2 formalization | Nothing | 0% |
| 4. OWL2 parsers | Nothing | 0% |
| 5. Extraction & deployment | EL extraction + synthetic benchmarks | ~60% |
| **Overall** | | **~35%** |

### After your work (thesis complete)

| Task | Status | Done |
|------|--------|------|
| 1. DL formalizations | EL + DL-Lite_A done, only DHL remaining | **~95%** |
| 2. Reasoners | EL + DL-Lite_A reasoners verified | **~60%** |
| 3. OWL2 formalization | DL-Lite_A semantics reusable for QL profile | **~15%** |
| 4. OWL2 parsers | Unchanged | 0% |
| 5. Extraction & deployment | Both reasoners extracted + real ontology benchmarks | **~75%** |
| **Overall** | | **~50–55%** |

### What remains for others after you

- DHL + def-Horn formalization and reasoner (Task 1 + Task 2 remainder)
- Full OWL2 syntax and semantics formalization (Task 3)
- All three OWL2 parsers with correctness proofs (Task 4)
- Protégé Java plugin with JNI bridge (Task 5 remainder)
- Closing ~40 `Admitted` obligations in EL normalization

---

## 9. Publication Opportunities

### Paper 1: Workshop paper (end of summer / early fall)

**Title:** *"Towards Verified Ontology-Mediated Query Answering: A Formalization of DL-Lite_A in Coq"*

**Contents:**
- Coq formalization of DL-Lite_A syntax and semantics
- Unverified but optimized OCaml implementation of PerfectRef
- Benchmark results on real ontologies
- Roadmap for full verification

**Target venues:**
- DL Workshop (Description Logic Workshop) — perfect fit, 6–8 pages
- ORE (OWL Reasoner Evaluation Workshop) — if emphasizing benchmarks
- ITP short paper track — if Coq formalization is substantial

**Novelty claim:** "First Coq formalization of DL-Lite_A syntax and semantics; first benchmark of a verified DL-Lite pipeline."

---

### Paper 2: Conference paper (end of thesis)

**Title:** *"Formally Verified Query Rewriting for Ontology-Mediated Query Answering in DL-Lite_A"*

**Contents:**
- Complete Coq formalization (syntax, semantics, reasoner)
- PerfectRef in Coq with termination proof
- Machine-checked soundness and completeness theorems
- Extraction to OCaml + benchmark comparison to Ontop/Rapid

**Target venues:**
- KR (Knowledge Representation and Reasoning) — top venue, excellent fit
- CPP (Certified Programs and Proofs) — top verified software venue
- IJCAR (Automated Reasoning) — top reasoning venue
- ITP (Interactive Theorem Proving) — top formalization venue
- ISWC (Semantic Web) — if framing as verified OWL2 QL tooling

**Novelty claim:** "First mechanically verified query rewriting algorithm; first machine-checked proof that PerfectRef is sound and complete."

---

### Paper 3 (stretch goal): Algorithm paper

**Title:** *"Optimized Query Rewriting for DL-Lite: Tighter Bounds for Restricted TBox Structures"*

**Contents:**
- Identify a structural property of real-world ontologies (bounded role depth, tree-shaped TBoxes)
- Prove polynomial rewriting for this class (vs. exponential in general)
- Implement specialized algorithm + benchmarks

**Target venues:**
- PODS (Principles of Database Systems)
- ICDT (Database Theory)
- KR

**Novelty claim:** "Tight complexity bounds for PerfectRef on [specific TBox class]."

---

## 10. Files You'll Create

```
src/
├── Logic/
│   └── DLLiteA.v                    ← DL-Lite_A syntax + semantics (Task 1)
│
├── Reasoning/
│   ├── DLLiteA_TBox.v               ← TBox consistency + subsumption (Task 2)
│   └── DLLiteA_QueryRewriting.v     ← PerfectRef algorithm (Task 2)
│
├── DLLiteA_Correctness/
│   ├── Soundness.v                  ← Soundness theorem
│   └── Completeness.v              ← Completeness theorem
│
└── Extraction/
    └── DLLiteA_Extraction.v         ← Extraction directives for DL-Lite_A

Extracted/
├── DLLiteA_Reasoner.ml              ← Auto-extracted verified reasoner
├── DLLiteA_Benchmarks.ml            ← Benchmark driver for real ontologies
└── ontologies/                      ← Parsed benchmark ontologies (LUBM, NPD, etc.)

benchmarks/
├── run_benchmarks.sh                ← Build + run script
├── results/                         ← Timing data, comparison tables
└── tools/
    └── owl_to_dllitea.ml            ← OWL parser that converts to DL-Lite_A KB format
```

---

## 11. Files to Study in the Existing Codebase

### Must read (in order)

| # | File | Why | When |
|---|------|-----|------|
| 1 | `GUIDE.md` | Best onboarding doc | Day 1 |
| 2 | `src/Logic/EL.v` | Template for your `DLLiteA.v` — how DL syntax looks in Coq | Week 3 |
| 3 | `src/Logic/ConcreteDomain.v` | `Logic_Primitives` — your types plug into this | Week 3 |
| 4 | `src/Classification/Classification.v` | How a reasoner is structured in Coq (fixpoint + rules) | Week 4 (skim) |
| 5 | `src/Extraction/Extraction.v` | How to extract your reasoner to OCaml | Week 10 |
| 6 | `Extracted/TestsMain.ml` | Where benchmarks plug in — your driver will look like this | Week 5 |
| 7 | `Extracted/Test_kbs_*.ml` | What a KB looks like as OCaml data — your parser output matches this shape | Week 5 |

### Read during thesis year

| File | Why | When |
|------|-----|------|
| `src/Correctness/Correctness.v` | How soundness + completeness proofs are structured | November |
| `src/Correctness/ChoiceInterpretation.v` | Model construction for completeness | November |
| `src/Classification/ClassificationDefinitions.v` | How invariants are defined | October |

### Avoid until needed

| File | Why avoid |
|------|-----------|
| `src/Normalization/NormalizationPartOne.v` | EL-specific, 3400 lines of dense obligations |
| `src/Normalization/NormalizationPartTwo.v` | Same — not relevant to DL-Lite_A |
| `src/Utils/*.v` | Use as needed; don't study proactively |

---

## Quick Reference Card

| Question | Answer |
|----------|--------|
| What logic am I formalizing? | DL-Lite_A (the DL behind OWL2 QL) |
| What algorithm am I implementing? | PerfectRef (Calvanese et al. 2007) |
| What language for the verified version? | Coq (then extracted to OCaml) |
| What language for the prototype? | OCaml (unverified, summer) |
| What's the correctness spec? | Soundness + completeness of query rewriting |
| What benchmark ontologies? | LUBM, NPD, UOBM |
| What do I compare against? | Ontop, Rapid, Requiem |
| Key paper? | Calvanese et al., JAIR 2007 |
| Key Coq reference in codebase? | `src/Logic/EL.v` (follow the same pattern) |
| First file to read? | `GUIDE.md` |
