"""Módulo de lectura de archivos XLSX/CSV"""
import os
import pandas as pd
from typing import List, Dict, Tuple
import re


def leer_archivo_datos(ruta_archivo: str) -> Tuple[List[Dict], Dict]:
    """Lee un archivo CSV o XLSX y retorna los datos y estadísticas.
    
    Args:
        ruta_archivo: Ruta al archivo CSV o XLSX
        
    Returns:
        Tupla: (lista de datos, diccionario de estadísticas)
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
    
    ext = os.path.splitext(ruta_archivo)[1].lower()
    
    if ext == '.csv':
        df = pd.read_csv(ruta_archivo)
    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(ruta_archivo)
    else:
        raise ValueError(f"Formato no soportado: {ext}. Use CSV o XLSX")
    
    df.columns = df.columns.str.strip().str.lower()
    
    required_cols = ['email', 'folio', 'address']
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        raise ValueError(f"Columnas faltantes: {', '.join(missing)}. "
                        f"Columnas encontradas: {', '.join(df.columns)}")
    
    df['email'] = df['email'].astype(str).str.strip()
    df['folio'] = df['folio'].astype(str).str.strip()
    df['address'] = df['address'].astype(str).str.strip()
    
    df = df.dropna(subset=['email'])
    
    datos = df[['email', 'folio', 'address']].to_dict('records')
    stats = validar_datos(datos)
    
    return datos, stats


def validar_datos(datos: List[Dict]) -> Dict:
    """Valida los datos y retorna estadísticas.
    
    Args:
        datos: Lista de diccionarios con email, folio, address
        
    Returns:
        Diccionario con estadísticas de validación
    """
    email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
    stats = {
        'total': len(datos),
        'validos': 0,
        'invalidos': 0,
        'emails_unicos': set()
    }
    
    for item in datos:
        email = item.get('email', '')
        if email and email_pattern.match(email):
            stats['validos'] += 1
            stats['emails_unicos'].add(email)
        else:
            stats['invalidos'] += 1
    
    stats['emails_unicos'] = len(stats['emails_unicos'])
    
    return stats


