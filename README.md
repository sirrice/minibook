# minipage

A Python tool for creating 8-page mini-book (zine) impositions from PDFs. Print one sheet front and back, fold, and you have an 8-page booklet.

## Installation

Requires Python 3 and pypdf:

```bash
pip install pypdf
```

## Usage

```bash
python3 minipage.py INPUT.pdf OUTPUT.pdf [--flip EDGE] [--margin SIZE]
```

### Arguments

- `INPUT.pdf`: Source PDF (up to 8 pages)
- `OUTPUT.pdf`: Output file with 2-page imposition
- `--flip`: Duplex flip edge
  - `long` (default): Flip on long edge
  - `short`: Flip on short edge
  - `none`: No duplex
- `--margin`: Size control in points
  - `>= 0`: Outer sheet margin (e.g., `18` for 18pt margins)
  - `< 0`: "Make bigger" mode - crops and scales content (e.g., `-18`)

### Examples

Basic usage with default long-edge flip:
```bash
python3 minipage.py input.pdf output.pdf
```

Make content bigger by cropping 18pt from edges:
```bash
python3 minipage.py input.pdf output.pdf --margin -18
```

Short-edge duplex with 12pt margins:
```bash
python3 minipage.py input.pdf output.pdf --flip short --margin 12
```

## Printing

1. Output is always **US Letter LANDSCAPE** (11×8.5 inches)
2. Print at **100% / Actual size** (no fit-to-page scaling)
3. Enable **duplex printing** with the appropriate flip edge
4. After printing, fold the sheet to create your mini-book

## How It Works

The tool arranges 8 pages into a specific imposition pattern:

**Front sheet (top row rotated 180°):**
```
8  1  2  7
6  3  4  5
```

**Back sheet** layout depends on flip mode (long vs short edge).

When you fold the printed sheet, the pages appear in the correct reading order.

## Margin Modes

### Positive margin (e.g., `--margin 18`)
Adds space around the entire imposition grid. Good for printers that can't print to the edge.

### Negative margin (e.g., `--margin -18`)
"Make bigger" mode:
1. Crops each source page by the specified amount on all sides
2. Scales the cropped content up to fill the cell plus extra bleed
3. Centers the result within each cell

Use this to eliminate white space and make text larger.

## License

MIT
