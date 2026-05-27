# CS Fundamentals Refresher — Read‑Once Before Your TikTok Tech 1

This is a focused, "just the fundamentals" pass — enough detail to actually answer follow‑ups, but short enough to read in one sitting. At the end there are **20 questions** for you to solve. Try them closed‑book first; check the hint/answer notes after.

Sections:
1. Operating Systems
2. Networking
3. Databases
4. Data Structures & Big‑O
5. Algorithms & Patterns
6. Concurrency
7. Web / HTTP / APIs
8. Object‑Oriented Programming
9. Software Testing fundamentals (SDET flavor)
10. Twenty practice questions

---

## 1. Operating Systems

### 1.1 Process vs Thread
- **Process** = an instance of a running program. Has its own address space (heap, stack, code, data). Switching between processes is expensive (full context switch, TLB flush).
- **Thread** = a unit of execution *within* a process. Threads in the same process **share heap and code** but have their own stack and registers. Cheaper to switch.
- Multi‑process gives isolation (one crash doesn't kill others); multi‑thread gives shared memory (faster communication, but you must synchronize).
- IPC (Inter‑Process Communication) is needed between processes: pipes, sockets, message queues, shared memory.

### 1.2 Context switch
The kernel saves the current process/thread's registers and PC, loads the next one's. CPU‑bound work suffers if you context‑switch too often.

### 1.3 Scheduling (high level)
- **FCFS**: simple, suffers from convoy effect.
- **SJF (Shortest Job First)**: optimal average wait, but starves long jobs and requires knowing job length.
- **Round Robin**: each task gets a time slice; fair, good for interactivity.
- **Priority**: priority‑based; risk of starvation, fixed with aging.
- **Multilevel feedback queue**: what most modern OSes use; tasks move between queues based on behavior.

### 1.4 Memory
- **Virtual memory**: each process sees a large, contiguous address space; the OS maps it to physical RAM via the **MMU** using **page tables**. The **TLB** is a cache of recent translations.
- **Paging**: address space divided into fixed‑size pages (e.g., 4KB). On miss → **page fault** → load page from disk (slow). Too many faults = **thrashing**.
- **Segmentation**: variable‑size logical segments (code, data, stack). Rarely used alone today.
- **Stack vs Heap**: stack = function frames, LIFO, fast, fixed size per thread. Heap = dynamic allocation, slower, managed by allocator (malloc / new) and garbage collector in managed languages.

### 1.5 Deadlock
Four necessary conditions (Coffman):
1. **Mutual exclusion** — resource held exclusively.
2. **Hold and wait** — hold one resource while waiting for another.
3. **No preemption** — resource only released voluntarily.
4. **Circular wait** — chain of processes each waiting on the next.

Break any one of them to prevent deadlock. The most practical: enforce a global ordering on resource acquisition (kills circular wait).

### 1.6 File system fundamentals
- **inode** holds file metadata + pointers to data blocks; the directory entry maps name → inode.
- Soft link = pointer to a path. Hard link = extra directory entry pointing to the same inode.
- Buffered I/O, page cache.

---

## 2. Networking

### 2.1 OSI model — useful as a mental map
1. Physical (cables, signals)
2. Data Link (Ethernet, MAC)
3. Network (IP, routing)
4. Transport (TCP, UDP)
5. Session
6. Presentation
7. Application (HTTP, DNS, SMTP, gRPC, WebSocket)

The TCP/IP model collapses these into: Link, Internet, Transport, Application. In interviews refer to layers 3 (IP), 4 (TCP/UDP), and 7 (HTTP) most.

### 2.2 TCP vs UDP
| Feature | TCP | UDP |
|---|---|---|
| Reliable | yes (ack + retransmit) | no |
| Ordered | yes (sequence numbers) | no |
| Connection | yes (handshake) | no |
| Flow + congestion control | yes | no |
| Overhead | higher | lower |
| Typical use | HTTP, SSH, DB | DNS, video/voice, games |

### 2.3 TCP three‑way handshake
`SYN → SYN-ACK → ACK`. Both sides agree on initial sequence numbers and that they can send + receive. Connection close is a four‑way handshake (FIN/ACK each direction).

### 2.4 What happens when you type `www.tiktok.com` and press enter?
1. **DNS lookup**: browser cache → OS cache → resolver → root → TLD (`.com`) → authoritative → A record (IP).
2. **TCP connect** to that IP on port 443 (3‑way handshake).
3. **TLS handshake**: server presents cert (chain signed by CA). Client validates. They negotiate cipher, exchange keys, derive a symmetric session key.
4. **HTTP request** sent (over TLS).
5. **Server processing**: load balancer → app server → DB/cache/service mesh → response.
6. **Response** (HTML/JSON) returns. Browser parses HTML, requests sub‑resources (CSS/JS/images), renders.

You should be able to give this 90‑second answer cold.

### 2.5 DNS records (the ones that come up)
- **A** — hostname → IPv4.
- **AAAA** — hostname → IPv6.
- **CNAME** — hostname → another hostname (alias).
- **MX** — mail server.
- **TXT** — arbitrary text (SPF, DKIM, verification).
- **NS** — name server for a zone.

### 2.6 HTTP basics
- Stateless request/response.
- Methods: **GET** (safe, idempotent, cacheable), **POST** (creates / side effects, not idempotent), **PUT** (full replace, idempotent), **PATCH** (partial update), **DELETE** (idempotent), **HEAD** (like GET, no body), **OPTIONS** (used in CORS preflight).
- Status code families: 1xx info, 2xx success, 3xx redirect, 4xx client error, 5xx server error.
- Common codes: 200 OK, 201 Created, 204 No Content, 301 Moved Permanently, 302 Found, 304 Not Modified, 400 Bad Request, 401 Unauthorized (no/invalid auth), 403 Forbidden (auth ok but not allowed), 404 Not Found, 409 Conflict, 422 Unprocessable, 429 Too Many Requests, 500 Internal, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout.
- 401 vs 403: 401 = "I don't know who you are"; 403 = "I know who you are but you can't do that."

### 2.7 HTTPS / TLS
- HTTPS = HTTP over TLS.
- TLS provides **confidentiality** (encryption), **integrity** (MAC), and **authentication** (server cert; optionally client cert).
- Handshake: client hello (supported ciphers) → server hello + cert → key exchange (e.g., ECDHE) → symmetric session key → application data.

### 2.8 Other essentials
- **Sockets**: endpoint = `(IP, port)`. Server listens, client connects.
- **WebSocket**: starts as HTTP, upgrades to a persistent full‑duplex connection. Used for live chat, livestream messages.
- **CDN**: edge caches that serve static (and sometimes dynamic) content close to users → lower latency and origin load.
- **Load balancer**: L4 (TCP, by IP/port) or L7 (HTTP, by URL/header/cookie). Strategies: round robin, least connections, IP hash, consistent hashing.

---

## 3. Databases

### 3.1 SQL vs NoSQL
- **SQL (relational)** — fixed schema, joins, ACID, strong consistency, good for relational data (orders, users, transactions). Examples: MySQL, Postgres.
- **NoSQL** — flexible schema, easier to scale horizontally, usually BASE (eventually consistent). Sub‑types:
  - **Key‑value**: Redis, DynamoDB (single‑item ops).
  - **Document**: MongoDB (JSON‑like docs).
  - **Wide‑column**: Cassandra, HBase (great for time‑series and write‑heavy).
  - **Graph**: Neo4j (social graphs).

Pick based on access pattern, not hype.

### 3.2 ACID (relational)
- **Atomicity**: a transaction is all‑or‑nothing.
- **Consistency**: a transaction takes the DB from one valid state to another (constraints hold).
- **Isolation**: concurrent transactions don't see each other's intermediate state (within the chosen isolation level).
- **Durability**: once committed, survives crashes (typically via write‑ahead log).

### 3.3 BASE (NoSQL)
**Basically Available**, **Soft state**, **Eventual consistency**. Trades strict consistency for availability and partition tolerance.

### 3.4 Isolation levels & phenomena
| Level | Dirty read | Non‑repeatable read | Phantom read |
|---|---|---|---|
| Read Uncommitted | possible | possible | possible |
| Read Committed | no | possible | possible |
| Repeatable Read | no | no | possible (MySQL InnoDB prevents most) |
| Serializable | no | no | no |

- **Dirty read**: see another tx's uncommitted changes.
- **Non‑repeatable read**: same row read twice in one tx, different value.
- **Phantom read**: same query twice in one tx, different set of rows (new rows appeared).

### 3.5 Indexes
- Default storage in most relational DBs is a **B+‑tree** index — ordered, supports range queries, log N lookups.
- **Hash index**: O(1) exact match, no range queries.
- **Clustered index**: row data physically stored in index order; one per table (primary key).
- **Non‑clustered (secondary)**: index has pointer to row.
- **Covering index**: includes all columns a query needs so the engine never touches the table.
- Trade‑offs: faster reads, **slower writes** (every insert/update touches each index), more storage.
- Index a column when it appears in WHERE / JOIN / ORDER BY and is reasonably selective.

### 3.6 Normalization (very briefly)
- **1NF**: atomic values, no repeating groups.
- **2NF**: 1NF + no partial dependency on a composite key.
- **3NF**: 2NF + no transitive dependency on the key.
- **Denormalization** is intentional duplication for read performance (common in NoSQL, warehouses).

### 3.7 Joins
- **INNER JOIN** — rows in both.
- **LEFT JOIN** — all left + matches from right (NULL where no match).
- **RIGHT JOIN** — mirror.
- **FULL OUTER JOIN** — all rows from both.
- **CROSS JOIN** — Cartesian product.

### 3.8 CAP theorem
In a network partition, you can pick **Consistency** or **Availability** but not both. Outside partitions, you generally get all three. Most real systems are AP (Cassandra, Dynamo) or CP (HBase, Spanner gets close to CA in practice with global clock).

### 3.9 Caching (you'll be asked)
- **Cache‑aside (lazy)**: app reads cache; on miss, reads DB and writes back to cache.
- **Read‑through / Write‑through**: cache itself talks to the store.
- **Write‑back (write‑behind)**: write to cache, async flush to DB. Fastest writes, risk of loss.
- Eviction: LRU, LFU, FIFO, TTL.
- Failure modes:
  - **Cache penetration**: queries for keys that don't exist hammer the DB. Fix: cache the negative result (with shorter TTL), or use a **bloom filter**.
  - **Cache breakdown**: a single hot key expires and stampedes the DB. Fix: mutex/single‑flight to rebuild, or never expire hot keys.
  - **Cache avalanche**: many keys expire at the same moment. Fix: jittered TTLs.

### 3.10 Sharding & replication
- **Replication**: copies of the data; gives read scaling and HA. Master‑slave (single writer) vs multi‑master.
- **Sharding**: split data across nodes by a shard key (hash, range, directory). Trade‑off: re‑sharding is painful; cross‑shard joins are expensive.
- **Consistent hashing** minimizes data movement when nodes are added/removed.

---

## 4. Data Structures & Big‑O

### 4.1 Big‑O notation
Asymptotic upper bound on growth. Common growth rates from fastest to slowest:
`O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)`

### 4.2 Cheat sheet
| Structure | Access | Search | Insert | Delete | Notes |
|---|---|---|---|---|---|
| Array | O(1) | O(n) | O(n) | O(n) | Contiguous, cache‑friendly |
| Dynamic array (vector / ArrayList) | O(1) | O(n) | amortized O(1) at end | O(n) | Doubles on resize |
| Linked list (singly) | O(n) | O(n) | O(1) given node | O(1) given node | No random access |
| Stack | — | — | O(1) push | O(1) pop | LIFO |
| Queue | — | — | O(1) enqueue | O(1) dequeue | FIFO |
| Deque | O(1) ends | O(n) | O(1) ends | O(1) ends | Both ends |
| Hash map | — | avg O(1), worst O(n) | avg O(1) | avg O(1) | Order not guaranteed (unless `LinkedHashMap` / Python 3.7+) |
| Hash set | — | avg O(1) | avg O(1) | avg O(1) | |
| Binary heap | — | — | O(log n) | O(log n) extract min/max | Array‑backed |
| Balanced BST (TreeMap, Red‑Black, AVL) | — | O(log n) | O(log n) | O(log n) | Ordered |
| Trie | — | O(L) L=word length | O(L) | O(L) | Prefix search |
| Graph (adj list) | — | — | O(1) edge | O(degree) | Sparse |
| Graph (adj matrix) | O(1) | — | O(1) | O(1) | Dense, O(V²) space |

### 4.3 When to use which
- Need fastest lookup by key → **hash map**.
- Need ordered iteration / range queries → **TreeMap / sorted structure**.
- Need to pop smallest/largest repeatedly → **heap**.
- Need FIFO (BFS, queue of tasks) → **queue / deque**.
- Need LIFO (DFS, undo) → **stack**.
- Need prefix search (autocomplete) → **trie**.
- Need union/find connectivity → **disjoint set union (DSU)** with path compression + union by rank, near O(1) amortized.

### 4.4 String / char gotchas
- String comparison: `==` compares references in Java; use `.equals`. In Python `==` compares value.
- Strings are immutable in Java/Python — concatenation in a loop is O(n²); use `StringBuilder` / `"".join(list)`.
- Unicode: 1 character ≠ 1 byte; emojis can be multiple code units.

---

## 5. Algorithms & Patterns

### 5.1 Sorting
- **Quick sort**: avg O(n log n), worst O(n²). In‑place. Not stable.
- **Merge sort**: O(n log n) always. Stable. Extra O(n) space.
- **Heap sort**: O(n log n). In‑place. Not stable.
- **Counting / Radix / Bucket**: O(n) under integer / bounded‑range constraints.
- Python's `sorted` / Java's `Arrays.sort` (objects) use **Timsort** — adaptive merge sort, O(n log n), stable.

### 5.2 Searching
- **Linear** O(n).
- **Binary search** O(log n). Requires sorted input. Watch out for off‑by‑one: use `while lo < hi: mid = (lo+hi)//2; if cond(mid): hi = mid else: lo = mid+1`.
- **Binary search on answer**: search the answer space when monotonic — Koko Eating Bananas, Split Array Largest Sum, Capacity to Ship Packages, etc.

### 5.3 Graph algorithms
- **BFS** (queue) — shortest path in unweighted graph; level order in trees.
- **DFS** (stack / recursion) — path existence, cycle detection, topological sort, connected components.
- **Topological sort** (DAG): Kahn's algorithm (BFS with in‑degree) or DFS post‑order reverse.
- **Dijkstra**: shortest path with non‑negative weights, O((V+E) log V) with binary heap.
- **Union‑Find** for connectivity (Kruskal's MST, dynamic connectivity).

### 5.4 Recursion → DP
1. Write recursion: `f(state) = some function of f(smaller states)`.
2. Add memoization: cache results by state — O(states × work).
3. Convert to tabulation if needed: build bottom up.
4. Optimize space: keep only the last row/column if recurrence is local.

### 5.5 Common patterns (and a one‑line tell)
- **Two pointers**: sorted array, pair sums, removing duplicates in place.
- **Sliding window**: contiguous subarray with constraint (longest substring, min window).
- **Fast & slow pointer**: cycle detection in linked list (Floyd's).
- **Prefix sum**: range sum queries, subarray sum equals K.
- **Monotonic stack**: next greater/smaller element, largest rectangle in histogram.
- **Backtracking**: permutations, combinations, N‑queens. Always restore state on return.
- **Greedy**: prove with exchange argument or by safe move.
- **Divide & conquer**: merge sort, quickselect, closest pair.

---

## 6. Concurrency

### 6.1 Why it's hard
Shared mutable state + non‑determinism. The bugs (race conditions, deadlocks, livelocks, starvation, memory visibility) are intermittent and hard to reproduce — which is why SDETs care a lot.

### 6.2 Primitives
- **Mutex / lock**: only one holder at a time; provides mutual exclusion. Use a **try‑with‑resources / `with` / `defer`** pattern so you can't forget to release.
- **Read‑write lock**: many readers OR one writer.
- **Semaphore**: counter of available permits. Useful for limiting concurrency (e.g., max 10 in‑flight requests).
- **Condition variable / monitor**: wait until a predicate becomes true.
- **Atomic operations / CAS**: compare‑and‑swap; lock‑free building block.

### 6.3 Memory model basics
- Without synchronization, one thread's writes may not be visible to another.
- `volatile` in Java/C++ provides visibility but **not atomicity**.
- Java's `synchronized` and explicit locks publish writes (happens‑before relationship).
- Don't write your own lock‑free code unless you really need it.

### 6.4 Race conditions
Two threads reading/writing the same data without synchronization, where the outcome depends on interleaving.
Fix: lock, atomic, or eliminate sharing (immutable / thread‑local).

### 6.5 Deadlock vs Livelock vs Starvation
- **Deadlock**: everyone is stuck waiting on each other.
- **Livelock**: everyone is busy reacting to each other but no progress.
- **Starvation**: a thread is perpetually denied a resource (often by an unfair lock / priority).

### 6.6 Python's GIL (worth knowing)
CPython has a global lock — only one thread executes Python bytecode at a time. So multi‑threading helps I/O‑bound work but **not** CPU‑bound. For CPU‑bound work use `multiprocessing` or write the hot path in C.

---

## 7. Web / HTTP / APIs

### 7.1 REST principles
- Resources identified by URLs.
- HTTP verbs map to actions (`GET /orders/{id}`).
- **Stateless** — server doesn't store client session in memory between requests (auth carried in token).
- Use proper status codes; consistent error shape.

### 7.2 REST vs gRPC
- REST: text JSON over HTTP/1.1, easy to debug, ubiquitous.
- gRPC: binary protobuf over HTTP/2, faster, streaming, schema‑first. Used inside microservice meshes (TikTok backend uses lots of gRPC‑style internal RPC).

### 7.3 Auth
- **Basic auth**: base64(user:pass). Only over HTTPS. Avoid for production.
- **API key**: opaque token in header. Simple, but coarse.
- **JWT (JSON Web Token)**: signed token (header.payload.signature). Self‑contained, stateless. Beware: a stolen JWT is valid until expiry — keep TTL short, support revocation lists for critical tokens.
- **OAuth 2.0 + OIDC**: delegated auth (login with Google). Flows: authorization code (web app), client credentials (service‑to‑service), PKCE (mobile).

### 7.4 Idempotency
A request is idempotent if applying it once == applying it many times.
- GET, PUT, DELETE: idempotent.
- POST: typically not, **make it idempotent for payments** by sending an **Idempotency‑Key** header so the server dedupes retries.

### 7.5 Rate limiting
- **Token bucket**: tokens added at rate R, requests consume tokens. Allows bursts.
- **Leaky bucket**: smooths traffic to a fixed rate.
- **Fixed window**: count per window — has edge spikes at boundaries.
- **Sliding window**: smoother; more expensive.
- Server returns **429 Too Many Requests** with `Retry‑After`.

### 7.6 Browser security primer
- **Same‑origin policy**: JS in page A can't read page B unless same origin.
- **CORS**: server explicitly allows cross‑origin (preflight OPTIONS).
- **CSRF**: malicious site triggers authenticated request on your behalf. Defense: CSRF tokens, `SameSite=Lax/Strict` cookies.
- **XSS**: attacker injects JS into your page. Defense: escape output, Content Security Policy.
- **SQL injection**: defense = parameterized queries / prepared statements.

---

## 8. Object‑Oriented Programming

### 8.1 Four pillars
1. **Encapsulation** — hide internals; expose behavior. Getters/setters where they make sense.
2. **Inheritance** — child reuses/extends parent. Favor composition over deep inheritance.
3. **Polymorphism** — many forms behind one interface. Runtime (override) and compile‑time (overload).
4. **Abstraction** — expose *what*, hide *how*.

### 8.2 SOLID
- **S — Single Responsibility**: one reason to change.
- **O — Open/Closed**: open to extension, closed to modification.
- **L — Liskov**: subtype must be substitutable for the supertype without breaking behavior.
- **I — Interface Segregation**: many small focused interfaces beat one big one.
- **D — Dependency Inversion**: depend on abstractions, not concretes. (How you make code testable!)

### 8.3 Class vs Interface vs Abstract Class
- **Interface** — pure contract; (Java) can have default methods now.
- **Abstract class** — partial implementation; can hold state.
- **Class** — fully implemented.

### 8.4 Design patterns that come up in interviews
- **Singleton** — one instance, global access. Watch out: harms testability and concurrency. Often a code smell.
- **Factory** — encapsulate object creation.
- **Builder** — fluent construction of complex objects (test data!).
- **Observer** — pub/sub.
- **Strategy** — interchangeable algorithms behind one interface.
- **Decorator** — wrap behavior.
- **Adapter** — convert one interface to another.

---

## 9. Software Testing Fundamentals (SDET lens)

### 9.1 Types of testing
- **Unit** — smallest unit in isolation, fast, deterministic.
- **Integration** — multiple components together.
- **System / E2E** — end‑to‑end through the real stack.
- **Acceptance** — does it meet user/business criteria.
- **Smoke** — bare minimum sanity at deploy time.
- **Regression** — old features still work after change.
- **Performance** (load, stress, soak), **Security**, **Accessibility**, **Localization**, **Compatibility**, **Chaos / Resilience**.

### 9.2 Test design techniques
- **Equivalence Partitioning** — group inputs that should behave the same; test one rep per group.
- **Boundary Value Analysis** — test min, min‑1, min+1, max, max+1.
- **Decision Tables** — for combinations of conditions.
- **State Transition** — for state machines (order lifecycle).
- **Pairwise** — when combinations explode, cover all 2‑variable interactions.
- **Error guessing / Exploratory** — heuristic, charter‑driven.

### 9.3 Test pyramid
Many fast unit tests at the bottom, fewer integration / API tests in the middle, very few UI / E2E tests at the top. The **inverted pyramid (ice‑cream cone)** is the anti‑pattern: slow, flaky, expensive.

### 9.4 Black box vs White box vs Gray box
- **Black box** — only the spec.
- **White box** — source visible; use coverage metrics (statement, branch, MC/DC).
- **Gray box** — partial knowledge; common for API testing.

### 9.5 Severity vs Priority
- **Severity** = how bad the bug is technically (crash > wrong data > UI typo).
- **Priority** = how urgently to fix (business decision).
- A typo on the home page can be low severity / high priority. A crash on a never‑used admin screen can be high severity / low priority.

### 9.6 Flake handling
Never just rerun. Categorize: timing, isolation (shared state), env/network, non‑determinism, real bug. Fix: explicit waits, isolated data, quarantine + owner + SLA.

### 9.7 CI/CD gates
- PR build: lint + unit + smoke API, target <10 min.
- Merge: full unit + API + small e2e.
- Nightly: full e2e + perf.
- Pre‑release: chaos + load + security.

---

# 10. Twenty Practice Questions

Solve them on paper or a blank doc first. Don't peek at the "what good looks like" until you have *something* written down. Time yourself: **conceptual ≈ 3 min each, coding ≈ 15 min each.**

## Conceptual (1–15)

**Q1.** Explain the difference between a process and a thread. Give one concrete situation where you'd choose one over the other.

**Q2.** Walk through what happens when a user types `https://www.tiktok.com` and hits enter, from DNS to first rendered pixel. Aim for 90 seconds.

**Q3.** TCP guarantees reliable, ordered delivery — describe the mechanisms it uses to achieve that (handshake, sequence numbers, ACK, retransmit, flow control, congestion control).

**Q4.** What's the difference between HTTP 401 and 403? Give an example request that returns each.

**Q5.** Compare clustered vs non‑clustered (secondary) indexes. Why might adding an index actually *hurt* performance?

**Q6.** Define ACID. Then explain why some distributed systems give up the C (strong consistency) and what they offer instead.

**Q7.** State the CAP theorem in your own words. Classify each of the following systems as CP or AP: MySQL primary‑replica, Cassandra, Redis (single node), DynamoDB.

**Q8.** What are cache penetration, breakdown, and avalanche? Give a mitigation for each.

**Q9.** Explain the four Coffman conditions for deadlock. Pick one and describe a real strategy to eliminate it.

**Q10.** In a hash map, lookup is "amortized O(1)" — what does "amortized" mean here, and what's the worst case, and why?

**Q11.** When would you use BFS vs DFS on a graph? Give one problem ideal for each.

**Q12.** What is idempotency in HTTP? Why is it critical for payment APIs? How would you implement an idempotent POST?

**Q13.** Explain SOLID in one sentence each. Then pick one principle and explain how violating it makes a system harder to test.

**Q14.** You are testing a function `int divide(int a, int b)`. List the equivalence classes and boundary values you would test. Then list 3 negative / error cases.

**Q15.** Your team's E2E test suite has a 12% flake rate. Walk through how you would diagnose and reduce it. Mention at least 4 root‑cause categories and 4 concrete fixes.

## Coding (16–20)

Write the function in your language of choice. State complexity. Then list test cases you would write for it.

**Q16. Valid Parentheses.** Given a string containing only `()[]{}`, return `true` if it is balanced.
Examples: `"()[]{}"` → true; `"(]"` → false; `"([{}])"` → true.

**Q17. Two Sum.** Given an array `nums` and `target`, return the indices `i, j` with `i != j` such that `nums[i] + nums[j] == target`. Assume exactly one solution exists. Aim for O(n).

**Q18. Binary Tree Level Order Traversal.** Given the root of a binary tree, return a list of lists where each inner list is the values at that level, left to right.

**Q19. Time Based Key‑Value Store (LeetCode 981 — confirmed asked at TikTok).**
Implement a class:
```
class TimeMap:
    void set(String key, String value, int timestamp)
    String get(String key, int timestamp)   # returns the value with the largest timestamp_prev <= timestamp; "" if none
```
All `set` calls for a given key have strictly increasing timestamps. Aim for O(1) set, O(log n) get.

**Q20. Number of Islands.** Given an `m x n` grid of `'1'` (land) and `'0'` (water), return the number of islands. An island = connected horizontally/vertically. Choose BFS or DFS and justify.

---

## Hints / What Good Looks Like (peek only after attempting)

**Q1.** Process = isolated address space; thread = shared within process. Pick *process* for isolation/security (e.g., browser tabs in Chrome). Pick *threads* when you need cheap shared memory (a web server pool serving I/O‑bound requests).

**Q2.** DNS recursion → TCP handshake → TLS handshake → HTTP request → LB → app → DB/cache → response → parse HTML → fetch sub‑resources → render. Mention CDN if relevant.

**Q3.** Sequence numbers + cumulative ACKs; retransmit on timeout / triple‑duplicate ACK; sliding receive window for flow control; congestion control via slow start, congestion avoidance, fast retransmit/recovery.

**Q4.** 401 = not authenticated (missing/invalid token; sending no auth on a protected endpoint). 403 = authenticated but not authorized (logged in as user A trying to read user B's resource).

**Q5.** Clustered = rows stored in index order, one per table, range queries cheap. Non‑clustered = separate index with row pointers. Indexes hurt when: writes dominate reads (every insert/update touches each index), low cardinality columns make the index useless, or the query optimizer picks a bad plan.

**Q6.** Atomicity, Consistency, Isolation, Durability. Distributed systems often give up strong consistency for availability under partition (CAP) and offer eventual consistency — replicas converge after a quiescent period.

**Q7.** Under network partition you can pick C or A, not both. Rough labels: MySQL primary‑replica → CP‑ish (if you require reads from primary), Cassandra → AP (tunable), single‑node Redis → CP within itself but not distributed, DynamoDB → AP (tunable consistency).

**Q8.** Penetration → cache the negative or use a bloom filter. Breakdown → single‑flight / mutex on rebuild, or pin hot keys. Avalanche → jittered TTLs and graceful degradation.

**Q9.** Mutual exclusion, hold & wait, no preemption, circular wait. Easiest in practice: enforce a global lock ordering (kills circular wait).

**Q10.** "Amortized" means averaged across many operations. Worst case is O(n) when many keys collide into one bucket (or during a rehash). Average O(1) assumes a good hash and load factor under threshold.

**Q11.** BFS = shortest path in unweighted graphs, level traversal. DFS = path existence, cycle detection, topo sort, connected components, backtracking.

**Q12.** Same request applied many times = same result. Critical because clients (and networks) retry payments and you must not double‑charge. Implement: client sends `Idempotency‑Key`; server records (key, response) for some window; subsequent identical key returns the stored response.

**Q13.** S — one reason to change. O — open to extension, closed to modification. L — subtypes substitutable. I — many small interfaces beat one big one. D — depend on abstractions. Violation example: a class that constructs its own DB client (DIP violation) cannot be tested without a real DB; inject the client interface and you can mock.

**Q14.** EP classes: a positive/b positive, a negative/b positive, a positive/b negative, a/b both negative, a zero / b non‑zero, **a non‑zero / b zero (must handle!)**. Boundaries: `Integer.MIN_VALUE`, `Integer.MAX_VALUE`. Negatives: b = 0 (divide by zero), `MIN_VALUE / -1` (overflow!), nulls if boxed, very large strings if input is parsed.

**Q15.** Root causes: timing/sync, test isolation (shared state, order dependency), environment/network, non‑determinism (random, time, concurrency), real product bug, test data drift. Fixes: explicit waits over sleeps; isolated per‑test data + cleanup; retries on infra calls (not on assertions!); quarantine + ticket + SLA; track flake rate per test; gate merges on flake rate. Promote integration over UI where possible.

**Q16.** Stack of expected closers. Push closer when you see an opener; for a closer, pop and compare. End: stack must be empty.
```python
def isValid(s):
    pairs = {'(': ')', '[': ']', '{': '}'}
    stack = []
    for c in s:
        if c in pairs:
            stack.append(pairs[c])
        else:
            if not stack or stack.pop() != c:
                return False
    return not stack
```
Complexity: O(n) time, O(n) space. Tests: empty, single open, single close, all opens, all closes, mismatched, deeply nested, very long input.

**Q17.** Hash map index by value as you iterate.
```python
def twoSum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
```
O(n) time, O(n) space. Tests: pair at start, pair at end, duplicates (`[3,3]` t=6), negatives, single elem (no answer), empty.

**Q18.** BFS with a queue, processing one level per iteration.
```python
from collections import deque
def levelOrder(root):
    if not root: return []
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            n = q.popleft()
            level.append(n.val)
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        out.append(level)
    return out
```
O(n) time, O(n) space. Tests: null root, single node, skewed left, skewed right, perfect tree.

**Q19. (LC 981 — bring this one to a memorable level.)** Per key, store a list of `(ts, value)` in append order — naturally sorted because `set` calls have increasing ts. On `get`, binary search for the largest ts ≤ query.
```python
import bisect
class TimeMap:
    def __init__(self):
        self.store = {}
    def set(self, key, value, timestamp):
        self.store.setdefault(key, ([], []))
        self.store[key][0].append(timestamp)
        self.store[key][1].append(value)
    def get(self, key, timestamp):
        if key not in self.store: return ""
        ts, vals = self.store[key]
        i = bisect.bisect_right(ts, timestamp) - 1
        return vals[i] if i >= 0 else ""
```
`set` O(1) amortized, `get` O(log n). Tests: get before any set (""), get exactly at a ts, get between two ts (returns earlier), key never set, many sets then mid‑range get, single set then queries before/at/after.

**Q20.** DFS sink islands. Iterate every cell; on `'1'`, increment count and DFS to mark all connected land as visited (mutate to `'0'` or use a `visited` set).
```python
def numIslands(grid):
    if not grid: return 0
    R, C = len(grid), len(grid[0])
    def dfs(r, c):
        if r < 0 or r >= R or c < 0 or c >= C or grid[r][c] != '1':
            return
        grid[r][c] = '0'
        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)
    count = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)
    return count
```
O(R·C) time and worst‑case space (recursion depth). BFS with a queue avoids recursion stack overflow on huge grids — call that out as a follow‑up. Tests: all water, all land, single cell, single row, diagonal land (not connected!), grid with hole in middle.

---

## How to use this doc tomorrow

1. Read sections 1–9 once, slowly. **~60–75 minutes total.**
2. Close the doc. Try all 20 questions on paper. **~90 minutes.**
3. Review your answers against the hints. Write down anything that surprised you in a "to‑drill" list.
4. Sleep. The marginal value of late cramming is negative.

You've already cleared the OA — that's the hardest filter. Tomorrow they want to see you *think out loud*, *clarify*, *write clean code*, and *talk like a tester*. You're ready. Go get it.
