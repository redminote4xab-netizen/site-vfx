import os
import threading
import requests
import customtkinter as ctk
from tkinter import messagebox
import webbrowser

# ==========================================================
# IMPORTAÇÃO DOS SEUS MÓDULOS
# ==========================================================
from modulos.renomeador import RenomeadorFrame
from modulos.fotos_xml import FotosXMLFrame
from modulos.fotos_hcn import FotosHCNFrame
from modulos.pasta_sequencia import PastaSequenciaFrame
from modulos.cd import CDFrame
from modulos.pdf_imagem import PDF_IMAGEM  # CORRIGIDO: Nome do arquivo correto
from modulos.nomenclatura import GestorNomenclaturaFrame
from modulos.ajuda import AjudaFrame
from modulos.controle_vendas import ControleVendasFrame # NOVO MÓDULO

# ==========================================================
# CONFIGURAÇÃO MASTER - SEU FIREBASE
# ==========================================================
URL_DATABASE = "https://sistema-delta-4-default-rtdb.firebaseio.com/usuarios.json"

# --- TELA DE ABERTURA (LOADING 4s) ---
class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Iniciando DELTA")
        self.geometry("500x350")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"500x350+{int((sw-500)/2)}+{int((sh-350)/2)}")
        self.configure(fg_color="#050505")
        
        self.logo = ctk.CTkLabel(self, text="DELTA", font=("Arial", 60, "bold"), text_color="#2ECC71")
        self.logo.pack(pady=(60, 10))

        self.lbl_contagem = ctk.CTkLabel(self, text="Iniciando em: 0s", font=("Arial", 18), text_color="#2ECC71")
        self.lbl_contagem.pack(pady=5)
        
        self.progress = ctk.CTkProgressBar(self, width=400, progress_color="#2ECC71", fg_color="#111")
        self.progress.pack(pady=30)
        self.progress.set(0)
        
        self.val = 0
        self.update_progress()

    def update_progress(self):
        if self.val <= 1:
            self.progress.set(self.val)
            segundos = int(self.val * 4)
            self.lbl_contagem.configure(text=f"Iniciando em: {segundos}s")
            self.val += 0.025 
            self.after(100, self.update_progress)
        else:
            self.lbl_contagem.configure(text="Iniciando em: 4s")
            self.after(200, self.finalizar)

    def finalizar(self):
        self.parent.mostrar_login()
        self.destroy()

# --- TELA DE LOGIN ---
class LoginScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("DELTA - Autenticação")
        self.geometry("400x600")
        self.configure(fg_color="#050505")
        self.protocol("WM_DELETE_WINDOW", self.parent.quit)
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"400x600+{int((sw-400)/2)}+{int((sh-600)/2)}")
        
        ctk.CTkLabel(self, text="SISTEMA DELTA", font=("Arial", 30, "bold"), text_color="#2ECC71").pack(pady=(50, 30))
        
        self.user_ent = ctk.CTkEntry(self, placeholder_text="Usuário", width=280, height=45, border_color="#2ECC71", fg_color="#111")
        self.user_ent.pack(pady=10)
        
        self.pass_ent = ctk.CTkEntry(self, placeholder_text="Senha", width=280, height=45, show="*", border_color="#2ECC71", fg_color="#111")
        self.pass_ent.pack(pady=10)
        
        self.btn_login = ctk.CTkButton(self, text="ENTRAR", width=280, height=50, 
                                      fg_color="#27AE60", text_color="black", 
                                      font=("Arial", 16, "bold"), command=self.validar_acesso)
        self.btn_login.pack(pady=30)

        self.frame_contato = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_contato.pack(pady=(20, 10))
        ctk.CTkLabel(self.frame_contato, text="Interessado em adquirir acesso?", font=("Arial", 12), text_color="white").pack()
        self.btn_zap = ctk.CTkButton(self.frame_contato, text=" ✆ (93) 98423-6665", font=("Arial", 14, "bold"),
                                     fg_color="transparent", text_color="#2ECC71", hover_color="#111",
                                     command=lambda: webbrowser.open("https://wa.me/5593984236665"))
        self.btn_zap.pack()

    def validar_acesso(self):
        u, s = self.user_ent.get().strip(), self.pass_ent.get().strip()
        if not u or not s: return
        self.btn_login.configure(state="disabled", text="VERIFICANDO...")
        threading.Thread(target=self._verificar_servidor, args=(u, s), daemon=True).start()

    def _verificar_servidor(self, user_digitado, senha_digitada):
        try:
            response = requests.get(URL_DATABASE, timeout=10)
            usuarios = response.json()
            if usuarios:
                for nome_db, dados in usuarios.items():
                    if nome_db.lower() == user_digitado.lower():
                        senha_db = str(dados.get('2025') if '2025' in dados else dados.get('senha'))
                        if senha_db == senha_digitada:
                            self.parent.usuario_logado = nome_db.upper()
                            self.after(0, self.login_sucesso)
                            return
            self.after(0, lambda: self.login_erro("Acesso negado!"))
        except:
            self.after(0, lambda: self.login_erro("Falha de conexão!"))

    def login_sucesso(self):
        self.parent.abrir_programa_principal()
        self.destroy()

    def login_erro(self, msg):
        self.btn_login.configure(state="normal", text="ENTRAR")
        messagebox.showerror("Erro", msg)

# --- CLASSE PRINCIPAL ---
class DeltaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("SISTEMA DELTA - V4.0 FULL")
        self.geometry("1150x750")
        
        self.usuario_logado = ""
        self.frames = {} # Dicionário para armazenar as abas
        
        SplashScreen(self)

    def mostrar_login(self):
        LoginScreen(self)

    def abrir_programa_principal(self):
        self.deiconify()
        self.layout_base()
        
        # --- REGISTRO DOS MÓDULOS ---
        self.frames["renomeador"] = RenomeadorFrame(self.main_view)
        self.frames["fotos_xml"] = FotosXMLFrame(self.main_view)
        self.frames["fotos_hcn"] = FotosHCNFrame(self.main_view)
        self.frames["pasta_sequencia"] = PastaSequenciaFrame(self.main_view)
        self.frames["cd"] = CDFrame(self.main_view)
        self.frames["pdf_doc"] = PDF_IMAGEM(self.main_view) 
        self.frames["nomenclatura"] = GestorNomenclaturaFrame(self.main_view)
        self.frames["vendas"] = ControleVendasFrame(self.main_view) # REGISTRO VENDAS
        self.frames["ajuda"] = AjudaFrame(self.main_view)
        
        # Mostra o renomeador por padrão
        self.show_frame("renomeador")

    def show_frame(self, nome):
        """Esconde todos os frames e mostra apenas o selecionado"""
        if nome in self.frames:
            for f in self.frames.values():
                f.pack_forget()
            self.frames[nome].pack(fill="both", expand=True)

    def add_menu_button(self, texto, frame_key):
        """Função auxiliar para adicionar botões no menu"""
        btn = ctk.CTkButton(self.sidebar, text=texto, fg_color="transparent", 
                            text_color="#2ECC71", hover_color="#1E3D1E", anchor="w", 
                            font=("Arial", 14, "bold"), height=40,
                            command=lambda k=frame_key: self.show_frame(k))
        btn.pack(fill="x", padx=15, pady=5)
        return btn

    def layout_base(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, fg_color="#071A07", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Cabeçalho da Sidebar
        self.lbl_user = ctk.CTkLabel(self.sidebar, text=self.usuario_logado, font=("Arial", 16, "bold"), text_color="#2ECC71")
        self.lbl_user.pack(pady=(30, 0))
        ctk.CTkLabel(self.sidebar, text="DELTA", font=("Arial", 38, "bold"), text_color="#2ECC71").pack(pady=(0, 30))
        
        # --- ÁREA DE BOTÕES DO MENU ---
        self.add_menu_button("📸  RENOMEADOR", "renomeador")
        self.add_menu_button("📄  FOTOS XML", "fotos_xml")
        self.add_menu_button("📂  FOTOS HCN/TXT", "fotos_hcn")
        self.add_menu_button("🚀  PASTA/SEQUENCIA", "pasta_sequencia")
        self.add_menu_button("🗳  CD", "cd")
        self.add_menu_button("🎴  PDF/IMAGEM", "pdf_doc")
        self.add_menu_button("🚩  NOMENCLATURA", "nomenclatura")
        self.add_menu_button("📊  CONTROLE VENDAS", "vendas") # BOTÃO VENDAS
        self.add_menu_button("ℹ️  AJUDA", "ajuda")

        # Área de Conteúdo Principal
        self.main_view = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.main_view.grid(row=0, column=1, sticky="nsew")

        # --- SEÇÃO SOBRE (RODAPÉ) ---
        self.footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.footer.pack(side="bottom", fill="x", pady=20, padx=15)
        
        ctk.CTkLabel(self.footer, text="Desenvolvido por:", font=("Arial", 11, "bold"), text_color="#2ECC71").pack(anchor="w")
        ctk.CTkLabel(self.footer, text="ARLISSON BATISTA", font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", pady=(0, 10))
        
        desc_txt = "O DELTA é uma solução profissional projetada para otimizar fluxos de trabalho e maximizar a produtividade."
        self.lbl_desc = ctk.CTkLabel(self.footer, text=desc_txt, font=("Arial", 10), text_color="#AAAAAA", wraplength=200, justify="left")
        self.lbl_desc.pack(anchor="w")

if __name__ == "__main__":
    app = DeltaApp()
    app.mainloop()