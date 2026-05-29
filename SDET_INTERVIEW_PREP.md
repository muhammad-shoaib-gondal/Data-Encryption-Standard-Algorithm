SDET Interview Practice Questions (TikTok-Focused)
==================================================

This document is a curated set of practice questions for SDET (Software Development Engineer in Test) interview preparation, distilled from real candidate experiences (TikTok San Jose / Seattle, 2024–2026). Use it alongside your LeetCode practice — it covers the *non-LeetCode* surface area that SDET loops actually test: testing mindset, scenario design, CS fundamentals, SQL, system design for test, and behavioral.

---

## How TikTok SDET Loops Are Typically Structured

Based on shared experiences, expect roughly:

1. **Recruiter screen** — background, motivation, logistics.
2. **Online Assessment (OA)** — LeetCode-style, sometimes with a testing twist (e.g., write tests for a function, not just implement it).
3. **Technical screen** — 1 LeetCode easy/medium + 1 scenario-based testing question. Sometimes conducted in Mandarin if both sides agree.
4. **SDET-focused round** — testing types, test design, debugging, automation frameworks, sometimes SQL.
5. **Hiring Manager round** — deeper test design, project deep-dive, behavioral, sometimes system design on one of your own projects.

Cadence between rounds is typically 4–5 days. All rounds are virtual.

---

## 1. Coding (LeetCode-style, Easy → Medium)

You said you're covered on LeetCode, so this section just lists the **patterns most frequently reported** so you can verify coverage and not over-train rare patterns.

- Two Sum and variants (hashmap two-pointer trade-offs) — explicitly mentioned.
- String manipulation: reverse, palindrome check, anagram groups, substring problems.
- Arrays: sliding window, prefix sum, in-place modification.
- Hashmap / set counting problems.
- Linked list basics: reverse, detect cycle, merge two sorted lists.
- Trees: BFS/DFS traversal, level order, lowest common ancestor.
- Stack/queue: valid parentheses, min stack, daily temperatures.
- Sorting / binary search basics.
- Easy DP: climbing stairs, house robber, coin change.

**SDET twist to practice:** for any solution you write, immediately list:

- Edge cases (empty, single element, negatives, duplicates, max/min int, very large input).
- How you would unit test it (table-driven tests, parametrized, mocking I/O).
- Time/space complexity, and what would change at 10×, 100×, 1000× scale.

---

## 2. Testing-Mindset Scenario Questions

These are the "given X, how would you test it?" questions that come up in nearly every loop. Practice answering each one out loud in 5–8 minutes, structured as:
**Clarify → Functional → Non-functional → Edge cases → Automation strategy → Test data / environment.**

### Practice scenarios

1. **How would you test a login page?** (Reported verbatim.)
   - Functional: valid creds, invalid creds, empty fields, SQL injection, XSS, password reset, "remember me," session expiry, social login.
   - Non-functional: brute-force lockout, rate limiting, latency under load, accessibility (keyboard, screen reader), localization, password masking, autofill.
   - Security: HTTPS only, secure/HttpOnly cookies, CSRF token, password hashing (server-side), error messages must not leak which field was wrong.
   - Cross-browser / cross-device / responsive.
2. **A user cannot access a certain page — how do you approach it?** (Reported verbatim.)
   - Reproduce: which user, which page, which client, which network, which time? Is it 100% or intermittent?
   - Layer-by-layer triage: client (cache, cookies, JS error in console) → network (DNS, TLS, status code, latency, CDN) → auth (token expiry, RBAC) → backend (logs, error rate, dependent services) → DB (slow query, missing row).
   - Check recent deploys, feature flags, A/B experiment buckets, regional rollouts.
   - Decide: user-specific data issue vs. config issue vs. regression. Write a regression test for whichever it turns out to be.
3. **Test the "Like" button on a TikTok video.** Functional (toggle, count increments, persistence after refresh, sync across devices), concurrency (double-tap, rapid taps, offline → online), idempotency of the API, eventual consistency of the counter, abuse/bot detection, analytics events fire exactly once.
4. **Test the video upload flow.** Formats, codecs, size limits, network drop mid-upload, resume, duplicate uploads, malicious files, content moderation hook, thumbnail generation, transcoding pipeline.
5. **Test an infinite-scroll feed.** Initial load, pagination cursor correctness, duplicate items, missing items, scroll restore on back-nav, memory leak on long scroll, slow network, empty state, pull-to-refresh.
6. **Test a search box with autocomplete.** Debounce, race conditions on out-of-order responses, empty results, special characters, very long query, IME composition (CJK input), keyboard navigation of suggestions.
7. **Test a payment / checkout flow.** Happy path, declined card, network timeout mid-charge (must not double-charge — idempotency key), partial refunds, currency rounding, tax calculation, 3DS challenge.
8. **Test a chat/DM feature.** Send/receive ordering, offline queue, read receipts, typing indicators, message edit/delete, large attachments, end-to-end across two devices.
9. **Test an elevator / vending machine / ATM** (classic warm-ups still asked).
10. **Test a REST API endpoint** (e.g., `GET /users/{id}`). Positive, negative, auth (none / wrong / expired token), authorization (other user's id), validation, content negotiation, schema contract, idempotency, rate limit headers, pagination, caching headers.

### Frameworks to memorize and quote in answers

- **Test pyramid:** unit → integration → end-to-end. More at the bottom, fewer at the top.
- **FIRST principles** for unit tests: Fast, Independent, Repeatable, Self-validating, Timely.
- **Equivalence partitioning** + **boundary value analysis**.
- **Decision tables** for combinatorial logic.
- **State-transition testing** for stateful UIs.
- **Pairwise / all-pairs** when input space is large.
- **Risk-based testing** to prioritize when time-boxed.

---

## 3. Types of Testing — Be Able to Define and Compare

Expect rapid-fire "what is X and when do you use it?":

- Unit vs. integration vs. system vs. end-to-end vs. acceptance.
- Smoke vs. sanity vs. regression.
- Functional vs. non-functional.
- Black-box vs. white-box vs. grey-box.
- Positive vs. negative testing.
- Load vs. stress vs. soak vs. spike vs. scalability.
- Performance vs. benchmark.
- Security testing (OWASP Top 10 — be able to name at least 5).
- Accessibility testing (WCAG basics).
- Localization vs. internationalization (l10n vs. i18n).
- Compatibility / cross-browser / cross-device.
- A/B testing vs. canary vs. blue-green vs. shadow traffic.
- Mutation testing, property-based testing, fuzz testing, chaos testing.
- Contract testing (Pact) for microservices.
- Snapshot / visual regression testing.

For each: **definition, when to use, one tool you'd reach for, one example from your own projects.**

---

## 4. Test Design & Test Case Writing

The hiring-manager round has been reported to fail candidates specifically on **test design depth**. Practice writing real test cases on paper.

- Write 15+ test cases for a **password field** (length, charset, leading/trailing spaces, unicode, paste behavior, copy disabled, autofill, password manager, show/hide toggle, accessibility).
- Write test cases for a **file upload** with `accept=".pdf,.png"` and 10MB limit.
- Write test cases for a **date range picker** (start > end, leap years, DST, time zones, max range).
- Write test cases for a **shopping cart** (add, remove, change quantity, out-of-stock during checkout, promo code, currency, persistence across sessions).
- Design a **test plan** for a new feature: scope, entry/exit criteria, environments, data, risks, automation strategy, owners, schedule.

For each scenario also articulate: **what would you automate first, what stays manual, and why** (cost vs. flake vs. value).

---

## 5. Automation & Tooling Knowledge

Be ready to discuss, even if you've only used a subset:

- **UI automation:** Selenium, Playwright, Cypress, Appium. Locator strategies, explicit waits vs. implicit waits, page object model, flake reduction.
- **API automation:** REST Assured, Postman/Newman, requests + pytest, supertest. Schema validation (JSON Schema, OpenAPI), contract tests.
- **Unit frameworks:** JUnit / TestNG (Java), pytest / unittest (Python), Jest / Mocha (JS), GoogleTest (C++).
- **Mocking:** Mockito, unittest.mock, WireMock, MSW.
- **CI/CD:** Jenkins, GitHub Actions, GitLab CI — running tests on PR, parallelization, sharding, flaky-test quarantine.
- **Reporting:** Allure, ExtentReports, JUnit XML.
- **Performance:** JMeter, k6, Locust, Gatling.
- **Coverage:** JaCoCo, coverage.py, Istanbul. Know that 100% coverage ≠ correct.
- **Containers:** Docker for hermetic test envs, docker-compose for integration suites.

Practice answering: **"Walk me through your automation framework architecture."** (Layers: drivers → page objects / API clients → test data → tests → reporting → CI hook.)

---

## 6. CS Fundamentals (asked verbatim per Reddit reports — CN, OS, DBMS)

### Computer Networks

- OSI vs. TCP/IP model, what lives at each layer.
- TCP vs. UDP, three-way handshake, connection teardown, TIME_WAIT.
- HTTP/1.1 vs. HTTP/2 vs. HTTP/3, head-of-line blocking.
- HTTPS / TLS handshake, certificates, MITM.
- DNS resolution path, DNS record types (A, AAAA, CNAME, MX, TXT).
- What happens when you type a URL and press enter? (Walk through every layer.)
- REST vs. gRPC vs. GraphQL vs. WebSocket — when to use which.
- Status codes: 2xx/3xx/4xx/5xx — name 10 you'd actually see.
- Cookies vs. localStorage vs. sessionStorage; SameSite, Secure, HttpOnly.
- CORS — what triggers preflight, how to debug "blocked by CORS" errors.

### Operating Systems

- Process vs. thread, context switching cost.
- Concurrency primitives: mutex, semaphore, condition variable, monitor.
- Deadlock — four conditions, how to detect, how to prevent.
- Race conditions, how to test for them deterministically.
- Memory: stack vs. heap, virtual memory, paging, page faults.
- Scheduling algorithms (FCFS, SJF, RR, MLFQ).
- File system basics, inodes, hard vs. soft links.
- Signals, IPC mechanisms (pipes, shared memory, sockets).

### DBMS / SQL

- ACID properties, isolation levels (read uncommitted → serializable), phenomena (dirty / non-repeatable / phantom).
- Normalization (1NF–3NF, BCNF), when to denormalize.
- Indexes: B-tree vs. hash, covering index, when an index *hurts*.
- Joins: inner / left / right / full / cross / self.
- Transactions, locking, MVCC.
- SQL vs. NoSQL trade-offs; CAP theorem.
- Sharding, replication, read replicas, eventual consistency.

---

## 7. SQL Practice Problems

Reported as a standalone question in at least one round. Be fluent at writing these on a whiteboard.

1. Second-highest salary (and *N*-th highest).
2. Employees who earn more than their manager.
3. Department-wise top-3 earners (window functions: `ROW_NUMBER`, `RANK`, `DENSE_RANK`).
4. Find duplicate emails / rows.
5. Consecutive days a user logged in (gaps-and-islands).
6. Running total / 7-day rolling average.
7. Customers who bought product A but not product B.
8. Pivot rows to columns (`CASE WHEN ... THEN ... END` aggregation).
9. Median salary per department.
10. Self-join: find pairs of employees in the same department.
11. Detect data anomalies (duplicates, nulls in NOT NULL columns, orphan FKs) — framed as a *test* you'd run nightly.

For each query, also state: **how would you test this query is correct?** (Seed data, expected result set, edge cases like empty table, all-tied values.)

---

## 8. Debugging Questions

- "A test passes locally but fails in CI — how do you debug?" (Env diff, flake, timing, test order, shared state, time zone, locale, parallelism, resource contention.)
- "A test is flaky — what do you do?" (Quantify flake rate, isolate, fix root cause vs. quarantine, never just retry.)
- "Production bug reported but not reproducible — how do you proceed?" (Logs, traces, metrics, user agent, A/B bucket, feature flag, time correlation with deploys.)
- "Read this stack trace / log — what's wrong?" (Practice with NPEs, off-by-one, deadlock traces.)
- Given a small buggy snippet (10–20 lines), find the bug and write a test that catches it.

---

## 9. System Design (light, often around your own project)

The first round at TikTok has been reported to ask **system design on one of your own projects**. Prepare 2 projects in depth:

- One-line elevator pitch.
- Architecture diagram from memory: clients → LB → services → datastores → async workers → observability.
- Why each tech choice; what you'd change with hindsight.
- Where the bugs lived; what testing strategy you applied at each layer.
- How you'd scale it 10× and 100×.

Also be comfortable with **"Design the test infrastructure for X"**, e.g.:

- Design a system to run 50,000 UI tests in under 30 minutes.
- Design a service health-check / synthetic monitoring system.
- Design an A/B testing framework's correctness validator.
- Design a load-test harness for a video upload service.

---

## 10. Behavioral (Hiring Manager round)

Prepare STAR-format stories for each:

- Most challenging project you've worked on. (Reported verbatim.)
- A bug you caught that others missed.
- A bug that escaped to production — what you learned, what you changed.
- Disagreement with a developer about whether something was a bug.
- Pushed back on a deadline because quality wasn't there.
- Improved a flaky / slow test suite.
- Mentored someone or improved team testing practices.
- Time you had to learn a new tool / language quickly.
- Why TikTok / why SDET / why now.

Have **2 thoughtful questions** ready for the interviewer (team's testing maturity, biggest quality pain point, on-call expectations, ratio of manual vs. automated testing, how SDETs partner with devs).

---

## 11. Two-Week Practice Schedule (suggested)

- **Days 1–3:** Drill the 10 scenario questions in section 2. Time-box each to 7 minutes, record yourself.
- **Days 4–5:** Section 3 + 4. Write full test-case lists for 5 features on paper.
- **Days 6–7:** Section 6 CS fundamentals. One-page cheat sheet per topic.
- **Days 8–9:** Section 7 SQL. Solve all 11 problems on a blank screen, no autocomplete.
- **Day 10:** Section 5 automation — sketch your framework architecture diagram from memory.
- **Day 11:** Section 8 debugging drills.
- **Day 12:** Section 9 system design — two whiteboard runs of your own project.
- **Day 13:** Section 10 behavioral — write out 8 STAR stories.
- **Day 14:** Mock loop end-to-end with a friend; one full LC medium + one scenario + behavioral.

---

## 12. Quick "Day-Before" Cheat Sheet

- Test pyramid, FIRST, equivalence partitioning, boundary value analysis.
- Always ask clarifying questions before testing a feature.
- For every coding answer: state complexity, list edge cases, propose unit tests.
- For every scenario: functional → non-functional → edge → automation → data/env.
- For every flake: find root cause, do not just retry.
- For every SQL: state assumptions about schema, nulls, duplicates.
- For every behavioral: STAR, quantify impact, end with what you learned.

Good luck.
