# Scripts

Helper scripts that aren't part of the importable `stt` package.

## `build_guide_pdf.py`

Regenerates the beginner-friendly project guide PDF.

### Setup

```bash
pip install -e ".[docs]"   # pulls reportlab
```

### Run

```bash
python scripts/build_guide_pdf.py
```

Output: `~/Documents/stt-project-guide.pdf` (~23 pages).

The PDF is intentionally **not** committed to the repo — regenerate it locally when you want a fresh copy. To change content, edit the `section_*` functions in `build_guide_pdf.py`.
