import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox

class CDFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # --- Variáveis de Controle Atualizadas ---
        self.pasta_alvo = ctk.StringVar(value="Nenhuma pasta selecionada")
        
        # Ajuste: Removido imagens de Gráficos e adicionado .ods
        self.ext_literais = ctk.StringVar(value=".pdf, .doc, .docx, .txt, .odt")
        self.ext_graficos = ctk.StringVar(value=".dwg, .kml, .kmz, .dxf, .mem, .ods") 
        # Ajuste: Adicionado .gpx
        self.ext_relatorios = ctk.StringVar(value=".xls, .xlsx, .csv, .xml, .log, .jff, .ttp, .gpx")
        self.ext_brutos = ctk.StringVar(value=".hcn, .dat, .raw, .23g, .23n, .23o") 
        # Nova variável para imagens
        self.ext_imagens = ctk.StringVar(value=".jpg, .jpeg, .png")
        
        self.setup_ui()

    def setup_ui(self):
        # --- 1. Título ---
        self.lbl_titulo = ctk.CTkLabel(self, text="MÓDULO: CD (ORGANIZADOR DE PROJETO)", 
                                     font=("Arial", 20, "bold"), text_color="#2ECC71")
        self.lbl_titulo.pack(pady=(10, 15))

        # --- 2. Seleção de Pasta ---
        self.frame_dir = ctk.CTkFrame(self, fg_color="#071A07", border_color="#2ECC71", border_width=1)
        self.frame_dir.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(self.frame_dir, text="PASTA DO PROJETO:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=15, pady=20)
        self.ent_pasta = ctk.CTkEntry(self.frame_dir, textvariable=self.pasta_alvo, width=350, height=35)
        self.ent_pasta.grid(row=0, column=1, padx=10, pady=20)
        ctk.CTkButton(self.frame_dir, text="BUSCAR PASTA", width=120, fg_color="#333", 
                       command=self.selecionar_pasta).grid(row=0, column=2, padx=15)

        # --- 3. Menu de Configuração de Formatos ---
        self.frame_config = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_config.pack(pady=20, padx=40, fill="x")
        
        self.lbl_cfg_titulo = ctk.CTkLabel(self.frame_config, text="CONFIGURAR FORMATOS POR PASTA:", 
                                          font=("Arial", 12, "bold"), text_color="#2ECC71")
        self.lbl_cfg_titulo.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        campos = [
            ("LITERAIS:", self.ext_literais),
            ("IMAGENS:", self.ext_imagens), # Adicionado campo visual para imagens
            ("GRÁFICOS:", self.ext_graficos),
            ("RELATÓRIOS:", self.ext_relatorios),
            ("DADOS BRUTOS:", self.ext_brutos)
        ]

        for i, (label_text, var) in enumerate(campos):
            row_idx = (i // 2) + 1
            col_idx = (i % 2) * 2
            ctk.CTkLabel(self.frame_config, text=label_text, font=("Arial", 11, "bold")).grid(row=row_idx, column=col_idx, sticky="e", padx=5, pady=8)
            ctk.CTkEntry(self.frame_config, textvariable=var, width=250).grid(row=row_idx, column=col_idx+1, padx=10, pady=8)

        # --- 4. Botão Executar ---
        self.btn_executar = ctk.CTkButton(self, text="▶ EXECUTAR ORGANIZAÇÃO CD", 
                                         fg_color="#2ECC71", text_color="black", 
                                         font=("Arial", 16, "bold"), height=60, width=400,
                                         command=self.executar_cd)
        self.btn_executar.pack(side="bottom", pady=40)

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta: self.pasta_alvo.set(pasta)

    def tratar_extensoes(self, texto):
        return [ext.strip().lower() if ext.strip().startswith(".") else "." + ext.strip().lower() 
                for ext in texto.split(",") if ext.strip()]

    def executar_cd(self):
        caminho_base = self.pasta_alvo.get()
        if "Nenhuma" in caminho_base or not os.path.exists(caminho_base):
            messagebox.showwarning("Atenção", "Selecione uma pasta válida!")
            return

        # Nomes das pastas de destino
        p_literais = "01 - Arquivos Literais"
        p_imagens = os.path.join(p_literais, "Imagens") # Subpasta de Imagens
        p_graficos = "02 - Aquivos Gráficos"
        p_processamento = "03 - Processamento e Relatórios"
        p_brutos = "04 - Dados Brutos"

        exts = {
            "LITERAIS": self.tratar_extensoes(self.ext_literais.get()),
            "IMAGENS": self.tratar_extensoes(self.ext_imagens.get()),
            "GRAFICOS": self.tratar_extensoes(self.ext_graficos.get()),
            "PROCESSAMENTO": self.tratar_extensoes(self.ext_relatorios.get()),
            "BRUTOS_REF": self.tratar_extensoes(self.ext_brutos.get())
        }

        try:
            # Criar estrutura inicial (incluindo subpasta de imagens)
            for p in [p_literais, p_graficos, p_processamento, p_brutos, p_imagens]:
                os.makedirs(os.path.join(caminho_base, p), exist_ok=True)

            itens = os.listdir(caminho_base)
            movidos = 0

            for item in itens:
                caminho_item = os.path.join(caminho_base, item)
                
                # Ignorar as próprias pastas de organização
                if item in [p_literais, p_graficos, p_processamento, p_brutos]:
                    continue

                # --- REGRA PARA PASTAS (Pasta Cabeça / Rinex / Sensores) ---
                if os.path.isdir(caminho_item):
                    # Se for uma pasta, movemos ela inteira para Dados Brutos
                    shutil.move(caminho_item, os.path.join(caminho_base, p_brutos, item))
                    movidos += 1

                # --- REGRA PARA ARQUIVOS SOLTOS ---
                elif os.path.isfile(caminho_item):
                    ext = os.path.splitext(item)[1].lower()
                    
                    # 1. Checar se é Imagem (Vai para Literais/Imagens)
                    if ext in exts["IMAGENS"]:
                        shutil.move(caminho_item, os.path.join(caminho_base, p_imagens, item))
                        movidos += 1
                    
                    # 2. Checar Literais (Geral)
                    elif ext in exts["LITERAIS"]:
                        shutil.move(caminho_item, os.path.join(caminho_base, p_literais, item))
                        movidos += 1
                    
                    # 3. Checar Gráficos (Inclui .ods agora)
                    elif ext in exts["GRAFICOS"]:
                        shutil.move(caminho_item, os.path.join(caminho_base, p_graficos, item))
                        movidos += 1
                    
                    # 4. Checar Processamento (Inclui .gpx agora)
                    elif ext in exts["PROCESSAMENTO"]:
                        shutil.move(caminho_item, os.path.join(caminho_base, p_processamento, item))
                        movidos += 1
                    
                    # 5. Checar se é arquivo bruto solto
                    elif ext in exts["BRUTOS_REF"]:
                        shutil.move(caminho_item, os.path.join(caminho_base, p_brutos, item))
                        movidos += 1
            
            messagebox.showinfo("Sucesso", f"Organização concluída!\nItens movidos: {movidos}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao organizar: {str(e)}")