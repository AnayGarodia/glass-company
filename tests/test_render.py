import os
import pytest
from ops import render


def test_fill_substitutes():
    html = render.fill("dossier", {"subject_name": "Maya", "codename": "NIGHTINGALE",
                                   "body_html": "<p>classified</p>"})
    assert "NIGHTINGALE" in html and "classified" in html


def test_fill_missing_key_raises():
    with pytest.raises(KeyError):
        render.fill("dossier", {"subject_name": "Maya"})


@pytest.mark.skipif(not os.path.exists(render.CHROME), reason="no Chrome")
def test_render_pdf(tmp_path):
    out = render.render_pdf("<h1>hello</h1>", str(tmp_path / "o.pdf"))
    assert open(out, "rb").read(4) == b"%PDF"


def test_watermark_overlays():
    html = render.fill("dossier", {"subject_name": "X", "codename": "Y",
                                   "body_html": "<p>z</p>"})
    marked = render.watermark(html)
    assert "PREVIEW — UNPAID" in marked
    assert marked.count("</body>") == 1
