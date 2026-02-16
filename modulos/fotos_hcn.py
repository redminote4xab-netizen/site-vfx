import os
import re
import shutil
import threading
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

class FotosHCNFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pasta_brutos = ctk.StringVar(value="Não selecionada")
        self.rel_bruto_path = ""
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="PROCESSADOR FOTOS HCN/TXT", font=("Arial", 26, "bold"), text_color="#2ECC71").pack(pady=20)
        
        sel_bruto_f = ctk.CTkFrame(self, fg_color="#0A0A0A", border_color="#27AE60", border_width=1)
        sel_bruto_f.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(sel_bruto_f, textvariable=self.pasta_brutos, text_color="#2ECC71").pack(side="left", padx=15, pady=10)
        ctk.CTkButton(sel_bruto_f, text="SELECIONAR PASTA", fg_color="#27AE60", text_color="black", command=self.sel_pasta).pack(side="right", padx=10)

        f_bruto_ctrl = ctk.CTkFrame(self, fg_color="transparent")
        f_bruto_ctrl.pack(fill="x", padx=30, pady=10)
        self.btn_exec = ctk.CTkButton(f_bruto_ctrl, text="INICIAR TRIAGEM", width=200, height=40, fg_color="#27AE60", text_color="black", font=("Arial", 14, "bold"), command=self.run_process)
        self.btn_exec.pack(side="left", padx=10)
        self.btn_rel = ctk.CTkButton(f_bruto_ctrl, text="ABRIR RELATÓRIO", width=200, height=40, state="disabled", command=lambda: os.startfile(self.rel_bruto_path))
        self.btn_rel.pack(side="left", padx=10)

        self.log_bruto = ctk.CTkTextbox(self, height=350, fg_color="#050505", border_color="#27AE60", border_width=1, text_color="#2ECC71")
        self.log_bruto.pack(fill="both", expand=True, padx=30, pady=10)

    def sel_pasta(self):
        p = filedialog.askdirectory()
        if p: self.pasta_brutos.set(p)

    def write_log(self, msg):
        self.log_bruto.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_bruto.see("end")

    def run_process(self):
        if "Não" in self.pasta_brutos.get(): return messagebox.showerror("Erro", "Selecione a pasta!")
        threading.Thread(target=self.logic, daemon=True).start()

    def logic(self):
        self.btn_exec.configure(state="disabled")
        raiz = self.pasta_brutos.get()
        p_fotos_estoque = os.path.join(raiz, "FOTOS")
        self.write_log("📡 Iniciando Processamento HCN/TXT...")

        if not os.path.exists(p_fotos_estoque):
            self.write_log("❌ Erro: Pasta FOTOS não encontrada.")
            self.btn_exec.configure(state="normal")
            return

        estoque = {re.sub(r'[^A-Z0-9]', '', f.split('.')[0].upper()): f for f in os.listdir(p_fotos_estoque)}
        rel_data = []
        pastas_data = [d for d in os.listdir(raiz) if os.path.isdir(os.path.join(raiz, d)) and d.startswith("20")]

        for data in pastas_data:
            caminho_fotos_data = os.path.join(raiz, data, "Fotos")
            if not os.path.exists(caminho_fotos_data): os.makedirs(caminho_fotos_data)

            for root, dirs, files in os.walk(os.path.join(raiz, data)):
                if "Nativos" in root:
                    resp = os.path.basename(root)
                    for arq in files:
                        v_encontrados = []
                        ext = arq.upper()
                        if ext.endswith('.HCN'):
                            nome = arq.split('.')[0].upper()
                            if "-M-" in nome: v_encontrados.append(nome)
                        elif ext.endswith('.TXT'):
                            try:
                                with open(os.path.join(root, arq), 'r', encoding='latin-1') as f:
                                    for linha in f:
                                        p = linha.split(',') if ',' in linha else linha.split(';')
                                        n = p[0].strip().upper()
                                        if "-M-" in n: v_encontrados.append(n)
                            except: pass

                        for v_nome in set(v_encontrados):
                            v_norm = re.sub(r'[^A-Z0-9]', '', v_nome)
                            if v_norm in estoque:
                                shutil.copy2(os.path.join(p_fotos_estoque, estoque[v_norm]), os.path.join(caminho_fotos_data, f"{v_nome}{os.path.splitext(estoque[v_norm])[1]}"))
                            else:
                                rel_data.append({"VÉRTICE": v_nome, "RESPONSÁVEL": resp, "DATA": data})

        self.rel_bruto_path = os.path.join(raiz, "RELATORIO_PENDENCIAS_FOTOS.xlsx")
        if rel_data:
            pd.DataFrame(rel_data).to_excel(self.rel_bruto_path, index=False)
            self.btn_rel.configure(state="normal")
        self.btn_exec.configure(state="normal")
        self.write_log("✅ Concluído!")