import json
from ops import products

CATALOGUE = {"sol_price_usd_cents": 7000, "products": [{"format": "crossword"}]}


def test_save_keeps_trailing_newline(tmp_path):
    p = tmp_path / "products.json"
    products.save(CATALOGUE, path=p)
    assert p.read_text().endswith("}\n")


def test_round_trip(tmp_path):
    p = tmp_path / "products.json"
    products.save(CATALOGUE, path=p)
    assert products.load(p) == CATALOGUE


def test_set_sol_price_changes_one_line_only(tmp_path):
    p = tmp_path / "products.json"
    products.save(CATALOGUE, path=p)
    before = p.read_text().splitlines(keepends=True)
    old, new = products.set_sol_price(7585, path=p)
    after = p.read_text().splitlines(keepends=True)
    assert (old, new) == (7000, 7585)
    assert len(before) == len(after)
    assert sum(1 for a, b in zip(before, after) if a != b) == 1


def test_real_catalogue_ends_with_newline():
    assert products.DEFAULT_PATH.read_text().endswith("\n")
    assert "sol_price_usd_cents" in json.loads(products.DEFAULT_PATH.read_text())
