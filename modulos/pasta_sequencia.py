import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import re
from datetime import datetime, timedelta

class PastaSequenciaFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variáveis de Controle
        self.pasta_destino = ctk.StringVar(value="")
        self.seq_inicio = ctk.StringVar(value="")
        self.seq_fim = ctk.StringVar(value="")
        
        self.setup_ui()

    def setup_ui(self):
        self.lbl_titulo = ctk.CTkLabel(self, text="MÓDULO: GERADOR DE SEQUÊNCIA (DATA/NÚMERO)", 
                                      font=("Arial", 20, "bold"), text_color="#2ECC71")
        self.lbl_titulo.pack(pady=(10, 20))

        # --- Container Diretorio ---
        self.frame_dir = ctk.CTkFrame(self, fg_color="#071A07", border_color="#2ECC71", border_width=1)
        self.frame_dir.pack(pady=5, padx=40, fill="x")

        ctk.CTkLabel(self.frame_dir, text="ONDE CRIAR:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=15, pady=15)
        self.ent_pasta = ctk.CTkEntry(self.frame_dir, textvariable=self.pasta_destino, width=400, height=35)
        self.ent_pasta.grid(row=0, column=1, padx=10, pady=15)
        ctk.CTkButton(self.frame_dir, text="BUSCAR PASTA", width=120, fg_color="#333", command=self.selecionar_pasta).grid(row=0, column=2, padx=15)

        # --- Container Início/Fim ---
        self.frame_params = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_params.pack(pady=20, padx=40)

        self.frame_ini = ctk.CTkFrame(self.frame_params, fg_color="#111", border_color="#333", border_width=1)
        self.frame_ini.pack(side="left", padx=10)
        ctk.CTkLabel(self.frame_ini, text="INÍCIO (DATA OU NÚMERO):", font=("Arial", 11, "bold"), text_color="#2ECC71").pack(pady=5, padx=20)
        ctk.CTkEntry(self.frame_ini, textvariable=self.seq_inicio, width=250, height=40, font=("Arial", 16), placeholder_text="Ex: 20260101 ou 001").pack(pady=10, padx=20)

        self.frame_fim = ctk.CTkFrame(self.frame_params, fg_color="#111", border_color="#333", border_width=1)
        self.frame_fim.pack(side="left", padx=10)
        ctk.CTkLabel(self.frame_fim, text="FIM (DATA OU NÚMERO):", font=("Arial", 11, "bold"), text_color="#2ECC71").pack(pady=5, padx=20)
        ctk.CTkEntry(self.frame_fim, textvariable=self.seq_fim, width=250, height=40, font=("Arial", 16), placeholder_text="Ex: 20261231 ou 100").pack(pady=10, padx=20)

        self.lbl_status = ctk.CTkLabel(self, text="O sistema detecta automaticamente se é uma data (YYYYMMDD) ou sequência de texto.", 
                                      font=("Arial", 12), text_color="#AAAAAA")
        self.lbl_status.pack(pady=20)

        self.btn_processar = ctk.CTkButton(self, text="▶ GERAR SEQUÊNCIA", 
                                         fg_color="#2ECC71", text_color="black", 
                                         font=("Arial", 16, "bold"), height=60, width=450,
                                         command=self.executar_logica)
        self.btn_processar.pack(side="bottom", pady=40)

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta: self.pasta_destino.set(pasta)

    def tentar_gerar_datas(self, inicio, fim):
        """Tenta gerar sequência de datas se o formato for YYYYMMDD (8 dígitos)"""
        if len(inicio) == 8 and len(fim) == 8 and inicio.isdigit() and fim.isdigit():
            try:
                d_ini = datetime.strptime(inicio, "%Y%m%d")
                d_fim = datetime.strptime(fim, "%Y%m%d")
                
                lista = []
                corrente = d_ini
                passo = timedelta(days=1) if d_ini <= d_fim else timedelta(days=-1)
                
                while True:
                    lista.append(corrente.strftime("%Y%m%d"))
                    if corrente == d_fim: break
                    corrente += passo
                return lista
            except ValueError:
                return None
        return None

    def gerar_numerico(self, ini, fim):
        """Lógica para sequências numéricas e textos (como FOTO 01 até FOTO 10)"""
        def extrair_partes(t):
            return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', t)]
        
        p_ini = extrair_partes(ini)
        p_fim = extrair_partes(fim)
        
        idx_diff = -1
        for i in range(min(len(p_ini), len(p_fim))):
            if p_ini[i] != p_fim[i]:
                idx_diff = i
                break
        
        if idx_diff == -1 or not isinstance(p_ini[idx_diff], int):
            return [ini, fim] if ini != fim else [ini]

        n1, n2 = p_ini[idx_diff], p_fim[idx_diff]
        passo = 1 if n1 <= n2 else -1
        orig_str = re.findall(r'\d+', ini)[0]
        zeros = len(orig_str)

        lista = []
        for n in range(n1, n2 + passo, passo):
            nova_parte = str(n).zfill(zeros)
            temp = list(p_ini)
            temp[idx_diff] = nova_parte
            lista.append("".join(map(str, temp)))
        return lista

    def executar_logica(self):
        destino = self.pasta_destino.get()
        ini, fim = self.seq_inicio.get().strip(), self.seq_fim.get().strip()

        if not all([destino, ini, fim]):
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return

        # 1. Tenta tratar como DATA primeiro
        lista_pastas = self.tentar_gerar_datas(ini, fim)
        
        # 2. Se não for data válida, trata como SEQUÊNCIA NUMÉRICA
        if lista_pastas is None:
            lista_pastas = self.gerar_numerico(ini, fim)

        try:
            criadas = 0
            for nome in lista_pastas:
                path = os.path.join(destino, nome)
                if not os.path.exists(path):
                    os.makedirs(path)
                    criadas += 1
            
            messagebox.showinfo("Sucesso", f"Total: {len(lista_pastas)} pastas.\nNovas criadas: {criadas}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao criar pastas: {e}")