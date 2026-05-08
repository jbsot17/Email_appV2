"""Módulo de gestión de credenciales Gmail"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

CONFIG_FILE = 'config.json'


def obtener_ruta_config() -> Path:
    """Obtiene la ruta del archivo de configuración."""
    return Path(__file__).parent.parent.resolve() / CONFIG_FILE


def cargar_credenciales() -> Dict:
    """Carga las credenciales desde el archivo."""
    ruta = obtener_ruta_config()
    if ruta.exists():
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def guardar_credenciales(credenciales: Dict) -> None:
    """Guarda las credenciales en el archivo.
    
    Args:
        credenciales: Diccionario con cuentas (lista)
    """
    ruta = obtener_ruta_config()
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(credenciales, f, indent=4, ensure_ascii=False)


def obtener_config() -> Dict:
    """Obtiene la configuración actual."""
    config = cargar_credenciales()
    if not config:
        config = {
            'cuentas': [],
            'cuenta_seleccionada': ''
        }
    return config


def lista_cuentas() -> List[str]:
    """Lista los nombres de las cuentas guardadas."""
    config = obtener_config()
    return [c['nombre'] for c in config.get('credenciales', [])]


def agregar_cuenta(nombre: str, email: str, app_password: str, sender_name: str = '') -> None:
    """Agrega una nueva cuenta."""
    config = obtener_config()
    
    if 'credenciales' not in config:
        config['credenciales'] = []
    
    # Verificar si ya existe
    existe = False
    for c in config['credenciales']:
        if c.get('nombre') == nombre:
            c['email'] = email
            c['app_password'] = app_password
            c['sender_name'] = sender_name
            existe = True
            break
    
    if not existe:
        config['credenciales'].append({
            'nombre': nombre,
            'email': email,
            'app_password': app_password,
            'sender_name': sender_name
        })
    
    # Si es la primera, seleccionarla
    if not config.get('cuenta_seleccionada'):
        config['cuenta_seleccionada'] = nombre
    
    guardar_credenciales(config)


def eliminar_cuenta(nombre: str) -> None:
    """Elimina una cuenta."""
    config = obtener_config()
    
    if 'credenciales' in config:
        config['credenciales'] = [c for c in config['credenciales'] if c['nombre'] != nombre]
    
    if config.get('cuenta_seleccionada') == nombre:
        config['cuenta_seleccionada'] = config['credenciales'][0]['nombre'] if config['credenciales'] else ''
    
    guardar_credenciales(config)


def seleccionar_cuenta(nombre: str) -> None:
    """Selecciona una cuenta por defecto."""
    config = obtener_config()
    config['cuenta_seleccionada'] = nombre
    guardar_credenciales(config)


def obtener_cuenta_activa() -> Optional[Dict]:
    """Obtiene la cuenta activa."""
    config = obtener_config()
    nombre = config.get('cuenta_seleccionada', '')
    
    if not nombre:
        return None
    
    for c in config.get('credenciales', []):
        if c['nombre'] == nombre:
            return c
    
    return None


def obtener_cuenta_por_nombre(nombre: str) -> Optional[Dict]:
    """Obtiene una cuenta por su nombre."""
    config = obtener_config()
    
    for c in config.get('credenciales', []):
        if c['nombre'] == nombre:
            return c
    
    return None


