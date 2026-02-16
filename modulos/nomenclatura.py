import os
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox

class GestorNomenclaturaFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.diretorio_nativos = ctk.StringVar(value="Selecione a pasta raiz dos NATIVOS...")
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="MÓDULO: GESTOR DE NOMENCLATURA (HCN/RINEX)", 
                     font=("Arial", 22, "bold"), text_color="#2ECC71").pack(pady=20)

        frame_top = ctk.CTkFrame(self, fg_color="#071A07", border_color="#2ECC71", border_width=1)
        frame_top.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkEntry(frame_top, textvariable=self.diretorio_nativos, width=600, height=35).grid(row=0, column=0, padx=15, pady=15)
        ctk.CTkButton(frame_top, text="BUSCAR NATIVOS", command=self.carregar_dados, fg_color="#333", height=35).grid(row=0, column=1, padx=10)

        self.frame_lista = ctk.CTkScrollableFrame(self, fg_color="#0a0a0a", height=550)
        self.frame_lista.pack(pady=10, padx=20, fill="both", expand=True)

    def criar_cabecalho_tabela(self, row_idx):
        headers = ["FILE NAME", "START TIME (UTC)", "END TIME (UTC)", "DURATION", "NEW NAME", "ACTION"]
        widths = [190, 210, 210, 100, 180, 80]
        for i, (text, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(self.frame_lista, text=text, font=("Arial", 11, "bold"), 
                         text_color="#2ECC71", width=w).grid(row=row_idx, column=i, padx=5, pady=10)
        return row_idx + 1

    def extrair_tempo_real_epocas(self, caminho_hcn):
        """Extrai o tempo real lendo as épocas do arquivo .23O correspondente"""
        pasta_pai = os.path.dirname(caminho_hcn)
        nome_hcn = os.path.basename(caminho_hcn)
        prefixo = os.path.splitext(nome_hcn)[0]
        pasta_rinex = os.path.join(pasta_pai, "Rinex")
        
        try:
            if os.path.exists(pasta_rinex):
                for f in os.listdir(pasta_rinex):
                    if f.startswith(prefixo) and f.lower().endswith(".23o"):
                        with open(os.path.join(pasta_rinex, f), 'r') as file:
                            linhas = file.readlines()
                            idx_dados = 0
                            for i, linha in enumerate(linhas):
                                if "END OF HEADER" in linha:
                                    idx_dados = i + 1
                                    break
                            
                            p_obs = linhas[idx_dados].strip().split()
                            off = 1 if p_obs[0] == '>' else 0
                            dt_s = datetime(int(p_obs[off]), int(p_obs[off+1]), int(p_obs[off+2]), 
                                            int(p_obs[off+3]), int(p_obs[off+4]), int(float(p_obs[off+5])))

                            for i in range(len(linhas)-1, idx_dados, -1):
                                l_s = linhas[i].strip().split()
                                if l_s and (l_s[0] == '>' or (len(l_s) > 5 and l_s[0].isdigit())):
                                    off = 1 if l_s[0] == '>' else 0
                                    dt_e = datetime(int(l_s[off]), int(l_s[off+1]), int(l_s[off+2]), 
                                                    int(l_s[off+3]), int(l_s[off+4]), int(float(l_s[off+5])))
                                    break
                            
                            duration = dt_e - dt_s
                            return (dt_s.strftime("%Y-%m-%d"), dt_s.strftime("%H:%M:%S")), \
                                   (dt_e.strftime("%Y-%m-%d"), dt_e.strftime("%H:%M:%S")), \
                                   str(duration).split('.')[0]
        except: pass
        return ("N/A", "N/A"), ("N/A", "N/A"), "0:00:00"

    def carregar_dados(self):
        pasta_raiz = filedialog.askdirectory()
        if not pasta_raiz: return
        self.diretorio_nativos.set(pasta_raiz)
        self.atualizar_view()

    def atualizar_view(self):
        pasta_raiz = self.diretorio_nativos.get()
        for widget in self.frame_lista.winfo_children(): widget.destroy()

        # Dicionário para agrupar: { "Responsável": [lista_de_caminhos_hcn] }
        dados_agrupados = {}

        # Busca recursiva em todas as subpastas
        for root, dirs, files in os.walk(pasta_raiz):
            for file in files:
                if file.lower().endswith(".hcn"):
                    # O "Responsável" é o nome da pasta onde o HCN está
                    responsavel = os.path.basename(root).upper()
                    if responsavel not in dados_agrupados:
                        dados_agrupados[responsavel] = []
                    dados_agrupados[responsavel].append(os.path.join(root, file))

        row = 0
        for resp in sorted(dados_agrupados.keys()):
            # Cabeçalho do Responsável
            f_resp = ctk.CTkFrame(self.frame_lista, fg_color="#1a1a1a", height=35)
            f_resp.grid(row=row, column=0, columnspan=6, sticky="ew", pady=(15, 5))
            ctk.CTkLabel(f_resp, text=f"  👤 RESPONSÁVEL: {resp}", font=("Arial", 12, "bold"), text_color="#3498DB").pack(side="left")
            
            row += 1
            row = self.criar_cabecalho_tabela(row)

            for caminho_full in sorted(dados_agrupados[resp]):
                nome_arq = os.path.basename(caminho_full)
                s, e, d = self.extrair_tempo_real_epocas(caminho_full)
                self.inserir_linha(row, nome_arq, s, e, d, caminho_full)
                row += 1

    def inserir_linha(self, row, arq, start, end, duration, caminho_completo):
        ctk.CTkLabel(self.frame_lista, text=arq, width=190, anchor="w", text_color="#777").grid(row=row, column=0, padx=5)
        
        # Start Time
        f_s = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        f_s.grid(row=row, column=1)
        ctk.CTkLabel(f_s, text=start[0], text_color="#777", font=("Consolas", 11)).pack(side="left")
        ctk.CTkLabel(f_s, text=f"  {start[1]}", text_color="white", font=("Consolas", 12, "bold")).pack(side="left")

        # End Time
        f_e = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        f_e.grid(row=row, column=2)
        ctk.CTkLabel(f_e, text=end[0], text_color="#777", font=("Consolas", 11)).pack(side="left")
        ctk.CTkLabel(f_e, text=f"  {end[1]}", text_color="white", font=("Consolas", 12, "bold")).pack(side="left")
        
        ctk.CTkLabel(self.frame_lista, text=duration, width=100, text_color="#2ECC71", font=("Arial", 12, "bold")).grid(row=row, column=3, padx=5)
        
        ent = ctk.CTkEntry(self.frame_lista, width=180, placeholder_text="Novo nome...")
        ent.grid(row=row, column=4, padx=5)
        
        btn = ctk.CTkButton(self.frame_lista, text="OK", width=80, fg_color="#2ECC71", text_color="black", font=("Arial", 12, "bold"),
                            command=lambda c=caminho_completo, e=ent: self.executar_renomeio(c, e))
        btn.grid(row=row, column=5, padx=10, pady=3)

    def executar_renomeio(self, caminho_antigo, entry):
        novo_nome_base = entry.get().strip()
        if not novo_nome_base: return
        
        try:
            pasta_pai = os.path.dirname(caminho_antigo)
            nome_antigo = os.path.basename(caminho_antigo)
            prefixo_antigo = os.path.splitext(nome_antigo)[0]
            
            # Renomeia o HCN
            os.rename(caminho_antigo, os.path.join(pasta_pai, f"{novo_nome_base}.HCN"))
            
            # Renomeia Rinex
            p_rinex = os.path.join(pasta_pai, "Rinex")
            if os.path.exists(p_rinex):
                for f in os.listdir(p_rinex):
                    if f.startswith(prefixo_antigo):
                        ext = os.path.splitext(f)[1]
                        os.rename(os.path.join(p_rinex, f), os.path.join(p_rinex, f"{novo_nome_base}{ext}"))
            
            self.atualizar_view()
        except Exception as err:
            messagebox.showerror("Erro", str(err))