import os
import re
import shutil
import threading
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

class FotosXMLFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pasta_raiz = ctk.StringVar(value="Não selecionada")
        self.rel_path = ""
        self.setup_ui()

    def setup_ui(self):
        header_f = ctk.CTkFrame(self, fg_color="transparent")
        header_f.pack(fill="x", pady=15)
        ctk.CTkLabel(header_f, text="PROCESSADOR FOTOS XML/XLSX", font=("Arial", 26, "bold"), text_color="#2ECC71").pack(side="left", padx=30)
        
        sel_f = ctk.CTkFrame(self, fg_color="#0A0A0A", border_color="#27AE60", border_width=1)
        sel_f.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(sel_f, textvariable=self.pasta_raiz, text_color="#2ECC71").pack(side="left", padx=15, pady=10)
        ctk.CTkButton(sel_f, text="SELECIONAR PASTA", fg_color="#27AE60", text_color="black", command=self.sel_pasta).pack(side="right", padx=10)

        self.prog_bar = ctk.CTkProgressBar(self, width=800, progress_color="#2ECC71")
        self.prog_bar.pack(pady=10); self.prog_bar.set(0)
        
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=5)
        self.btn_run = ctk.CTkButton(btns, text="INICIAR PROCESSO XML", width=200, height=40, fg_color="#27AE60", text_color="black", command=self.run_process)
        self.btn_run.pack(side="left", padx=10)
        self.btn_rel = ctk.CTkButton(btns, text="ABRIR RELATÓRIO", width=200, height=40, state="disabled", command=self.abrir_relatorio)
        self.btn_rel.pack(side="left", padx=10)

        self.log_text = ctk.CTkTextbox(self, height=350, fg_color="#050505", border_color="#27AE60", border_width=1, text_color="#2ECC71")
        self.log_text.pack(fill="both", expand=True, padx=30, pady=10)

    def sel_pasta(self):
        p = filedialog.askdirectory()
        if p: self.pasta_raiz.set(p)

    def write_log(self, msg):
        self.log_text.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see("end")

    def abrir_relatorio(self):
        if os.path.exists(self.rel_path):
            os.startfile(self.rel_path)

    def run_process(self):
        if "Não" in self.pasta_raiz.get(): return messagebox.showerror("Erro", "Selecione a pasta raiz!")
        self.btn_run.configure(state="disabled")
        threading.Thread(target=self.logic, daemon=True).start()

    def logic(self):
        raiz = self.pasta_raiz.get()
        p_fotos_estoque = os.path.join(raiz, "FOTOS")
        self.write_log("🚀 Iniciando Fluxo FOTOS XML (Ajustado)...")
        
        if not os.path.exists(p_fotos_estoque):
            self.write_log("❌ ERRO: Pasta 'FOTOS' não encontrada!")
            self.btn_run.configure(state="normal")
            return

        estoque = {re.sub(r'[^A-Z0-9]', '', f.split('.')[0].upper()): f for f in os.listdir(p_fotos_estoque)}
        rel_xls = []
        pastas_dia = [d for d in os.listdir(raiz) if os.path.isdir(os.path.join(raiz, d)) and d.startswith("20")]
        
        for d in pastas_dia:
            caminho_dia = os.path.join(raiz, d)
            p_fotos_dia = os.path.join(caminho_dia, "Fotos")
            if not os.path.exists(p_fotos_dia): os.makedirs(p_fotos_dia)
            
            for arq in [f for f in os.listdir(caminho_dia) if f.endswith((".xlsx", ".xls"))]:
                try:
                    df = pd.read_excel(os.path.join(caminho_dia, arq))
                    df.columns = [str(c).upper() for c in df.columns]
                    
                    col_v = next((c for c in df.columns if "VERTICE" in c), None)
                    col_m = next((c for c in df.columns if c in ["MATR", "MATRICULA", "RESPONSAVEL"]), None)
                    
                    if col_v:
                        for _, row in df.iterrows():
                            v = str(row[col_v]).upper().strip()
                            if "-M-" not in v or v == "NAN": continue
                            
                            v_norm = re.sub(r'[^A-Z0-9]', '', v)
                            resp = str(row[col_m]) if col_m else "N/A"
                            
                            if v_norm in estoque:
                                ext = os.path.splitext(estoque[v_norm])[1]
                                shutil.move(os.path.join(p_fotos_estoque, estoque[v_norm]), 
                                            os.path.join(p_fotos_dia, f"{v}{ext}"))
                                self.write_log(f"📦 MOVIDO: {v}")
                                del estoque[v_norm]
                            else:
                                # Verifica se já não existe no destino
                                if not any(v in f.upper() for f in os.listdir(p_fotos_dia)):
                                    rel_xls.append({
                                        "VÉRTICE": v,
                                        "RESPONSÁVEL": resp,
                                        "DATA_PASTA": d,
                                        "PLANILHA": arq,
                                        "STATUS": "PENDENTE",
                                        "OBSERVAÇÃO": f"FOTO {v} NÃO ENCONTRADA NO DIA {d}"
                                    })
                except Exception as e:
                    self.write_log(f"⚠️ Erro em {arq}: {e}")

        # --- GERAÇÃO DO RELATÓRIO COM FORMATAÇÃO ---
        self.rel_path = os.path.join(raiz, "RELATORIO_PENDENCIAS_XML.xlsx")
        if rel_xls:
            try:
                df_rel = pd.DataFrame(rel_xls)
                writer = pd.ExcelWriter(self.rel_path, engine='xlsxwriter')
                df_rel.to_excel(writer, index=False, sheet_name='Pendencias')
                
                workbook = writer.book
                worksheet = writer.sheets['Pendencias']
                
                # Formato Vermelho para Pendências
                fmt_red = workbook.add_format({'bg_color': '#FF0000', 'font_color': '#FFFFFF', 'bold': True, 'border': 1})
                
                # Auto-ajuste de colunas e aplicação do formato
                for i, col in enumerate(df_rel.columns):
                    largura = max(df_rel[col].astype(str).map(len).max(), len(col)) + 5
                    worksheet.set_column(i, i, largura)
                
                # Aplica o vermelho se a célula não estiver vazia
                worksheet.conditional_format(1, 0, len(df_rel), len(df_rel.columns)-1, {
                    'type': 'no_blanks',
                    'format': fmt_red
                })
                
                writer.close()
                self.btn_rel.configure(state="normal")
                self.write_log(f"📄 Relatório pronto: {len(rel_xls)} itens.")
            except Exception as e:
                self.write_log(f"❌ Erro ao salvar Excel: {e}")
        else:
            self.write_log("✅ Nenhuma pendência encontrada.")

        self.write_log("✨ PROCESSO FINALIZADO!")
        self.btn_run.configure(state="normal")