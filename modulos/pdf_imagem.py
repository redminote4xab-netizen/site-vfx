import os
import img2pdf
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

class PDF_IMAGEM(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Título
        ctk.CTkLabel(self, text="MÓDULO PDF/IMAGEM", font=("Arial", 26, "bold"), text_color="#2ECC71").pack(pady=20)
        
        # Container
        container = ctk.CTkFrame(self, fg_color="#0A0A0A", border_color="#27AE60", border_width=1)
        container.pack(fill="both", expand=True, padx=30, pady=10)
        
        ctk.CTkLabel(container, text="🖼️ CONVERSÃO DE IMAGENS", font=("Arial", 18, "bold"), text_color="#2ECC71").pack(pady=(20, 10))
        
        # Botões
        btn_f = ctk.CTkFrame(container, fg_color="transparent")
        btn_f.pack(pady=10)
        
        ctk.CTkButton(btn_f, text="IMAGENS -> PDF ÚNICO", width=220, height=45, fg_color="#1E3D1E", 
                      hover_color="#27AE60", command=self.imagens_para_pdf_unificado).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_f, text="IMAGENS -> PDFs INDIVIDUAIS", width=220, height=45, fg_color="#1E3D1E", 
                      hover_color="#27AE60", command=self.imagens_para_pdf_individual).pack(side="left", padx=10)
        
        # Log
        self.log_widget = ctk.CTkTextbox(container, height=300, fg_color="#050505", border_color="#1E3D1E", border_width=1, text_color="#2ECC71")
        self.log_widget.pack(fill="both", expand=True, padx=20, pady=20)

    def write_log(self, msg):
        self.log_widget.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_widget.see("end")

    def imagens_para_pdf_unificado(self):
        arquivos = filedialog.askopenfilenames(title="Selecione as imagens", filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if not arquivos: return
        destino = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not destino: return
        try:
            pdf_bytes = img2pdf.convert(arquivos)
            with open(destino, "wb") as f: f.write(pdf_bytes)
            self.write_log(f"✅ SUCESSO: PDF unificado gerado em {os.path.basename(destino)}")
            messagebox.showinfo("Sucesso", "PDF Unificado criado!")
        except Exception as e:
            self.write_log(f"❌ ERRO: {e}")

    def imagens_para_pdf_individual(self):
        arquivos = filedialog.askopenfilenames(title="Selecione as imagens", filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if not arquivos: return
        pasta_dest = filedialog.askdirectory()
        if not pasta_dest: return
        cont = 0
        for img in arquivos:
            try:
                nome_pdf = os.path.splitext(os.path.basename(img))[0] + ".pdf"
                caminho_full = os.path.join(pasta_dest, nome_pdf)
                with open(caminho_full, "wb") as f: f.write(img2pdf.convert(img))
                cont += 1
            except: continue
        self.write_log(f"✅ CONCLUÍDO: {cont} PDFs individuais gerados.")
        messagebox.showinfo("Fim", f"{cont} arquivos convertidos!")