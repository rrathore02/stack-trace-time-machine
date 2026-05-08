"""Generate the beginner-friendly project guide PDF.

Run from the project root:

    python scripts/build_guide_pdf.py

Output: ~/Documents/stt-project-guide.pdf
"""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path(os.path.expanduser("~/Documents/stt-project-guide.pdf"))


# ---------- Styles ----------

styles = getSampleStyleSheet()

TITLE_BLUE = colors.HexColor("#0f3d6e")
ACCENT_BLUE = colors.HexColor("#1d4ed8")
CODE_BG = colors.HexColor("#f1f5f9")
CODE_BORDER = colors.HexColor("#cbd5e1")
GREY_TEXT = colors.HexColor("#475569")

styles.add(
    ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontSize=28,
        leading=34,
        textColor=TITLE_BLUE,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="DocSubtitle",
        parent=styles["Normal"],
        fontSize=14,
        leading=18,
        textColor=GREY_TEXT,
        alignment=TA_CENTER,
        spaceAfter=24,
    )
)
styles.add(
    ParagraphStyle(
        name="H1",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=TITLE_BLUE,
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="H2",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=ACCENT_BLUE,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="H3",
        parent=styles["Heading3"],
        fontSize=12,
        leading=16,
        textColor=ACCENT_BLUE,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        spaceAfter=8,
        alignment=TA_LEFT,
    )
)
styles.add(
    ParagraphStyle(
        name="Note",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        textColor=GREY_TEXT,
        leftIndent=12,
        spaceAfter=8,
        borderColor=CODE_BORDER,
        borderPadding=8,
        borderWidth=0.5,
        backColor=colors.HexColor("#fefce8"),
    )
)
styles.add(
    ParagraphStyle(
        name="MyCode",
        parent=styles["Code"],
        fontSize=9,
        leading=12,
        backColor=CODE_BG,
        borderColor=CODE_BORDER,
        borderWidth=0.5,
        borderPadding=8,
        leftIndent=0,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="MyBullet",
        parent=styles["Body"],
        leftIndent=18,
        bulletIndent=6,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="QA",
        parent=styles["Body"],
        leftIndent=10,
        spaceAfter=10,
    )
)


# ---------- Helpers ----------

def p(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(text, styles[style])


def code(text: str) -> Preformatted:
    return Preformatted(text, styles["MyCode"])


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph(f"&bull;&nbsp;&nbsp;{item}", styles["MyBullet"]) for item in items]


def numbered(items: list[str]) -> list[Paragraph]:
    out = []
    for i, item in enumerate(items, start=1):
        out.append(Paragraph(f"<b>{i}.</b>&nbsp;&nbsp;{item}", styles["MyBullet"]))
    return out


def section(title: str, level: int = 1):
    style = {1: "H1", 2: "H2", 3: "H3"}[level]
    return Paragraph(title, styles[style])


def small_table(rows: list[list[str]], header: bool = True) -> Table:
    t = Table(rows, hAlign="LEFT", colWidths=None)
    style_cmds = [
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.4, CODE_BORDER),
    ]
    if header:
        style_cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), CODE_BG),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ]
    t.setStyle(TableStyle(style_cmds))
    return t


# ---------- Page template with footer ----------

def _on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY_TEXT)
    canvas.drawString(0.75 * inch, 0.5 * inch, "Stack Trace Time Machine — Project Guide")
    canvas.drawRightString(LETTER[0] - 0.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_doc():
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="Stack Trace Time Machine — Project Guide",
        author="rrathore02",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_on_page)])
    return doc


# ---------- Story builders ----------

def title_page() -> list:
    return [
        Spacer(1, 1.4 * inch),
        Paragraph("Stack Trace Time Machine", styles["DocTitle"]),
        Paragraph(
            "A Beginner&rsquo;s Guide and Project Walkthrough",
            styles["DocSubtitle"],
        ),
        Spacer(1, 0.4 * inch),
        Paragraph(
            "Find the commit that broke your test &mdash; automatically.",
            ParagraphStyle(
                name="tag",
                parent=styles["Normal"],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=GREY_TEXT,
                fontName="Helvetica-Oblique",
            ),
        ),
        Spacer(1, 2.5 * inch),
        Paragraph(
            "github.com/rrathore02/stack-trace-time-machine",
            ParagraphStyle(
                name="link",
                parent=styles["Normal"],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=ACCENT_BLUE,
                fontName="Courier",
            ),
        ),
        PageBreak(),
    ]


def toc_page() -> list:
    items = [
        ("1.  What this project is", "Big-picture overview"),
        ("2.  Concepts you need first", "Tests, Git, commits, regressions, bisect, CI, PRs"),
        ("3.  The problem we&rsquo;re solving", "Why finding a bad commit is hard"),
        ("4.  How stt works", "Architecture and key ideas"),
        ("5.  Walking through the code", "What lives where"),
        ("6.  Using stt on a GitHub repo", "Step by step"),
        ("7.  The web dashboard", "Browser-based history viewer"),
        ("8.  Understanding the results", "Reading CLI and dashboard output"),
        ("9.  Future expansions", "Where this could go"),
        ("10. Interview questions", "20+ questions for prep"),
    ]
    rows = [[k, v] for k, v in items]
    t = Table(rows, colWidths=[2.5 * inch, 3.8 * inch])
    t.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Helvetica", 11),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TEXTCOLOR", (0, 0), (0, -1), TITLE_BLUE),
                ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, CODE_BORDER),
            ]
        )
    )
    return [
        section("Contents"),
        Spacer(1, 6),
        t,
        PageBreak(),
    ]


def section_1_what_this_is() -> list:
    return [
        section("1. What this project is"),
        p(
            "Imagine you&rsquo;re a software developer working on a project with thousands "
            "of lines of code. Your team makes hundreds of changes every week. One day, "
            "you run your <b>tests</b> &mdash; small programs that check your real program "
            "still works &mdash; and one of them <b>fails</b>. It was passing yesterday. "
            "So somewhere in the changes you and your team made, one of them broke this test. "
            "Which one?"
        ),
        p(
            "Finding that one bad change among 50 or 100 recent ones, by hand, is slow and "
            "tedious. It can easily take a developer 15 minutes to four hours of focused work. "
            "Multiply that across a 100-engineer company with two regressions a week, and "
            "you&rsquo;re burning ~520 engineer-hours a year on detective work."
        ),
        p(
            "<b>Stack Trace Time Machine</b> (<i>stt</i> for short) is a small command-line "
            "tool that automates this detective work. You give it a failing test, point it at "
            "your project, and it tells you exactly which commit caused the regression. It "
            "even uses the failing error message itself to skip commits that couldn&rsquo;t "
            "possibly be the culprit, making it much faster than a manual search."
        ),
        section("Who would use this?", level=2),
        *bullets(
            [
                "Software developers who work with Git and have a test suite.",
                "Especially useful when test setup is slow (containers, fixtures, integration tests) "
                "&mdash; every saved iteration is real time.",
                "Engineers tired of running <font face='Courier'>git bisect</font> by hand.",
            ]
        ),
        Paragraph(
            "<b>Note:</b> &nbsp;This is a developer tool. If you&rsquo;re not a software "
            "developer, the tool itself probably isn&rsquo;t for you, but the rest of this "
            "guide will still help you understand what it does and why it matters.",
            styles["Note"],
        ),
        PageBreak(),
    ]


def section_2_concepts() -> list:
    return [
        section("2. Concepts you need first"),
        p(
            "If you&rsquo;re new to software, the project description above used several "
            "terms without explaining them. This section defines each one in plain English, "
            "in the order you&rsquo;ll encounter them. Skip ahead if you already know all of "
            "this."
        ),
        section("2.1  Tests", level=2),
        p(
            "A test is a tiny program that checks your real program does what you expect. "
            "If you wrote a function called <font face='Courier'>add(a, b)</font>, you might "
            "write a test that says: <i>&ldquo;If I call add(2, 3), the answer should be 5.&rdquo;</i> "
            "If your test fails &mdash; the answer is something other than 5 &mdash; you "
            "have a bug."
        ),
        p(
            "Modern projects have hundreds or thousands of tests. They run automatically every "
            "time someone changes the code, so bugs are caught quickly."
        ),
        section("2.2  Git, commits, repos", level=2),
        p(
            "<b>Git</b> is a tool that tracks every change you make to your code. It&rsquo;s "
            "the most popular such tool in the world."
        ),
        p(
            "A <b>commit</b> is a saved snapshot &mdash; like a checkpoint in a video game. "
            "Each commit has:"
        ),
        *bullets(
            [
                "A <b>message</b> describing what changed (e.g., &ldquo;Fix login bug&rdquo;).",
                "A unique <b>SHA</b> (a long hash that looks like <font face='Courier'>4a3f2c1b8d9e</font>). "
                "The first 7&ndash;10 characters are usually enough to identify it.",
                "A <b>parent</b> &mdash; the commit that came before it. This is how Git knows the order.",
            ]
        ),
        p(
            "A <b>repository</b> (or <b>repo</b>) is a project that&rsquo;s being tracked by Git. "
            "When you go to <font face='Courier'>github.com/some/project</font> and download the "
            "code, you&rsquo;re cloning that repo onto your computer."
        ),
        p(
            "A <b>branch</b> is a named line of development. Most projects have a default branch "
            "called <font face='Courier'>main</font> (or <font face='Courier'>master</font>). When "
            "developers work on a new feature they create a branch off main, do their work, then "
            "merge it back."
        ),
        p(
            "<b>HEAD</b> is Git&rsquo;s name for &ldquo;the commit you have checked out right now.&rdquo; "
            "<font face='Courier'>HEAD~50</font> means &ldquo;50 commits before HEAD.&rdquo;"
        ),
        section("2.3  Regressions", level=2),
        p(
            "A <b>regression</b> is a bug introduced by a change to code that previously worked. "
            "If a test was passing yesterday and is failing today, you have a regression. "
            "<i>stt</i> exists specifically to find which commit caused a regression."
        ),
        section("2.4  Stack traces", level=2),
        p(
            "When code crashes, it spits out a multi-line error message that shows which "
            "functions were running and where the error happened. That&rsquo;s a "
            "<b>stack trace</b>. Example (Python):"
        ),
        code(
            "Traceback (most recent call last):\n"
            "  File \"src/billing.py\", line 14, in compute_total\n"
            "    return invoice * tax_rate()\n"
            "  File \"src/tax.py\", line 7, in tax_rate\n"
            "    return CONFIG['rate']\n"
            "KeyError: 'rate'"
        ),
        p(
            "Notice the file paths: <font face='Courier'>src/billing.py</font> and "
            "<font face='Courier'>src/tax.py</font>. <i>stt</i> uses these to skip commits "
            "that didn&rsquo;t touch any of those files &mdash; they can&rsquo;t plausibly "
            "be the cause."
        ),
        section("2.5  Bisect (binary search)", level=2),
        p(
            "<b>Bisect</b> means &ldquo;cut in half.&rdquo; In computing, a binary search "
            "finds something in a sorted list by repeatedly cutting the search range in half. "
            "Here&rsquo;s the idea applied to commits:"
        ),
        *numbered(
            [
                "You know commit A (50 commits ago) is good &mdash; the test passed.",
                "You know commit B (right now) is bad &mdash; the test fails.",
                "Test the commit right in the middle. If it passes, the bug is in the second half. "
                "If it fails, the bug is in the first half.",
                "Repeat with the smaller half. Then again. And again.",
                "After about <font face='Courier'>log&#8322;(50)</font> &asymp; <b>6 tests</b>, "
                "you&rsquo;ve narrowed it down to one commit.",
            ]
        ),
        p(
            "Without bisect you&rsquo;d need to test up to 50 commits one by one. With bisect, "
            "6 is enough. <i>This is the central idea</i> &mdash; it&rsquo;s why a bisect is "
            "much faster than brute force."
        ),
        section("2.6  CI (Continuous Integration)", level=2),
        p(
            "<b>CI</b> is a system that automatically runs your tests every time someone "
            "pushes code. The little green checkmark or red X you see next to a commit on "
            "GitHub is from CI. The most popular system is <b>GitHub Actions</b>, which is "
            "what this project itself uses."
        ),
        section("2.7  Pull Request (PR)", level=2),
        p(
            "On GitHub, a <b>Pull Request</b> is a proposed change to a project. Someone says "
            "&ldquo;here&rsquo;s my change &mdash; please review and merge it.&rdquo; Other "
            "people review the diff, leave comments, ask for changes, and eventually approve "
            "and merge. Reverting a bad change is also done via a PR (a &ldquo;revert PR&rdquo;)."
        ),
        PageBreak(),
    ]


def section_3_problem() -> list:
    return [
        section("3. The problem we&rsquo;re solving"),
        section("3.1  The traditional way: by hand", level=2),
        p(
            "Picture this. A test that was green yesterday is red today. The team made 50 "
            "commits since yesterday. The traditional process for finding the bad one looks "
            "like this:"
        ),
        *numbered(
            [
                "Pull the latest code.",
                "Confirm the test fails locally (sometimes it doesn&rsquo;t fail on your laptop &mdash; another problem).",
                "Pick a commit somewhere in the middle of yesterday&rsquo;s 50.",
                "Check out that commit (<font face='Courier'>git checkout SHA</font>).",
                "Run the test. Pass or fail?",
                "Adjust your search range. Pick another commit. Check it out. Run the test.",
                "Repeat 5&ndash;10 more times.",
                "Eventually find the bad one. Read the diff. Decide whether to fix forward or revert.",
            ]
        ),
        p(
            "Each iteration involves checking out a different commit, often re-installing "
            "dependencies, sometimes rebuilding containers, then running a test that may take "
            "minutes. <b>For a non-trivial regression, the whole loop is 15 minutes to "
            "four hours.</b>"
        ),
        section("3.2  With <font face='Courier'>git bisect</font>", level=2),
        p(
            "Git ships with a built-in tool called <font face='Courier'>git bisect</font> "
            "that does the binary-search math for you. You start it, mark a known-good commit "
            "and a known-bad one, and Git keeps jumping you to commits in the middle of the "
            "remaining range. <b>You still have to run the test manually at every step.</b>"
        ),
        p(
            "This helps. But it doesn&rsquo;t solve the slow part: each iteration is still a "
            "manual <i>checkout, run test, mark, repeat</i> cycle. And there&rsquo;s no help "
            "with flaky tests, no use of the failing error message, no automation."
        ),
        section("3.3  With <i>stt</i>", level=2),
        p(
            "<i>stt</i> automates the whole loop. You run one command:"
        ),
        code(
            "stt bisect --repo /path/to/project \\\n"
            "           --good v1.4.2 \\\n"
            "           --test tests/test_billing.py::test_invoice_total"
        ),
        p("And it does:"),
        *bullets(
            [
                "Lists the commits in your range.",
                "For each binary-search step: checks out the commit, runs <i>only</i> the failing test (not the whole suite), records pass or fail.",
                "Uses the failing stack trace to skip commits that didn&rsquo;t touch any of the relevant files.",
                "If a test looks flaky, re-runs it a few times to make sure the failure is real.",
                "When it&rsquo;s done, prints the bad commit&rsquo;s SHA, and optionally drafts a revert PR.",
            ]
        ),
        p(
            "Net result: you go from <i>&ldquo;the test is failing&rdquo;</i> to "
            "<i>&ldquo;here&rsquo;s the exact commit that broke it&rdquo;</i> in one command, "
            "in the time it takes to grab coffee."
        ),
        PageBreak(),
    ]


def section_4_how_it_works() -> list:
    return [
        section("4. How <i>stt</i> works"),
        section("4.1  Architecture in one diagram", level=2),
        p(
            "<i>stt</i> is built out of small, decoupled pieces. Each box below is a single "
            "Python module under <font face='Courier'>stt/</font>:"
        ),
        code(
            "                  ┌─────────────────┐\n"
            "                  │   stt CLI       │\n"
            "                  │  (cli.py)       │\n"
            "                  └────────┬────────┘\n"
            "                           │\n"
            "    ┌──────────────────────┼──────────────────────┐\n"
            "    │                      │                      │\n"
            "    ▼                      ▼                      ▼\n"
            "┌─────────┐         ┌──────────────┐        ┌──────────┐\n"
            "│ Storage │         │ Stack Trace  │        │  Test    │\n"
            "│ SQLite  │         │   Parser     │        │ Runner   │\n"
            "└────┬────┘         └──────┬───────┘        └────┬─────┘\n"
            "     │                     │                     │\n"
            "     │ last passing SHA    │ files in trace      │ pass/fail\n"
            "     ▼                     ▼                     ▼\n"
            "          ┌──────────────────────────────────┐\n"
            "          │     Core Bisect Loop             │\n"
            "          │  (binary search + smart filter)  │\n"
            "          └─────────────────┬────────────────┘\n"
            "                            │\n"
            "                            ▼\n"
            "          ┌──────────────────────────────────┐\n"
            "          │   Flaky Test Re-confirmation     │\n"
            "          └─────────────────┬────────────────┘\n"
            "                            │\n"
            "                            ▼\n"
            "          ┌──────────────────────────────────┐\n"
            "          │    GitHub Revert-PR Drafter      │\n"
            "          └──────────────────────────────────┘\n"
            "                            ▲\n"
            "                            │ same SQLite DB\n"
            "                            │\n"
            "          ┌──────────────────────────────────┐\n"
            "          │    Web Dashboard (FastAPI)       │\n"
            "          └──────────────────────────────────┘"
        ),
        section("4.2  The bisect loop, step by step", level=2),
        p(
            "Given a known-good commit and a known-bad commit, here&rsquo;s what the loop does:"
        ),
        *numbered(
            [
                "Use Git to list every commit between good (exclusive) and bad (inclusive). Call this list <i>candidates</i>.",
                "Pick the candidate at the middle index.",
                "Check it out: <font face='Courier'>git checkout SHA</font>.",
                "Run the failing test using pytest.",
                "If the test passes &rarr; the bug must be in the upper half. Move the lower bound up.",
                "If the test fails &rarr; this commit could be the bug, but maybe an earlier one is. Move the upper bound down.",
                "Repeat until lower bound exceeds upper bound. The most recently failing commit is the answer.",
                "Restore the original HEAD so the user&rsquo;s working directory isn&rsquo;t left in a strange state.",
            ]
        ),
        section("4.3  The smart filter (the cool part)", level=2),
        p(
            "Plain bisect is already <i>O(log n)</i>, but in practice each iteration can be "
            "slow because the test itself is slow. The clever optimization in <i>stt</i> is to "
            "<b>skip commits that couldn&rsquo;t plausibly be the regression.</b>"
        ),
        p(
            "When the test fails, the error output names specific source files. <i>stt</i> "
            "extracts those filenames and tells the bisect loop: &ldquo;don&rsquo;t even bother "
            "testing commits that didn&rsquo;t touch any of these files.&rdquo;"
        ),
        p(
            "On a real codebase, this typically prunes 80&ndash;95% of candidate commits. A "
            "200-commit range that would have needed 8 test runs might now need just 2 or 3."
        ),
        Paragraph(
            "<b>Important caveat:</b> &nbsp;This is a <i>heuristic</i>. A regression caused by "
            "a config change, or by a file that gets imported but doesn&rsquo;t appear in the "
            "trace, will be missed and falsely attributed to a later commit. The "
            "<font face='Courier'>--trace-file</font> flag is opt-in, and the docstring is "
            "explicit about this tradeoff. When in doubt, run without it.",
            styles["Note"],
        ),
        section("4.4  Flaky test handling", level=2),
        p(
            "A <b>flaky test</b> is one that sometimes passes and sometimes fails on the same "
            "code, usually because of timing, randomness, or external dependencies. If we trust "
            "a single failure, a 5%-flaky test will make <i>stt</i> blame whichever commit "
            "happened to fail on the first roll &mdash; the wrong commit."
        ),
        p(
            "The fix is to re-run apparent failures multiple times and require a "
            "<b>majority</b> to actually fail before declaring the commit bad. "
            "<font face='Courier'>--flaky-runs 5 --flaky-threshold 0.6</font> says &ldquo;run up "
            "to 5 times; if at least 60% fail, treat it as a real failure.&rdquo; We only re-run "
            "<i>failures</i>, not passes &mdash; flakiness is virtually always intermittent "
            "failures, never intermittent passes."
        ),
        p(
            "There&rsquo;s also a short-circuit: as soon as the verdict is unambiguous (e.g., "
            "two passes already make 60% impossible), the loop stops. No wasted runs."
        ),
        section("4.5  Storage", level=2),
        p(
            "Every commit <i>stt</i> tests is recorded in a small SQLite database at "
            "<font face='Courier'>~/.stt/history.db</font>. The schema is one table with five "
            "columns: <font face='Courier'>repo, test_id, sha, passed, timestamp</font>."
        ),
        p(
            "This gives us two things for free:"
        ),
        *bullets(
            [
                "Next time you bisect the same test, <i>stt</i> can default <font face='Courier'>--good</font> to the most recent SHA where the test was green.",
                "The web dashboard (Section 7) is a viewer over this same database.",
            ]
        ),
        section("4.6  GitHub PR drafter", level=2),
        p(
            "Once <i>stt</i> identifies the bad commit, it can optionally automate the next "
            "step: cut a branch, run <font face='Courier'>git revert</font> on the bad commit, "
            "push it, and open a draft Pull Request via the GitHub CLI (<font face='Courier'>gh</font>). "
            "Default behavior is <i>dry-run</i>: it prints the title and body of the PR it "
            "<i>would</i> have opened, so you can see what it would do without committing to "
            "anything. Pass <font face='Courier'>--open-pr</font> to actually open it."
        ),
        PageBreak(),
    ]


def section_5_code_walkthrough() -> list:
    return [
        section("5. Walking through the code"),
        p(
            "If you cloned the repo and opened the <font face='Courier'>stt/</font> folder, "
            "here&rsquo;s what each file is for. None of them are large &mdash; the whole "
            "package is under 1,000 lines of Python."
        ),
        small_table(
            [
                ["File", "What it does"],
                ["stt/cli.py", "The user-facing command-line interface (Click). Parses args and wires the pieces together."],
                ["stt/git_utils.py", "A thin wrapper around the `git` command-line tool. We chose subprocess over pygit2 to keep installation friction zero."],
                ["stt/bisect.py", "The binary-search loop. Takes a test predicate and an optional candidate filter."],
                ["stt/stack_trace.py", "Pulls source-file paths out of failing-test output. Drops stdlib and pytest internals."],
                ["stt/runners/", "Pluggable test runners. Today: pytest. The base class makes adding Jest, Go, etc. trivial."],
                ["stt/storage.py", "Tiny SQLite database remembering past test runs."],
                ["stt/flaky.py", "Re-runs failures and short-circuits as soon as the verdict is unambiguous."],
                ["stt/github_integration.py", "Builds a revert PR via the gh CLI. Pure-function PR builder + the network-touching part are split."],
                ["stt/web/", "Optional FastAPI dashboard. Templates use Jinja2 + Tailwind via CDN."],
            ]
        ),
        Spacer(1, 12),
        section("Design choices worth noting", level=2),
        *bullets(
            [
                "<b>Subprocess over pygit2.</b> We only need ~5 git commands and they&rsquo;re not in a hot loop. Avoiding C-extension dependencies keeps install friction at zero.",
                "<b>Test runner is pluggable.</b> Adding Jest is just a new class implementing <font face='Courier'>TestRunner.run()</font>.",
                "<b>SQLite, not a server.</b> This is a local single-user tool. A server-backed DB would be overkill.",
                "<b>Web UI is optional.</b> Lives behind a <font face='Courier'>[web]</font> install extra so the core stays small.",
                "<b>PR drafter is split into pure and impure halves.</b> <font face='Courier'>build_revert_pr()</font> is a pure function (trivially testable). <font face='Courier'>open_revert_pr()</font> is the part that touches the network.",
            ]
        ),
        PageBreak(),
    ]


def section_6_using_on_repo() -> list:
    return [
        section("6. Using <i>stt</i> on a GitHub repo"),
        p(
            "This is the &ldquo;how do I actually use this on real code?&rdquo; section. "
            "We&rsquo;ll walk through pointing <i>stt</i> at a project on GitHub from scratch. "
            "<b>Important:</b> <i>stt</i> currently supports Python projects with pytest. "
            "Other languages would need a small extension to add their test runner (see Section 9)."
        ),
        section("6.1  Install <i>stt</i> itself", level=2),
        p("Only needed once on your machine."),
        code(
            "git clone https://github.com/rrathore02/stack-trace-time-machine.git\n"
            "cd stack-trace-time-machine\n"
            "pip install -e .\n"
            "stt --help    # verify it&rsquo;s on your PATH"
        ),
        section("6.2  Clone the repo you want to bisect", level=2),
        p(
            "<i>stt</i> works on a local copy of the code. So first, get a local copy:"
        ),
        code(
            "cd ~/projects\n"
            "git clone https://github.com/some-org/some-project.git\n"
            "cd some-project"
        ),
        p(
            "If the project uses Python and pytest, you also need to install its dependencies "
            "so the tests can run. The project will usually have a <font face='Courier'>requirements.txt</font> "
            "or <font face='Courier'>pyproject.toml</font> file:"
        ),
        code(
            "pip install -e .             # if pyproject.toml has the project setup\n"
            "# or\n"
            "pip install -r requirements.txt"
        ),
        section("6.3  Verify the failing test actually fails", level=2),
        p(
            "Before bisecting, make sure you can reproduce the failure. <i>stt</i> can&rsquo;t "
            "find a bug it can&rsquo;t see."
        ),
        code(
            "pytest tests/test_billing.py::test_invoice_total"
        ),
        p(
            "If this passes, you&rsquo;re looking at a different problem (maybe environment-"
            "specific). If it fails &mdash; great, you&rsquo;re ready to bisect."
        ),
        section("6.4  Find a commit where the test was passing", level=2),
        p("Three common ways to find a known-good commit:"),
        *bullets(
            [
                "<b>A release tag.</b> If the project tags releases (e.g., <font face='Courier'>v1.4.2</font>) and the test was green at that release, use that.",
                "<b>A date.</b> <font face='Courier'>git log --before=&quot;2 weeks ago&quot;</font> finds commits from before the bug.",
                "<b>HEAD~N.</b> If you suspect the bug is recent, just go back N commits: <font face='Courier'>HEAD~50</font>.",
            ]
        ),
        p(
            "Optional: check out that commit and run the test, just to confirm it really was "
            "green there:"
        ),
        code(
            "git checkout v1.4.2\n"
            "pytest tests/test_billing.py::test_invoice_total\n"
            "git checkout main"
        ),
        section("6.5  Run <i>stt</i>", level=2),
        code(
            "stt bisect \\\n"
            "  --repo . \\\n"
            "  --good v1.4.2 \\\n"
            "  --bad HEAD \\\n"
            "  --test tests/test_billing.py::test_invoice_total"
        ),
        p(
            "The <font face='Courier'>--repo .</font> means &ldquo;the current directory.&rdquo; "
            "<font face='Courier'>--bad HEAD</font> is the default (your latest code) so you can "
            "actually leave it off. Watch <i>stt</i> work:"
        ),
        code(
            "Bisecting v1.4.2..HEAD for test &lsquo;...test_invoice_total&rsquo; using pytest\n"
            "  step 1: 8e2d1c0b5a &rarr; FAIL\n"
            "  step 2: 3f4a8b9c1d &rarr; PASS\n"
            "  step 3: 5b9f2e7c4a &rarr; FAIL\n"
            "\n"
            "First bad commit: 5b9f2e7c4a3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f"
        ),
        section("6.6  Optional flags worth knowing", level=2),
        small_table(
            [
                ["Flag", "Why you&rsquo;d use it"],
                ["--trace-file FAILURE.txt", "Save the failing test&rsquo;s output to a file and pass it here. Enables the smart filter for big speedups."],
                ["--flaky-runs 3", "If the test is flaky, re-run failures up to 3 times. Default 1 means &ldquo;trust the first result.&rdquo;"],
                ["--open-pr", "Push a revert branch and open a draft PR via gh. Requires the GitHub CLI and a token."],
                ["--no-restore", "Don&rsquo;t put HEAD back at the end. Useful if you want to immediately keep working at the bad commit."],
            ]
        ),
        Spacer(1, 12),
        Paragraph(
            "<b>Watch out:</b> &nbsp;<i>stt</i> refuses to run if your working tree has uncommitted "
            "changes. Stash or commit them first &mdash; otherwise checkout would clobber your work.",
            styles["Note"],
        ),
        PageBreak(),
    ]


def section_7_dashboard() -> list:
    return [
        section("7. The web dashboard"),
        section("7.1  What it is", level=2),
        p(
            "Every commit <i>stt</i> tests is recorded in a SQLite database. The dashboard is "
            "a small read-only web app that shows you what&rsquo;s in that database, in a "
            "browser, with colored badges and a timeline. It&rsquo;s useful when you want to "
            "browse history without firing up the CLI &mdash; or when you want to demo the "
            "tool to someone."
        ),
        p(
            "It&rsquo;s <b>not</b> a service, has no auth, and runs entirely on your own machine. "
            "Think of it as a fancy way to look at one local file."
        ),
        section("7.2  Launching it", level=2),
        code(
            "pip install -e &quot;.[web]&quot;     # one-time: installs FastAPI + uvicorn + Jinja2\n"
            "stt web                    # serves on http://127.0.0.1:8765"
        ),
        p(
            "Open the URL it prints. If you&rsquo;ve never run a bisect, the page will be empty "
            "&mdash; that&rsquo;s expected. Either run a bisect (Section 6) or seed sample data "
            "(see <font face='Courier'>DASHBOARD.md</font> in the repo)."
        ),
        section("7.3  The pages", level=2),
        section("Dashboard (`/`)", level=3),
        p(
            "The home page shows three sections:"
        ),
        *bullets(
            [
                "<b>Stats row.</b> How many distinct tests <i>stt</i> has data on, how many are currently failing, and how many recent runs are shown.",
                "<b>Tests table.</b> One row per test ever recorded, with a red or green pill, total run count, fail rate %, and last run timestamp. Click a test name to drill in.",
                "<b>Recent runs feed.</b> The last 50 runs across all tests and repos, newest first.",
            ]
        ),
        section("Per-test history (`/test`)", level=3),
        p("Reached by clicking a test name from the dashboard. Shows:"),
        *bullets(
            [
                "<b>Test name and repo path</b> at the top.",
                "<b>Last passing commit SHA</b> &mdash; the one <i>stt bisect</i> would default to if you didn&rsquo;t pass <font face='Courier'>--good</font>.",
                "<b>Timeline.</b> Colored squares (green = pass, red = fail), oldest on the left. Hover for details.",
                "<b>Full run history table.</b> Every recorded run with timestamps and SHAs.",
            ]
        ),
        section("API docs (`/docs`)", level=3),
        p(
            "Auto-generated <b>Swagger UI</b>. Every JSON endpoint is listed with try-it-now "
            "forms. Useful if you want to script against the dashboard or build other tools "
            "on top of it. The site nav (Home / API docs / GitHub) is rendered above Swagger "
            "UI so you can always get back to the dashboard."
        ),
        section("7.4  How to read the dashboard", level=2),
        p("A few things to know when interpreting what you see:"),
        *bullets(
            [
                "<b>&ldquo;Currently red&rdquo;</b> means the most recent run for this test was a fail. The test could pass again on the next run if a fix lands.",
                "<b>Fail rate</b> is total failures &divide; total runs across <i>all</i> recorded history for that test. A high fail rate <i>over time</i> often means the test is flaky &mdash; not that the code is constantly broken.",
                "<b>The timeline</b> tells you whether a regression is recent (a long green tail then suddenly red) or chronic (alternating green and red).",
                "The dashboard auto-picks up new rows on <i>page refresh</i> &mdash; not in real time. There&rsquo;s no live updating yet.",
            ]
        ),
        section("7.5  Where the data comes from", level=2),
        p(
            "One file: <font face='Courier'>~/.stt/history.db</font>. Anything that writes to "
            "that file shows up in the dashboard."
        ),
        p("There are two ways data gets in:"),
        *numbered(
            [
                "<b>Running <font face='Courier'>stt bisect</font>.</b> Every commit it tests becomes a row.",
                "<b>Direct insert.</b> For demos, you can insert rows from Python using <font face='Courier'>Storage.record(repo, test_id, sha, passed)</font>. The repo also includes a sample seed snippet in <font face='Courier'>DASHBOARD.md</font>.",
            ]
        ),
        Paragraph(
            "<b>Heads up:</b> &nbsp;The dashboard does not watch external repos, doesn&rsquo;t "
            "poll CI, and doesn&rsquo;t run tests on its own. It&rsquo;s a viewer. The CLI does "
            "the work; the dashboard shows the result.",
            styles["Note"],
        ),
        PageBreak(),
    ]


def section_8_understanding_results() -> list:
    return [
        section("8. Understanding the results"),
        section("8.1  Anatomy of <i>stt</i>&rsquo;s CLI output", level=2),
        code(
            "Bisecting v1.4.2..HEAD for test &lsquo;tests/test_billing.py::test_invoice_total&rsquo; using pytest\n"
            "Smart bisect: filtering to commits touching 3 file(s):\n"
            "  - src/billing/invoice.py\n"
            "  - src/billing/tax.py\n"
            "  - tests/test_billing.py\n"
            "  step 1: 3f4a8b9c1d &rarr; PASS\n"
            "  step 2: 8e2d1c0b5a &rarr; FAIL\n"
            "  step 3: 5b9f2e7c4a &rarr; FAIL\n"
            "\n"
            "First bad commit: 5b9f2e7c4a3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f\n"
            "  iterations: 3\n"
            "  skipped 47 of 53 commits via stack-trace filter\n"
            "\n"
            "Dry run &mdash; pass --open-pr to push a revert branch and open a draft PR.\n"
            "  branch: stt/revert-5b9f2e7c\n"
            "  title:  Revert &quot;5b9f2e7c&quot; &mdash; auto-detected regression"
        ),
        p("Reading line by line:"),
        *bullets(
            [
                "<b>Bisecting v1.4.2..HEAD ...</b> &mdash; the range and test being checked.",
                "<b>Smart bisect: filtering to commits touching N file(s)</b> &mdash; the smart filter is on; these are the files extracted from the failing trace.",
                "<b>step N: SHA &rarr; PASS / FAIL</b> &mdash; one line per binary-search step. Each one is a commit checkout + test run.",
                "<b>First bad commit</b> &mdash; the answer. The full SHA is shown so you can <font face='Courier'>git show</font> it directly.",
                "<b>iterations</b> &mdash; how many commits were tested. Without the smart filter this would be ~log&#8322;(53) &asymp; 6.",
                "<b>skipped 47 of 53 commits</b> &mdash; the smart filter pruned 47 commits without running the test on them.",
                "<b>Dry run</b> &mdash; we&rsquo;re showing the PR title and branch but not actually pushing. Pass <font face='Courier'>--open-pr</font> to push for real.",
            ]
        ),
        section("8.2  What to do with the bad commit SHA", level=2),
        *numbered(
            [
                "Look at the diff: <font face='Courier'>git show &lt;SHA&gt;</font>",
                "If it&rsquo;s a small mistake, fix it forward (write a new commit that fixes the bug).",
                "If you need to unblock <i>main</i> immediately, revert: <font face='Courier'>git revert &lt;SHA&gt;</font> &mdash; or use <font face='Courier'>--open-pr</font> on the next bisect run.",
                "Tell the original author. They&rsquo;ll usually want to know.",
            ]
        ),
        section("8.3  Reading the dashboard", level=2),
        p(
            "When you open the dashboard after running a bisect, the test you bisected will "
            "have appeared in the table with a red pill (because the most recent run failed). "
            "Click it to open the per-test page."
        ),
        p(
            "The timeline at the top is the most useful single visual. A typical regression looks "
            "like:"
        ),
        code(
            "[ G G G G G G G | R R R ]\n"
            "  ^^^^^^^^^^^^^   ^^^^^\n"
            "    healthy     regression"
        ),
        p(
            "All-green for a long stretch, then suddenly red. The <i>border</i> between green "
            "and red is exactly the bad commit <i>stt</i> identified."
        ),
        p("A flaky test looks different:"),
        code(
            "[ G G R G G R G G G R G ]\n"
            "  alternating &mdash; not a regression"
        ),
        p(
            "When you see this pattern, raise <font face='Courier'>--flaky-runs</font> and "
            "<font face='Courier'>--flaky-threshold</font>, or fix the test."
        ),
        section("8.4  Using the JSON API", level=2),
        p(
            "If you&rsquo;re building tooling, every page has a JSON equivalent:"
        ),
        code(
            "curl http://127.0.0.1:8765/api/runs?limit=10\n"
            "curl http://127.0.0.1:8765/api/tests\n"
            "curl http://127.0.0.1:8765/api/health"
        ),
        p(
            "Use these to feed bisect history into a Slack bot, a Grafana dashboard, or "
            "anything else."
        ),
        PageBreak(),
    ]


def section_9_future() -> list:
    return [
        section("9. Future expansions"),
        p(
            "<i>stt</i> is intentionally small and focused. Here&rsquo;s where it could go &mdash; "
            "in roughly the order I&rsquo;d build them:"
        ),
        section("9.1  Parallel bisect (high impact)", level=2),
        p(
            "Currently <i>stt</i> tests one commit at a time. Using <font face='Courier'>git "
            "worktree</font>, we could test two or four commits in parallel on different "
            "directories. For tests that take 30+ seconds, this roughly halves wall time. "
            "It&rsquo;s the single biggest remaining lever on speed."
        ),
        section("9.2  More test runners", level=2),
        p(
            "Today only pytest is supported. The runner abstraction is already in place &mdash; "
            "adding new ones is a small file each:"
        ),
        *bullets(
            [
                "<b>Jest</b> for JavaScript / TypeScript projects.",
                "<b>go test</b> for Go.",
                "<b>cargo test</b> for Rust.",
                "<b>Bun test</b> for newer JS projects.",
            ]
        ),
        section("9.3  CI integration", level=2),
        p(
            "A GitHub Action that automatically runs <i>stt</i> when <i>main</i> goes red, "
            "then comments on the PR with the offending commit and a link to the revert PR. "
            "This is the dream version: regressions get attributed and reverted before anyone "
            "even notices."
        ),
        section("9.4  Trigger bisects from the web", level=2),
        p(
            "The dashboard is read-only today. Adding a &ldquo;Start bisect&rdquo; form would "
            "make it self-service for non-CLI users. This needs a job queue (so the web request "
            "doesn&rsquo;t block waiting for the bisect to finish), and Server-Sent Events or "
            "WebSockets for streaming live progress to the browser."
        ),
        section("9.5  Verify-before-revert", level=2),
        p(
            "Right now, <font face='Courier'>--open-pr</font> blindly reverts the bad commit. "
            "Better behavior: cut the revert branch, run the <i>full</i> test suite on it, and "
            "only open the PR if the suite is green. This avoids reverting a commit that fixed "
            "<i>another</i> bug along the way."
        ),
        section("9.6  Multi-repo / team dashboards", level=2),
        p(
            "Today the dashboard reads one local SQLite file. A multi-user team version would "
            "let an entire engineering org see &ldquo;all currently red tests across all our "
            "repos.&rdquo; This is a meaningful expansion of scope &mdash; needs a server-side "
            "DB, auth, and probably an organization concept."
        ),
        section("9.7  ML-based prediction", level=2),
        p(
            "More speculative: train a model on (commit features) &rarr; (likelihood of "
            "introducing a regression) using historical bisect data. Could be used to flag "
            "high-risk commits on a PR before merge."
        ),
        section("9.8  Better merge-commit handling", level=2),
        p(
            "Linear histories are easy. Merge commits get philosophically interesting &mdash; "
            "if a merge introduced the bug, which side of the merge is &ldquo;bad&rdquo;? Git "
            "bisect itself has good logic here that we could lean on more."
        ),
        PageBreak(),
    ]


def section_10_interview_questions() -> list:
    qa = [
        # Fundamentals
        ("F", "What does this project do, in one sentence?",
         "It automatically finds the commit that broke a test by bisecting Git history and using the failing stack trace to skip irrelevant commits."),
        ("F", "Why is bisect O(log n) instead of O(n)?",
         "Each iteration cuts the search range in half. After k iterations, the remaining range is n / 2^k. Solving 2^k = n gives k = log&#8322;(n)."),
        ("F", "Why did you pick Python?",
         "Python has the largest test ecosystem (pytest is everywhere). Click + FastAPI + SQLite gave a complete CLI + web stack with no compilation step."),
        ("F", "What&rsquo;s the difference between <font face='Courier'>git bisect</font> and your tool?",
         "Git bisect does the binary-search math. <i>stt</i> automates the &ldquo;run the test at each step&rdquo; part, adds a stack-trace heuristic for big speedups, handles flaky tests, and can draft revert PRs."),

        # Architecture
        ("A", "Walk me through the architecture.",
         "Five core modules: git_utils (subprocess wrapper), bisect (binary search loop), stack_trace (parse error output), runners (pluggable test runners), storage (SQLite history). Three optional layers: flaky (re-confirmation wrapper), github_integration (PR drafter), web (FastAPI dashboard). Each is small and decoupled."),
        ("A", "Why subprocess instead of pygit2 or libgit2?",
         "We only need ~5 git commands and they&rsquo;re not in a hot loop. Subprocess avoids C-extension dependencies (which often fail to install on Windows). Zero install friction is more valuable than the small perf gain."),
        ("A", "Why SQLite for storage?",
         "Single-user local tool. SQLite gives us atomic writes, a real query language, and zero setup. A Postgres dependency would be silly here."),
        ("A", "How is the test runner abstraction structured?",
         "A <font face='Courier'>TestRunner</font> abstract base class with a single <font face='Courier'>run(repo, test_id) &rarr; TestResult</font> method. Currently one implementation: <font face='Courier'>PytestRunner</font>. New runners are a single file each."),
        ("A", "Why is the dashboard optional?",
         "Most users only need the CLI. Pulling FastAPI for them would 4x the dependency tree. <font face='Courier'>pip install -e &quot;.[web]&quot;</font> is a clean opt-in."),

        # Smart bisect (deep)
        ("S", "Explain the smart filter heuristic.",
         "When the test fails, the error output names specific source files. We extract those and tell bisect to only test commits that touched at least one of them. Rationale: a regression is most often caused by a commit that modified one of the files in the trace."),
        ("S", "When does the smart filter give a wrong answer?",
         "When the regression is caused by a file that doesn&rsquo;t appear in the trace &mdash; e.g., a config file, an environment variable, or a transitively-imported file. In those cases the filter prunes the actual culprit and we falsely blame a later commit."),
        ("S", "How would you make it more robust?",
         "Two ideas: (1) Two-pass strategy: bisect on filtered candidates first, but verify the result by running the test on the next-older filtered candidate to confirm the boundary. (2) Track commits that historically touched files <i>imported by</i> traced files (using static analysis), and include them in the candidate set."),
        ("S", "What&rsquo;s the worst-case time complexity?",
         "Same as plain bisect: O(test_runtime &times; log&#8322;(n)). Worst case is when the filter prunes nothing &mdash; then you fall back to the full bisect. Best case is when only one filtered commit remains: O(test_runtime &times; 1)."),

        # Hard
        ("H", "How would you implement parallel bisect?",
         "Use <font face='Courier'>git worktree</font> to create N parallel checkouts. The bisect loop currently picks one mid-point; in parallel mode pick the 1/3 and 2/3 points and run them concurrently. After both finish, you can narrow to one of three sub-ranges. The challenge is correctly merging results when one finishes much faster than the other."),
        ("H", "How would you handle merge commits?",
         "Use <font face='Courier'>git log --first-parent</font> to flatten history first, treating each merge as one commit. If a merge is identified as bad, recursively bisect <i>inside</i> that merge&rsquo;s side branch."),
        ("H", "How would you scale this across hundreds of repos?",
         "The CLI doesn&rsquo;t need to scale &mdash; each user runs it locally. The dashboard does. Move from local SQLite to a shared Postgres, add organization/repo as first-class entities, add auth, and let the dashboard show fleet-wide health."),
        ("H", "How would you handle a flaky test more aggressively?",
         "Beyond simple re-runs: track per-test flakiness over time in the storage layer. If a test has &ge;X% flake rate historically, automatically apply a higher <font face='Courier'>--flaky-runs</font> default for that test. Optionally quarantine it from blocking bisect."),

        # Project / behavioral
        ("P", "What was the hardest part?",
         "The smart filter, because it&rsquo;s a heuristic. Getting the speedup matters in practice but you have to be honest about correctness. Documenting the tradeoff clearly &mdash; both in the code and in the README &mdash; was the actual work."),
        ("P", "What would you do differently?",
         "Two things. First, I&rsquo;d add an integration test that runs the whole CLI end-to-end against a generated git repo &mdash; the unit tests cover each piece but not their composition. Second, I&rsquo;d write the parallel-bisect mode earlier, because it changes the shape of the bisect loop and would have been cleaner to design in from the start."),
        ("P", "What&rsquo;s next on your roadmap?",
         "Parallel bisect via <font face='Courier'>git worktree</font>. After that, a Jest runner so I can use <i>stt</i> on JavaScript projects too. Then a GitHub Action that auto-runs <i>stt</i> when <i>main</i> goes red."),
        ("P", "How did you decide what to build first?",
         "MVP first &mdash; the simplest end-to-end pipeline (one test runner, one bisect strategy, one CLI command). Everything else got added only after the MVP could be demoed. The smart filter, flaky handling, dashboard, and PR drafter are each opt-in extensions on top."),
    ]

    cat_names = {
        "F": "Fundamentals",
        "A": "Architecture &amp; design",
        "S": "Smart bisect (deep dive)",
        "H": "Harder technical questions",
        "P": "Project &amp; behavioral",
    }

    out = [
        section("10. Interview questions"),
        p(
            "These are real questions a thoughtful interviewer might ask if you&rsquo;re "
            "presenting this project. Each one is followed by a model answer in your own "
            "voice &mdash; use them as starting points, not memorized scripts. Recruiters "
            "smell rehearsed answers."
        ),
    ]

    current_cat = None
    for cat, q, a in qa:
        if cat != current_cat:
            out.append(section(cat_names[cat], level=2))
            current_cat = cat
        out.append(Paragraph(f"<b>Q.</b>&nbsp;&nbsp;{q}", styles["QA"]))
        out.append(
            Paragraph(
                f"<font color='#475569'><b>A.</b></font>&nbsp;&nbsp;{a}",
                styles["QA"],
            )
        )

    return out


def closing() -> list:
    return [
        Spacer(1, 0.3 * inch),
        Paragraph(
            "<i>End of guide. The repo lives at "
            "<font color='#1d4ed8'>github.com/rrathore02/stack-trace-time-machine</font>.</i>",
            ParagraphStyle(
                name="closing",
                parent=styles["Body"],
                alignment=TA_CENTER,
                fontSize=10,
                textColor=GREY_TEXT,
            ),
        ),
    ]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = build_doc()
    story: list = []
    story.extend(title_page())
    story.extend(toc_page())
    story.extend(section_1_what_this_is())
    story.extend(section_2_concepts())
    story.extend(section_3_problem())
    story.extend(section_4_how_it_works())
    story.extend(section_5_code_walkthrough())
    story.extend(section_6_using_on_repo())
    story.extend(section_7_dashboard())
    story.extend(section_8_understanding_results())
    story.extend(section_9_future())
    story.extend(section_10_interview_questions())
    story.extend(closing())
    doc.build(story)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
