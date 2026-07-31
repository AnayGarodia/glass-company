from ops import crossword

WORDS = ["MAYA", "AMSTERDAM", "TIRAMISU", "SCRABBLE", "OCTOBER", "BEACH"]


def test_generates_connected_grid():
    g = crossword.generate(WORDS, seed=1)
    assert g is not None
    assert len(g["placements"]) >= 5  # ceil(70% of 6)
    for p in g["placements"]:
        for i, ch in enumerate(p["word"]):
            r = p["row"] + (i if p["dir"] == "down" else 0)
            c = p["col"] + (i if p["dir"] == "across" else 0)
            assert g["cells"][f"{r},{c}"] == ch
    coords = [tuple(map(int, k.split(","))) for k in g["cells"]]
    assert min(r for r, _ in coords) == 0 and min(c for _, c in coords) == 0


def test_numbers_are_unique_per_start():
    g = crossword.generate(WORDS, seed=1)
    starts = {(p["row"], p["col"], p["dir"]) for p in g["placements"]}
    assert len(starts) == len(g["placements"])


def test_impossible_words_return_none():
    assert crossword.generate(["QQQQ", "ZZZZ", "XXXX"], seed=0) is None
