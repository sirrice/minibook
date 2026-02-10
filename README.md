# One-page mini-zine creator

Create 8-page mini-books (zines) from your PDF files. Print on one side, fold, cut, and twist into an 8-page booklet from a single sheet of paper!

## 🌐 Web App (Recommended)

**[Use the online tool here →](https://eugenewu.github.io/minibook/)** *(Update with your actual GitHub Pages URL)*

The web app runs entirely in your browser - no installation, no upload, completely private. Just drag and drop your PDF!

## 🐍 Python CLI Tool

For command-line users, there's also a Python version:

## Installation

Requires Python 3 and pypdf:

```bash
pip install pypdf
```

## Usage

```bash
python3 minibook.py INPUT.pdf OUTPUT.pdf [--flip EDGE] [--margin SIZE]
```

### Arguments

- `INPUT.pdf`: Source PDF (up to 8 pages)
- `OUTPUT.pdf`: Output file with single-page imposition
- `--flip`: Duplex flip edge (for legacy 2-page mode)
  - `long` (default): Flip on long edge
  - `short`: Flip on short edge
  - `none`: No duplex
- `--margin`: Size control in points
  - `>= 0`: Outer sheet margin (e.g., `18` for 18pt margins)
  - `< 0`: "Make bigger" mode - crops and scales content (e.g., `-18`)

**Note:** The web app generates a single-page layout (print on one side only). The Python CLI can generate both single-page and two-page duplex layouts.

### Examples

Basic usage with default long-edge flip:
```bash
python3 minibook.py input.pdf output.pdf
```

Make content bigger by cropping 18pt from edges:
```bash
python3 minibook.py input.pdf output.pdf --margin -18
```

Short-edge duplex with 12pt margins:
```bash
python3 minibook.py input.pdf output.pdf --flip short --margin 12
```

## Printing & Folding

### Printing
1. Output is **US Letter LANDSCAPE** (11×8.5 inches)
2. Print at **100% / Actual size** (no fit-to-page scaling)
3. **Web app:** Print **single-sided** (one side only)
4. **Python CLI:** Can do duplex printing with `--flip` option

### Folding Instructions
1. Fold the paper in half lengthwise (hotdog fold)
2. Fold in half again, then once more (you'll have 8 sections)
3. Unfold once so you see 4 sections
4. Cut along the center fold between the two middle sections
5. Unfold completely, fold lengthwise, and push the ends together - it will twist into a booklet!

See the [web app](https://eugenewu.github.io/minibook/) for a visual diagram. *(Update URL)*

**Credit:** Folding technique by [Marek Bennett](https://marekbennett.com/2020/01/24/1sheet-mini-01/)

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

## Files in this Repository

- `index.html` - Web app (single-page mini-zine creator)
- `minibook.py` - Python CLI tool
- `source.pdf` - Example PDF (8 pages)
- `instructions.jpg` - Folding diagram by Marek Bennett

## Development

### Running Locally

To test the web app locally, just open `index.html` in your browser. For best results, use a local web server:

```bash
# Python 3
python3 -m http.server 8000

# Then open http://localhost:8000
```

### Deploying to GitHub Pages

1. Push your changes to the `main` branch
2. Go to repository Settings → Pages
3. Under "Source", select "Deploy from a branch"
4. Select `main` branch and `/ (root)` folder
5. Click Save

Your site will be live at `https://YOUR_USERNAME.github.io/minibook/`

## License

MIT
