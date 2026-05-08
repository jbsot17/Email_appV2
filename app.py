"""ESIMO - ESI MailOps"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from threading import Thread
from PIL import Image
import customtkinter as ctk

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

sys.path.insert(0, str(Path(__file__).parent))

from src.reader import leer_archivo_datos
from src.auth import (
    agregar_cuenta, lista_cuentas, seleccionar_cuenta,
    obtener_cuenta_activa, obtener_cuenta_por_nombre, eliminar_cuenta
)
from src.templates import listar_templates, obtener_template, obtener_subject_template, eliminar_template, listar_firmas, guardar_firma, obtener_firma, inject_signature
from src.gmail_draft import GmailBorrador
from src.template_import import importar_template


class ESIMOApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ESIMO - ESI MailOps")
        self.root.geometry("950x680")
        self.root.minsize(850, 620)
        self.root.iconbitmap(str(Path(__file__).parent / "images" / "logo.ico"))
        
        self.color_company = "#2b2b2b"
        self.color_success = "#2CC985"
        self.color_danger = "#FF5C5C"
        self.color_warning = "#F59E0B"
        
        self.datos = None
        self.stats = None
        self.template_seleccionado = None
        self.adjunto = None
        self.ruta_pdf_importar = None
        self.crear_interfaz()

    def crear_interfaz(self):
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_rowconfigure(4, weight=0)
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # === HEADER (row 0) ===
        header = ctk.CTkFrame(self.root, fg_color=self.color_company, height=75)
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 0))
        
        logo_path = Path(__file__).parent / "images" / "logo.png"
        if logo_path.exists():
            logo_img = ctk.CTkImage(Image.open(logo_path), size=(55, 55))
            ctk.CTkLabel(header, image=logo_img, text="").pack(side="left", padx=(10, 5))
        
        header_content = ctk.CTkFrame(header, fg_color=self.color_company)
        header_content.pack(side="left", expand=True)
        
        ctk.CTkLabel(header_content, text="ESIMO", font=("Roboto", 34, "bold"), text_color="white").pack(anchor="center", pady=(10, 0))
        ctk.CTkLabel(header_content, text="ESI MailOps", font=("Roboto", 12), text_color="white").pack(anchor="center", pady=(0, 8))
        
        # === 1. CUENTA GMAIL (row 1) ===
        f1 = ctk.CTkFrame(self.root)
        f1.grid(row=1, column=0, sticky="ew", padx=15, pady=(8, 4))
        
        ctk.CTkLabel(f1, text="1. Cuenta Gmail", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=(5, 2))
        
        top_row = ctk.CTkFrame(f1, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(0, 3))
        
        self.combo_cuentas = ctk.CTkComboBox(top_row, values=lista_cuentas(), width=200)
        self.combo_cuentas.pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(top_row, text="Usar", command=self.seleccionar_cuenta_usar, width=60).pack(side="left", padx=2)
        ctk.CTkButton(top_row, text="Eliminar", command=self.eliminar_cuenta, fg_color=self.color_danger, width=70).pack(side="left", padx=2)
        
        fields_row = ctk.CTkFrame(f1, fg_color="transparent")
        fields_row.pack(fill="x", padx=10, pady=(0, 3))
        
        ctk.CTkLabel(fields_row, text="Nombre:", font=("Roboto", 11)).pack(side="left")
        self.entry_nombre = ctk.CTkEntry(fields_row, width=90, font=("Roboto", 11))
        self.entry_nombre.pack(side="left", padx=3)
        
        ctk.CTkLabel(fields_row, text="Email:", font=("Roboto", 11)).pack(side="left", padx=(10, 0))
        self.entry_email = ctk.CTkEntry(fields_row, width=140, font=("Roboto", 11))
        self.entry_email.pack(side="left", padx=3)
        
        ctk.CTkLabel(fields_row, text="Pass:", font=("Roboto", 11)).pack(side="left", padx=(10, 0))
        self.entry_password = ctk.CTkEntry(fields_row, width=90, show="*", font=("Roboto", 11))
        self.entry_password.pack(side="left", padx=3)
        
        ctk.CTkButton(fields_row, text="+ Agregar", command=self.agregar_cuenta, fg_color=self.color_success, width=80).pack(side="left", padx=(10, 0))
        
        sender_row = ctk.CTkFrame(f1, fg_color="transparent")
        sender_row.pack(fill="x", padx=10, pady=(0, 6))
        
        ctk.CTkLabel(sender_row, text="Remitente:", font=("Roboto", 11)).pack(side="left")
        self.entry_sender = ctk.CTkEntry(sender_row, width=180, font=("Roboto", 11))
        self.entry_sender.pack(side="left", padx=3)
        
        # === ROW 2: 2. Archivo | 3. Template ===
        row2 = ctk.CTkFrame(self.root)
        row2.grid(row=2, column=0, sticky="ew", padx=15, pady=4)
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)
        
        # 2. Archivo (izquierda)
        f2 = ctk.CTkFrame(row2)
        f2.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(f2, text="2. Archivo de Datos", font=("Roboto", 13, "bold")).pack(anchor="w", padx=10, pady=(5, 2))
        ctk.CTkButton(f2, text="Cargar XLSX/CSV", command=self.cargar_datos, fg_color=self.color_success, width=150).pack(anchor="w", padx=10, pady=(0, 3))
        self.lbl_datos = ctk.CTkLabel(f2, text="Sin archivo cargado", text_color="gray", font=("Roboto", 10))
        self.lbl_datos.pack(anchor="w", padx=10, pady=(0, 6))
        
        # 3. Template (derecha)
        f3 = ctk.CTkFrame(row2)
        f3.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(f3, text="3. Template", font=("Roboto", 13, "bold")).pack(anchor="w", padx=10, pady=(5, 2))
        
        templates = listar_templates()
        self.combo_template = ctk.CTkComboBox(f3, values=templates, width=180)
        self.combo_template.pack(anchor="w", padx=10, pady=(0, 3))
        self.combo_template.configure(command=self.seleccionar_template)
        
        btn_preview = ctk.CTkFrame(f3, fg_color="transparent")
        btn_preview.pack(anchor="w", padx=10, pady=(0, 2))
        ctk.CTkButton(btn_preview, text="Ver Preview", command=self.ver_preview, width=80).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_preview, text="Eliminar", command=self.eliminar_template, fg_color=self.color_danger, width=70).pack(side="left", padx=2)
        
        self.lbl_subject = ctk.CTkLabel(f3, text="", text_color="gray", font=("Roboto", 9))
        self.lbl_subject.pack(anchor="w", padx=10, pady=(0, 2))

        firma_row = ctk.CTkFrame(f3, fg_color="transparent")
        firma_row.pack(anchor="w", padx=10, pady=(0, 6))
        ctk.CTkLabel(firma_row, text="Firma:", font=("Roboto", 11)).pack(side="left")
        self.combo_firma = ctk.CTkComboBox(firma_row, values=listar_firmas(), width=130)
        self.combo_firma.pack(side="left", padx=5)
        ctk.CTkButton(firma_row, text="Firmas", command=self.abrir_gestor_firmas, width=60).pack(side="left")
        
        # === ROW 3: 4. Adjunto | 5. Importar Template | ENVIAR ===
        row3 = ctk.CTkFrame(self.root)
        row3.grid(row=3, column=0, sticky="ew", padx=15, pady=4)
        row3.grid_columnconfigure(0, weight=1)
        row3.grid_columnconfigure(1, weight=1)
        row3.grid_columnconfigure(2, weight=0)
        
        # 4. Adjunto (col 0)
        f4 = ctk.CTkFrame(row3)
        f4.grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkLabel(f4, text="4. Adjunto", font=("Roboto", 13, "bold")).pack(anchor="w", padx=10, pady=(5, 2))
        ctk.CTkButton(f4, text="Seleccionar PDF", command=self.seleccionar_adjunto, width=150).pack(anchor="w", padx=10, pady=(0, 3))
        self.lbl_adj = ctk.CTkLabel(f4, text="Ninguno", text_color="gray", font=("Roboto", 10))
        self.lbl_adj.pack(anchor="w", padx=10, pady=(0, 6))
        
        # 5. Importar Template (col 1)
        f_import = ctk.CTkFrame(row3)
        f_import.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        ctk.CTkLabel(f_import, text="5. Importar Template", font=("Roboto", 13, "bold")).pack(anchor="w", padx=10, pady=(5, 2))
        import_row = ctk.CTkFrame(f_import, fg_color="transparent")
        import_row.pack(fill="x", padx=10, pady=(0, 5))
        ctk.CTkButton(import_row, text="Cargar PDF", command=self.seleccionar_archivo_template, width=90).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(import_row, text="Nombre:", font=("Roboto", 11)).pack(side="left")
        self.entry_template_nombre = ctk.CTkEntry(import_row, width=100, font=("Roboto", 11))
        self.entry_template_nombre.pack(side="left", padx=3)
        ctk.CTkButton(import_row, text="+ Agregar", command=self.agregar_template, fg_color=self.color_success, width=75).pack(side="left")
        self.lbl_import_status = ctk.CTkLabel(f_import, text="", text_color="gray", font=("Roboto", 10))
        self.lbl_import_status.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Boton ENVIAR (col 2)
        self.btn_enviar = ctk.CTkButton(
            row3, 
            text="ENVIAR EMAILS", 
            command=self.enviar_emails, 
            fg_color=self.color_company,
            hover_color="#A0000B",
            font=("Roboto", 14, "bold"),
            height=45,
            width=150
        )
        self.btn_enviar.grid(row=0, column=2, sticky="e", padx=(5, 0))

        # === ROW 4: Resumen ===
        f_resumen = ctk.CTkFrame(self.root, fg_color="#f0f0f0")
        f_resumen.grid(row=4, column=0, sticky="ew", padx=15, pady=4)
        self.lbl_resumen = ctk.CTkLabel(f_resumen, text="Estado: Sin datos cargados", font=("Roboto", 12), text_color="gray")
        self.lbl_resumen.pack(padx=10, pady=6)
        
        # === ROW 5: Log (expande) ===
        f_log = ctk.CTkFrame(self.root)
        f_log.grid(row=5, column=0, sticky="nsew", padx=15, pady=(4, 10))
        ctk.CTkLabel(f_log, text="Log de actividad", font=("Roboto", 11, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        log_scroll = ctk.CTkScrollableFrame(f_log, height=130)
        log_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_scroll, font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)
        self.log = lambda m: (self.log_text.insert("end", m + "\n"), self.log_text.see("end"))
        
        self.cargar_config()
        self.root.mainloop()

    def actualizar_resumen(self):
        if self.datos and self.template_seleccionado and self.stats:
            adj_text = f" | {os.path.basename(self.adjunto)}" if self.adjunto else ""
            addr = self.datos[0].get('address', '') if self.datos else ''
            folio = self.datos[0].get('folio', '') if self.datos else ''
            data_text = f" | {addr}" if addr else ""
            data_text += f" (Folio {folio})" if folio else ""
            self.lbl_resumen.configure(text=f"Resumen: {self.stats['total']} | {self.template_seleccionado}{data_text}{adj_text}", text_color=self.color_success)
        elif self.datos and self.stats:
            self.lbl_resumen.configure(text=f"Resumen: {self.stats['total']} | Sin template", text_color=self.color_warning)
        else:
            self.lbl_resumen.configure(text="Estado: Sin datos cargados", text_color="gray")

    def cargar_config(self):
        cuentas = lista_cuentas()
        self.combo_cuentas.configure(values=cuentas)
        if cuentas:
            self.combo_cuentas.set(cuentas[0])
            cuenta = obtener_cuenta_activa()
            if cuenta:
                self.entry_email.insert(0, cuenta.get('email', ''))
                self.entry_sender.insert(0, cuenta.get('sender_name', ''))
                self.log(f"[ESIMO] Cuenta: {cuenta.get('nombre')}")

    def agregar_cuenta(self):
        nombre = self.entry_nombre.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        sender = self.entry_sender.get().strip()
        if not nombre or not email or not password:
            messagebox.showwarning("Falta", "Datos incompletos")
            return
        agregar_cuenta(nombre, email, password, sender)
        self.entry_nombre.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_sender.delete(0, tk.END)
        self.combo_cuentas.configure(values=lista_cuentas())
        self.log(f"[ESIMO] Cuenta '{nombre}' guardada")

    def seleccionar_cuenta_usar(self):
        nombre = self.combo_cuentas.get()
        if not nombre: return
        cuenta = obtener_cuenta_por_nombre(nombre)
        if cuenta:
            seleccionar_cuenta(nombre)
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, cuenta.get('email', ''))
            self.entry_sender.delete(0, tk.END)
            self.entry_sender.insert(0, cuenta.get('sender_name', ''))
            self.log(f"[ESIMO] Cuenta: {nombre}")

    def eliminar_cuenta(self):
        nombre = self.combo_cuentas.get()
        if not nombre: return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar '{nombre}'?"): return
        eliminar_cuenta(nombre)
        self.entry_email.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_sender.delete(0, tk.END)
        self.combo_cuentas.configure(values=lista_cuentas())
        self.log(f"[ESIMO] Cuenta eliminada")

    def cargar_datos(self):
        archivo = filedialog.askopenfilename(title="Seleccionar archivo", filetypes=[("Excel", "*.xlsx *.xls"), ("CSV", "*.csv")])
        if archivo:
            try:
                self.datos, self.stats = leer_archivo_datos(archivo)
                self.lbl_datos.configure(text=f"✅ {self.stats['total']} registros cargados", text_color=self.color_success)
                self.actualizar_resumen()
                self.log(f"[ESIMO] Archivo: {self.stats['total']} registros")
                if self.template_seleccionado:
                    subject = obtener_subject_template(self.template_seleccionado, self.datos[0].get('address', ''), self.datos[0].get('folio', ''))
                    self.lbl_subject.configure(text=f"Asunto: {subject}", text_color=self.color_success)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.log(f"[ERROR] {str(e)}")

    def seleccionar_template(self, val=None):
        self.template_seleccionado = self.combo_template.get()
        if self.template_seleccionado:
            if self.datos:
                subject = obtener_subject_template(self.template_seleccionado, self.datos[0].get('address', ''), self.datos[0].get('folio', ''))
                self.lbl_subject.configure(text=f"Asunto: {subject}", text_color=self.color_success)
            else:
                self.lbl_subject.configure(text=f"Template: {self.template_seleccionado}", text_color=self.color_success)
            self.actualizar_resumen()
            self.log(f"[ESIMO] Template: {self.template_seleccionado}")

    def ver_preview(self):
        if not self.template_seleccionado:
            messagebox.showwarning("!", "Seleccione template")
            return
        try:
            from src.templates import aplicar_variables
            html = aplicar_variables(obtener_template(self.template_seleccionado), {'Folio Number': 'EXAMPLE-001', 'Property Address': '123 Main Street'})
            firma = self.combo_firma.get()
            if firma:
                firma_html = obtener_firma(firma)
                html = inject_signature(html, firma_html)
            import tempfile, webbrowser
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
                f.write(html)
                webbrowser.open(f.name)
            self.log(f"[ESIMO] Preview abierta")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def abrir_gestor_firmas(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Administrar Firmas")
        win.geometry("450x380")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="Firmas Existentes", font=("Roboto", 13, "bold")).pack(anchor="w", padx=15, pady=(12, 2))
        firmas = listar_firmas()
        lbl_firmas = ctk.CTkLabel(win, text="\n".join(firmas) if firmas else "(ninguna)", font=("Roboto", 11), text_color="gray", justify="left")
        lbl_firmas.pack(anchor="w", padx=15, pady=(0, 8))

        ctk.CTkLabel(win, text="Crear Nueva Firma", font=("Roboto", 13, "bold")).pack(anchor="w", padx=15, pady=(4, 4))

        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=(0, 8))

        fields = [
            ("Nombre:", "person_name"),
            ("Cargo:", "title"),
            ("Email:", "email"),
            ("Tel. Directo:", "direct_phone"),
            ("Tel. Oficina:", "office_phone"),
        ]
        entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(frame, text=label, font=("Roboto", 11)).grid(row=i, column=0, sticky="w", pady=2)
            entry = ctk.CTkEntry(frame, width=280, font=("Roboto", 11))
            entry.grid(row=i, column=1, sticky="w", padx=(8, 0), pady=2)
            entries[key] = entry

        def guardar():
            data = {}
            for key, entry in entries.items():
                val = entry.get().strip()
                if not val:
                    messagebox.showwarning("Falta", f"Complete el campo: {key}")
                    return
                data[key] = val
            nombre_archivo = data["person_name"].lower().replace(" ", "_") + ".json"
            ruta = guardar_firma(nombre_archivo, data)
            self.combo_firma.configure(values=listar_firmas())
            win.destroy()
            self.log(f"[ESIMO] Firma creada: {nombre_archivo}")

        ctk.CTkButton(win, text="Guardar Firma", command=guardar, fg_color=self.color_success, width=120).pack(pady=(4, 12))

    def seleccionar_archivo_template(self):
        archivo = filedialog.askopenfilename(title="Seleccionar PDF", filetypes=[("PDF", "*.pdf")])
        if archivo:
            self.ruta_pdf_importar = archivo
            self.lbl_import_status.configure(text=os.path.basename(archivo), text_color=self.color_success)
            self.log(f"[ESIMO] PDF seleccionado: {os.path.basename(archivo)}")

    def agregar_template(self):
        if not self.ruta_pdf_importar:
            messagebox.showwarning("!", "Seleccione un archivo PDF primero")
            return
        nombre = self.entry_template_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("!", "Ingrese un nombre para el template")
            return
        try:
            importar_template(self.ruta_pdf_importar, nombre)
            self.ruta_pdf_importar = None
            self.entry_template_nombre.delete(0, tk.END)
            self.lbl_import_status.configure(text="")
            self.combo_template.configure(values=listar_templates())
            self.log(f"[ESIMO] Template '{nombre}' importado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"[ERROR] {str(e)}")

    def eliminar_template(self):
        if not self.template_seleccionado:
            messagebox.showwarning("!", "Seleccione un template")
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar '{self.template_seleccionado}'?"):
            return
        try:
            eliminar_template(self.template_seleccionado)
            self.template_seleccionado = None
            self.lbl_subject.configure(text="")
            self.combo_template.configure(values=listar_templates())
            self.actualizar_resumen()
            self.log(f"[ESIMO] Template eliminado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"[ERROR] {str(e)}")

    def seleccionar_adjunto(self):
        archivo = filedialog.askopenfilename(title="Seleccionar adjunto", filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")])
        if archivo:
            self.adjunto = archivo
            self.lbl_adj.configure(text=f"📎 {os.path.basename(archivo)}", text_color=self.color_success)
            self.actualizar_resumen()
            self.log(f"[ESIMO] Adjunto: {os.path.basename(archivo)}")

    def enviar_emails(self):
        if not self.datos:
            messagebox.showwarning("!", "Cargue archivo de datos")
            return
        if not self.template_seleccionado:
            messagebox.showwarning("!", "Seleccione template")
            return
        cuenta = obtener_cuenta_activa()
        if not cuenta:
            messagebox.showwarning("!", "Seleccione cuenta")
            return
        if not messagebox.askyesno("Confirmar", f"¿Enviar {len(self.datos)} emails?"):
            return
        try:
            template = obtener_template(self.template_seleccionado)
            subject = obtener_subject_template(self.template_seleccionado, self.datos[0].get('address', ''), self.datos[0].get('folio', ''))
            firma_html = obtener_firma(self.combo_firma.get())
            if firma_html:
                template = inject_signature(template, firma_html)
            Gmail = GmailBorrador(cuenta['email'], cuenta['app_password'])
            self.btn_enviar.configure(state="disabled", text="ENVIANDO...")
            self.log(f"[ESIMO] Enviando {len(self.datos)}...")

            def proceso():
                try:
                    stats = Gmail.crear_borradores(datos=self.datos, template=template, subject=subject, adjunto=self.adjunto, sender_name=cuenta.get('sender_name', ''), callback=self.log)
                    self.root.after(0, lambda: messagebox.showinfo("Completado", f"OK: {stats['creados']} | Errores: {stats['fallidos']}"))
                    self.root.after(0, lambda: self.btn_enviar.configure(state="normal", text="ENVIAR EMAILS"))
                except Exception as ex:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(ex)))
                    self.root.after(0, lambda: self.btn_enviar.configure(state="normal", text="ENVIAR EMAILS"))

            Thread(target=proceso, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == '__main__':
    ESIMOApp()
