"""Módulo de gestión de templates HTML"""
import os
from pathlib import Path
from typing import List, Dict


# Subjects por defecto para cada template
SUBJECTS = {
    'template1.html': 'Quick question about {address} recertification',
    'template2.html': 'Why its usually better not to wait on {address} recertification',
    'template3.html': 'How to make the Recertification of {address} simpler',
    'template4.html': 'Important difference when choosing help for {address}',
    'template4_planB.html': 'Important difference when choosing help for {address}',
    'template5.html': '{address} recertification. Should I close your file?'
}


def obtener_ruta_templates() -> Path:
    """Obtiene la ruta del directorio de templates."""
    # Usar ruta absoluta desde la ubicación del script
    base = Path(__file__).parent.parent.resolve()
    return base / 'templates'


def listar_templates() -> List[str]:
    """Lista las plantillas disponibles."""
    import os
    ruta = obtener_ruta_templates()
    
    if not ruta.exists():
        ruta = Path.cwd() / 'templates'
    
    if not ruta.exists():
        return []
    
    archivos = sorted(os.listdir(ruta))
    return [f for f in archivos if f.endswith('.html')]


def obtener_template(nombre: str) -> str:
    """Obtiene el contenido de una plantilla.
    
    Args:
        nombre: Nombre del archivo de plantilla
        
    Returns:
        Contenido HTML de la plantilla
    """
    ruta = obtener_ruta_templates() / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró la plantilla: {nombre}")
    
    with open(ruta, 'r', encoding='utf-8') as f:
        return f.read()


def aplicar_variables(template: str, variables: Dict[str, str]) -> str:
    """Aplica variables a una plantilla.
    
    Args:
        template: Contenido HTML de la plantilla
        variables: Diccionario con variables a reemplazar
        
    Returns:
        Template con variables reemplazadas
    """
    resultado = template
    for clave, valor in variables.items():
        resultado = resultado.replace('{{' + clave + '}}', str(valor))
    return resultado


def obtener_subject_template(nombre: str, property_address: str = '') -> str:
    """Obtiene el subject para un template.
    
    Args:
        nombre: Nombre del template
        property_address: Dirección de la propiedad
        
    Returns:
        Subject con la dirección reemplazada
    """
    subject = SUBJECTS.get(nombre, 'Email from Engineering Services')
    if property_address:
        subject = subject.replace('{address}', property_address)
    return subject