#!/usr/bin/env python3
"""
minipage.py — one-sheet mini book (8-page zine fold) imposition.

Usage:
  python3 minipage.py INPUT.pdf OUTPUT.pdf --flip long --margin -18

Notes:
- Output is always US Letter LANDSCAPE (11x8.5).
- --margin is the only sizing knob:
    margin >= 0 : outer sheet margin (points)
    margin < 0  : "make bigger" mode:
        * crop each source page by abs(margin) on all sides
        * scale to (cell + 2*abs(margin)) so content prints larger
        * center within the cell
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Optional, Tuple

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf._page import PageObject

LETTER_LANDSCAPE = (11 * 72, 8.5 * 72)  # points


@dataclass(frozen=True)
class CellPlacement:
    page_num: int     # logical page number 1..8
    col: int          # 0..3
    row: int          # 0..1 (0=top, 1=bottom)
    rotate_180: bool


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_pdf")
    ap.add_argument("output_pdf")
    ap.add_argument("--flip", choices=["short", "long", "none"], default="long")
    ap.add_argument(
        "--margin",
        type=float,
        default=18.0,
        help=(
            "If >=0: outer sheet margin (pt). "
            "If <0: auto crop+bleed amount (pt) to make text bigger (e.g., -12, -18)."
        ),
    )
    return ap.parse_args()


def ensure_8_pages(reader: PdfReader) -> List[Optional[PageObject]]:
    pages: List[Optional[PageObject]] = list(reader.pages)
    if len(pages) == 0:
        raise ValueError("Input PDF has 0 pages.")
    if len(pages) > 8:
        raise ValueError(f"Input has {len(pages)} pages; this layout supports up to 8.")

    # pad with None (we will leave those cells blank; no blank-page objects needed)
    while len(pages) < 8:
        pages.append(None)
    return pages


def crop_in_place(page: PageObject, crop: float) -> None:
    """Crop page by `crop` points on all sides, in-place. Safe if called once per page."""
    if crop <= 0:
        return

    mb = page.mediabox
    left = float(mb.left) + crop
    bottom = float(mb.bottom) + crop
    right = float(mb.right) - crop
    top = float(mb.top) - crop

    # If crop is too aggressive, do nothing.
    if right <= left or top <= bottom:
        return

    mb.lower_left = (left, bottom)
    mb.upper_right = (right, top)

    # Keep cropbox consistent
    page.cropbox.lower_left = mb.lower_left
    page.cropbox.upper_right = mb.upper_right


def layout_for_flip(flip: str) -> Tuple[List[CellPlacement], List[CellPlacement]]:
    # FRONT:
    # top:    8  1  2  7   (rot 180)
    # bottom: 6  3  4  5
    front = [
        CellPlacement(8, 0, 0, True),
        CellPlacement(1, 1, 0, True),
        CellPlacement(2, 2, 0, True),
        CellPlacement(7, 3, 0, True),
        CellPlacement(6, 0, 1, False),
        CellPlacement(3, 1, 1, False),
        CellPlacement(4, 2, 1, False),
        CellPlacement(5, 3, 1, False),
    ]

    # BACK (short-edge duplex assumption)
    back_short = [
        CellPlacement(5, 0, 0, True),
        CellPlacement(4, 1, 0, True),
        CellPlacement(3, 2, 0, True),
        CellPlacement(6, 3, 0, True),
        CellPlacement(7, 0, 1, False),
        CellPlacement(2, 1, 1, False),
        CellPlacement(1, 2, 1, False),
        CellPlacement(8, 3, 1, False),
    ]

    if flip in ("short", "none"):
        return front, back_short

    # BACK (long-edge duplex correction: swap rows)
    back_long = [
        CellPlacement(7, 0, 0, True),
        CellPlacement(2, 1, 0, True),
        CellPlacement(1, 2, 0, True),
        CellPlacement(8, 3, 0, True),
        CellPlacement(5, 0, 1, False),
        CellPlacement(4, 1, 1, False),
        CellPlacement(3, 2, 1, False),
        CellPlacement(6, 3, 1, False),
    ]
    return front, back_long


def place_page_into_cell(
    sheet: PageObject,
    src: PageObject,
    sheet_w: float,
    sheet_h: float,
    outer_margin: float,
    col: int,
    row: int,
    rotate_180: bool,
    bleed: float,
) -> None:
    usable_w = sheet_w - 2 * outer_margin
    usable_h = sheet_h - 2 * outer_margin
    cell_w = usable_w / 4.0
    cell_h = usable_h / 2.0

    x0 = outer_margin + col * cell_w
    y0 = outer_margin + (1 - row) * cell_h  # row 0 is top

    src_w = float(src.mediabox.width)
    src_h = float(src.mediabox.height)

    # Fit to (cell + 2*bleed) so negative margin makes it larger
    target_w = cell_w + 2.0 * bleed
    target_h = cell_h + 2.0 * bleed
    scale = min(target_w / src_w, target_h / src_h)

    placed_w = src_w * scale
    placed_h = src_h * scale

    # Center in the actual cell
    dx = x0 + (cell_w - placed_w) / 2.0
    dy = y0 + (cell_h - placed_h) / 2.0

    t = Transformation().scale(scale, scale)

    if rotate_180:
        cx = placed_w / 2.0
        cy = placed_h / 2.0
        t = t.translate(-cx, -cy).rotate(180).translate(cx, cy)

    t = t.translate(dx, dy)
    sheet.merge_transformed_page(src, t, expand=False)


def build_sheet(
    pages_8: List[Optional[PageObject]],
    placements: List[CellPlacement],
    outer_margin: float,
    crop: float,
    bleed: float,
) -> PageObject:
    sheet_w, sheet_h = LETTER_LANDSCAPE
    sheet = PageObject.create_blank_page(width=sheet_w, height=sheet_h)

    for pl in placements:
        # Remap logical booklet page -> source page index (1..8) for your fold direction
        LOGICAL_TO_SOURCE = {1: 8, 2: 7, 3: 3, 4: 4, 5: 5, 6: 2, 7: 6, 8: 1}

        src = pages_8[LOGICAL_TO_SOURCE[pl.page_num] - 1]
        #src = pages_8[pl.page_num - 1]
        if src is None:
            continue  # leave blank

        if crop > 0:
            crop_in_place(src, crop)

        place_page_into_cell(
            sheet=sheet,
            src=src,
            sheet_w=sheet_w,
            sheet_h=sheet_h,
            outer_margin=outer_margin,
            col=pl.col,
            row=pl.row,
            rotate_180=pl.rotate_180,
            bleed=bleed,
        )

    return sheet


def main() -> None:
    args = parse_args()
    reader = PdfReader(args.input_pdf)
    pages_8 = ensure_8_pages(reader)

    # Single knob behavior
    if args.margin >= 0:
        outer_margin = args.margin
        crop = 0.0
        bleed = 0.0
    else:
        outer_margin = 0.0
        crop = -args.margin
        bleed = -args.margin

    front_pl, back_pl = layout_for_flip(args.flip)

    front_sheet = build_sheet(pages_8, front_pl, outer_margin, crop, bleed)
    back_sheet = build_sheet(pages_8, back_pl, outer_margin, crop, bleed)

    writer = PdfWriter()
    writer.add_page(front_sheet)
    writer.add_page(back_sheet)

    with open(args.output_pdf, "wb") as f:
        writer.write(f)

    print(f"Wrote: {args.output_pdf}")
    print("Print: LANDSCAPE, 100%/Actual size (no fit-to-page).")
    if args.flip != "none":
        print(f"Duplex: flip on {args.flip} edge.")


if __name__ == "__main__":
    main()
