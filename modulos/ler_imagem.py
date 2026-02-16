import os
import re
import xlwt 
import easyocr
import numpy as np
import pdfplumber
from docx import Document
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk

class LerImagemFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#121212", corner_radius=15)
        self.lista_arquivos = []
        # Tenta inicializar o leitor. Nota: Na primeira vez, ele vai baixar o modelo (+- 80MB)
        try:
            self.reader = easyocr.Reader(['pt'], gpu=False) 
        except Exception as e:
            print(f"Erro ao carregar EasyOCR: {e}")
        
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="SISTEMA DELTA PRO - SIGEF", font=("Segoe UI", 24, "bold"), text_color="#2ECC71").pack(pady=20)

        self.frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btns.pack(fill="x", padx=20)

        ctk.CTkButton(self.frame_btns, text="📂 ADICIONAR ARQUIVOS", command=self.carregar, fg_color="#1f6aa5").pack(side="left", padx=5, expand=True)
        ctk.CTkButton(self.frame_btns, text="🗑️ LIMPAR HISTÓRICO", command=self.limpar, fg_color="#E74C3C").pack(side="left", padx=5, expand=True)

        self.tree_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.tree_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Configuração da Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a1a1a", foreground="white", fieldbackground="#1a1a1a", borderwidth=0)
        style.map("Treeview", background=[('selected', '#2ECC71')])

        self.tree = ttk.Treeview(self.tree_frame, columns=("V", "X", "Y", "C"), show='headings')
        self.tree.heading("V", text="VÉRTICE")
        self.tree.heading("X", text="ESTE (X)")
        self.tree.heading("Y", text="NORTE (Y)")
        self.tree.heading("C", text="CONFRONTANTE")
        
        self.tree.column("V", width=100, anchor="center")
        self.tree.column("X", width=130, anchor="center")
        self.tree.column("Y", width=130, anchor="center")
        self.tree.column("C", width=350, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self.btn_gerar = ctk.CTkButton(self, text="🚀 GERAR EXCEL (LIMPEZA TOTAL)", command=self.processar, 
                                       fg_color="#27AE60", height=50, font=("Arial", 16, "bold"), state="disabled")
        self.btn_gerar.pack(pady=20, padx=20, fill="x")

    def limpar(self):
        self.lista_arquivos = []
        for i in self.tree.get_children(): self.tree.delete(i)
        self.btn_gerar.configure(state="disabled")

    def carregar(self):
        files = filedialog.askopenfilenames(filetypes=[("Todos os arquivos suportados", "*.pdf *.jpg *.png *.jpeg *.docx")])
        if files:
            self.lista_arquivos.extend(list(files))
            self.btn_gerar.configure(state="normal")
            messagebox.showinfo("Arquivos", f"{len(files)} arquivos adicionados com sucesso!")

    def limpeza_bruta(self, texto):
        texto = " ".join(texto.split())
        # Regex melhorada para pegar o confrontante
        padrao = r'(?:propriedade\s+de|confrontando\s+com\s+o|confrontando\s+com\s+a|com\s+a|com\s+o|confrontante|confronta\s+com)\s+(.*?)(?=[,]|com\s+azimute|azimute|partir|$)'
        match = re.search(padrao, texto, re.IGNORECASE)
        
        if match:
            nome = match.group(1).strip().upper()
            # Remove prefixos indesejados de forma iterativa sem risco de loop infinito
            for _ in range(5):
                nome = re.sub(r'^(PROPRIEDADE|LOTE|RAMAL|DE|DA|DO|O|A|COM|GLEBA)\s+', '', nome).strip()
                nome = re.sub(r'^[,\.\s:-]+', '', nome).strip()
            return nome if len(nome) > 1 else "NÃO IDENTIFICADO"
        return "NÃO IDENTIFICADO"

    def get_text(self, p):
        try:
            if p.lower().endswith('.pdf'):
                with pdfplumber.open(p) as pdf:
                    return " ".join([page.extract_text() or "" for page in pdf.pages])
            elif p.lower().endswith('.docx'):
                doc = Document(p)
                return " ".join([para.text for para in doc.paragraphs])
            else: # Imagens (JPG, PNG)
                resultado = self.reader.readtext(p, detail=0) # detail=0 retorna apenas o texto
                return " ".join(resultado)
        except Exception as e:
            print(f"Erro ao ler {p}: {e}")
            return ""

    def processar(self):
        if not self.lista_arquivos: return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".xls", filetypes=[("Excel 97", "*.xls")])
        if not save_path: return

        wb = xlwt.Workbook()
        ws = wb.add_sheet('PLANILHA')
        
        headers = ["VERTICE", "ESTE=X", "NORTE=Y", "ALTIT=Z", "CONFRONTANTE", "SIGMA X", "SIGMA Y"]
        for c, h in enumerate(headers):
            ws.write(0, c, h, xlwt.easyxf('font: bold on; align: horiz center'))
            ws.col(c).width = 7500

        row_idx = 1
        for f in self.lista_arquivos:
            texto = self.get_text(f)
            # Regex robusta para SIGEF/INCRA
            blocos = re.split(r'(?i)(?=v[ée]rtice)', texto)

            for bloco in blocos:
                # Procura Vértice, Norte (iniciando com 9 ou 8) e Este (iniciando com 7, 6 ou 5)
                v = re.search(r'(?i)v[ée]rtice\s+([A-Z0-9-]+)', bloco)
                n = re.search(r'N\s?[:=]?\s?([89]\.?\d{3}\.?\d{3}[,\.]\d{2,3})', bloco)
                e = re.search(r'E\s?[:=]?\s?([1-8]\d{2}\.?\d{3}[,\.]\d{2,3})', bloco)

                if v and n and e:
                    v_nome = v.group(1).upper()
                    n_val = n.group(1).replace('.', '').replace(',', '.')
                    e_val = e.group(1).replace('.', '').replace(',', '.')
                    conf = self.limpeza_bruta(bloco)

                    self.tree.insert("", "end", values=(v_nome, e_val, n_val, conf))
                    ws.write(row_idx, 0, v_nome)
                    ws.write(row_idx, 1, e_val)
                    ws.write(row_idx, 2, n_val)
                    ws.write(row_idx, 3, "0.00")
                    ws.write(row_idx, 4, conf)
                    row_idx += 1

        try:
            wb.save(save_path)
            messagebox.showinfo("Sucesso", f"Excel gerado com sucesso!\n{row_idx-1} vértices processados.")
            os.startfile(os.path.dirname(save_path))
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")