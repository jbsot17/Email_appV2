"""Módulo de importación de templates desde PDF"""
import os
from pathlib import Path
from src.templates import guardar_template

CSS = """\
body{margin:0;padding:20px;font-family:Arial,Helvetica,sans-serif;color:#333333;font-size:15px;line-height:1.6}
.greeting{font-size:16px;line-height:1.6;margin-bottom:18px}
.message{font-size:15px;line-height:1.6;margin-bottom:15px}
.property-box{background:#f9f9f9;padding:15px;margin:20px 0;text-align:left}
.property-label{font-size:12px;color:#666666;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px}
.property-value{font-size:15px;font-weight:bold}
.signature{margin-top:30px;padding-top:20px;border-top:1px solid #ddd;text-align:left}
.signature .name{font-weight:bold;font-size:15px;color:#333}
.signature .title{font-size:13px;color:#666;margin-bottom:8px}
.signature .contact{font-size:13px;color:#333}
.signature .contact a{color:#00aaff;text-decoration:none}
.signature .company{color:#dc000d;font-weight:bold;font-size:14px}
.signature .motto{font-size:11px;color:#888;font-style:italic;margin-top:8px}"""

PROPERTY_BOX = """\
<div class="property-box">
    <p class="property-label">Property Address</p>
    <p class="property-value">{{Property Address}}</p>
    <p class="property-label" style="margin-top:12px">Folio Number</p>
    <p class="property-value">{{Folio Number}}</p>
</div>"""


def importar_template(ruta_pdf: str, nombre: str) -> Path:
    ext = os.path.splitext(ruta_pdf)[1].lower()
    if ext != '.pdf':
        raise ValueError(f"Formato no soportado: {ext}. Solo PDF.")
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_pdf}")

    subject, body_html = _pdf_a_html(ruta_pdf)
    return guardar_template(nombre, body_html, subject)


def _pdf_a_html(ruta: str):
    import fitz
    doc = fitz.open(ruta)
    raw_text = ""
    for page in doc:
        raw_text += page.get_text()
    doc.close()

    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]

    if not lines:
        raise ValueError("El PDF no contiene texto extraíble.")

    subject = ""
    preheader = ""
    body_lines = []

    for i, line in enumerate(lines):
        lower = line.lower()
        if lower.startswith("subject line"):
            rest = line[len("subject line"):].strip(": ").strip()
            if rest:
                subject = rest
            elif i + 1 < len(lines):
                subject = lines[i + 1]
        elif lower.startswith("preview") and "preheader" in lower:
            rest = line.split(":", 1)[1].strip() if ":" in line else ""
            if rest:
                preheader = rest
            elif i + 1 < len(lines):
                preheader = lines[i + 1]
        elif lower.startswith("email body"):
            rest = line[len("email body"):].strip(": ").strip()
            body_lines = ([rest] + lines[i+1:]) if rest else lines[i+1:]
            break

    if not subject:
        subject = lines[0]
        body_lines = lines[1:]

    preheader_html = f'<div style="display:none;max-height:0px;overflow:hidden;color:transparent;font-size:0px;line-height:0px;mso-hide:all;">{preheader}</div>' if preheader else ""
    body_paragraphs = "\n".join(f'<p class="message">{l}</p>' for l in body_lines[1:]) if len(body_lines) > 1 else ""

    body = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><style>{CSS}</style></head>
<body>
{preheader_html}
<p class="greeting">{body_lines[0] if body_lines else ""}</p>
{body_paragraphs}
{PROPERTY_BOX}
</body>
</html>"""
    return subject, body
