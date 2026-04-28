"""
Build a comprehensive PDF for CIS 761 — Exam 2.

Contents
--------
1. Concept primer covering every topic that appears on the exam
   (triggers, stored procedures, UDFs, transactions/ACID, isolation
    levels, concurrency anomalies, indexes, B+ trees, MapReduce).
2. Section I — True/False questions, with answer + explanation.
3. Section II — Multiple-choice questions, with answer + explanation.
4. Section III — Triggers & MapReduce free-response problems.
5. Section IV — B+ tree range query, insertion, and deletion problems
   worked out step by step.

Run:  python3 build_solutions_pdf.py
Output: CIS761_Exam2_Solved.pdf
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted,
    Table, TableStyle, KeepTogether, ListFlowable, ListItem,
)


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleX", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=22, leading=26, alignment=TA_CENTER, spaceAfter=8,
    textColor=colors.HexColor("#1f3864"),
)
subtitle_style = ParagraphStyle(
    "SubtitleX", parent=styles["Normal"], fontName="Helvetica",
    fontSize=12, leading=15, alignment=TA_CENTER, spaceAfter=18,
    textColor=colors.HexColor("#404040"),
)
h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=17, leading=21, spaceBefore=14, spaceAfter=8,
    textColor=colors.HexColor("#1f3864"),
)
h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=13.5, leading=17, spaceBefore=10, spaceAfter=4,
    textColor=colors.HexColor("#2e5597"),
)
h3 = ParagraphStyle(
    "H3", parent=styles["Heading3"], fontName="Helvetica-Bold",
    fontSize=11.5, leading=14, spaceBefore=8, spaceAfter=2,
    textColor=colors.HexColor("#333333"),
)
body = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Helvetica",
    fontSize=10.5, leading=14, alignment=TA_JUSTIFY, spaceAfter=6,
)
body_tight = ParagraphStyle(
    "BodyTight", parent=body, spaceAfter=2,
)
ans_style = ParagraphStyle(
    "Ans", parent=body, fontName="Helvetica-Bold",
    textColor=colors.HexColor("#0b5d2c"), spaceAfter=4,
)
note_style = ParagraphStyle(
    "Note", parent=body, fontName="Helvetica-Oblique",
    textColor=colors.HexColor("#555555"),
)
code_style = ParagraphStyle(
    "Code", parent=styles["Code"], fontName="Courier",
    fontSize=9, leading=11, leftIndent=10, spaceBefore=4, spaceAfter=8,
    textColor=colors.HexColor("#222222"),
    backColor=colors.HexColor("#f4f5f7"),
    borderColor=colors.HexColor("#d0d4da"),
    borderWidth=0.5, borderPadding=6,
)


def P(text, style=body):
    return Paragraph(text, style)


def CODE(text):
    return Preformatted(text, code_style)


def hr_rule():
    t = Table([[""]], colWidths=[6.5 * inch], rowHeights=[0.05 * inch])
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 0.6, colors.HexColor("#bbbbbb")),
    ]))
    return t


# ---------------------------------------------------------------------------
# Document content
# ---------------------------------------------------------------------------
story = []

# ---- Title page -----------------------------------------------------------
story.append(Spacer(1, 0.6 * inch))
story.append(P("CIS 761 — Database Management Systems", title_style))
story.append(P("Exam 2 — Worked Solutions &amp; Concept Guide", subtitle_style))
story.append(Spacer(1, 0.1 * inch))
story.append(P(
    "This document solves every question on Exam 2 and explains the "
    "underlying database concepts in detail. Section A is a concept "
    "primer that covers <i>everything</i> the exam touches: triggers, "
    "stored procedures, user-defined functions, transactions and the "
    "ACID properties, isolation levels and concurrency anomalies, "
    "indexes, B+ trees (including step-by-step insertion and deletion "
    "rules), and the MapReduce programming model. Sections I–IV then "
    "present each exam question with the correct answer in green and a "
    "thorough explanation in plain English.",
    body))
story.append(Spacer(1, 0.25 * inch))

toc_data = [
    ["Section", "Topic", "Points"],
    ["A", "Concept Primer (background reading)", "—"],
    ["I", "True / False Questions", "10"],
    ["II", "Multiple-Choice Questions", "10"],
    ["III", "Triggers & MapReduce", "15"],
    ["IV", "Indexes and B+ Trees", "15"],
    ["", "Total exam points", "50"],
]
toc = Table(toc_data, colWidths=[0.9 * inch, 4.4 * inch, 1.0 * inch])
toc.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3864")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10.5),
    ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ("ALIGN", (2, 0), (2, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
        [colors.whitesmoke, colors.HexColor("#eef2f8")]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
]))
story.append(toc)
story.append(PageBreak())

# ---------------------------------------------------------------------------
# SECTION A — Concept primer
# ---------------------------------------------------------------------------
story.append(P("Section A — Concept Primer", h1))
story.append(P(
    "Read this section first if any of the topics feel unfamiliar. "
    "Each subsection introduces the concept in plain language, then "
    "states the technical rules you need to apply on the exam.",
    body))

# ---- Triggers -------------------------------------------------------------
story.append(P("A.1 — Triggers", h2))
story.append(P(
    "A <b>trigger</b> is a named block of SQL/PL-SQL code that the DBMS "
    "fires <i>automatically</i> in response to an INSERT, UPDATE, or "
    "DELETE event on a specific table or view. The user never calls a "
    "trigger directly; the database engine invokes it as part of the "
    "modifying statement.",
    body))
story.append(P("Anatomy of a trigger", h3))
story.append(ListFlowable([
    ListItem(P("<b>Event</b> — INSERT, UPDATE, or DELETE (and optionally "
               "the specific column for UPDATE OF col).", body_tight)),
    ListItem(P("<b>Timing</b> — <code>BEFORE</code> (run before the row "
               "change is applied; useful for validation/transformation) "
               "or <code>AFTER</code> (run after the change; useful for "
               "auditing/cascading actions).", body_tight)),
    ListItem(P("<b>Granularity</b> — <code>FOR EACH ROW</code> (row-level: "
               "fires once per affected row, exposes <code>OLD</code> and "
               "<code>NEW</code> pseudo-records) or <code>FOR EACH "
               "STATEMENT</code> (statement-level: fires once regardless "
               "of how many rows are touched).", body_tight)),
    ListItem(P("<b>Body</b> — a PL/SQL block (BEGIN … END) containing "
               "any legal SQL plus control-flow (IF/LOOP/etc.).",
               body_tight)),
], bulletType="bullet"))
story.append(P("Why triggers exist", h3))
story.append(ListFlowable([
    ListItem(P("Enforce <i>complex</i> integrity constraints that go "
               "beyond CHECK / FOREIGN KEY (e.g. cross-table rules).",
               body_tight)),
    ListItem(P("Maintain derived data automatically (totals, counts, "
               "history tables).", body_tight)),
    ListItem(P("Audit logging — record who changed what and when.",
               body_tight)),
    ListItem(P("Cascading business actions (send notification, write "
               "into a queue, delete dependent records).", body_tight)),
], bulletType="bullet"))

# ---- Stored procedures ----------------------------------------------------
story.append(P("A.2 — Stored Procedures", h2))
story.append(P(
    "A <b>stored procedure</b> is a named, pre-compiled block of SQL "
    "stored in the database. Unlike triggers, stored procedures are "
    "called <i>explicitly</i> by an application (<code>CALL "
    "proc(args)</code> / <code>EXEC proc args</code>). They accept "
    "input and output parameters and may return result sets.",
    body))
story.append(P("Benefits", h3))
story.append(ListFlowable([
    ListItem(P("<b>Performance</b> — parsed and optimized once; the "
               "server caches the execution plan.", body_tight)),
    ListItem(P("<b>Data quality</b> — every application calls the "
               "<i>same</i> validated SQL, removing ad-hoc query bugs.",
               body_tight)),
    ListItem(P("<b>Security</b> — users can be granted EXECUTE on the "
               "procedure without being granted direct DML on the "
               "underlying tables. Procedures may run with definer "
               "privileges, hiding the schema.", body_tight)),
    ListItem(P("<b>Maintainability</b> — business logic lives in one "
               "place rather than copy-pasted across applications.",
               body_tight)),
], bulletType="bullet"))
story.append(P(
    "Most DBMS products separate the privilege to <i>create</i> "
    "procedures (CREATE PROCEDURE) from the privilege to <i>execute</i> "
    "them. A DBA grants CREATE PROCEDURE only to trusted developers; "
    "this prevents arbitrary users from injecting code into the schema.",
    body))

# ---- UDFs -----------------------------------------------------------------
story.append(P("A.3 — User-Defined Functions (UDFs)", h2))
story.append(P(
    "A UDF is a named function stored in the database that can be "
    "called from inside SQL expressions. There are two kinds:",
    body))
story.append(ListFlowable([
    ListItem(P("<b>Scalar UDF</b> — returns <i>exactly one</i> scalar "
               "value (a number, string, date, etc.). Usable anywhere "
               "a scalar expression is allowed.", body_tight)),
    ListItem(P("<b>Table-valued UDF</b> — returns a result set; usable "
               "in the FROM clause like a view.", body_tight)),
], bulletType="bullet"))
story.append(P(
    "If you need to return multiple values, use either a "
    "table-valued function or a stored procedure with OUT parameters. "
    "A scalar UDF cannot return multiple scalar values — that is a "
    "frequent exam trap.",
    body))

# ---- Transactions ---------------------------------------------------------
story.append(P("A.4 — Transactions and the ACID Properties", h2))
story.append(P(
    "A <b>transaction</b> is a logical unit of work that takes the "
    "database from one consistent state to another. The DBMS guarantees "
    "the four ACID properties:",
    body))
acid_data = [
    ["Property", "Guarantee", "Example"],
    ["Atomicity", "All operations succeed or none of them do.",
     "Bank transfer either debits and credits, or leaves both rows alone."],
    ["Consistency", "Each transaction takes the DB from a valid state to "
     "another valid state, preserving every integrity constraint.",
     "Invariant x + y = constant holds before and after the txn."],
    ["Isolation", "Concurrent transactions appear to execute serially.",
     "Two concurrent transfers don't see each other's intermediate writes."],
    ["Durability", "Once committed, changes survive crashes.",
     "After COMMIT, a power failure does not lose the update."],
]
acid_t = Table(acid_data, colWidths=[1.0 * inch, 2.5 * inch, 2.9 * inch])
acid_t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e5597")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
        [colors.whitesmoke, colors.HexColor("#eef2f8")]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
]))
story.append(acid_t)
story.append(Spacer(1, 0.1 * inch))
story.append(P(
    "If you do not start an explicit transaction with <code>BEGIN "
    "TRANSACTION</code>, most DBMSes run in <b>auto-commit</b> mode: "
    "every individual SQL statement is wrapped in its own implicit "
    "BEGIN…COMMIT pair, so each statement is its own atomic unit.",
    body))

# ---- Isolation levels & anomalies -----------------------------------------
story.append(P("A.5 — Isolation Levels and Concurrency Anomalies", h2))
story.append(P(
    "The SQL standard defines four isolation levels. Stricter levels "
    "prevent more anomalies but reduce concurrency.",
    body))
iso_data = [
    ["Anomaly", "What goes wrong"],
    ["Dirty read",
     "T1 reads a value that T2 has written but not yet committed. If T2 "
     "rolls back, T1 saw a value that never existed."],
    ["Lost update",
     "T1 and T2 both read x=v. Each computes a new value from v and writes "
     "back. The second write overwrites the first; T1's update is lost."],
    ["Non-repeatable read",
     "T1 reads row R, T2 updates R and commits, T1 reads R again and gets a "
     "different value within the same transaction."],
    ["Phantom read",
     "T1 runs a range query, T2 inserts a new row that satisfies the "
     "predicate and commits, T1 re-runs the query and now sees a 'phantom' "
     "extra row."],
]
iso_t = Table(iso_data, colWidths=[1.6 * inch, 4.8 * inch])
iso_t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e5597")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
        [colors.whitesmoke, colors.HexColor("#eef2f8")]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
]))
story.append(iso_t)
story.append(Spacer(1, 0.06 * inch))
levels_data = [
    ["Isolation level", "Dirty read", "Non-repeatable", "Phantom"],
    ["READ UNCOMMITTED", "possible", "possible", "possible"],
    ["READ COMMITTED",   "prevented", "possible", "possible"],
    ["REPEATABLE READ",  "prevented", "prevented", "possible"],
    ["SERIALIZABLE",     "prevented", "prevented", "prevented"],
]
lv_t = Table(levels_data, colWidths=[2.0 * inch, 1.4 * inch,
                                     1.6 * inch, 1.4 * inch])
lv_t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e5597")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
        [colors.whitesmoke, colors.HexColor("#eef2f8")]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
]))
story.append(lv_t)
story.append(Spacer(1, 0.08 * inch))
story.append(P(
    "<b>SERIALIZABLE</b> is the strictest level and produces an "
    "execution equivalent to running the transactions one at a time. "
    "It prevents all anomalies — including lost updates and phantoms — "
    "but it acquires the most locks (or relies on heavy-weight snapshot "
    "validation), which can severely hurt throughput.",
    body))

# ---- Indexes --------------------------------------------------------------
story.append(P("A.6 — Indexes", h2))
story.append(P(
    "An <b>index</b> is an auxiliary data structure that maps key "
    "values to the locations of matching rows in a table. The DBMS "
    "uses an index to find rows without scanning the entire table, so "
    "queries that filter or join on indexed columns run much faster. "
    "The trade-off is that every INSERT/UPDATE/DELETE must also update "
    "the index, so writes get slower.",
    body))
story.append(ListFlowable([
    ListItem(P("<b>Clustered index</b> — the table is physically stored "
               "in index key order. Each table can have at most one. "
               "(In SQL Server it is the default for the primary key; "
               "in MySQL InnoDB the primary key always clusters.)",
               body_tight)),
    ListItem(P("<b>Non-clustered (secondary) index</b> — a separate "
               "structure whose leaves contain the key plus a pointer "
               "to the actual row. A table can have many.",
               body_tight)),
    ListItem(P("<b>Unique index</b> — automatically created by most "
               "DBMSes whenever you declare a UNIQUE or PRIMARY KEY "
               "constraint, because the index is what lets the engine "
               "check duplicates in O(log n) time.", body_tight)),
    ListItem(P("<b>B+ tree index</b> — supports equality <i>and</i> "
               "range queries. <b>Hash index</b> — supports equality "
               "only.", body_tight)),
], bulletType="bullet"))

# ---- B+ trees -------------------------------------------------------------
story.append(P("A.7 — B+ Trees", h2))
story.append(P(
    "A B+ tree is the workhorse data structure for disk-resident "
    "indexes. It is a balanced multi-way search tree with these key "
    "properties:",
    body))
story.append(ListFlowable([
    ListItem(P("<b>All data lives in the leaves.</b> Internal nodes "
               "store only routing keys (separators).", body_tight)),
    ListItem(P("<b>Perfectly height-balanced.</b> Every root-to-leaf "
               "path has <i>exactly</i> the same length. Search, insert, "
               "and delete all run in O(log<sub>d</sub>&nbsp;n) I/Os.",
               body_tight)),
    ListItem(P("<b>Leaves are linked.</b> Each leaf points to the next "
               "(usually doubly-linked), so a range scan is one "
               "downward traversal followed by a leaf-list walk.",
               body_tight)),
    ListItem(P("<b>Fan-out parameter d.</b> An internal node (other "
               "than the root) holds between d and 2d keys, i.e. "
               "between d+1 and 2d+1 child pointers. A leaf holds "
               "between d and 2d data entries.", body_tight)),
], bulletType="bullet"))

story.append(P("Insertion algorithm", h3))
story.append(ListFlowable([
    ListItem(P("Walk from the root to the appropriate leaf.",
               body_tight)),
    ListItem(P("Insert the new key in the leaf in sorted order.",
               body_tight)),
    ListItem(P("If the leaf now has more than 2d keys, <b>split</b> it "
               "in half. <i>Copy up</i> the smallest key of the right "
               "half into the parent (the key remains in the right "
               "leaf as well — leaves keep all data).", body_tight)),
    ListItem(P("If an internal node overflows, split and <b>push up</b> "
               "the middle key into the parent (this key leaves the "
               "child entirely — internal nodes are not data).",
               body_tight)),
    ListItem(P("If the root splits, a brand new root is created above "
               "it. This is the only way the tree grows in height.",
               body_tight)),
], bulletType="bullet"))

story.append(P("Deletion algorithm", h3))
story.append(ListFlowable([
    ListItem(P("Walk to the leaf and remove the key.", body_tight)),
    ListItem(P("If the leaf still has &ge; d keys, you are done.",
               body_tight)),
    ListItem(P("Otherwise the leaf <b>underflows</b>. Try "
               "<b>redistribution</b>: borrow a key from a sibling that "
               "has &gt; d keys and update the separator key in the "
               "parent.", body_tight)),
    ListItem(P("If neither sibling can lend, <b>merge</b> with a "
               "sibling and pull the separator key down from the "
               "parent. The parent may now underflow; recurse upward.",
               body_tight)),
    ListItem(P("If merging propagates to the root and the root ends up "
               "empty, delete the root — the tree shrinks by one level.",
               body_tight)),
], bulletType="bullet"))

# ---- MapReduce ------------------------------------------------------------
story.append(P("A.8 — MapReduce", h2))
story.append(P(
    "MapReduce is a programming model for processing very large data "
    "sets on a cluster. The user writes only two functions, "
    "<code>map</code> and <code>reduce</code>; the framework handles "
    "scheduling, parallelism, data movement, and fault tolerance.",
    body))
story.append(P("Pipeline phases (in execution order)", h3))
story.append(ListFlowable([
    ListItem(P("<b>Map</b> — each mapper reads input records as "
               "(k, v) and emits zero or more intermediate "
               "(k', v') pairs.", body_tight)),
    ListItem(P("<b>Combiner</b> (optional) — a mini-reducer that runs "
               "on the mapper's machine to pre-aggregate values for "
               "the same key, reducing network traffic. Must be "
               "associative and commutative.", body_tight)),
    ListItem(P("<b>Partitioner</b> — assigns each intermediate key to "
               "exactly one reducer (default = "
               "<code>hash(k') mod R</code>).", body_tight)),
    ListItem(P("<b>Shuffle &amp; Sort</b> — the framework transfers "
               "intermediate data across the network and sorts it so "
               "that each reducer receives <i>all</i> values for its "
               "keys, grouped together and sorted by key.",
               body_tight)),
    ListItem(P("<b>Reduce</b> — for each intermediate key, the reducer "
               "receives (k', list-of-v') and emits the final output.",
               body_tight)),
], bulletType="bullet"))
story.append(P(
    "<b>Data locality</b> is a core MapReduce design principle: the "
    "framework schedules mapper tasks on (or near) the cluster nodes "
    "that physically hold the input data blocks (in HDFS), so that the "
    "expensive part — moving bytes over the network — happens only "
    "during shuffle and not during map.",
    body))
story.append(P(
    "A mapper may emit <b>any number</b> of intermediate pairs per "
    "input record, including zero. A filter mapper, for example, emits "
    "nothing for records that fail its predicate.",
    body))

story.append(PageBreak())

# ---------------------------------------------------------------------------
# SECTION I — True/False
# ---------------------------------------------------------------------------
story.append(P("Section I — True / False Questions", h1))

tf = [
    ("Q1.",
     "A trigger can only be used for audit purposes, i.e., to update a "
     "log file/table when the audited data file/table changes.",
     "FALSE",
     "Triggers are far more versatile than auditing. Because the "
     "trigger body is an arbitrary PL/SQL block, it can enforce "
     "complex business rules, maintain referential integrity, cascade "
     "changes to related tables, send notifications, compute derived "
     "values, or block invalid operations. Auditing is just one common "
     "use case."),
    ("Q2.",
     "Quality of data can be improved by using stored procedures. Each "
     "user interaction will use the same set of SQL statements for "
     "transactions, ensuring consistency and accuracy.",
     "TRUE",
     "Centralising business logic inside stored procedures means every "
     "application calls the <i>same</i> tested, validated code. Ad-hoc "
     "queries cannot bypass the validation rules, which improves "
     "consistency and accuracy of the stored data."),
    ("Q3.",
     "Not all users may be permitted to write stored procedures. "
     "Selected users are granted permission to write procedures. This "
     "ensures data security.",
     "TRUE",
     "In every major DBMS (SQL Server, PostgreSQL, Oracle, MySQL) the "
     "CREATE PROCEDURE privilege is a separate grant from the DML "
     "privileges. A DBA gives CREATE PROCEDURE only to trusted "
     "developers, which limits the risk of malicious or buggy code "
     "entering the schema."),
    ("Q4.",
     "A user-defined function can return multiple scalar values.",
     "FALSE",
     "A <i>scalar</i> UDF returns exactly one scalar value — that's "
     "what 'scalar' means. To return many values, use a table-valued "
     "function (which returns a result set) or a stored procedure with "
     "OUT parameters."),
    ("Q5.",
     "In a B+ tree the lengths of the paths from the root to all leaf "
     "nodes differ from each other by at most 1.",
     "FALSE",
     "B+ trees are <i>perfectly</i> height-balanced: every root-to-leaf "
     "path has <i>exactly</i> the same length, not 'at most 1'. "
     "(The 'at most 1' rule describes AVL trees.) This zero-difference "
     "balance is what gives B+ trees worst-case "
     "O(log<sub>d</sub>&nbsp;n) search time."),
    ("Q6.",
     "The DBMS automatically creates a non-clustered index on every "
     "unique attribute (or group of attributes) to enforce the UNIQUE "
     "KEY constraint.",
     "TRUE",
     "When you declare UNIQUE, the engine has to detect duplicates on "
     "every insert/update. The cheapest way to do that is to maintain "
     "a unique index, so SQL Server, MySQL InnoDB, PostgreSQL, etc. "
     "all create one automatically. The index is non-clustered unless "
     "the unique column happens to be the primary key."),
    ("Q7.",
     "If you don't group statements into explicit transactions, SQL "
     "automatically treats each SQL statement as a separate "
     "transaction.",
     "TRUE",
     "This is <b>auto-commit mode</b>: each statement is wrapped in an "
     "implicit BEGIN…COMMIT pair. Changes become permanent immediately "
     "after the statement, so you cannot roll back across multiple "
     "statements unless you opened an explicit transaction with "
     "<code>BEGIN TRANSACTION</code>."),
    ("Q8.",
     "Concurrency is a problem when data is being modified but not "
     "when two or more transactions simply read the same data.",
     "TRUE",
     "Read-only transactions cannot conflict with one another because "
     "reading does not change state. All concurrency anomalies (dirty "
     "read, lost update, non-repeatable read, phantom) require at "
     "least one writer."),
    ("Q9.",
     "In MapReduce, a mapper must generate at least one key/value "
     "intermediate pair for each input key/value pair.",
     "FALSE",
     "A mapper may emit <b>zero, one, or many</b> intermediate pairs "
     "per input record. A filter mapper, for instance, emits nothing "
     "when the input record fails its predicate."),
    ("Q10.",
     "To determine the frequency of each non-stopword (instead of "
     "every word), you need to change ONLY the map() function in the "
     "WordCount pseudocode.",
     "TRUE",
     "Stopword filtering belongs entirely to the mapper: before "
     "emitting <code>(word, 1)</code>, the mapper checks whether the "
     "word is in the stopword list and skips it. The reducer, which "
     "simply sums the 1s for each key it receives, does not need any "
     "modification."),
]

for num, q, ans, expl in tf:
    flow = [
        P(f"<b>{num}</b> {q}", body),
        P(f"Answer: {ans}", ans_style),
        P(f"<b>Explanation.</b> {expl}", body),
        Spacer(1, 0.05 * inch),
    ]
    story.append(KeepTogether(flow))

story.append(PageBreak())

# ---------------------------------------------------------------------------
# SECTION II — Multiple Choice
# ---------------------------------------------------------------------------
story.append(P("Section II — Multiple-Choice Questions", h1))

mcq = [
    ("Q1.",
     "A B+ tree with four levels (including the root) — what is the "
     "maximum number of NEWLY CREATED nodes when inserting one key?",
     [("a", "5"),
      ("b", "4"),
      ("c", "3"),
      ("d", "2")],
     "b",
     "The worst case is when a leaf split cascades all the way to the "
     "root. With 4 levels, splitting can happen at every level, and "
     "<i>each split creates exactly one new node</i>: one new sibling "
     "leaf, one new sibling at each internal level, and one new root "
     "when the original root splits. That is 4 new nodes total, one "
     "per level. Option (a) 5 would require 5 levels of splits."),
    ("Q2.",
     "A named set of SQL statements configured to run automatically "
     "when data modifications occur is called ___.",
     [("a", "aggregate function"),
      ("b", "stored procedure"),
      ("c", "trigger"),
      ("d", "view")],
     "c",
     "A <b>trigger</b> fires automatically in response to "
     "INSERT/UPDATE/DELETE — no user calls it. A stored procedure "
     "runs only when explicitly invoked. An aggregate function (SUM, "
     "COUNT, …) is a calculation. A view is a stored query."),
    ("Q3.",
     "If you delete and then recreate a stored procedure, function, "
     "or trigger…",
     [("a", "you delete the tables on which the object is based"),
      ("b", "you disable access to the tables on which the object is "
             "based"),
      ("c", "you delete the security permissions assigned to the "
             "deleted object"),
      ("d", "none of the above")],
     "c",
     "Dropping any database object also drops the GRANT/REVOKE "
     "permissions attached to it. The underlying tables are not "
     "affected at all. After recreating the object, the DBA must "
     "re-grant the necessary EXECUTE permissions."),
    ("Q4.",
     "The purpose of an index in SQL is:",
     [("a", "to enforce data integrity constraints"),
      ("b", "to store intermediate query results"),
      ("c", "to improve the speed of data retrieval operations"),
      ("d", "to perform calculations on aggregate data")],
     "c",
     "An index is a separate data structure (B+ tree, hash table, …) "
     "that maps key values to row locations, letting the optimiser "
     "find matching rows without scanning the whole table. Integrity "
     "is enforced by constraints; intermediate results live in temp "
     "tables/CTEs; aggregations are done by aggregate functions."),
    ("Q5.",
     "A <b>lost update</b> occurs when:",
     [("a", "an insert by another transaction affects rows being "
             "updated"),
      ("b", "a transaction selects uncommitted data"),
      ("c", "two transactions read the same row and then update it "
             "based on the original values"),
      ("d", "two SELECTs get different values because of an "
             "intervening update")],
     "c",
     "Classic lost-update: T1 reads x = 100, T2 reads x = 100, T1 "
     "writes x = 150, T2 writes x = 120. T1's write is overwritten — "
     "'lost' — because T2 computed its new value from a stale read. "
     "Option (b) is a dirty read; option (d) is a non-repeatable read."),
    ("Q6.",
     "One drawback of using the SERIALIZABLE isolation level is:",
     [("a", "it can result in lost updates"),
      ("b", "it allows too many transactions simultaneously"),
      ("c", "it can cause severe performance problems"),
      ("d", "it can cause security problems")],
     "c",
     "SERIALIZABLE is the strictest level. It either acquires range "
     "locks (2-phase locking) or relies on heavy-weight snapshot "
     "validation (SSI). Either way, concurrency drops sharply and "
     "throughput suffers. SERIALIZABLE actually <i>prevents</i> lost "
     "updates and has nothing to do with security."),
    ("Q7.",
     "The transaction <code>read(x); x:=x-50; write(x); read(y); "
     "y:=y+50; write(y)</code> — the constraint that x+y stays "
     "constant is which ACID property?",
     [("a", "Atomicity"),
      ("b", "Consistency"),
      ("c", "Isolation"),
      ("d", "Durability")],
     "b",
     "<b>Consistency</b> says the transaction must take the database "
     "from one valid state to another, preserving all integrity "
     "constraints. The invariant x + y = constant is exactly such a "
     "constraint. Atomicity = all-or-nothing; Isolation = no "
     "interference between concurrent transactions; Durability = "
     "committed changes survive crashes."),
    ("Q8.",
     "Select the correct statement about MapReduce:",
     [("a", "MapReduce tries to place the data and the compute as "
             "close as possible"),
      ("b", "Map Task is performed using Mapper() function"),
      ("c", "Reduce Task is performed using Map() function"),
      ("d", "All of the mentioned")],
     "a",
     "Data locality is a core design principle of Hadoop / MapReduce: "
     "mappers are scheduled on (or near) the nodes that already hold "
     "the input HDFS blocks, so input bytes do not have to travel "
     "across the network. Option (b) is loosely worded but the "
     "function is <code>map()</code>, not <code>Mapper()</code>; "
     "option (c) is just wrong (reduce tasks call <code>reduce()</code>); "
     "so (d) is wrong as well."),
    ("Q9.",
     "Which component maps input key/value pairs to intermediate "
     "key/value pairs?",
     [("a", "Mapper"),
      ("b", "Reducer"),
      ("c", "Combiner"),
      ("d", "Partitioner")],
     "a",
     "By definition, the Mapper takes each input (k, v) and emits "
     "zero or more intermediate (k', v') pairs. The Reducer aggregates "
     "values that share an intermediate key; the Combiner is an "
     "optional local mini-reducer; the Partitioner just routes "
     "intermediate keys to the right reducer."),
    ("Q10.",
     "Put the MapReduce phases in execution order:",
     [("a", "Mapper → Reducer → Partitioner → Shuffle&amp;Sort → "
             "Combiner"),
      ("b", "Mapper → Partitioner → Combiner → Reducer → "
             "Shuffle&amp;Sort"),
      ("c", "Mapper → Shuffle&amp;Sort → Reducer → Combiner → "
             "Partitioner"),
      ("d", "Mapper → Combiner → Partitioner → Shuffle&amp;Sort → "
             "Reducer")],
     "d",
     "Execution order: (1) <b>Mapper</b> reads input and emits "
     "intermediate (k, v). (2) <b>Combiner</b> (optional) locally "
     "pre-aggregates mapper output to reduce network traffic. (3) "
     "<b>Partitioner</b> assigns each key to a specific reducer. (4) "
     "<b>Shuffle &amp; Sort</b> moves and sorts the intermediate data "
     "by key so each reducer gets all values for its keys. (5) "
     "<b>Reducer</b> processes each key group and writes the final "
     "output."),
]

for num, q, options, correct, expl in mcq:
    parts = [P(f"<b>{num}</b> {q}", body)]
    for letter, text in options:
        marker = "&#9679;" if letter == correct else "&#9675;"
        line = f"&nbsp;&nbsp;&nbsp;{marker} <b>{letter}.</b> {text}"
        parts.append(P(line, body_tight))
    parts.append(P(f"Answer: ({correct})", ans_style))
    parts.append(P(f"<b>Explanation.</b> {expl}", body))
    parts.append(Spacer(1, 0.05 * inch))
    story.append(KeepTogether(parts))

story.append(PageBreak())

# ---------------------------------------------------------------------------
# SECTION III — Triggers & MapReduce
# ---------------------------------------------------------------------------
story.append(P("Section III — Triggers &amp; MapReduce", h1))

story.append(P("Schema", h3))
story.append(CODE(
    "Highschooler(ID, name, grade)   -- one row per student\n"
    "Friend(ID1, ID2)                -- mutual friendship\n"
    "                                -- (A,B) is also stored as (B,A)\n"
    "Likes(ID1, ID2)                 -- ID1 likes ID2 (one-directional)"
))

# ---- III.Q1 ---------------------------------------------------------------
story.append(P("Q1 [5 pts] — Trigger: delete a student when grade > 12",
               h2))
story.append(P(
    "We need an <code>AFTER UPDATE</code> trigger on the grade column. "
    "Whenever a row's grade is set above 12, the student has graduated, "
    "so the row is deleted from <code>Highschooler</code>.",
    body))
story.append(CODE(
"""CREATE TRIGGER delete_graduated
AFTER UPDATE OF grade ON Highschooler
FOR EACH ROW
WHEN (NEW.grade > 12)
BEGIN
    DELETE FROM Highschooler
    WHERE  ID = :NEW.ID;
END;"""))
story.append(P("Why this works", h3))
story.append(ListFlowable([
    ListItem(P("<b>AFTER UPDATE OF grade</b> — the trigger fires only "
               "when the grade column changes, not on every column "
               "update.", body_tight)),
    ListItem(P("<b>FOR EACH ROW</b> — row-level granularity, so we "
               "have access to <code>NEW</code>/<code>OLD</code> "
               "pseudo-records for the row that just changed.",
               body_tight)),
    ListItem(P("<b>WHEN (NEW.grade &gt; 12)</b> — the trigger body runs "
               "only for rows whose new grade is past senior year. "
               "Equivalently you can wrap the DELETE in <code>IF "
               "NEW.grade &gt; 12 THEN … END IF;</code>.", body_tight)),
    ListItem(P("If <code>Friend</code> and <code>Likes</code> have "
               "foreign keys to <code>Highschooler</code> with "
               "<code>ON DELETE CASCADE</code>, related rows will be "
               "removed automatically; otherwise the schema designer "
               "must add additional triggers or FK actions.",
               body_tight)),
], bulletType="bullet"))

# ---- III.Q2 ---------------------------------------------------------------
story.append(P("Q2 [5 pts] — MapReduce: number of friends per student",
               h2))
story.append(P(
    "Because the <code>Friend</code> table stores friendships in both "
    "directions — both <code>(A,B)</code> and <code>(B,A)</code> are "
    "present — we can count friends with the simplest possible "
    "MapReduce job. Every row contributes +1 to the friend count of "
    "<code>ID1</code>.",
    body))
story.append(CODE(
"""map(key, value):
    # value is one row from the Friend table: (ID1, ID2)
    (ID1, ID2) = parse(value)
    emit(ID1, 1)

reduce(key, values):
    # key    = a student ID
    # values = a list of 1's, one per friend relationship
    count = 0
    for v in values:
        count = count + v
    emit(key, count)        # output: (student_ID, #friends)"""))
story.append(P("Why this works", h3))
story.append(P(
    "Because both <code>(A,B)</code> and <code>(B,A)</code> are stored, "
    "the mapper that processes <code>(A,B)</code> emits "
    "<code>(A, 1)</code> and the mapper that processes "
    "<code>(B,A)</code> emits <code>(B, 1)</code>. After shuffle, each "
    "student's reducer receives one '1' per friend relationship. "
    "Summing the list gives the friend count, with no special "
    "handling for symmetry.",
    body))
story.append(P(
    "(If the table were stored only one way, the mapper would have "
    "had to emit <code>(ID1, 1)</code> <i>and</i> <code>(ID2, 1)</code> "
    "for each row.)",
    note_style))

# ---- III.Q3 ---------------------------------------------------------------
story.append(P("Q3 [5 pts] — MapReduce: find mutual likes", h2))
story.append(P(
    "<i>Goal:</i> output every pair (A, B) such that both <code>(A "
    "likes B)</code> and <code>(B likes A)</code> appear in the "
    "<code>Likes</code> table — once per mutual pair, in lexicographic "
    "order.",
    body))
story.append(P(
    "<b>Idea.</b> If we make the <i>unordered</i> pair "
    "<code>(min(ID1,ID2), max(ID1,ID2))</code> the intermediate key, "
    "both directions of the same friendship hash to the <i>same</i> "
    "reducer. The reducer then receives the original directed pairs "
    "as values and only has to check that both directions are "
    "present.",
    body))
story.append(CODE(
"""map(key, value):
    # value is one row from the Likes table: (ID1, ID2)
    (ID1, ID2) = parse(value)
    A = min(ID1, ID2)
    B = max(ID1, ID2)
    emit( (A, B), (ID1, ID2) )      # key = unordered pair

reduce(key, values):
    # key = (A, B) with A < B
    # values = list of directed (id1, id2) pairs that map to this key
    forward  = False                # did A like B?
    backward = False                # did B like A?
    (A, B) = key
    for (id1, id2) in values:
        if id1 == A and id2 == B: forward  = True
        if id1 == B and id2 == A: backward = True
    if forward and backward:
        emit(key, "mutual")         # output: (A, B)"""))
story.append(P("Why this works", h3))
story.append(ListFlowable([
    ListItem(P("Both <code>(A,B)</code> and <code>(B,A)</code> generate "
               "the same key <code>(min, max)</code>, so MapReduce "
               "delivers them to the <i>same</i> reducer.",
               body_tight)),
    ListItem(P("The reducer flags whether each direction was seen and "
               "emits the pair exactly once when both flags are true.",
               body_tight)),
    ListItem(P("Using <code>(min, max)</code> as the key automatically "
               "produces the pair in lexicographic order, so we never "
               "output a duplicate <code>(B, A)</code>.", body_tight)),
], bulletType="bullet"))

story.append(PageBreak())

# ---------------------------------------------------------------------------
# SECTION IV — B+ Trees
# ---------------------------------------------------------------------------
story.append(P("Section IV — Indexes and B+ Trees", h1))

story.append(P("Starting tree (degree d = 2)", h3))
story.append(P(
    "Each non-root internal node holds 2 to 4 keys (3 to 5 child "
    "pointers); each leaf holds 2 to 4 keys.",
    body))
story.append(CODE(
"""Level 0 (root):       [ 20 ]
Level 1 (internal):   [ 6, 10 ]                    [ 30, 40 ]
Level 2 (leaves):
    [ 2, 4 ] -> [ 6, 8, 9 ] -> [ 10, 13 ] -> [ 20, 23 ]
              -> [ 31, 32 ] -> [ 43, 54, 69, 87 ]"""))

# ---- IV.Q1 ----------------------------------------------------------------
story.append(P("Q1 [3 pts] — Range query: 10 &le; key &lt; 40", h2))
story.append(P(
    "B+ tree range queries have two phases: (i) descend from root to "
    "the leftmost leaf containing a key &ge; lo, then (ii) walk the "
    "leaf-level sibling pointers until a key reaches the upper bound.",
    body))
story.append(P("Step-by-step traversal", h3))
story.append(ListFlowable([
    ListItem(P("Visit <b>root [20]</b>. 10 &lt; 20, so follow the "
               "<i>left</i> child pointer.", body_tight)),
    ListItem(P("Visit <b>internal [6, 10]</b>. 10 &ge; 10 (and "
               "10 &ge; 6), so follow the <i>rightmost</i> child "
               "pointer of this node, which leads to leaf [10, 13].",
               body_tight)),
    ListItem(P("Read <b>leaf [10, 13]</b> — keys 10 and 13 are both "
               "in the range. Output them.", body_tight)),
    ListItem(P("Follow the next-leaf pointer to <b>leaf [20, 23]</b> — "
               "both keys still &lt; 40. Output them.", body_tight)),
    ListItem(P("Follow the next-leaf pointer to <b>leaf [31, 32]</b> — "
               "both keys still &lt; 40. Output them.", body_tight)),
    ListItem(P("Follow the next-leaf pointer to <b>leaf [43, 54, 69, "
               "87]</b>. The first key 43 is &ge; 40, so <b>STOP</b>.",
               body_tight)),
], bulletType="bullet"))
story.append(P(
    "<b>Result.</b> Keys returned: 10, 13, 20, 23, 31, 32. "
    "Nodes visited: root + internal [6,10] + four leaves "
    "([10,13], [20,23], [31,32]) — i.e. <b>5 nodes traversed</b> "
    "(plus the leaf [43,54,69,87] is read only to confirm we have "
    "passed the upper bound, depending on convention).",
    body))
story.append(P(
    "This is exactly why B+ trees are the standard structure for "
    "indexes that must support range queries: descent cost is "
    "O(log<sub>d</sub>&nbsp;n), and the rest is a sequential scan.",
    note_style))

# ---- IV.Q2(i) -------------------------------------------------------------
story.append(P("Q2(i) [6 pts] — Insert key 7, then key 70", h2))

story.append(P("Inserting 7", h3))
story.append(ListFlowable([
    ListItem(P("Locate the target leaf: root [20] &rarr; left "
               "(7 &lt; 20) &rarr; internal [6, 10] &rarr; middle "
               "child (6 &le; 7 &lt; 10) &rarr; <b>leaf [6, 8, 9]</b>.",
               body_tight)),
    ListItem(P("That leaf has 3 keys; the maximum is 2d = 4, so we "
               "have room for one more — <b>no split needed</b>.",
               body_tight)),
    ListItem(P("Insert 7 in sorted order: leaf becomes "
               "<b>[6, 7, 8, 9]</b>.", body_tight)),
], bulletType="bullet"))
story.append(CODE(
"""After inserting 7:

Root:         [ 20 ]
Internal:     [ 6, 10 ]                    [ 30, 40 ]
Leaves:
  [2,4] -> [6,7,8,9] -> [10,13] -> [20,23] -> [31,32] -> [43,54,69,87]"""))

story.append(P("Inserting 70", h3))
story.append(ListFlowable([
    ListItem(P("Locate the target leaf: root [20] &rarr; right "
               "(70 &gt; 20) &rarr; internal [30, 40] &rarr; rightmost "
               "child (70 &gt; 40) &rarr; <b>leaf [43, 54, 69, 87]</b>.",
               body_tight)),
    ListItem(P("That leaf is already full (4 keys = 2d). Inserting 70 "
               "tentatively gives <b>[43, 54, 69, 70, 87]</b> — 5 "
               "keys, an overflow. <b>Split.</b>", body_tight)),
    ListItem(P("Split point: take the smallest key of the right half "
               "= 69. Left half keeps [43, 54]; right half = "
               "[69, 70, 87]. The separator <b>69</b> is "
               "<i>copied up</i> to the parent (it is a leaf split, "
               "so the key remains in the right leaf as well).",
               body_tight)),
    ListItem(P("Parent internal node was [30, 40]; it becomes "
               "<b>[30, 40, 69]</b>, which is within the 4-key max — "
               "no further splits.", body_tight)),
    ListItem(P("The root is unchanged.", body_tight)),
], bulletType="bullet"))
story.append(CODE(
"""After also inserting 70:

Root:         [ 20 ]
Internal:     [ 6, 10 ]                  [ 30, 40, 69 ]
Leaves:
  [2,4] -> [6,7,8,9] -> [10,13] -> [20,23] -> [31,32]
        -> [43,54] -> [69,70,87]"""))

# ---- IV.Q2(ii) ------------------------------------------------------------
story.append(P("Q2(ii) [6 pts] — From the original tree: delete 13, "
               "then delete 8", h2))

story.append(P("Deleting 13", h3))
story.append(ListFlowable([
    ListItem(P("Key 13 lives in <b>leaf [10, 13]</b>. After deletion "
               "the leaf has only 1 key — <b>underflow</b> (minimum "
               "is d = 2).", body_tight)),
    ListItem(P("Look at the left sibling <b>[6, 8, 9]</b>: it has 3 "
               "keys, more than the minimum, so we can "
               "<b>redistribute</b> (borrow) instead of merging.",
               body_tight)),
    ListItem(P("Borrow the largest key from the left sibling — "
               "<b>9</b>. Left sibling becomes [6, 8]; the underflowing "
               "leaf becomes [9, 10].", body_tight)),
    ListItem(P("Update the parent separator that used to be 10 (the "
               "old smallest key of the right leaf): the new smallest "
               "key of the right leaf is 9, so the separator changes "
               "from 10 to 9. The internal node [6, 10] becomes "
               "<b>[6, 9]</b>.", body_tight)),
], bulletType="bullet"))
story.append(CODE(
"""After deleting 13:

Root:         [ 20 ]
Internal:     [ 6, 9 ]                    [ 30, 40 ]
Leaves:
  [2,4] -> [6,8] -> [9,10] -> [20,23] -> [31,32] -> [43,54,69,87]"""))

story.append(P("Deleting 8 (continuing from the original tree)", h3))
story.append(P(
    "The exam asks for each deletion <i>independently</i> from the "
    "original tree, so we restart from the starting tree and remove 8.",
    note_style))
story.append(ListFlowable([
    ListItem(P("Key 8 lives in <b>leaf [6, 8, 9]</b>. After deletion "
               "the leaf has 2 keys = d, the minimum — <b>no "
               "underflow</b>.", body_tight)),
    ListItem(P("No redistribution, no merge, no parent updates — the "
               "leaf simply becomes [6, 9].", body_tight)),
], bulletType="bullet"))
story.append(CODE(
"""After deleting 8 (from the ORIGINAL tree):

Root:         [ 20 ]
Internal:     [ 6, 10 ]                   [ 30, 40 ]
Leaves:
  [2,4] -> [6,9] -> [10,13] -> [20,23] -> [31,32] -> [43,54,69,87]"""))

story.append(P("Why these rules", h3))
story.append(ListFlowable([
    ListItem(P("<b>Insert / split (leaf)</b>: copy-up the smallest key "
               "of the right half to the parent — leaves keep <i>all</i> "
               "the data.", body_tight)),
    ListItem(P("<b>Insert / split (internal)</b>: push-up the middle "
               "key — internal nodes only route, and a routing key "
               "exists in exactly one place.", body_tight)),
    ListItem(P("<b>Delete / redistribute</b>: borrow from a sibling "
               "with &gt; d keys; update the parent separator to the "
               "new smallest key of the right neighbour.", body_tight)),
    ListItem(P("<b>Delete / merge</b>: if neither sibling can lend, "
               "merge with one and pull the parent separator down. "
               "Recurse upward if the parent now underflows.",
               body_tight)),
    ListItem(P("<b>Tree height</b> only changes by splitting the root "
               "(grows) or by merging children of a 1-key root "
               "(shrinks).", body_tight)),
], bulletType="bullet"))

# ---------------------------------------------------------------------------
# Quick reference card
# ---------------------------------------------------------------------------
story.append(PageBreak())
story.append(P("Appendix — Quick Reference Card", h1))

ref_data = [
    ["Concept", "Key points to remember"],
    ["Trigger",
     "Auto-fires on INSERT/UPDATE/DELETE; BEFORE vs AFTER; FOR EACH ROW "
     "vs FOR EACH STATEMENT; OLD/NEW pseudo-records."],
    ["Stored procedure",
     "Named, pre-compiled SQL block; called explicitly; CREATE PROCEDURE "
     "is a separate privilege; centralises business logic."],
    ["Scalar UDF",
     "Returns exactly ONE scalar value; usable inside any SQL "
     "expression. For multiple return values use a table-valued "
     "function or a procedure with OUT params."],
    ["ACID",
     "Atomicity (all or nothing), Consistency (invariants preserved), "
     "Isolation (no concurrent interference), Durability (committed "
     "changes survive crashes)."],
    ["Auto-commit",
     "Without explicit BEGIN TRANSACTION, every SQL statement is its "
     "own transaction."],
    ["Isolation levels",
     "READ UNCOMMITTED < READ COMMITTED < REPEATABLE READ < "
     "SERIALIZABLE; higher = fewer anomalies, lower throughput."],
    ["Anomalies",
     "Dirty read, lost update, non-repeatable read, phantom read — "
     "each is removed by progressively stricter levels."],
    ["Index purpose",
     "Speeds up SELECT (especially WHERE/JOIN); slows down "
     "INSERT/UPDATE/DELETE because the index must be maintained."],
    ["Unique constraint",
     "DBMS automatically backs it with a (usually non-clustered) "
     "unique index for fast duplicate detection."],
    ["B+ tree",
     "All data in leaves; leaves linked; perfectly height-balanced; "
     "supports both equality and range queries in "
     "O(log_d n) I/Os."],
    ["B+ tree insert",
     "Find leaf → insert → split if overflow → leaves COPY-UP, "
     "internals PUSH-UP. Tree only grows by root split."],
    ["B+ tree delete",
     "Find leaf → delete → if underflow, redistribute from sibling, "
     "else merge and recurse upward. Tree only shrinks by root merge."],
    ["MapReduce",
     "User writes map() and reduce(); framework handles parallelism, "
     "shuffle, and fault tolerance. Mapper may emit 0/1/many pairs."],
    ["MR phases",
     "Map → Combiner (optional) → Partitioner → Shuffle &amp; Sort → "
     "Reduce."],
    ["Combiner",
     "Local mini-reducer that pre-aggregates mapper output; must be "
     "associative and commutative."],
    ["Partitioner",
     "Routes intermediate keys to specific reducers; default = "
     "hash(key) mod R."],
    ["Data locality",
     "Hadoop schedules mappers on (or near) the nodes that hold the "
     "input HDFS blocks, minimising network I/O."],
]

ref_table_rows = []
for c, k in ref_data:
    ref_table_rows.append([P(f"<b>{c}</b>", body_tight), P(k, body_tight)])
ref_table = Table(ref_table_rows, colWidths=[1.5 * inch, 5.0 * inch])
ref_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3864")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
        [colors.whitesmoke, colors.HexColor("#eef2f8")]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(ref_table)


# ---------------------------------------------------------------------------
# Page footer with page numbers
# ---------------------------------------------------------------------------
def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawString(0.75 * inch, 0.5 * inch,
                      "CIS 761 — Exam 2 Solutions & Concept Guide")
    canvas.drawRightString(LETTER[0] - 0.75 * inch, 0.5 * inch,
                           f"Page {doc.page}")
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(
        "CIS761_Exam2_Solved.pdf",
        pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.7 * inch, bottomMargin=0.8 * inch,
        title="CIS 761 — Exam 2 Worked Solutions & Concept Guide",
        author="CIS 761 Study Notes",
    )
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print("Wrote CIS761_Exam2_Solved.pdf")


if __name__ == "__main__":
    main()
