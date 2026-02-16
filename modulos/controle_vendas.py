import customtkinter as ctk
import json
import os
import subprocess # Necessário para a integração com o GitHub
from tkinter import messagebox

class ControleVendasFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#000000", corner_radius=0)
        
        # Título
        self.label = ctk.CTkLabel(self, text="📊 CONTROLE DE VENDAS E MAPA", font=("Arial", 24, "bold"), text_color="#2ECC71")
        self.label.pack(pady=20)

        # Container Central
        self.container = ctk.CTkFrame(self, fg_color="#071A07", border_color="#2ECC71", border_width=1)
        self.container.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(self.container, text="GESTÃO DE STATUS E ÂNGULOS", font=("Arial", 16, "bold"), text_color="white").pack(pady=10)

        # --- SELEÇÃO DE LOTEAMENTO ---
        ctk.CTkLabel(self.container, text="Selecione o Loteamento:", font=("Arial", 12), text_color="#2ECC71").pack(pady=(10, 0))
        
        # Lista as pastas locais (LOTEAMENTO 1, 2, etc)
        self.loteamentos_disponiveis = [f for f in os.listdir('.') if os.path.isdir(f) and f.startswith("LOTEAMENTO")]
        
        if not self.loteamentos_disponiveis:
            self.loteamentos_disponiveis = ["Nenhum loteamento encontrado"]

        self.loteamento_var = ctk.StringVar(value=self.loteamentos_disponiveis[0])
        self.loteamento_menu = ctk.CTkOptionMenu(
            self.container, 
            values=self.loteamentos_disponiveis,
            variable=self.loteamento_var,
            fg_color="#1E3D1E", 
            button_color="#2ECC71",
            width=250
        )
        self.loteamento_menu.pack(pady=10)

        # Campo ID do Lote
        self.lote_ent = ctk.CTkEntry(self.container, placeholder_text="Número do Lote (Ex: 6)", width=250, border_color="#2ECC71")
        self.lote_ent.pack(pady=10)

        # Menu de Status
        self.status_var = ctk.StringVar(value="disponivel")
        self.status_menu = ctk.CTkOptionMenu(self.container, values=["disponivel", "vendido", "reservado"], 
                                            variable=self.status_var, fg_color="#1E3D1E", button_color="#2ECC71")
        self.status_menu.pack(pady=10)

        # Observações
        self.obs_txt = ctk.CTkTextbox(self.container, width=400, height=100, border_color="#2ECC71", border_width=1)
        self.obs_txt.insert("0.0", "Observações ou Promoções do lote...")
        self.obs_txt.pack(pady=10)

        # Botão Salvar
        self.btn_salvar = ctk.CTkButton(self.container, text="ATUALIZAR NO MAPA", fg_color="#2ECC71", text_color="black", 
                                       font=("Arial", 14, "bold"), command=self.processar_atualizacao)
        self.btn_salvar.pack(pady=20)

    def sincronizar_github(self, mensagem):
        """ Faz o push automático para o site atualizar """
        try:
            # Executa os comandos exatamente como fizemos no terminal
            subprocess.run("git add .", shell=True, check=True)
            subprocess.run(f'git commit -m "{mensagem}"', shell=True, check=True)
            subprocess.run("git push", shell=True, check=True)
            return True
        except Exception as e:
            print(f"Erro no auto-push: {e}")
            return False

    def processar_atualizacao(self):
        loteamento_selecionado = self.loteamento_var.get()
        id_lote_alvo = self.lote_ent.get().strip()
        novo_status = self.status_var.get()
        nova_obs = self.obs_txt.get("0.0", "end").strip()

        caminho_geojson = os.path.join(loteamento_selecionado, "LOTES.geojson")

        if not os.path.exists(caminho_geojson):
            messagebox.showerror("Erro", "Arquivo LOTES.geojson não encontrado!")
            return

        try:
            # 1. Atualiza o arquivo JSON local
            with open(caminho_geojson, 'r', encoding='utf-8') as f:
                data = json.load(f)

            lote_encontrado = False
            for feature in data['features']:
                props = feature['properties']
                # Verifica ID, id ou Lote
                if str(props.get('Lote')) == id_lote_alvo or str(props.get('id')) == id_lote_alvo or str(props.get('ID')) == id_lote_alvo:
                    props['status'] = novo_status
                    props['obs'] = nova_obs
                    lote_encontrado = True
                    break

            if lote_encontrado:
                with open(caminho_geojson, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                # 2. DISPARA A ATUALIZAÇÃO PARA O GITHUB
                msg = f"Atualizacao Lote {id_lote_alvo} - {loteamento_selecionado}"
                if self.sincronizar_github(msg):
                    messagebox.showinfo("Sucesso", "Mapa atualizado com sucesso no site!")
                else:
                    messagebox.showwarning("Git", "Salvo localmente, mas falha ao enviar para o GitHub. Verifique o Token.")
            else:
                messagebox.showwarning("Erro", "Lote não encontrado no mapa.")

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"{e}")