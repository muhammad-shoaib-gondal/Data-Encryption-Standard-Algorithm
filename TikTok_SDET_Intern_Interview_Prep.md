# TikTok SDET Intern — Global E‑Commerce (Seattle, Summer 2026)
## The Only Document You Need Before Your Interview

> Role: Software Development Engineer in Test (SDET) Intern, Global E‑Commerce — TikTok / ByteDance, Seattle. Job code A204374A. Compensation $33.25/hr, 12‑week summer internship.

This doc compresses the role description, what TikTok actually asks at the interview (based on 2025 and 2026 Glassdoor / Medium / Dev.to / LeetCode‑discuss writeups), and the exact technical + behavioral material you need to revise. Read it top to bottom once, then re‑skim the **"Cheat Sheets"** sections the day before.

---

## 0. TL;DR — If You Only Have 1 Hour

1. **Know the team.** TikTok Global E‑Commerce = TikTok Shop. Three customer surfaces (buyer / seller / creator) + a SaaS backend, on Android, iOS, web frontend, and server. You'll test all of them.
2. **OA is real.** Most candidates get a HackerRank / CodeSignal assessment: **~5 MCQs on CS fundamentals + 2 coding problems (medium, sometimes one hard)** in roughly 90–110 minutes. Some strong resumes get the OA waived and go straight to technicals.
3. **2 (sometimes 3) technical rounds**, 45–60 min each, on Lark / Zoom / CoderPad. Structure per round: ~5 min intro → 10–15 min project / resume deep‑dive → 25–35 min coding (often medium LeetCode with follow‑ups) → 5–10 min testing / system / Q&A.
4. **For SDET specifically:** expect a **"how would you test X" question** (login, comments, a checkout flow, an API). Use a structured framework (functional → boundary → negative → performance → security → compatibility → recoverability). Also expect **"write unit tests for the code you just wrote"**.
5. **Languages to be fluent in:** Python or Java is safest. TikTok lists Python/Java/Go/C++/Objective‑C as acceptable. Pick **one** and own it.
6. **Behavioral = ByteStyles.** Be ready with STAR stories for: *Always Day 1*, *Aim for the Highest*, *Be Grounded and Courageous*, *Be Open and Humble*, *Be Candid and Clear*, *Diversity & Inclusion*.
7. **Communicate constantly.** TikTok interviewers explicitly say they evaluate communication and problem‑solving process, not just whether you AC the problem.

---

## 1. The Role in Plain English

You will be a quality / test engineer who **writes code** to validate the TikTok Shop product. From the JD plus the public USDS variant of the same role:

- Buyer side, seller side, creator side, and the e‑commerce SaaS backend all need testing. Coverage spans **Android, iOS, web frontend, and server**.
- You design test plans from the PRD and the tech spec, execute them, file and track defects, and root‑cause failures.
- You write **automation**: functional, regression, performance, and stress test suites.
- You build **internal tooling / frameworks / platforms** that make the dev + QA team faster.
- You participate in **PRD review and architectural design review** — that means you have to read product specs and push back on testability, edge cases, and risk.
- You join the on‑call/quality loop: continuously analyze online and offline issues and improve the system.

What this means for the interview: they want a hybrid mindset — *engineer who codes* + *tester who breaks things*. Plain "manual QA" answers will fail.

### What TikTok Shop actually does (so you can sound informed)
- Discovery and impulse purchase tied to short video and livestream.
- Three sides of the marketplace: **buyers, sellers (merchants), creators (affiliates)**.
- Key product areas in 2026: **GMV Max** (ML‑driven ad campaign optimization), **FBT (Fulfilled by TikTok)** (TikTok‑run logistics / 2‑day delivery / 15 US warehouses), **countdown bidding** (live auction), **shoppable photos**, listing risk / governance, search and discovery.
- Headline stat: TikTok Shop says US small‑seller sales grew ~66% in 2025; 64% of consumers go to TikTok Shop first to discover new products.
- Pain points testers care about: listing safety / fraud, payment correctness, livestream latency, recommendation correctness, returns / refunds, cross‑border tax & currency, mobile performance, app stability.

If asked **"How would you test TikTok Shop?"**, anchor on those concrete areas — don't speak in generalities.

---

## 2. Interview Process — What to Expect

Based on 2025–2026 writeups for TikTok intern roles (SWE, SDET, ML) and the JD:

| Stage | Format | Duration | What's tested |
|---|---|---|---|
| Resume screen | Recruiter | — | Fit, GPA, prior internships, projects |
| Online Assessment (sometimes waived) | HackerRank or CodeSignal | 90–110 min | ~5 MCQs (CS fundamentals) + 2 coding (1 medium + 1 medium/hard) |
| Tech 1 | Video (Lark / Zoom / CoderPad) | 45–60 min | Coding + light project deep‑dive + sometimes unit tests |
| Tech 2 | Video | 60 min | Coding (harder / with follow‑ups) + project deep‑dive + scenario testing + light system design |
| Tech 3 (only some candidates) | Video | 60 min | Scenario / business / system / testing strategy |
| HR / Behavioral | Video | 30–45 min | ByteStyles, motivation, availability, comp |

End‑to‑end timeline: ~3–8 weeks. There can be 1–2 week gaps between rounds. That is normal. Do not interpret silence as rejection.

**Tools:** Coding is usually in a plain editor (no autocomplete, no syntax highlighting). Practice writing in a basic text box, not your IDE.

**Language note:** Most rounds are in English. Roles that interface with Beijing teams occasionally include a Chinese‑language interviewer for native speakers — for a US intern role you should plan on English only.

---

## 3. The Online Assessment (OA) — Detail

### 3.1 Format you should rehearse
- **5 multiple choice questions** on CS fundamentals (Databases, OS, Networking, Data Structures).
- **2 coding problems** in LeetCode‑style sandbox. Common combos seen in 2024–2026:
  - 1 medium array/string + 1 medium binary search / hashmap.
  - 1 medium simulation + 1 medium/hard graph (BFS/DFS).
  - 1 medium DP + 1 medium tree.
- Time: 90–110 minutes total.
- Some TikTok OAs in 2026 are reported as "low to medium difficulty, classic simulation + arrays". But you should prep for the harder bar in case.

### 3.2 MCQ topics that show up
Memorize each of these bullets:

**Networking**
- OSI model layers (know L3 IP, L4 TCP/UDP, L7 HTTP).
- TCP vs UDP: TCP reliable, ordered, flow & congestion control, 3‑way handshake (SYN, SYN‑ACK, ACK); UDP best effort, lower overhead.
- HTTP vs HTTPS: HTTPS = HTTP over TLS. TLS handshake basics (cert, session key).
- HTTP verbs: GET (safe, idempotent, cacheable), POST (not idempotent), PUT (idempotent replace), PATCH (partial), DELETE (idempotent).
- HTTP status codes: 2xx success, 3xx redirect, 4xx client (400 bad req, 401 unauth, 403 forbidden, 404, 409 conflict, 429 rate limit), 5xx server (500, 502, 503, 504).
- DNS, what each record (A, AAAA, CNAME, MX) does.

**Operating Systems**
- Process vs thread (process = own memory; thread = shared memory in same process).
- Concurrency primitives: mutex, semaphore, monitor, condition variable.
- Deadlock 4 conditions: mutual exclusion, hold & wait, no preemption, circular wait. Prevention strategies.
- Scheduling: FCFS, SJF, Round Robin, Priority, Multilevel feedback.
- Virtual memory, paging, page fault, TLB, segmentation.
- IPC: pipes, message queues, shared memory, sockets.

**Databases**
- ACID vs BASE.
- Normal forms 1NF / 2NF / 3NF / BCNF (just be able to recognize violations).
- Indexes: B‑tree vs hash; clustered vs non‑clustered; covering index. Trade‑off: faster read, slower write, more storage.
- Transactions and isolation levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable. Phenomena: dirty read, non‑repeatable read, phantom read.
- SQL: joins (inner, left, right, full, cross, self), `GROUP BY`, `HAVING`, window functions (`ROW_NUMBER`, `RANK`).
- CAP theorem: pick 2 of consistency / availability / partition tolerance under network partition. Most distributed DBs are AP or CP.
- Cache strategies: cache‑aside, read‑through, write‑through, write‑back. Failures to know: cache breakdown (hot key expires), cache penetration (no value exists), cache avalanche (many keys expire together).

**Data Structures / Algorithms**
- Big‑O of common ops on array, linked list, stack, queue, deque, hash map, hash set, heap, BST, balanced BST, trie.
- Sorting: quick (avg n log n, worst n^2), merge (n log n stable), heap (n log n), counting / radix (linear under constraints).
- Graph traversal: BFS uses queue (shortest path in unweighted); DFS uses stack/recursion (path / cycle / topo).
- Recursion vs iteration; memoization vs tabulation.

### 3.3 Coding problems — patterns that have shown up
Practice 2–3 problems in each pattern. These are the ones that recur in TikTok / ByteDance OAs and intern interviews:

- **Array / Two pointers / Sliding window**: Longest substring without repeating chars, Container With Most Water, Trapping Rain Water, Minimum Window Substring, Subarray Sum Equals K, 3Sum.
- **HashMap / set**: Group Anagrams, Two Sum, Longest Consecutive Sequence, LRU Cache.
- **Binary search (including "binary search on answer")**: Search in Rotated Sorted Array, Find Min in Rotated Sorted Array, Koko Eating Bananas, Split Array Largest Sum, Median of Two Sorted Arrays.
- **Binary tree**: Level Order Traversal (BFS), Right Side View, Lowest Common Ancestor, Validate BST, Diameter, Serialize/Deserialize Binary Tree, Binary Tree Maximum Path Sum.
- **Graph (BFS/DFS)**: Number of Islands, Clone Graph, Course Schedule I/II (topo sort), Word Ladder, Pacific Atlantic Water Flow, Shortest Bridge.
- **Heap / PQ**: Top K Frequent Elements, Kth Largest in Stream, Merge K Sorted Lists, Find Median From Data Stream.
- **Intervals**: Merge Intervals, Insert Interval, Meeting Rooms II, Non‑Overlapping Intervals.
- **DP (medium)**: House Robber, Coin Change, Longest Increasing Subsequence, Edit Distance, Unique Paths, Word Break, Decode Ways, Longest Palindromic Substring.
- **Design**: LRU Cache, LFU Cache, Time Based Key‑Value Store (LC 981 — confirmed asked at TikTok), Twitter / News Feed (intern‑lite).
- **Simulation**: Spiral Matrix, Game of Life, Rotate Image. (TikTok 2026 OA had a hollow square pattern and a round‑trip time simulation — simulation is in scope.)

> Reported real TikTok question (2026 NG round): **LeetCode 981 — Time Based Key‑Value Store**. Make sure you can write this end‑to‑end with binary search.

### 3.4 OA tactics
- Read all problems first, do easy → hard.
- Submit early to use sample test cases; iterate.
- Don't get stuck on one MCQ; mark and move.
- For coding: dry‑run on a small input before submitting. Watch off‑by‑one on intervals and binary search.

---

## 4. Technical Round Anatomy — What Actually Happens

Each round is ~45–60 min. The recurring shape from 2025–2026 candidate writeups:

```
00:00–05:00   Introductions, "walk me through your resume"
05:00–20:00   Deep dive on ONE project on your resume
20:00–45:00   1 (sometimes 2) coding problems with follow-ups
45:00–55:00   Either: write unit tests for your code  |  scenario test design  |  mini system design  |  CS fundamentals rapid-fire
55:00–60:00   Your questions for the interviewer
```

### 4.1 Project deep dive — answer like a senior, not a student
Pick **one project** (ideally the most recent and most relevant to e‑commerce / backend / testing) and rehearse answers to:

- One‑minute elevator pitch: what, why, your role, the outcome.
- Architecture diagram you can sketch (boxes + arrows) in 60 seconds.
- "Why did you pick X over Y?" for every major component (language, framework, DB, queue, cache, deployment).
- What were the bottlenecks? How did you measure? (Latency numbers, QPS, memory, error rate.)
- Trade‑offs you consciously made.
- What would you do differently with hindsight?
- How would you scale this 10x? 100x?
- How did you **test** it? Unit / integration / e2e split, what coverage, what was flaky and how did you fix it?
- If asked "how would you make this production‑grade?" think: observability (logs, metrics, traces), alerting, rollback strategy, feature flags, on‑call runbook.

For an SDET interview, **always** end with "and here is how I tested it / would test it". That's your differentiator.

### 4.2 Coding round — execution checklist
For every coding problem, in this order:

1. **Restate** the problem in your own words. Confirm input/output and constraints.
2. **Clarify** edge cases: empty input, single element, duplicates, negatives, overflow, max sizes. (Interviewers explicitly grade this.)
3. **Brute force first**, name its complexity. Then propose the optimized idea before coding.
4. **Confirm approach** with the interviewer ("Sound good? Should I start coding?") — don't silently start.
5. **Code** while narrating. Use meaningful variable names. Keep functions small.
6. **Trace** through a small example by hand to verify.
7. **State complexity** (time and space) at the end.
8. **Follow‑ups** to expect: "What if N is 10^9?", "What if input is a stream?", "What if duplicates?", "Optimize space to O(1).", "Now make it thread‑safe.", "How would you unit‑test this?"

### 4.3 Unit testing your own code — almost always asked for SDET
After you finish coding, expect: *"Now write tests for it."* What good looks like:

- Group tests by: **happy path**, **boundary**, **negative / error**, **idempotency / repeatability**.
- For a function like `int[] twoSum(int[] nums, int target)` your test list:
  - happy path with one valid pair
  - multiple valid pairs → which to return per spec
  - duplicates (`[3,3]`, target 6)
  - target requires same index twice → not allowed
  - empty array
  - single element
  - negatives
  - integer overflow (`Integer.MAX_VALUE + 1`)
  - very large N
  - null input
- Mention you'd use parameterized tests (pytest `@pytest.mark.parametrize` / JUnit `@ParameterizedTest`) to keep it DRY.
- Mention assertions other than equality: throws, time bound, ordering, set equality (when order doesn't matter).
- Mention mocking external dependencies (DB, network) and dependency injection so tests stay fast and deterministic.

---

## 5. SDET Cheat Sheet — Testing Knowledge They Will Probe

You **must** sound fluent here. This is where SDET candidates differentiate themselves from generic SWE candidates.

### 5.1 Test design techniques (know names + when to use)
- **Equivalence Partitioning** — divide input domain into classes that are treated the same; test one rep per class. (e.g., age 0–17, 18–64, 65+.)
- **Boundary Value Analysis** — test min, min‑1, min+1, max‑1, max, max+1. (Off‑by‑one is the most common production bug.)
- **Decision Table** — for combinations of conditions (good for business rules like discount = f(cart, coupon, membership)).
- **State Transition** — for stateful flows (order: created → paid → shipped → delivered → returned).
- **Pairwise / All‑pairs** — when input combinatorics explode, cover all 2‑variable interactions.
- **Use Case / Scenario testing** — end‑to‑end realistic flows.
- **Error guessing** — heuristic based on experience (null, empty, huge, weird unicode, leap year, DST).
- **Exploratory testing** — time‑boxed, charter‑driven, simultaneous learn + test.

### 5.2 Test types (be able to define + give example)
- **Functional**: feature behaves per spec.
- **Regression**: previously working features still work after change.
- **Smoke**: bare minimum "is the build alive?" test pre‑run.
- **Sanity**: narrow, deep after a small fix.
- **Integration**: components together.
- **System**: end‑to‑end.
- **Acceptance / UAT**: business signoff.
- **Non‑functional**: performance, load, stress, soak/endurance, scalability, security, accessibility, usability, localization, compatibility.
- **Performance vs Load vs Stress**: performance = baseline behavior; load = expected peak; stress = beyond breaking point to find limits.
- **Chaos / resilience**: inject failures (kill pods, drop network) to test recovery.

### 5.3 White box / Black box / Gray box
- **Black box**: only the spec/UI, no code. Equivalence, BVA, decision tables.
- **White box**: source visible. Coverage metrics: statement, branch, condition, MC/DC, path. As an SDET you should know how to read coverage reports (`jacoco`, `coverage.py`).
- **Gray box**: mixture — common in API testing where you know schema + behavior but not implementation.

### 5.4 The test pyramid
- Bottom: **Unit tests** (many, ms, isolated, written by devs and SDETs).
- Middle: **Integration / API / contract tests** (some, hundreds of ms, real components but bounded).
- Top: **UI / E2E tests** (few, slow, flaky, expensive — only critical user journeys).
- Anti‑pattern: **ice‑cream cone** (lots of UI, few unit) — flaky, slow, brittle. If asked "how would you fix our regression suite?" you almost always answer: shift left → push tests down the pyramid.

### 5.5 Automation framework — design like an engineer
If they ask *"How would you design a test automation framework for TikTok Shop's checkout?"*, structure your answer:

**Layered architecture**
1. **Driver / runner layer**: pytest / TestNG / JUnit5; manages parallelism, retries, tagging.
2. **API client layer**: typed clients per service (RestAssured / `httpx`), authentication, retry, logging interceptors.
3. **Page Object layer (UI)**: each screen = a class with locators + actions, hiding raw selectors from tests. (Mobile: equivalent Screen Object using Appium / Espresso / XCUITest.)
4. **Test data layer**: factories / fixtures, environment‑specific data, seeding & cleanup hooks. Never hard‑code IDs.
5. **Config layer**: environment‑aware (dev / staging / preprod), secrets pulled from vault, never committed.
6. **Utilities**: smart waits, screenshot/video on failure, logging, retry decorator for flake.
7. **Reporting**: Allure / HTML + JUnit XML, ties results to CI build.

**Cross‑cutting concerns**
- Test isolation (each test creates and tears down its own state).
- Idempotency / re‑runnability.
- Parallelism with per‑worker test data.
- CI/CD: run on every PR (subset), nightly (full), pre‑release (perf + security).
- Quarantine for flaky tests + ownership rotation to fix them.
- Metrics: pass rate, flake rate, runtime per stage, defect escape ratio.

**Patterns to namedrop with confidence**
- Page Object Model (POM).
- Builder pattern for test data.
- Factory pattern for entities (User, Product, Order).
- Dependency injection for driver/config (so tests are pure).
- Singleton — and why you usually avoid it for parallelism.

### 5.6 API testing depth
Don't just "send a GET". Cover:
- **Status code** + **response time** + **headers** + **body schema** (JSON Schema or Pydantic) + **business value of each field** + **idempotency on retry** + **auth handling** + **error responses**.
- **Contract tests** between services (Pact) so a breaking change in service A fails before integration.
- **Negative path matters as much as happy path** — invalid token, expired token, missing required field, oversized payload, wrong content‑type, SQL‑injection‑shaped strings, unicode, very large pagination.
- **Concurrency**: place 100 orders for the same product with stock=1 → exactly 1 success expected.
- **Idempotency keys** for payment endpoints — retry must not double‑charge.

### 5.7 Flaky tests — how to talk about them
- Senior answer: never just rerun. **Root‑cause** the flake into: timing/sync, test isolation (shared state), environment/network, non‑determinism (random / time / order), real product bug.
- Fixes: explicit waits not sleeps, deterministic test data, quarantine + ticket + owner + SLA to fix or delete in 1–2 sprints.
- Track **flake rate** as a first‑class metric.

### 5.8 CI/CD integration
- PR build: lint + unit + smoke API. Goal: <10 min.
- Merge build: full unit + API + small e2e.
- Nightly: full e2e + perf regression.
- Pre‑release: chaos + load + security.
- Gates: red on PR blocks merge; flake rate gate prevents merging tests that destabilize main.

### 5.9 Risk‑based prioritization
"You can't test everything. How do you decide what to automate?" Senior answer: matrix of **business impact × failure probability × frequency of use × cost to automate**. Automate high‑impact, high‑frequency, stable‑spec areas first. Don't automate UI that changes weekly — test below it via API.

---

## 6. "How Would You Test ___" — Scenario Drills

These come up in nearly every SDET interview. Use this 7‑bucket template, then tailor:

> **Template:** *Functional → Boundary → Negative/Error → Performance → Security → Compatibility/Localization → Reliability/Recovery → Test strategy (manual vs automated, pyramid level, who owns it).*

### 6.1 "How would you test a login page?"
- **Functional**: valid email+pwd → success; invalid pwd; non‑existent email; social login; SSO; "remember me"; 2FA via SMS / authenticator / email.
- **Boundary**: max email length (254), max password length, min length, special chars in email (`+`, `.`), unicode in name.
- **Negative**: empty, only spaces, SQL injection (`' OR 1=1 --`), XSS (`<script>...</script>`), 5 wrong attempts → lockout, expired session, reused old password if disallowed.
- **Performance**: login latency p50/p95/p99, throughput at peak, response under 10k concurrent logins.
- **Security**: pwd hashed (bcrypt/argon2) not stored, cookie flags `HttpOnly` + `Secure` + `SameSite`, CSRF tokens, brute‑force / rate limiting, account enumeration prevention (same error for "wrong pwd" vs "no such user").
- **Compatibility**: Chrome / Safari / Firefox / Edge, iOS / Android, low‑bandwidth, dark/light mode, screen reader.
- **Localization**: RTL languages, long translated strings.
- **Reliability**: backend down → graceful error; partial outage of 2FA provider → fallback.
- **Pyramid**: unit (validators) + API (`/login`) + 1 UI smoke for the happy path. Do not pile e2e tests on every variation.

### 6.2 "How would you test TikTok Shop checkout?"
- **Functional flows**: cart → address → shipping → payment → confirmation. Buyer logged in / guest. Multiple items, multiple sellers, mixed shipping, COD, prepaid, BNPL.
- **Pricing correctness** (the highest‑risk area in e‑commerce):
  - Discount stacking: % off + flat off + coupon + creator code.
  - Tax calc per state / country.
  - Currency conversion + rounding (use BigDecimal, not float — call this out).
  - Shipping fees thresholds (free over $X).
  - Tip / donation if applicable.
- **Inventory**: race condition with stock=1 and 100 concurrent buyers → exactly one wins. Reserve‑then‑confirm flow. Reservation timeout releases stock.
- **Payment**: success, decline, 3DS challenge, timeout mid‑auth, double‑submit (idempotency keys must dedupe), refund partial/full, chargeback.
- **Boundary**: cart max items, max quantity per item, address length, zip format per country.
- **Negative**: out‑of‑stock during checkout, price changed during checkout, address invalid, payment fraud.
- **Performance**: checkout p95 latency under peak; livestream "buy now" spikes.
- **Security**: PCI‑DSS scope (no PAN in your DB), tokenization via processor, signed webhooks, replay protection.
- **Compatibility**: iOS / Android / mWeb / desktop. Slow 3G.
- **Localization**: addresses (no state in many countries), phone formats, languages, currency symbols.
- **Reliability**: payment provider down → graceful retry; partial failure (charged but order didn't save) → reconciliation job.
- **Observability**: every state transition emits a trace; alerting on conversion drop > X%.
- **Automation strategy**: heavy at API level (all the pricing matrix), narrow at UI (1 happy path per platform).

### 6.3 "How would you test the comments feature?"
- Functional: post, reply, edit, delete, like; sorted by recent / top.
- Boundary: 0 chars, 1 char, max length, only emoji, only whitespace, mixed scripts (Arabic + Chinese + Latin).
- Negative: profanity filter, spam, repeated posts, hateful content moderation pipeline.
- Performance: live video with 100k viewers commenting at once → fan‑out, backpressure.
- Security: XSS via comment body, link injection, rate limit per user.
- Reliability: comment posted but feed cache not updated → eventual consistency window; show optimistic UI.

### 6.4 "How would you test a search API for products?"
- Relevance: known queries return known SKUs in top N.
- Ranking: A/B between models — define an offline eval set with NDCG / MRR / Recall@K.
- Boundary: empty query, query with only emoji, very long query, special chars.
- Performance: p95 latency < target at peak QPS.
- Caching: hot query cached; verify cache stampede protection.
- I18N: multilingual queries; transliteration.
- Personalization: same query, different users → different results, but never leak PII.
- Data freshness: new listing visible in search within SLA.

### 6.5 "How would you test livestream + countdown bidding?"
- Real‑time: clock sync, last‑second bid acceptance window, server time vs client time.
- Race conditions: two users bid at same ms — deterministic tiebreaker (server timestamp + sequence number).
- Failure mid‑auction: seller disconnect, viewer disconnect, payment fail at close.
- Anti‑sniping: extension rules.
- Scale: tens of thousands of viewers, hundreds of bidders.
- Audit: full bid log replayable; immutable.

> **Pro tip:** when answering any "how would you test" question, *say the framework names out loud*: "I'd start with equivalence partitioning to bucket inputs, then boundary value analysis on each numeric range, then decision tables for the discount rules, then state‑transition tests across the order lifecycle." That single sentence flags you as ISTQB‑literate.

---

## 7. CS Fundamentals — Rapid Fire

You will get 3–6 of these in 5 minutes between coding and Q&A. One‑line answers below — be able to *expand* each into 60 seconds.

| Question | One‑liner answer |
|---|---|
| Process vs thread | Process = isolated memory, expensive switch; thread = shares memory of process, cheap switch, needs sync. |
| TCP vs UDP | TCP reliable, ordered, flow+congestion control, slower; UDP best‑effort, faster, used for streaming/games. |
| HTTP vs HTTPS | HTTPS = HTTP over TLS; provides encryption, integrity, server (and optionally client) authentication. |
| GET vs POST | GET: safe, idempotent, cacheable, in URL. POST: not idempotent, body, side effects. |
| 3‑way handshake | SYN → SYN‑ACK → ACK to open a TCP connection. |
| What happens when you type a URL? | DNS lookup → TCP connect → TLS handshake → HTTP request → server processes (LB → app → DB) → response → render. |
| REST vs RPC | REST = resource‑oriented, HTTP verbs, statelessness; RPC = action‑oriented, often binary (gRPC), schema‑first (proto). |
| SQL vs NoSQL | SQL: relational, schema, ACID, joins. NoSQL: flexible schema, horizontal scale, BASE. Pick per access pattern. |
| Index trade‑off | Faster reads, slower writes, more storage. |
| ACID | Atomicity, Consistency, Isolation, Durability. |
| CAP | Under partition you pick consistency or availability. |
| Cache breakdown / penetration / avalanche | Hot key expires / value never exists / many keys expire together. Mitigations: mutex rebuild, bloom filter, randomize TTL. |
| Deadlock 4 conditions | Mutual exclusion, hold & wait, no preemption, circular wait. |
| MVC / MVVM | Separation of concerns between data, view, and controller/viewmodel. |
| Big‑O of HashMap ops | Average O(1) get/put, worst O(n) on collisions. |
| BFS vs DFS | BFS uses queue, shortest path in unweighted; DFS uses stack/recursion, good for path/cycle/topo. |
| Time vs Space DP | Memoization stores subproblem results; trade space for time. |
| Mutex vs Semaphore | Mutex = binary, ownership; Semaphore = counter, no ownership. |
| What is idempotency | Same request, same result regardless of how many times applied — critical for payments / retries. |
| What is eventual consistency | All replicas converge after some time when no new updates; common in distributed caches and NoSQL. |

---

## 8. Mini System Design — Intern‑Lite

Even intern interviews include "design a simple system" prompts. Practice these two patterns:

### 8.1 Design a URL shortener (or any ID generator) — classic
Hit these beats in 8 minutes:
1. **Requirements**: functional (shorten, redirect, custom alias, expiration), non‑functional (read‑heavy, low latency, high availability).
2. **Back of the envelope**: 100M URLs/day → ~1.2k QPS write, 100x read = 120k QPS read.
3. **API**: `POST /shorten`, `GET /{code}`.
4. **Code generation**: base62 of an auto‑increment ID, or hash + collision check.
5. **Storage**: relational (code, longUrl, userId, createdAt, expiresAt) with index on code. Sharding by code prefix.
6. **Cache**: Redis LRU in front, 95% hit target.
7. **Scaling**: read replicas, CDN for very hot codes.
8. **Edge cases**: collisions, abuse, malicious URLs, analytics.

### 8.2 Design a "recently viewed products" service for TikTok Shop
1. **Requirements**: per user, last N items, ordered by recency, dedupe.
2. **Data structure**: Redis sorted set per user, score = timestamp, trim to N.
3. **Write path**: `ZADD user:{id} ts product_id; ZREMRANGEBYRANK user:{id} 0 -N-1`.
4. **Read path**: `ZREVRANGE user:{id} 0 N`.
5. **Persistence**: async backup to durable store; OK to lose seconds on cache fail.
6. **Scale**: shard by userId hash; TTL on inactive users.
7. **Privacy**: deletion on user request; retention policy.
8. **How would you test it** (bring this back to SDET!):
   - Unit on dedupe + trimming logic.
   - Integration with Redis testcontainer.
   - Property‑based test: after k writes, length == min(k, N) and order is descending by ts.
   - Load test at expected QPS.

### 8.3 General checklist for any design question
- Clarify scope & scale first.
- Functional vs non‑functional requirements explicit.
- Numbers (QPS, storage, latency target).
- Components: client → LB → service → cache → DB → queue → worker.
- Data model.
- Scaling strategy (vertical / horizontal / sharding / replication).
- Failure modes (and your testing strategy for each).
- Trade‑offs you consciously took.

---

## 9. Languages — One‑Page Refreshers

Pick **one** primary. Python is the safest bet for SDET (most common framework: pytest + requests + Playwright/Selenium + locust).

### 9.1 Python — must know cold
- Mutable vs immutable types; list vs tuple.
- `dict`, `set`, `collections.Counter`, `collections.defaultdict`, `collections.deque`, `heapq` (min‑heap; for max‑heap negate).
- List comprehensions; generator expressions; `yield`.
- `*args` / `**kwargs`, default args gotcha (mutable default!).
- `with` context manager, `try/except/else/finally`.
- Decorators, `functools.lru_cache`.
- f‑strings, `str.format`.
- GIL: CPython has one global lock → CPU‑bound multithreading doesn't speed up; use `multiprocessing` or async. I/O‑bound threading is fine.
- Testing: `pytest`, fixtures, `parametrize`, `monkeypatch`, `tmp_path`. `unittest.mock` for mocking.

### 9.2 Java — must know cold
- Primitives vs boxed; `==` vs `.equals`; `String` immutability; `StringBuilder` for concat in loop.
- `ArrayList`, `LinkedList`, `HashMap`, `LinkedHashMap`, `TreeMap`, `HashSet`, `PriorityQueue`, `ArrayDeque`.
- Generics, wildcards (`? extends T`, `? super T`).
- Streams + lambdas; `Optional` to handle null.
- Concurrency: `synchronized`, `volatile`, `ReentrantLock`, `ConcurrentHashMap`, `ExecutorService`, `CompletableFuture`.
- Exceptions: checked vs unchecked; try‑with‑resources.
- Testing: JUnit 5, Mockito, AssertJ. RestAssured for API tests. TestNG also fine.

### 9.3 Don't fight the tool
- Use the language whose libraries you actually know. Don't write Go for the first time in an interview.

---

## 10. Behavioral — ByteStyles in Depth

TikTok (and ByteDance) evaluate against six core values. Prepare **two STAR‑L stories per value**. STAR‑L = Situation, Task, Action, Result, **Learning** (TikTok loves the Learning bit).

### 10.1 The values, in TikTok's own words

1. **Aim for the Highest** — set ambitious targets, refuse "good enough".
2. **Be Grounded and Courageous** — speak truth respectfully, take hard decisions.
3. **Be Open and Humble** — admit you don't know, accept feedback, share credit.
4. **Be Candid and Clear** — say what you mean, no politics, no fluff.
5. **Always Day 1** — beginner's mindset, keep learning, challenge the status quo.
6. **Champion Diversity and Inclusion** — actively include different perspectives.

### 10.2 Questions to expect (almost guaranteed)
- "Why TikTok?" *(answer threads: short video disrupting commerce, Always Day 1 culture, the scale, the specific team's mission.)*
- "Why this team / why e‑commerce?"
- "Tell me about a project you're most proud of."
- "Tell me about a time you failed / made a mistake."
- "Tell me about a time you disagreed with a teammate."
- "Tell me about a time you had to learn something new under pressure." *(Always Day 1)*
- "Tell me about a time you challenged the status quo."
- "What's your biggest weakness?" *(real one, with the work you're doing on it.)*
- "Tell me about a time you found a bug everyone else missed." *(SDET‑specific; have one ready.)*
- "Describe a time you had to ship under tight time pressure."
- "How do you decide what to test when you can't test everything?"
- "What do you do when you disagree with the dev about whether something is a bug?"
- "Where do you see yourself in 5 years?"

### 10.3 Story bank — minimum stories to prepare
- A **technical project** you led or made a big contribution to. (Hits: Aim for Highest, Always Day 1.)
- A **failure / bug you owned**. (Hits: Open and Humble, Candid and Clear.)
- A **conflict resolved**. (Hits: Open and Humble, Grounded and Courageous.)
- A **rapid learning** story — new tool, new domain, short timeline. (Hits: Always Day 1.)
- A **leadership / influence without authority** story. (Hits: Aim for Highest, Candid and Clear.)
- A **diverse team / mentoring / inclusion** story. (Hits: D&I.)
- An **SDET‑flavored story**: bug you found, test you wrote that caught a regression, automation you built that saved time.

### 10.4 STAR‑L structure (drill this out loud)
- **S**ituation: 1 sentence context.
- **T**ask: 1 sentence what you owned.
- **A**ction: 3–5 sentences, ***your individual actions***, with specifics.
- **R**esult: 1–2 sentences, **quantify** (latency cut by X%, test runtime down by Y minutes, defect leak rate down from A to B).
- **L**earning: 1 sentence on what you took away.

Total: <3 minutes. Practice with a timer.

---

## 11. Questions to Ask the Interviewer

Asking sharp questions is graded. Prepare 6, pick 2–3 per round based on time.

Strong ones for an SDET intern:
- "What does the test pyramid look like for your service today? Where would you like it to be?"
- "How does the QA / SDET team partner with developers — embedded, central, or hybrid?"
- "What's the biggest quality challenge for Global E‑Commerce right now?"
- "How are flaky tests handled and tracked?"
- "What test frameworks and tools does the team use day to day?"
- "What does success look like for an intern by end of the 12 weeks?"
- "What's a project a past intern shipped that the team still uses?"
- "How does the team measure quality — what KPIs do you watch?"
- "How does TikTok Shop balance speed of feature shipping with risk management for payments / listings?"
- (To the HM) "What would make you say 'this intern was incredible'?"

Avoid: comp questions in technical rounds (save for HR), googleable basics, "what does your company do".

---

## 12. Logistics & Day‑Of Checklist

### The week before
- Re‑skim sections 3, 5, 6, 7, 10 of this doc.
- Do 1–2 fresh LeetCode mediums per day (binary tree, graph, intervals, hashmap, two‑pointer, sliding window).
- Mock interview at least once out loud — talk through a problem to a friend or to a mirror or to a recording.
- Re‑read your own resume — every project, every bullet, every metric — out loud.

### The day before
- Re‑skim the **Cheat Sheet sections** (TL;DR, CS fundamentals table, ByteStyles list, scenario template, STAR‑L template).
- Prepare 1‑min, 3‑min, and 5‑min versions of your top project.
- Sleep 8 hours. No new material after 9pm.

### 60 minutes before the interview
- Quiet room. Door closed. Phone silent.
- Water + paper + pen + this doc open to TL;DR.
- Mic + camera tested. Wired internet if you have it; mobile hotspot as backup.
- Re‑read your own STAR‑L bullet points.
- Have a notepad open to scribble while the interviewer talks.

### During the interview
- Smile and greet by name.
- Have 2 sentences of "about me" ready.
- For every technical problem: clarify → brute force → optimize → confirm → code → trace → complexity → tests → follow‑ups.
- For every behavioral: STAR‑L, quantified, under 3 minutes.
- If stuck: think out loud, ask a clarifying question, propose a brute force.
- Always leave 3–5 minutes for **your** questions.
- End with a clear "thank you, I'm very interested in this role; what are the next steps?"

### After the interview
- Within 24 hours, send a brief thank‑you email through the recruiter if you have their address.
- Write down: questions asked, where you stumbled, what to drill before the next round.

---

## 13. Red Flags That Sink Candidates (avoid these)

- Jumping into code before clarifying the problem.
- Silent coding — interviewer can't grade what they can't hear.
- "I'd Google it." Better: "I'd start from first principles and verify against docs."
- Saying "manual testing" without mentioning automation.
- Treating QA as a step after dev. SDETs are *embedded* with dev from PRD on.
- Generic answers to "why TikTok / why this team". Show you've thought specifically about Shop.
- Resume claims you can't defend in detail. If you wrote it, expect to be drilled.
- Memorized "perfect" behavioral answers. They smell rehearsed. Use real specifics.
- Not asking any questions at the end.

---

## 14. Final Confidence Boost

You are interviewing for a position that, historically, has a sub‑5% offer rate at TikTok — and you got the interview. They already think you can do the job. Your job in the interview is **not** to be flawless. It is to:

1. Communicate your thought process clearly.
2. Show that you can engineer *and* break.
3. Show that you'll be a good teammate (open, humble, candid, hungry).

Bring curiosity. Bring specifics. Bring an "Always Day 1" energy. You've got this.

---

## Appendix A — Mini Cheat Sheet (print this page)

**Coding flow**: Clarify → Brute force → Optimize → Confirm → Code → Trace → Complexity → Tests → Follow‑ups.

**Test design**: Equivalence Partitioning, Boundary Value Analysis, Decision Table, State Transition, Pairwise, Error Guessing, Exploratory.

**Scenario template (7 buckets)**: Functional → Boundary → Negative → Performance → Security → Compatibility/I18N → Reliability/Recovery → Strategy (pyramid level).

**Test pyramid**: many unit, some API/integration, few UI E2E.

**ByteStyles**: Aim for the Highest · Be Grounded and Courageous · Be Open and Humble · Be Candid and Clear · Always Day 1 · Champion D&I.

**STAR‑L**: Situation · Task · Action · Result · Learning. <3 minutes. Quantify the Result.

**CS fundamentals to drop in casually**: idempotency, eventual consistency, ACID, CAP, cache breakdown/penetration/avalanche, 3‑way handshake, process vs thread, B‑tree index, isolation levels.

**LeetCode topics to drill**: Binary Tree, Graph BFS/DFS, Intervals, HashMap, Two Pointers, Sliding Window, Binary Search on Answer, Heap/Top‑K, DP medium, Design (LRU, Time‑Based KV).

**Confirmed real TikTok questions seen recently**: LC 981 Time Based Key‑Value Store. LC‑style binary tree level order. Heap top‑K variant. Simulation problems.

**Languages**: pick one (Python or Java). Don't fight the tool.

**Always end coding with**: "Now let me write tests for it" — they love that.

Good luck.
