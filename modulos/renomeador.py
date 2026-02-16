import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk

class RenomeadorFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variáveis de Controle
        self.pasta_fotos = ""
        self.fotos_lista = []
        self.foto_atual_idx = 0
        self.siglas = ["SUAT", "GRR"]
        self.sigla_selecionada = ctk.StringVar(value="SUAT")
        
        # Variáveis de Zoom e Pan
        self.zoom_level = 1.0
        self.img_original = None
        self.image_id = None
        self.pan_start_x = 0
        self.pan_start_y = 0

        self.setup_ui()

    def setup_ui(self):
        # --- Topo: Busca e Contadores ---
        self.frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_topo.pack(pady=(5, 5), fill="x", padx=20)

        self.btn_buscar = ctk.CTkButton(self.frame_topo, text="📂 BUSCAR PASTA", fg_color="#2ECC71", 
                                      text_color="black", font=("Arial", 13, "bold"), 
                                      width=180, height=40, command=self.selecionar_pasta)
        self.btn_buscar.pack(side="left")

        self.lbl_info_fotos = ctk.CTkLabel(self.frame_topo, text="Fotos: 0 / 0", 
                                         font=("Arial", 14, "bold"), text_color="#2ECC71")
        self.lbl_info_fotos.pack(side="right", padx=10)
        
        self.lbl_nome_arquivo = ctk.CTkLabel(self, text="Arquivo: ---", 
                                           font=("Arial", 12), text_color="#AAAAAA")
        self.lbl_nome_arquivo.pack(pady=(0, 2))

        # --- Visualizador de Imagem ---
        self.canvas = Canvas(self, width=700, height=380, bg="#0A0A0A", highlightthickness=0)
        self.canvas.pack(pady=2)
        self.canvas.bind("<MouseWheel>", self.processar_zoom)
        self.canvas.bind("<ButtonPress-1>", self.iniciar_pan)
        self.canvas.bind("<B1-Motion>", self.executar_pan)

        # --- Navegação: VOLTAR e PULAR ---
        self.frame_nav = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_nav.pack(pady=5)
        ctk.CTkButton(self.frame_nav, text="⬅ VOLTAR", width=120, fg_color="#333", command=self.voltar_foto).pack(side="left", padx=10)
        ctk.CTkButton(self.frame_nav, text="PULAR ➡", width=120, fg_color="#333", command=self.pular_foto).pack(side="left", padx=10)

        # --- Siglas (Scrollable) ---
        ctk.CTkLabel(self, text="SIGLA PADRÃO SELECIONADA:", font=("Arial", 12, "bold"), text_color="#2ECC71").pack()
        
        self.frame_siglas = ctk.CTkScrollableFrame(self, fg_color="transparent", orientation="horizontal", height=45, width=650)
        self.frame_siglas.pack(pady=2, padx=20)
        self.atualizar_radio_siglas()

        # --- Input ---
        self.frame_input = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_input.pack(pady=5)
        self.lbl_prefixo = ctk.CTkLabel(self.frame_input, text=f"{self.sigla_selecionada.get()}-M-", font=("Arial", 22, "bold"), text_color="white")
        self.lbl_prefixo.grid(row=0, column=0, padx=10)
        self.ent_num = ctk.CTkEntry(self.frame_input, placeholder_text="Numeração", width=200, height=45, font=("Arial", 18), border_color="#2ECC71")
        self.ent_num.grid(row=0, column=1, padx=10)
        self.ent_num.bind("<Return>", lambda e: self.renomear_foto())

        # --- Botões Adicionar/Remover Sigla (AJUSTADO PARA NÃO CORTAR) ---
        self.frame_botoes_sigla = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botoes_sigla.pack(pady=(10, 10), anchor="center") # Centralizado para melhor visibilidade
        ctk.CTkButton(self.frame_botoes_sigla, text="- REMOVER SIGLA", width=140, fg_color="#331111", text_color="#E74C3C", font=("Arial", 11, "bold"), command=self.remover_sigla).pack(side="left", padx=5)
        ctk.CTkButton(self.frame_botoes_sigla, text="+ ADICIONAR SIGLA", width=140, fg_color="#1E3D1E", text_color="#2ECC71", font=("Arial", 11, "bold"), command=self.janela_add_sigla).pack(side="left", padx=5)

    def selecionar_pasta(self):
        path = filedialog.askdirectory()
        if path:
            self.pasta_fotos = path
            self.fotos_lista = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.foto_atual_idx = 0
            self.carregar_foto_atual()

    def carregar_foto_atual(self):
        if self.fotos_lista and 0 <= self.foto_atual_idx < len(self.fotos_lista):
            self.zoom_level = 1.0
            self.lbl_info_fotos.configure(text=f"Fotos: {self.foto_atual_idx + 1} / {len(self.fotos_lista)}")
            nome_arq = self.fotos_lista[self.foto_atual_idx]
            self.lbl_nome_arquivo.configure(text=f"Arquivo Atual: {nome_arq}")
            img_raw = Image.open(os.path.join(self.pasta_fotos, nome_arq))
            img_raw.thumbnail((700, 400))
            self.img_original = img_raw
            self.atualizar_canvas()
        else:
            self.canvas.delete("all")
            self.lbl_info_fotos.configure(text="Fotos: 0 / 0")

    def atualizar_canvas(self):
        if not self.img_original: return
        largura, altura = self.img_original.size
        nova_largura = int(largura * self.zoom_level)
        nova_altura = int(altura * self.zoom_level)
        img_exibir = self.img_original.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img_exibir)
        self.canvas.delete("all")
        self.image_id = self.canvas.create_image(350, 190, image=self.tk_img, anchor="center")

    def processar_zoom(self, event):
        self.zoom_level *= 1.1 if event.delta > 0 else 0.9
        self.zoom_level = max(0.5, min(self.zoom_level, 4.0))
        self.atualizar_canvas()

    def iniciar_pan(self, event):
        self.pan_start_x, self.pan_start_y = event.x, event.y

    def executar_pan(self, event):
        if self.image_id:
            dx, dy = event.x - self.pan_start_x, event.y - self.pan_start_y
            self.canvas.move(self.image_id, dx, dy)
            self.pan_start_x, self.pan_start_y = event.x, event.y

    def voltar_foto(self):
        if self.foto_atual_idx > 0:
            self.foto_atual_idx -= 1
            self.carregar_foto_atual()

    def pular_foto(self):
        if self.foto_atual_idx < len(self.fotos_lista) - 1:
            self.foto_atual_idx += 1
            self.carregar_foto_atual()

    def atualizar_radio_siglas(self):
        for widget in self.frame_siglas.winfo_children(): widget.destroy()
        for s in self.siglas:
            ctk.CTkRadioButton(self.frame_siglas, text=s, variable=self.sigla_selecionada, value=s, 
                               command=lambda: self.lbl_prefixo.configure(text=f"{self.sigla_selecionada.get()}-M-"),
                               fg_color="#2ECC71", text_color="white").pack(side="left", padx=10)

    def janela_add_sigla(self):
        dialog = ctk.CTkInputDialog(text="Nova Sigla:", title="Adicionar")
        res = dialog.get_input()
        if res:
            s = res.strip().upper()
            if s and s not in self.siglas:
                self.siglas.append(s)
                self.atualizar_radio_siglas()

    def remover_sigla(self):
        sigla = self.sigla_selecionada.get()
        if len(self.siglas) > 1 and messagebox.askyesno("Remover", f"Remover {sigla}?"):
            self.siglas.remove(sigla)
            self.sigla_selecionada.set(self.siglas[0])
            self.lbl_prefixo.configure(text=f"{self.siglas[0]}-M-")
            self.atualizar_radio_siglas()

    def renomear_foto(self):
        num = self.ent_num.get().strip()
        if not self.fotos_lista or not num: return
        antigo = self.fotos_lista[self.foto_atual_idx]
        novo = f"{self.sigla_selecionada.get()}-M-{num}{os.path.splitext(antigo)[1]}"
        try:
            os.rename(os.path.join(self.pasta_fotos, antigo), os.path.join(self.pasta_fotos, novo))
            self.ent_num.delete(0, 'end')
            self.fotos_lista[self.foto_atual_idx] = novo
            self.pular_foto()
        except Exception as e: 
            messagebox.showerror("Erro", str(e))