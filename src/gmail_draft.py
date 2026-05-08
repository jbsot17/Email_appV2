"""Módulo de creación de emails en Gmail"""
import os
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.generator import Generator
from io import BytesIO
from typing import Dict, List, Optional, Callable
from pathlib import Path
from src.templates import aplicar_variables


class GmailBorrador:
    """Clase para crear/enviar emails en Gmail."""
    
    def __init__(self, gmail_email: str, app_password: str):
        self.gmail_email = gmail_email
        self.app_password = app_password
    
    def crear_borrador(self, destinatario: str, subject: str, body_html: str, 
                    adjunto: Optional[str] = None,
                    sender_name: Optional[str] = None) -> bool:
        """Crea y envía un email."""
        try:
            # Crear mensaje MIME
            msg = MIMEMultipart()
            
            # Formatear remitente como "Nombre" <email@dominio.com>
            if sender_name and sender_name.strip():
                from_header = f'"{sender_name}" <{self.gmail_email}>'
            else:
                from_header = self.gmail_email
            
            msg['From'] = from_header
            msg['To'] = destinatario
            msg['Subject'] = subject
            
            # Parte HTML
            msg.attach(MIMEText(body_html, 'html', 'utf-8'))
            
            # Adjunto si existe
            if adjunto and os.path.exists(adjunto):
                nombre_archivo = os.path.basename(adjunto)
                
                with open(adjunto, 'rb') as f:
                    contenido = f.read()
                
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(contenido)
                encoders.encode_base64(part)
                
                part.add_header(
                    'Content-Disposition', 
                    f'attachment; filename="{nombre_archivo}"'
                )
                part.add_header('Content-ID', f'<{nombre_archivo}>')
                msg.attach(part)
            
            # Enviar
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.gmail_email, self.app_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return str(e)
    
    def crear_borradores(self, datos: List[Dict], template: str, subject: str,
                        adjunto: Optional[str] = None,
                        callback: Optional[Callable] = None,
                        delay: float = 1.0,
                        sender_name: Optional[str] = None) -> Dict:
        """Crea múltiples emails."""
        import time
        
        stats = {'creados': 0, 'fallidos': 0, 'total': len(datos)}
        
        for i, dato in enumerate(datos, 1):
            variables = {
                'Folio Number': str(dato.get('folio', '')),
                'Property Address': str(dato.get('address', ''))
            }
            
            body = aplicar_variables(template, variables)
            destino = dato.get('email', '')
            
            resultado = self.crear_borrador(destino, subject, body, adjunto, sender_name)
            
            if resultado is True:
                stats['creados'] += 1
                msg = f"[{i}/{stats['total']}] OK: {destino}"
            else:
                stats['fallidos'] += 1
                msg = f"[{i}/{stats['total']}] FAIL: {resultado}"
            
            if callback:
                callback(msg)
            
            if i < len(datos):
                time.sleep(delay)
        
        return stats


