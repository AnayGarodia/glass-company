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


WATERMARK = ('<div style="position:fixed;top:40%;left:0;right:0;text-align:center;'
             'transform:rotate(-24deg);font-size:64px;color:rgba(160,0,0,0.18);'
             'font-family:Helvetica,Arial,sans-serif;font-weight:800;'
             'letter-spacing:6px;z-index:9999;pointer-events:none">'
             'PREVIEW — UNPAID</div>')


def watermark(html: str) -> str:
    """Overlay the unpaid-preview watermark on a rendered artifact page."""
    return html.replace("</body>", WATERMARK + "</body>")


def render_pdf(html: str, out_pdf: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        src = f.name
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={out_pdf}", f"file://{src}"],
        check=True, capture_output=True, timeout=120)
    return out_pdf
