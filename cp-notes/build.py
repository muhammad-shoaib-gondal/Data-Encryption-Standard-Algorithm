#!/usr/bin/env python3
"""Verify every C++ snippet in NOTES.md, then render it to cpp-cheatsheet.pdf.

    python3 build.py            # verify + build the PDF
    python3 build.py --verify   # only type-check the snippets
    python3 build.py --pdf      # only render the PDF

Needs g++ for verification and Google Chrome for the PDF; the PDF step also
needs the `markdown` and `pygments` packages (pip install markdown pygments).
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTES = HERE / "NOTES.md"
PDF = HERE / "cpp-cheatsheet.pdf"

FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.M | re.S)
PRELUDE = "#include <bits/stdc++.h>\nusing namespace std;\n"


def cpp_blocks(text):
    return [(m.start(), m.group(2)) for m in FENCE.finditer(text) if m.group(1) == "cpp"]


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def verify(text):
    """Type-check the snippets cumulatively.

    Each block is first tried at namespace scope (definitions of functions,
    structs and globals) and then, if that fails, as a function body (loose
    statements). A block that fits neither way is a real error.
    """
    blocks = cpp_blocks(text)
    if not blocks:
        print("no cpp blocks found", file=sys.stderr)
        return False

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        header = tmp / "harness.h"
        header.write_text(PRELUDE)
        subprocess.run(
            ["g++", "-std=gnu++17", "-x", "c++-header", str(header), "-o", str(tmp / "harness.h.gch")],
            check=True,
        )
        src = tmp / "harness.cpp"
        accepted = '#include "harness.h"\n'

        for i, (offset, code) in enumerate(blocks):
            candidates = [code, f"void _block_{i}() {{\n{code}\n}}\n"]
            last_err = ""
            for cand in candidates:
                src.write_text(accepted + f"\n// ---- block {i}\n" + cand)
                res = subprocess.run(
                    ["g++", "-std=gnu++17", "-fsyntax-only", "-I", str(tmp), str(src)],
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0:
                    accepted += f"\n// ---- block {i}\n" + cand
                    break
                last_err = res.stderr
            else:
                print(f"FAILED: NOTES.md block starting at line {line_of(text, offset)}", file=sys.stderr)
                print(code, file=sys.stderr)
                print(last_err, file=sys.stderr)
                return False

    print(f"verified {len(blocks)} C++ snippets")
    return True


CSS = """
@page { size: A4; margin: 11mm 10mm 11mm 10mm; }
* { box-sizing: border-box; }
body {
  font-family: "DejaVu Sans", Arial, sans-serif;
  font-size: 9pt; line-height: 1.38; color: #16181d; margin: 0;
}
h1 { font-size: 19pt; margin: 0 0 3pt; color: #0b1020; }
h1 + p { color: #555; font-size: 8.6pt; margin-top: 0; }
h2 {
  font-size: 12pt; margin: 13pt 0 5pt; padding: 3pt 6pt; color: #fff;
  background: #22303f; border-radius: 3px; break-after: avoid;
}
h3 {
  font-size: 9.8pt; margin: 8pt 0 3pt; color: #0b3d6b;
  border-bottom: 1px solid #cdd7e1; padding-bottom: 1pt; break-after: avoid;
}
p, li { margin: 2.5pt 0; }
ul { margin: 3pt 0 3pt 0; padding-left: 14pt; }
code {
  font-family: "DejaVu Sans Mono", Consolas, monospace; font-size: 8.3pt;
  background: #eef1f5; padding: 0 2px; border-radius: 2px;
}
pre {
  background: #f7f9fb; border: 1px solid #dde3ea; border-left: 3px solid #4a7fb5;
  border-radius: 3px; padding: 3.5pt 6pt; margin: 4pt 0; overflow: hidden;
  break-inside: avoid; page-break-inside: avoid;
}
pre code {
  background: none; padding: 0; font-size: 7.9pt; line-height: 1.3;
  white-space: pre-wrap; word-break: break-word;
}
table { border-collapse: collapse; width: 100%; margin: 5pt 0; font-size: 8.4pt; }
th, td { border: 1px solid #ccd4dd; padding: 1.5pt 5pt; text-align: left; }
th { background: #eaeff5; }
tr:nth-child(even) td { background: #fafbfd; }
hr { display: none; }
strong { color: #0b1020; }
a { color: inherit; text-decoration: none; }
.toc { font-size: 8.2pt; border: 1px solid #dde3ea; margin: 6pt 0;
       background: #fafbfd; padding: 5pt 8pt; border-radius: 3px; }
.toc ul { list-style: none; margin: 0; padding: 0;
          display: flex; flex-wrap: wrap; gap: 2pt 14pt; }
.toc li { white-space: nowrap; }
/* pygments */
.hll { background: #ffc }
.c, .c1, .cm, .cs, .cp, .cpf { color: #6a8a5b; font-style: italic }
.k, .kt, .kd, .kn, .kr { color: #0a5bbd; font-weight: bold }
.s, .s1, .s2, .sc, .se { color: #a03030 }
.m, .mi, .mf, .mh, .mo, .il { color: #7a4ac0 }
.n, .nf, .nc, .nl, .nb { color: #16181d }
.o, .p { color: #444 }
"""

HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>C++ Competitive Programming Notes</title>
<style>{css}</style></head><body>{body}</body></html>
"""


def build_pdf(text):
    import markdown

    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "codehilite", "toc", "sane_lists"],
        extension_configs={
            "codehilite": {"noclasses": False, "guess_lang": False},
            "toc": {"toc_depth": "2-2"},
        },
    )
    body = md.convert(text)
    body = body.replace("<hr />", f'<div class="toc">{md.toc}</div>', 1)
    html_path = HERE / "cpp-cheatsheet.html"
    html_path.write_text(HTML.format(css=CSS, body=body))

    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        print("Chrome not found; wrote HTML only:", html_path)
        return False
    if PDF.exists():
        PDF.unlink()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--virtual-time-budget=10000",
        f"--print-to-pdf={PDF}",
        html_path.as_uri(),
    ]
    # headless Chrome writes the PDF but then sometimes never exits, so wait for
    # the file to stop growing and kill it ourselves
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    last = -1
    for _ in range(180):
        if proc.poll() is not None:
            break
        time.sleep(0.5)
        size = PDF.stat().st_size if PDF.exists() else -1
        if size > 0 and size == last:
            proc.kill()
            break
        last = size
    proc.wait()
    if not PDF.exists():
        print("Chrome did not produce a PDF", file=sys.stderr)
        return False
    print(f"wrote {PDF} ({PDF.stat().st_size // 1024} KB)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--pdf", action="store_true")
    args = ap.parse_args()
    do_all = not (args.verify or args.pdf)

    text = NOTES.read_text()
    if (args.verify or do_all) and not verify(text):
        return 1
    if (args.pdf or do_all) and not build_pdf(text):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
