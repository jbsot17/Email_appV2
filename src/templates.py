"""Módulo de gestión de templates HTML"""
import json
import os
from pathlib import Path
from typing import List, Dict
import re


SUBJECTS_JSON = 'subjects.json'

SUBJECTS_BUILTIN = {
    'template1.html': 'Quick question about {address} recertification',
    'template2.html': 'Why its usually better not to wait on {address} recertification',
    'template3.html': 'How to make the Recertification of {address} simpler',
    'template4.html': 'Important difference when choosing help for {address}',
    'template4_planB.html': 'Important difference when choosing help for {address}',
    'template5.html': '{address} recertification. Should I close your file?'
}

SIGNATURE_TEMPLATE = """\
<div class="signature">
    <p class="name">{person_name}</p>
    <p class="title">{title}</p>
    <p class="contact">
        <a href="mailto:{email}">{email}</a> | <strong>Direct:</strong> {direct_phone}<br>
        <span class="company">Engineering Services, Inc.</span><br>
        Office: {office_phone} | <a href="https://engsv.com/recertification">engsv.com</a>
    </p>
    <p class="motto">Committed engineering. Seamless compliance.</p>
</div>"""


def _ruta_subjects() -> Path:
    return obtener_ruta_templates() / SUBJECTS_JSON


def _cargar_subjects() -> Dict[str, str]:
    ruta = _ruta_subjects()
    if ruta.exists():
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _guardar_subjects(subjects: Dict[str, str]) -> None:
    ruta = _ruta_subjects()
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(subjects, f, indent=2, ensure_ascii=False)


def guardar_template(nombre: str, contenido: str, subject: str = '') -> Path:
    filename = nombre if nombre.endswith('.html') else nombre + '.html'
    ruta = obtener_ruta_templates() / filename
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(contenido)
    if subject:
        subjects = _cargar_subjects()
        subjects[filename] = subject
        _guardar_subjects(subjects)
    return ruta


def eliminar_template(nombre: str) -> None:
    ruta = obtener_ruta_templates() / nombre
    if ruta.exists():
        ruta.unlink()
    subjects = _cargar_subjects()
    subjects.pop(nombre, None)
    _guardar_subjects(subjects)


def obtener_ruta_firmas() -> Path:
    base = Path(__file__).parent.parent.resolve()
    return base / 'signatures'


def render_firma(data: Dict) -> str:
    return SIGNATURE_TEMPLATE.format(**data)


def listar_firmas() -> List[str]:
    ruta = obtener_ruta_firmas()
    if not ruta.exists():
        return []
    archivos = sorted(f for f in os.listdir(ruta) if f.endswith('.json'))
    return archivos


def obtener_firma(nombre: str) -> str:
    ruta = obtener_ruta_firmas() / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró la firma: {nombre}")
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return render_firma(data)


def inject_signature(html: str, firma_html: str) -> str:
    start = html.find('<div class="signature">')
    if start >= 0:
        depth = 1
        pos = start + len('<div class="signature">')
        while depth > 0 and pos < len(html):
            if html[pos:pos+4] == '<div':
                depth += 1
                pos += 4
            elif html[pos:pos+5] == '</div':
                depth -= 1
                pos += 5
            else:
                pos += 1
        html = html[:start] + html[pos:]
    html = html.replace('</body>', f'{firma_html}\n</body>')
    return html


def guardar_firma(nombre: str, data: Dict) -> Path:
    filename = nombre if nombre.endswith('.json') else nombre + '.json'
    ruta = obtener_ruta_firmas() / filename
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return ruta


def obtener_ruta_templates() -> Path:
    base = Path(__file__).parent.parent.resolve()
    return base / 'templates'


def listar_templates() -> List[str]:
    import os
    ruta = obtener_ruta_templates()
    if not ruta.exists():
        ruta = Path.cwd() / 'templates'
    if not ruta.exists():
        return []
    archivos = sorted(os.listdir(ruta))
    return [f for f in archivos if f.endswith('.html')]


def obtener_template(nombre: str) -> str:
    ruta = obtener_ruta_templates() / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró la plantilla: {nombre}")
    with open(ruta, 'r', encoding='utf-8') as f:
        return f.read()


def aplicar_variables(template: str, variables: Dict[str, str]) -> str:
    resultado = template
    for clave, valor in variables.items():
        resultado = resultado.replace('{{' + clave + '}}', str(valor))
    return resultado


def obtener_subject_template(nombre: str, property_address: str = '') -> str:
    todos = {**SUBJECTS_BUILTIN, ** _cargar_subjects()}
    subject = todos.get(nombre, 'Email from Engineering Services')
    if property_address:
        subject = subject.replace('{address}', property_address)
    return subject
