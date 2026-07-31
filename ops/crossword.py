"""Criss-cross crossword layout. Pure, deterministic per seed. Layout only."""
import random


def _fits(cells, word, r, c, d):
    dr, dc = (0, 1) if d == "across" else (1, 0)
    crossed = False
    if (r - dr, c - dc) in cells or (r + dr * len(word), c + dc * len(word)) in cells:
        return False
    for i, ch in enumerate(word):
        rr, cc = r + dr * i, c + dc * i
        if (rr, cc) in cells:
            if cells[(rr, cc)] != ch:
                return False
            crossed = True
        else:
            pr, pc = (1, 0) if d == "across" else (0, 1)
            if (rr + pr, cc + pc) in cells or (rr - pr, cc - pc) in cells:
                return False
    return crossed


def generate(words, seed: int = 0):
    words = [w.upper().replace(" ", "") for w in words]
    rng = random.Random(seed)
    order = sorted(words, key=len, reverse=True)
    cells: dict = {}
    placements = []
    first = order[0]
    for i, ch in enumerate(first):
        cells[(0, i)] = ch
    placements.append({"word": first, "row": 0, "col": 0, "dir": "across"})
    for word in order[1:]:
        options = []
        for i, ch in enumerate(word):
            for (r, c), cell_ch in cells.items():
                if cell_ch != ch:
                    continue
                options.append((r - i, c, "down", word))
                options.append((r, c - i, "across", word))
        rng.shuffle(options)
        for r, c, d, w in options:
            if _fits(cells, w, r, c, d):
                dr, dc = (0, 1) if d == "across" else (1, 0)
                for i, wch in enumerate(w):
                    cells[(r + dr * i, c + dc * i)] = wch
                placements.append({"word": w, "row": r, "col": c, "dir": d})
                break
    if len(placements) < max(2, -(-len(words) * 7 // 10)):  # ceil(70%)
        return None
    minr = min(r for r, _ in cells)
    minc = min(c for _, c in cells)
    maxr = max(r for r, _ in cells)
    maxc = max(c for _, c in cells)
    for p in placements:
        p["row"] -= minr
        p["col"] -= minc
    norm_cells = {f"{r - minr},{c - minc}": ch for (r, c), ch in cells.items()}
    starts = sorted({(p["row"], p["col"]) for p in placements})
    numbers = {rc: i + 1 for i, rc in enumerate(starts)}
    for p in placements:
        p["number"] = numbers[(p["row"], p["col"])]
    return {
        "placements": placements,
        "rows": maxr - minr + 1,
        "cols": maxc - minc + 1,
        "cells": norm_cells,
    }
