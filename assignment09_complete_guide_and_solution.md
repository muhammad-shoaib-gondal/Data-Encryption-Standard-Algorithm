# Assignment 09 -- Complete Concept Guide & Detailed Solution

## CIS 570/770: Formal Language Theory

---

# PART I: BUILDING THE INTUITION -- EVERY CONCEPT YOU NEED

---

## 1. Context-Free Grammars (CFGs) -- The Foundation

### 1.1 What Is a Context-Free Grammar?

A **context-free grammar** (CFG) is a set of rules that describe how to build strings in a language. It has four components:

| Component | Symbol | Meaning |
|-----------|--------|---------|
| **Variables** (non-terminals) | Upper-case letters like S, R, F | Placeholders that get rewritten |
| **Terminals** | Lower-case letters, symbols like `a`, `c`, `;`, `{`, `}` | The actual characters in the final string |
| **Productions** (rules) | `S -> aR` | How to rewrite a variable |
| **Start symbol** | Usually `S` | Where derivation begins |

### 1.2 How Productions Work

A production `A -> XYZ` means: "wherever you see the variable A, you may replace it with the string XYZ."

**Example:** Given productions:

```
S -> aB
B -> b
B -> cB
```

We can derive:
- `S => aB => ab` (used `B -> b`)
- `S => aB => acB => acb` (used `B -> cB`, then `B -> b`)
- `S => aB => acB => accB => accb` (used `B -> cB` twice, then `B -> b`)

The **language** L(G) is the set of *all* strings of terminals you can derive from the start symbol.

### 1.3 The Special Symbol lambda (the empty string)

The symbol **lambda** (sometimes written as the Greek letter, here written `lambda`) represents the **empty string** -- a string with zero characters. A production like:

```
R -> lambda
```

means "R can be replaced by *nothing*." This is crucial because it lets parts of the grammar be *optional*.

**Example:** With rules `S -> aR` and `R -> b | lambda`:
- `S => aR => ab` (R became b)
- `S => aR => a` (R became nothing -- it vanished)

### 1.4 Derivations and Parse Trees

A **derivation** is a sequence of rewriting steps from the start symbol to a string of terminals.

- **Leftmost derivation:** always expand the leftmost variable first.
- **Rightmost derivation:** always expand the rightmost variable first.

A **parse tree** is a tree representation of a derivation:
- Root = start symbol
- Internal nodes = variables
- Leaves (read left to right) = the derived string
- Children of a node A = right-hand side of the production used to expand A

**Example:** Grammar: `S -> aR`, `R -> ;S | lambda`

Parse tree for `a;a`:

```
        S
       / \
      a   R
         / \
        ;   S
           / \
          a   R
              |
           (lambda)
```

### 1.5 Understanding the Grammar in Assignment 09

The grammar G has these productions:

```
S -> aR           (a statement begins with an assignment, followed by remaining commands)
S -> c{S}FR       (a conditional: condition c, true-branch {S}, optional false-branch F, remaining commands R)
R -> lambda       (no more commands)
R -> ;S           (semicolon followed by another statement)
F -> lambda       (no false branch)
F -> {S}          (false branch enclosed in braces)
```

**Variables:** S, R, F
**Terminals:** a, c, ;, {, }
**Start symbol:** S

The grammar models a simple imperative language:
- `a` = an assignment statement
- `c{...}{...}` = a conditional (if-then-else)
- `;` = separator between sequential commands
- `{...}` = braces around code blocks
- R = "rest of the commands" (optional continuation with `;`)
- F = "false branch" (optional else clause)

**Example string:** `c{c{a;a};a}{a}`

This represents:

```
if ... then {
    if ... then { a; a };
    a
} else { a }
```

Let us verify it belongs to L(G) by constructing a leftmost derivation:

```
S
=> c{S}FR                         (S -> c{S}FR)
=> c{c{S}FR}FR                   (S -> c{S}FR for inner S)
=> c{c{aR}FR}FR                  (S -> aR)
=> c{c{a;S}FR}FR                 (R -> ;S)
=> c{c{a;aR}FR}FR                (S -> aR)
=> c{c{a;a}FR}FR                 (R -> lambda)
=> c{c{a;a}R}FR                  (F -> lambda)
=> c{c{a;a};S}FR                 (R -> ;S)
=> c{c{a;a};aR}FR                (S -> aR)
=> c{c{a;a};a}FR                 (R -> lambda)
=> c{c{a;a};a}{S}R               (F -> {S})
=> c{c{a;a};a}{aR}R              (S -> aR)
=> c{c{a;a};a}{a}R               (R -> lambda)
=> c{c{a;a};a}{a}                (R -> lambda)
```

The string `c{c{a;a};a}{a}` is confirmed to be in L(G).

---

## 2. The FIRST Function -- "What Could a String Start With?"

### 2.1 Definition

For any string alpha of variables and/or terminals:

> **FIRST(alpha)** = the set of terminals that can appear as the **first symbol** of some string derived from alpha, plus lambda if alpha can derive the empty string.

More precisely:
- A terminal `b` is in FIRST(alpha) if alpha =>* b... (alpha can derive something starting with b)
- lambda is in FIRST(alpha) if alpha =>* lambda (alpha can derive the empty string)

### 2.2 How to Compute FIRST for a Single Variable

For each variable A, look at every production `A -> X1 X2 ... Xn`:

**Rule 1:** If `X1` is a **terminal**, add `X1` to FIRST(A).

**Rule 2:** If `X1` is a **variable**, add everything in `FIRST(X1)` (except lambda) to `FIRST(A)`.

**Rule 3:** If lambda is in FIRST(X1), then also look at X2:
- Add everything in FIRST(X2) (except lambda) to FIRST(A).
- If lambda is also in FIRST(X2), look at X3, and so on.

**Rule 4:** If lambda is in FIRST(X1), FIRST(X2), ..., FIRST(Xn) for ALL Xi (or if n=0, i.e., the production is `A -> lambda`), then add lambda to FIRST(A).

### 2.3 How to Compute FIRST for a String

For a string alpha = X1 X2 ... Xn:

1. Start with FIRST(X1) (without lambda).
2. If lambda is in FIRST(X1), also add FIRST(X2) (without lambda).
3. If lambda is in FIRST(X1) AND FIRST(X2), also add FIRST(X3) (without lambda).
4. Continue until you hit some Xi where lambda is NOT in FIRST(Xi), or you run out of symbols.
5. If lambda is in FIRST of ALL symbols X1 through Xn, then lambda is in FIRST(alpha).

### 2.4 Worked Example (Arithmetic Expressions)

Grammar (factorized for LL parsing):

```
E -> TR       R -> +E | lambda
T -> FQ       Q -> *T | lambda
F -> (E) | i | n
```

**Computing FIRST:**

| Variable | Productions | FIRST |
|----------|------------|-------|
| F | `F -> (E)`, `F -> i`, `F -> n` | { (, i, n } |
| T | `T -> FQ`, and FIRST(F) = {(, i, n}, lambda not in FIRST(F) | { (, i, n } |
| E | `E -> TR`, and FIRST(T) = {(, i, n}, lambda not in FIRST(T) | { (, i, n } |
| Q | `Q -> *T`, `Q -> lambda` | { *, lambda } |
| R | `R -> +E`, `R -> lambda` | { +, lambda } |

Note how lambda propagates: T -> FQ, and since lambda is NOT in FIRST(F), we do NOT look at Q. So FIRST(T) = FIRST(F) = {(, i, n} with no lambda.

### 2.5 Key Intuition

FIRST tells you: **"If I need to parse variable A, which input symbols could I possibly see first?"** This is essential for building a parser that decides which production to use based on the next input symbol.

---

## 3. The FOLLOW Function -- "What Could Come After a Variable?"

### 3.1 Definition

For a variable A, with S the start symbol:

> **FOLLOW(A)** = the set of terminals that can appear **immediately after** A in some derivation from S, plus $ (end-of-input marker) if A can appear at the very end.

More precisely:
- A terminal `b` is in FOLLOW(A) if S =>* ...Ab... for some strings before and after
- $ is in FOLLOW(A) if S =>* ...A (A can appear at the end of a derivation)

### 3.2 How to Compute FOLLOW

**Initialization:** Put `$` in FOLLOW(S) where S is the start symbol (because after the whole program, there is end-of-input).

**Then for every production `A -> ... B beta` (where B is a variable and beta is whatever comes after B in the right-hand side):**

**Rule 1:** Add everything in FIRST(beta) *except* lambda to FOLLOW(B).

> *Rationale:* If `A -> ...B beta`, then whatever beta can start with can follow B.

**Rule 2:** If beta is empty (B is the last symbol), OR if lambda is in FIRST(beta), then add everything in FOLLOW(A) to FOLLOW(B).

> *Rationale:* If beta can vanish (or doesn't exist), then whatever can follow A can also follow B.

**Repeat until no more changes.** (FOLLOW computation can require multiple passes because of circular dependencies.)

### 3.3 Worked Example (Arithmetic Expressions)

Grammar:

```
E -> TR       R -> +E | lambda
T -> FQ       Q -> *T | lambda
F -> (E) | i | n
```

Starting with:

```
FOLLOW(E) = { $ }   (start symbol, so $ is automatic)
```

**From `F -> (E)`:** The `)` follows E, so add `)` to FOLLOW(E). Now FOLLOW(E) = { $, ) }.

**From `E -> TR`:**
- R follows T; FIRST(R) = {+, lambda}. Add `+` to FOLLOW(T). Since lambda in FIRST(R), also add FOLLOW(E) to FOLLOW(T). So FOLLOW(T) = {+, $, )}.
- R is the last symbol in the production for E; add FOLLOW(E) to FOLLOW(R). So FOLLOW(R) = {$, )}.

**From `T -> FQ`:**
- Q follows F; FIRST(Q) = {*, lambda}. Add `*` to FOLLOW(F). Since lambda in FIRST(Q), also add FOLLOW(T) to FOLLOW(F). So FOLLOW(F) = {*, +, $, )}.
- Q is last; add FOLLOW(T) to FOLLOW(Q). So FOLLOW(Q) = {+, $, )}.

**From `R -> +E`:** E is last; add FOLLOW(R) to FOLLOW(E). FOLLOW(E) already has {$, )}.

**Final result:**

| Variable | FOLLOW |
|----------|--------|
| E | { $, ) } |
| R | { $, ) } |
| T | { +, $, ) } |
| Q | { +, $, ) } |
| F | { *, +, $, ) } |

### 3.4 Key Intuition

FOLLOW tells you: **"When a variable can produce lambda (vanish), what input symbols tell me it *should* vanish?"** Specifically, if you are trying to parse variable A and the next input symbol is in FOLLOW(A) but not in FIRST of any production for A, and A has a lambda-production, then you should apply the lambda-production.

### 3.5 Why FOLLOW Matters for Lambda-Productions

Consider `R -> ;S | lambda`. When should the parser choose `R -> lambda`? Answer: when the next input symbol is something that could legitimately follow R in the grammar. That is exactly what FOLLOW(R) tells us.

---

## 4. LL(1) Parsing Tables -- Putting FIRST and FOLLOW Together

### 4.1 What Is an LL(1) Parser?

An **LL(1) parser** is a top-down parser that:
- Reads input from **L**eft to right
- Produces a **L**eftmost derivation
- Uses **1** symbol of lookahead

It uses a **parsing table** `LL[A, t]` where:
- A is a variable (row)
- t is a terminal or $ (column)
- The entry tells which production to use when you need to expand A and the next input is t.

### 4.2 How to Build the LL(1) Parsing Table

For each production `A -> alpha`:

**Step 1:** For every terminal `t` in FIRST(alpha), put `A -> alpha` in `LL[A, t]`.

> *Reason:* If the next input could start with what alpha produces, this production is appropriate.

**Step 2:** If lambda is in FIRST(alpha) (meaning alpha can vanish), then for every symbol `t` in FOLLOW(A) (including possibly $), put `A -> alpha` in `LL[A, t]`.

> *Reason:* If alpha can produce nothing, and the next input is something that can follow A, then it is appropriate to "produce nothing" (apply the lambda-production).

### 4.3 FIRST of a String (needed for the table)

To apply Step 1, we often need FIRST of the entire right-hand side of a production, not just FIRST of its first symbol. Use the rules from Section 2.3.

**Example:** FIRST(aR) = { a } because the first symbol is terminal `a`.

**Example:** FIRST(FR) where FIRST(F) = { {, lambda } and FIRST(R) = { ;, lambda }:
- Start with FIRST(F) \ {lambda} = { { }.
- Since lambda is in FIRST(F), also include FIRST(R) \ {lambda} = { ; }.
- Since lambda is in both FIRST(F) and FIRST(R), include lambda.
- Result: FIRST(FR) = { {, ;, lambda }.

### 4.4 When Is a Grammar LL(1)?

A grammar is **LL(1)** if the parsing table has **at most one entry per cell**. If any cell has two or more entries, there is a **conflict**, and the grammar is NOT LL(1).

A grammar **cannot** be LL(1) if:
- It is **ambiguous** (same string has two parse trees).
- It has **left recursion** like `E -> E + T`.
- It has **common prefixes** like `E -> T+E | T` that haven't been factorized.

### 4.5 Worked Example: Building a Table (Arithmetic Expressions)

For the arithmetic expression grammar, let us trace a few productions:

**Production `Q -> *T`:**
- FIRST(*T) = {*} (starts with terminal *)
- Put `Q -> *T` in LL[Q, *]

**Production `Q -> lambda`:**
- FIRST(lambda) = {lambda}
- Since lambda is in FIRST, look at FOLLOW(Q) = {+, $, )}
- Put `Q -> lambda` in LL[Q, +], LL[Q, $], LL[Q, )]

No conflicts because {*} and {+, $, )} are disjoint.

### 4.6 The Parsing Table (complete for arithmetic expressions)

|   | + | * | i | n | ( | ) | $ |
|---|---|---|---|---|---|---|---|
| E |   |   | TR | TR | TR |   |   |
| R | +E |   |   |   |   | lambda | lambda |
| T |   |   | FQ | FQ | FQ |   |   |
| Q | lambda | *T |   |   |   | lambda | lambda |
| F |   |   | i | n | (E) |   |   |

---

## 5. LL(1) Parsing Algorithm -- How the Parser Runs

### 5.1 The Machinery

The LL(1) parser uses:
- A **stack** (initially contains the start symbol S, with $ underneath)
- The **input string** (with $ appended at the end)
- The **parsing table**

### 5.2 The Algorithm

Repeat:
1. Let X = top of stack, and a = next input symbol.

2. **If X is a terminal:**
   - If X == a: **match!** Pop X from the stack, advance input (consume a).
   - If X != a: **error!** The input doesn't match the grammar.

3. **If X is $:**
   - If a is also $: **accept!** Parsing is successful.
   - Otherwise: **error!**

4. **If X is a variable:**
   - Look up `LL[X, a]` in the parsing table.
   - If the entry is a production `X -> Y1 Y2 ... Yn`:
     - Pop X from the stack.
     - Push Y1, Y2, ..., Yn onto the stack **in reverse order** (so Y1 ends up on top).
     - If the production is `X -> lambda`, just pop X (push nothing).
   - If the entry is empty: **error!**

### 5.3 Detailed Trace Example (Arithmetic Grammar)

Let us parse `a+b*c` with the arithmetic grammar. The stack is shown with the top on the LEFT side.

| Step | Stack | Input | Action |
|------|-------|-------|--------|
| 1 | `E $` | `a+b*c$` | LL[E, a] = TR. Pop E, push TR. |
| 2 | `T R $` | `a+b*c$` | LL[T, a] = FQ. Pop T, push FQ. |
| 3 | `F Q R $` | `a+b*c$` | LL[F, a] = a. Pop F, push a. |
| 4 | `a Q R $` | `a+b*c$` | Match a with a. Pop a, consume a. |
| 5 | `Q R $` | `+b*c$` | LL[Q, +] = lambda. Pop Q. |
| 6 | `R $` | `+b*c$` | LL[R, +] = +E. Pop R, push +E. |
| 7 | `+ E $` | `+b*c$` | Match + with +. Pop +, consume +. |
| 8 | `E $` | `b*c$` | LL[E, b] = TR. Pop E, push TR. |
| 9 | `T R $` | `b*c$` | LL[T, b] = FQ. Pop T, push FQ. |
| 10 | `F Q R $` | `b*c$` | LL[F, b] = b. Pop F, push b. |
| 11 | `b Q R $` | `b*c$` | Match b with b. Pop b, consume b. |
| 12 | `Q R $` | `*c$` | LL[Q, *] = *T. Pop Q, push *T. |
| 13 | `* T R $` | `*c$` | Match * with *. Pop *, consume *. |
| 14 | `T R $` | `c$` | LL[T, c] = FQ. Pop T, push FQ. |
| 15 | `F Q R $` | `c$` | LL[F, c] = c. Pop F, push c. |
| 16 | `c Q R $` | `c$` | Match c with c. Pop c, consume c. |
| 17 | `Q R $` | `$` | LL[Q, $] = lambda. Pop Q. |
| 18 | `R $` | `$` | LL[R, $] = lambda. Pop R. |
| 19 | `$` | `$` | Both are $. **ACCEPT!** |

### 5.4 Key Insight: The Stack Mirrors the Parse Tree

At any point during parsing, the consumed input concatenated with the stack contents (reading top to bottom, ignoring $) gives the current **sentential form** of a leftmost derivation. Each "expand" step corresponds to one step in the leftmost derivation.

---

## 6. Determinism and Conflicts -- When LL(1) Fails

### 6.1 What Makes a Table Non-Deterministic?

If a cell `LL[A, t]` has **two or more** productions, the parser doesn't know which one to choose. This is a **conflict**.

### 6.2 Common Causes of Conflicts

**Cause 1: Overlapping FIRST sets.**
If `A -> alpha` and `A -> beta` both have terminal `t` in their FIRST sets, then LL[A, t] has two entries.

**Cause 2: A FIRST/FOLLOW overlap when lambda is involved.**
If `A -> alpha` has `t` in FIRST(alpha), and `A -> lambda` has `t` in FOLLOW(A), then LL[A, t] has two entries.

**Example of a conflict:** Suppose for some variable R with productions `R -> ;S | lambda`:
- `R -> ;S` puts an entry in LL[R, ;] (because `;` is in FIRST(;S)).
- If `;` were also in FOLLOW(R), then `R -> lambda` would also go into LL[R, ;].
- Result: LL[R, ;] has two entries => conflict => NOT LL(1).

### 6.3 Why This Matters for Assignment 09 Part 5

Part 5 asks: if we change `F -> {S}` to `F -> S`, would `;` enter FOLLOW(R)? If so, the table would have a conflict at (R, ;) because:
- `R -> ;S` says: "on seeing `;`, shift and parse a statement."
- `R -> lambda` says: "on seeing `;`, do nothing."

The parser wouldn't know which to choose. This is exactly the kind of ambiguity/non-determinism that makes a grammar not LL(1).

---

## 7. Understanding How Grammar Design Affects Parseability

### 7.1 Left Recursion Kills LL Parsing

A production like `E -> E + T` causes infinite loops in top-down parsing: the parser tries to expand E, sees E again, tries to expand it, etc.

**Solution:** Rewrite using right recursion or factorize:
```
E -> T R
R -> + T R | lambda
```

### 7.2 Common Prefixes Need Factoring

Productions `A -> alpha beta1 | alpha beta2` cause conflicts because both start with alpha.

**Solution:** Factor out the common prefix:
```
A -> alpha B
B -> beta1 | beta2
```

### 7.3 The Grammar in Assignment 09 Is Already Well-Designed

The grammar:
```
S -> aR | c{S}FR
R -> lambda | ;S
F -> lambda | {S}
```

has no left recursion and no unfactored common prefixes. The two productions for each variable start with *different* terminals (or one of them is lambda). This is a strong hint that it IS LL(1).

---

# PART II: SOLVING ASSIGNMENT 09 -- COMPLETE DETAILED SOLUTION

---

## The Grammar

```
S -> aR           (P1)
S -> c{S}FR       (P2)
R -> lambda       (P3)
R -> ;S           (P4)
F -> lambda       (P5)
F -> {S}          (P6)
```

**Variables:** S, R, F
**Terminals:** a, c, ;, {, }
**Start symbol:** S

---

## Problem 1 (3 points): Compute FIRST(S), FIRST(R), FIRST(F)

### FIRST(S)

Look at S-productions:

- `S -> aR`: The first symbol is terminal `a`. So **a is in FIRST(S)**.
- `S -> c{S}FR`: The first symbol is terminal `c`. So **c is in FIRST(S)**.
- Neither production produces lambda (both start with a terminal), so lambda is NOT in FIRST(S).

> **FIRST(S) = { a, c }**

### FIRST(R)

Look at R-productions:

- `R -> lambda`: R can produce the empty string. So **lambda is in FIRST(R)**.
- `R -> ;S`: The first symbol is terminal `;`. So **; is in FIRST(R)**.

> **FIRST(R) = { ;, lambda }**

### FIRST(F)

Look at F-productions:

- `F -> lambda`: F can produce the empty string. So **lambda is in FIRST(F)**.
- `F -> {S}`: The first symbol is terminal `{`. So **{ is in FIRST(F)**.

> **FIRST(F) = { {, lambda }**

### Summary Table

| Variable | FIRST |
|----------|-------|
| S | { a, c } |
| R | { ;, lambda } |
| F | { {, lambda } |

---

## Problem 2 (6 points): Compute FOLLOW(S), FOLLOW(R), FOLLOW(F) -- Detailed Justification

### Initialization

S is the start symbol, so by definition:

> **$ is in FOLLOW(S).**

**Starting state:** FOLLOW(S) = { $ }, FOLLOW(R) = { }, FOLLOW(F) = { }

### Systematic Analysis of Each Production

We examine every production and for each variable appearing on the right-hand side, we determine what can follow it.

---

#### Production P1: `S -> aR`

Right-hand side: `a R`

**Variable R in position: `a [R]`** (R is the last symbol)

- R is at the end of the RHS, so by Rule 2: everything in FOLLOW(S) goes into FOLLOW(R).

> **FOLLOW(S) is a subset of FOLLOW(R).** In particular, $ (which is in FOLLOW(S)) is in FOLLOW(R).

---

#### Production P2: `S -> c{S}FR`

Right-hand side: `c { S } F R`

**Variable S in position: `c { [S] } F R`** (S is followed by `}FR`)

- The string after S is `}FR`, whose FIRST starts with the terminal `}`.
- By Rule 1: add `}` to FOLLOW(S).

> **} is in FOLLOW(S)** because in derivations using `S -> c{S}FR`, the `}` immediately follows S.

**Variable F in position: `c { S } [F] R`** (F is followed by `R`)

- The string after F is `R`, and FIRST(R) = { ;, lambda }.
- By Rule 1: add everything in FIRST(R) except lambda to FOLLOW(F). So add `;`.

> **; is in FOLLOW(F)** because F is followed by R, and R can start with `;`.

- Since lambda is in FIRST(R), and R is the last symbol on the RHS: by Rule 2, everything in FOLLOW(S) goes into FOLLOW(F).

> **FOLLOW(S) is a subset of FOLLOW(F).** So $ and } are in FOLLOW(F).

**Variable R in position: `c { S } F [R]`** (R is the last symbol)

- R is at the end of the RHS, so by Rule 2: everything in FOLLOW(S) goes into FOLLOW(R).

> **FOLLOW(S) is a subset of FOLLOW(R).** (This was already established from P1.)

---

#### Production P3: `R -> lambda`

No variables on the RHS. Nothing to learn.

---

#### Production P4: `R -> ;S`

Right-hand side: `; S`

**Variable S in position: `; [S]`** (S is the last symbol)

- S is at the end of the RHS, so by Rule 2: everything in FOLLOW(R) goes into FOLLOW(S).

> **FOLLOW(R) is a subset of FOLLOW(S).**

---

#### Production P5: `F -> lambda`

No variables on the RHS. Nothing to learn.

---

#### Production P6: `F -> {S}`

Right-hand side: `{ S }`

**Variable S in position: `{ [S] }`** (S is followed by `}`)

- The string after S is `}`, a terminal.
- By Rule 1: add `}` to FOLLOW(S).

> **} is in FOLLOW(S)** (already established from P2).

---

### Collecting the Subset Relationships

From our analysis, we have these dependency relationships:

1. **FOLLOW(S) is a subset of FOLLOW(R)** (from P1 and P2: R is the last symbol in both S-productions)
2. **FOLLOW(R) is a subset of FOLLOW(S)** (from P4: S is the last symbol in `R -> ;S`)
3. **FOLLOW(S) is a subset of FOLLOW(F)** (from P2: F is followed by R, and lambda is in FIRST(R))

Relationships 1 and 2 mean that FOLLOW(S) = FOLLOW(R) -- they must contain exactly the same elements.

### Fixed-Point Propagation

**After initial analysis:**
- FOLLOW(S) = { $, } }
- FOLLOW(R) = { $ } (from the subset relationship with FOLLOW(S))
- FOLLOW(F) = { ; } (direct), plus FOLLOW(S) = { $, } }

**Propagation round 1:**

From relationship 1 (FOLLOW(S) subset of FOLLOW(R)):
- FOLLOW(R) gains `}`. Now FOLLOW(R) = { $, } }.

From relationship 2 (FOLLOW(R) subset of FOLLOW(S)):
- FOLLOW(S) already has everything in FOLLOW(R). No change.

From relationship 3 (FOLLOW(S) subset of FOLLOW(F)):
- FOLLOW(F) gains `}` and `$`. Now FOLLOW(F) = { ;, }, $ }.

**Propagation round 2:** No further changes. Fixed point reached.

### Final Results

| Variable | FOLLOW | Justification |
|----------|--------|---------------|
| **S** | **{ }, $ }** | $ because S is the start symbol. } from P2 (S is followed by `}` in `c{S}FR`) and P6 (S is followed by `}` in `{S}`). |
| **R** | **{ }, $ }** | Equal to FOLLOW(S) because (i) R is the last symbol in both S-productions so FOLLOW(S) is a subset of FOLLOW(R), and (ii) S is the last symbol in `R -> ;S` so FOLLOW(R) is a subset of FOLLOW(S). |
| **F** | **{ ;, }, $ }** | ; because F is followed by R in P2, and ; is in FIRST(R). } and $ because F is followed by R, lambda is in FIRST(R), so FOLLOW(S) is a subset of FOLLOW(F), and FOLLOW(S) = { }, $ }. |

### Detailed Element-by-Element Justification

**FOLLOW(S):**
- **$**: S is the start symbol. By definition, $ is in FOLLOW(S).
- **}**: In production `S -> c{S}FR`, the variable S on the RHS is directly followed by `}`. Also confirmed by `F -> {S}` where S is followed by `}`.

**FOLLOW(R):**
- **$**: From P1 (`S -> aR`), R is the last symbol, so FOLLOW(S) is a subset of FOLLOW(R). Since $ is in FOLLOW(S), $ is in FOLLOW(R). Concretely: `S =>* ... aR` at the end of the whole input, so $ can follow R.
- **}**: Similarly, from P1 (`S -> aR`) and P2 (`S -> c{S}FR`), FOLLOW(S) is a subset of FOLLOW(R). Since } is in FOLLOW(S), } is in FOLLOW(R). Concretely: consider `c{aR}...` -- the `}` follows R.

**FOLLOW(F):**
- **;**: From P2 (`S -> c{S}FR`), F is followed by R, and `;` is in FIRST(R). Concretely: `c{...};...` -- the semicolon can follow F (when R -> ;S).
- **}**: From P2, F is followed by R, lambda is in FIRST(R), so FOLLOW(S) is a subset of FOLLOW(F). Since `}` is in FOLLOW(S), `}` is in FOLLOW(F). Concretely: consider `c{c{...}F_inner R_inner}F_outer R_outer` -- after F_inner comes R_inner which may be lambda, so `}` follows.
- **$**: Same reasoning as `}`. Since `$` is in FOLLOW(S), it is in FOLLOW(F). Concretely: consider the string `c{a}` at the end of the input -- this is S -> c{S}FR where S=a(R=lambda), F=lambda, R=lambda, and F (which is lambda here) is followed by R (which is lambda), which is followed by $.

---

## Problem 3 (8 points): Construct the LL(1) Parsing Table

### The Method

For each production `A -> alpha`:
1. For each terminal `t` in FIRST(alpha), put `A -> alpha` in cell [A, t].
2. If lambda is in FIRST(alpha), then for each symbol `t` in FOLLOW(A), put `A -> alpha` in cell [A, t].

### Computing FIRST of Each Right-Hand Side

| Production | RHS | FIRST(RHS) | Reasoning |
|------------|-----|------------|-----------|
| P1: S -> aR | aR | { a } | Starts with terminal `a` |
| P2: S -> c{S}FR | c{S}FR | { c } | Starts with terminal `c` |
| P3: R -> lambda | lambda | { lambda } | Is the empty string |
| P4: R -> ;S | ;S | { ; } | Starts with terminal `;` |
| P5: F -> lambda | lambda | { lambda } | Is the empty string |
| P6: F -> {S} | {S} | { { } | Starts with terminal `{` |

### Production-by-Production Table Construction

**P1: `S -> aR`**
- FIRST(aR) = { a }.
- Put `S -> aR` in **[S, a]**.

**P2: `S -> c{S}FR`**
- FIRST(c{S}FR) = { c }.
- Put `S -> c{S}FR` in **[S, c]**.

**P3: `R -> lambda`**
- FIRST(lambda) = { lambda }.
- Lambda is present, so use FOLLOW(R) = { }, $ }.
- Put `R -> lambda` in **[R, }]** and **[R, $]**.

**P4: `R -> ;S`**
- FIRST(;S) = { ; }.
- Put `R -> ;S` in **[R, ;]**.

**P5: `F -> lambda`**
- FIRST(lambda) = { lambda }.
- Lambda is present, so use FOLLOW(F) = { ;, }, $ }.
- Put `F -> lambda` in **[F, ;]**, **[F, }]**, and **[F, $]**.

**P6: `F -> {S}`**
- FIRST({S}) = { { }.
- Put `F -> {S}` in **[F, {]**.

### The Complete LL(1) Parsing Table

|       | **a**       | **c**         | **;**       | **{**     | **}**       | **$**       |
|-------|-------------|---------------|-------------|-----------|-------------|-------------|
| **S** | S -> aR     | S -> c{S}FR   |             |           |             |             |
| **R** |             |               | R -> ;S     |           | R -> lambda | R -> lambda |
| **F** |             |               | F -> lambda | F -> {S}  | F -> lambda | F -> lambda |

### Verification: The Grammar IS LL(1)

Check every cell for conflicts:

- **[S, a]:** Only `S -> aR`. The sets { a } and { c } are disjoint, so the two S-productions never compete.
- **[S, c]:** Only `S -> c{S}FR`.
- **[R, ;]:** Only `R -> ;S`. The key question: is `;` in FOLLOW(R)? No! FOLLOW(R) = { }, $ }, and `;` is not in it. So `R -> lambda` does not compete.
- **[R, }]:** Only `R -> lambda`. The set { ; } does not contain `}`, so `R -> ;S` does not compete.
- **[R, $]:** Only `R -> lambda`. Same reasoning.
- **[F, ;]:** Only `F -> lambda`. The set { { } does not contain `;`, so `F -> {S}` does not compete.
- **[F, {]:** Only `F -> {S}`. The set { ;, }, $ } does not contain `{`, so `F -> lambda` does not compete.
- **[F, }]:** Only `F -> lambda`. Same as [F, ;] reasoning.
- **[F, $]:** Only `F -> lambda`.

**No cell has two entries. The grammar is LL(1).**

---

## Problem 4 (10 points): Simulate LL(1) Parsing of `c{c{a;a};a}{a}`

### Setup

- **Input string:** `c { c { a ; a } ; a } { a } $`
  - (14 terminal symbols plus $)
- **Initial stack:** `S $` (S on top, $ on bottom)
- **Parsing table:** as constructed in Problem 3

### Convention

- Stack is written with the **top on the left**.
- We abbreviate productions: P1 = `S -> aR`, P2 = `S -> c{S}FR`, P3 = `R -> lambda`, P4 = `R -> ;S`, P5 = `F -> lambda`, P6 = `F -> {S}`.

### Complete Simulation

| Step | Stack | Remaining Input | Action |
|------|-------|-----------------|--------|
| 1 | `S $` | `c{c{a;a};a}{a}$` | LL[S, c] = P2. Pop S, push `c { S } F R`. |
| 2 | `c { S } F R $` | `c{c{a;a};a}{a}$` | Top = c, input = c. **Match.** Pop c, consume c. |
| 3 | `{ S } F R $` | `{c{a;a};a}{a}$` | Top = {, input = {. **Match.** Pop {, consume {. |
| 4 | `S } F R $` | `c{a;a};a}{a}$` | LL[S, c] = P2. Pop S, push `c { S } F R`. |
| 5 | `c { S } F R } F R $` | `c{a;a};a}{a}$` | Top = c, input = c. **Match.** Pop c, consume c. |
| 6 | `{ S } F R } F R $` | `{a;a};a}{a}$` | Top = {, input = {. **Match.** Pop {, consume {. |
| 7 | `S } F R } F R $` | `a;a};a}{a}$` | LL[S, a] = P1. Pop S, push `a R`. |
| 8 | `a R } F R } F R $` | `a;a};a}{a}$` | Top = a, input = a. **Match.** Pop a, consume a. |
| 9 | `R } F R } F R $` | `;a};a}{a}$` | LL[R, ;] = P4. Pop R, push `; S`. |
| 10 | `; S } F R } F R $` | `;a};a}{a}$` | Top = ;, input = ;. **Match.** Pop ;, consume ;. |
| 11 | `S } F R } F R $` | `a};a}{a}$` | LL[S, a] = P1. Pop S, push `a R`. |
| 12 | `a R } F R } F R $` | `a};a}{a}$` | Top = a, input = a. **Match.** Pop a, consume a. |
| 13 | `R } F R } F R $` | `};a}{a}$` | LL[R, }] = P3. Pop R (R -> lambda, push nothing). |
| 14 | `} F R } F R $` | `};a}{a}$` | Top = }, input = }. **Match.** Pop }, consume }. |
| 15 | `F R } F R $` | `;a}{a}$` | LL[F, ;] = P5. Pop F (F -> lambda, push nothing). |
| 16 | `R } F R $` | `;a}{a}$` | LL[R, ;] = P4. Pop R, push `; S`. |
| 17 | `; S } F R $` | `;a}{a}$` | Top = ;, input = ;. **Match.** Pop ;, consume ;. |
| 18 | `S } F R $` | `a}{a}$` | LL[S, a] = P1. Pop S, push `a R`. |
| 19 | `a R } F R $` | `a}{a}$` | Top = a, input = a. **Match.** Pop a, consume a. |
| 20 | `R } F R $` | `}{a}$` | LL[R, }] = P3. Pop R (R -> lambda). |
| 21 | `} F R $` | `}{a}$` | Top = }, input = }. **Match.** Pop }, consume }. |
| 22 | `F R $` | `{a}$` | LL[F, {] = P6. Pop F, push `{ S }`. |
| 23 | `{ S } R $` | `{a}$` | Top = {, input = {. **Match.** Pop {, consume {. |
| 24 | `S } R $` | `a}$` | LL[S, a] = P1. Pop S, push `a R`. |
| 25 | `a R } R $` | `a}$` | Top = a, input = a. **Match.** Pop a, consume a. |
| 26 | `R } R $` | `}$` | LL[R, }] = P3. Pop R (R -> lambda). |
| 27 | `} R $` | `}$` | Top = }, input = }. **Match.** Pop }, consume }. |
| 28 | `R $` | `$` | LL[R, $] = P3. Pop R (R -> lambda). |
| 29 | `$` | `$` | Top = $, input = $. **ACCEPT!** |

### Corresponding Leftmost Derivation

Each "expand" step (where we replace a variable using the parsing table) corresponds to one step of the leftmost derivation. Reading off the productions used:

```
S
=> c{S}FR                                  (step 1: P2)
=> c{c{S}FR}FR                             (step 4: P2)
=> c{c{aR}FR}FR                            (step 7: P1)
=> c{c{a;S}FR}FR                           (step 9: P4)
=> c{c{a;aR}FR}FR                          (step 11: P1)
=> c{c{a;a}FR}FR                           (step 13: P3, R -> lambda)
=> c{c{a;a}R}FR                            (step 15: P5, F -> lambda)
=> c{c{a;a};S}FR                           (step 16: P4)
=> c{c{a;a};aR}FR                          (step 18: P1)
=> c{c{a;a};a}FR                           (step 20: P3, R -> lambda)
=> c{c{a;a};a}{S}R                         (step 22: P6)
=> c{c{a;a};a}{aR}R                        (step 24: P1)
=> c{c{a;a};a}{a}R                         (step 26: P3, R -> lambda)
=> c{c{a;a};a}{a}                          (step 28: P3, R -> lambda)
```

The string `c{c{a;a};a}{a}` is accepted.

---

## Problem 5 (3 points): What Happens if We Replace `F -> {S}` with `F -> S`?

### The Modified Grammar

```
S -> aR           (P1)
S -> c{S}FR       (P2)
R -> lambda       (P3)
R -> ;S           (P4)
F -> lambda       (P5)
F -> S            (P6')  <-- MODIFIED
```

### Claim: `;` would be in FOLLOW(R)

We need to show that with the modified grammar, `;` enters FOLLOW(R).

**Argument:**

From production P2: `S -> c{S}FR`.

Consider the variable R at the end. R is the last symbol, so FOLLOW(S) is a subset of FOLLOW(R) (same as before).

Now consider the variable F in `c{S}FR`. F is followed by R. Since lambda is in FIRST(R), we have FOLLOW(S) is a subset of FOLLOW(F) (same as before).

Now, **the key change**: In the modified production P6', `F -> S`, the variable S is the last (and only) symbol on the RHS. Therefore:

> Everything in FOLLOW(F) is in FOLLOW(S).

And from production P1 (`S -> aR`), R is the last symbol, so:

> Everything in FOLLOW(S) is in FOLLOW(R).

Now let us trace the chain:

1. From P2, F is followed by R in `c{S}FR`, and `;` is in FIRST(R).
   Therefore: **; is in FOLLOW(F)**.

2. From P6' (`F -> S`), S is last, so FOLLOW(F) is a subset of FOLLOW(S).
   Therefore: **; is in FOLLOW(S)**.

3. From P1 (`S -> aR`), R is last, so FOLLOW(S) is a subset of FOLLOW(R).
   Therefore: **; is in FOLLOW(R)**.

The chain is: `;` in FOLLOW(F) --> `;` in FOLLOW(S) --> `;` in FOLLOW(R).

### Why this makes the LL(1) table non-deterministic

With `;` in FOLLOW(R), the table entry **[R, ;]** would contain TWO productions:

1. **`R -> ;S`** -- because `;` is in FIRST(;S) = { ; }.
2. **`R -> lambda`** -- because `;` is now in FOLLOW(R), and we place `R -> lambda` in [R, t] for every t in FOLLOW(R).

Two entries in one cell means a **conflict**. The parser, upon seeing `;` with R on top of the stack, would not know whether to:
- **Apply `R -> ;S`:** consume the semicolon and parse another statement, or
- **Apply `R -> lambda`:** do nothing and let the semicolon be handled by something else (as part of a higher-level structure).

This conflict makes the modified grammar **not LL(1)**.

### Intuition for Why This Happens

In the original grammar, `F -> {S}` means the false branch is always wrapped in braces. The `{` clearly signals "here comes a false branch," and a `;` clearly signals "here come more commands" (via R). There is no ambiguity.

With `F -> S`, the false branch is just a bare statement. Now when the parser sees `;`, it cannot tell: is this semicolon part of the false branch (an F that expanded to S, which contains R -> ;S)? Or does the false branch end here (F -> lambda) and the semicolon belongs to the outer R? The braces were serving as *delimiters* that resolved this ambiguity.

---

# PART III: QUICK REFERENCE SUMMARY

## Formulas at a Glance

### FIRST Rules

For `A -> X1 X2 ... Xn`:
- Add FIRST(X1) \ {lambda} to FIRST(A)
- If lambda in FIRST(X1): also add FIRST(X2) \ {lambda}
- Continue until you find Xi with lambda not in FIRST(Xi)
- If lambda in FIRST(Xi) for ALL i: add lambda to FIRST(A)

### FOLLOW Rules

1. Put $ in FOLLOW(start symbol).
2. For `A -> alpha B beta`:
   - Add FIRST(beta) \ {lambda} to FOLLOW(B)
   - If lambda in FIRST(beta) or beta is empty: add FOLLOW(A) to FOLLOW(B)
3. Repeat until stable (fixed point).

### LL(1) Table Construction

For each production `A -> alpha`:
- For each terminal t in FIRST(alpha): put `A -> alpha` in [A, t]
- If lambda in FIRST(alpha): for each t in FOLLOW(A), put `A -> alpha` in [A, t]

### LL(1) Condition

No cell has more than one entry, which requires:
- For two productions `A -> alpha | beta`:
  - FIRST(alpha) and FIRST(beta) are disjoint (ignoring lambda)
  - If lambda in FIRST(alpha), then FIRST(beta) and FOLLOW(A) are disjoint
  - At most one of alpha, beta can derive lambda

## Assignment 09 Answers at a Glance

| Problem | Answer |
|---------|--------|
| 1. FIRST(S) | { a, c } |
| 1. FIRST(R) | { ;, lambda } |
| 1. FIRST(F) | { {, lambda } |
| 2. FOLLOW(S) | { }, $ } |
| 2. FOLLOW(R) | { }, $ } |
| 2. FOLLOW(F) | { ;, }, $ } |
| 3. LL(1) table | See table in Problem 3 (no conflicts) |
| 4. Parse trace | 29-step simulation (see Problem 4) |
| 5. Modified grammar | ; enters FOLLOW(R) via chain F->S->R, causing conflict at [R, ;] |
