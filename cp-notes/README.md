# C++ competitive programming notes

A printable reference sheet for contests: STL containers and algorithms,
lambdas, stack / queue / linked list / map / tree, graphs, classic data
structures, dynamic programming patterns, number theory, strings and a bug
checklist.

| File | What it is |
| --- | --- |
| `cpp-cheatsheet.pdf` | **The printable sheet** (A4, 26 pages) |
| `NOTES.md` | Source of the sheet, readable on GitHub |
| `cpp-cheatsheet.html` | Intermediate render, useful for reading on screen |
| `build.py` | Verifies every snippet, then rebuilds the PDF |

## Rebuilding

```bash
pip install markdown pygments        # one time
python3 build.py                     # verify snippets + write the PDF
python3 build.py --verify            # only type-check the C++ snippets
```

`--verify` feeds every ```` ```cpp ```` block in `NOTES.md` to `g++
-std=gnu++17 -fsyntax-only`, cumulatively, so a snippet may use anything
defined in an earlier one. A block is first tried at namespace scope and then
as a function body, which lets the notes mix full definitions with loose
statements. Nothing reaches the PDF unless it compiles.

The PDF step renders the Markdown to HTML (Pygments for highlighting) and
prints it with headless Google Chrome.
