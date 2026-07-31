"""Fill HTML artifact templates and print them to PDF with headless Chrome."""
import subprocess
import tempfile
from pathlib import Path
from string import Template

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def fill(template_name: str, context: dict) -> str:
    tpl = (TEMPLATES / f"{template_name}.html").read_text()
    return Template(tpl).substitute(context)


def render_pdf(html: str, out_pdf: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        src = f.name
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={out_pdf}", f"file://{src}"],
        check=True, capture_output=True, timeout=120)
    return out_pdf
