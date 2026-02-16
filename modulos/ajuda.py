import customtkinter as ctk

class AjudaFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # O texto agora fica salvo aqui dentro, sem precisar de arquivo externo
        self.texto_manual = """=== MANUAL DO SISTEMA DELTA ===

1. MÓDULO FOTOS XML:
   - Selecione a pasta raiz onde estão as fotos e planilhas.
   - O sistema fará a triagem baseada nos dados do XML.

2. MÓDULO CD:
   - O sistema cria automaticamente a estrutura de pastas padrão do CD
   - como 01 – Arquivos Literais, 02 – Arquivos Gráficos, entre outras.
   -  Além da criação das pastas, ele realiza a organização completa do diretório
   - identificando todos os arquivos que estão dispersos e movendo cada um para a pasta 
   - correspondente, de acordo com seu tipo e finalidade.

3. MÓDULO PDF/IMAGEM:
   - Selecione as imagens JPG ou PNG.
   - Escolha entre gerar um PDF único ou um para cada imagem.

4. RENOMEADOR:
   - Utilize para padronizar nomes de arquivos com siglas específicas.

--------------------------------------------------
Desenvolvido para alta produtividade em campo.
"""
        self.setup_ui()

    def setup_ui(self):
        # Título
        ctk.CTkLabel(self, text="📖 CENTRAL DE AJUDA", 
                    font=("Arial", 24, "bold"), text_color="#2ECC71").pack(pady=15)

        # Container Principal
        self.container = ctk.CTkFrame(self, fg_color="#0A0A0A", border_color="#27AE60", border_width=1)
        self.container.pack(fill="both", expand=True, padx=30, pady=10)

        # Área de Texto (Apenas Leitura)
        self.txt_ajuda = ctk.CTkTextbox(self.container, font=("Consolas", 14), 
                                       fg_color="transparent", text_color="#DCDCDC",
                                       activate_scrollbars=True)
        self.txt_ajuda.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Insere o texto embutido e bloqueia edição
        self.txt_ajuda.insert("1.0", self.texto_manual)
        self.txt_ajuda.configure(state="disabled")