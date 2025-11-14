from client_desktop import api_client
import sys
import os
import tkinter as tk
from tkinter import messagebox, Toplevel, Listbox, END, Label, Entry, Button, Frame

# Adiciona a pasta raiz (sistema_academico_pim) ao "caminho" do Python
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)


# --- Classe Genérica de Formulário (sem alterações) ---

class FormularioPopup(Toplevel):
    def __init__(self, master, titulo, campos, callback_salvar, dados_preenchidos=None):
        super().__init__(master)
        self.title(titulo)
        self.geometry("350x450")
        self.transient(master)
        self.grab_set()

        self.campos = campos
        self.callback = callback_salvar
        self.entries = {}

        form_frame = Frame(self)
        form_frame.pack(pady=10, padx=10)

        for i, campo in enumerate(campos):
            label_texto = f"{campo.capitalize()}:"
            Label(form_frame, text=label_texto).grid(row=i, column=0, padx=10, pady=8, sticky='w')

            entry_options = {}
            if "senha" in campo.lower():
                entry_options['show'] = '*'

            entry = Entry(form_frame, width=30, **entry_options)
            entry.grid(row=i, column=1, padx=10, pady=8)

            if dados_preenchidos and campo in dados_preenchidos:
                entry.insert(0, dados_preenchidos[campo])
                if "id" in campo.lower():
                    entry.config(state="readonly")

            self.entries[campo] = entry

        Button(self, text="Salvar", command=self.salvar).pack(pady=20)

    def salvar(self):
        dados = {}
        for campo, entry in self.entries.items():
            dados[campo] = entry.get()
        self.callback(dados)
        self.destroy()


# === PAINEL DO ALUNO (ÉPICO 4) ===
class AlunoPanel(Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.id_aluno = usuario['id_aluno']
        self.title(f"Painel Aluno - Bem-vindo, {usuario['nome']}")
        self.geometry("800x600")

        Label(self, text=f"Usuário: {usuario['email']} (ID Aluno: {self.id_aluno})", font=(
            "Arial", 10)).pack(pady=5)

        # --- Frames ---
        action_frame = Frame(self)
        action_frame.pack(pady=10)

        list_frame = Frame(self)
        list_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # --- Botões de Ação ---
        Button(action_frame, text="Consultar Meu Boletim",
               command=self.carregar_boletim).pack(side=tk.LEFT, padx=5)
        Button(action_frame, text="Listar Minhas Atividades",
               command=self.carregar_atividades).pack(side=tk.LEFT, padx=5)
        Button(action_frame, text="Enviar Atividade Selecionada",
               command=self.abrir_form_entrega).pack(side=tk.LEFT, padx=5)

        # --- Listbox ---
        self.listbox = Listbox(list_frame, width=120, height=25)
        self.listbox.pack(pady=10, padx=10, fill='both', expand=True)

        # --- Variáveis de Estado ---
        self.atividades_carregadas = {}  # Guarda os dados das atividades
        self.modo_lista = None  # 'boletim' ou 'atividades'

    def carregar_boletim(self):
        self.modo_lista = 'boletim'
        self.listbox.delete(0, END)
        self.listbox.insert(END, "Carregando boletim...")

        resposta = api_client.get_boletim(self.id_aluno)

        self.listbox.delete(0, END)
        if "erro" in resposta:
            self.listbox.insert(END, f"ERRO: {resposta['erro']}")
        else:
            boletim = resposta.get("boletim", [])
            if not boletim:
                self.listbox.insert(
                    END, "Nenhum dado encontrado para este aluno.")
                return

            self.listbox.insert(
                END, f"--- Boletim de {self.usuario['nome']} ---")
            for item in boletim:
                self.listbox.insert(END, "")
                self.listbox.insert(
                    END, f"Disciplina: {item['nome_disciplina']} | Situação: {item['situacao']}")
                self.listbox.insert(
                    END, f"    Média Final: {item['media_final']}")
                self.listbox.insert(
                    END, f"    Frequência: {item['pct_frequencia']}% (Total de Faltas: {item['total_faltas']})")

    def carregar_atividades(self):
        self.modo_lista = 'atividades'
        self.atividades_carregadas = {}
        self.listbox.delete(0, END)
        self.listbox.insert(END, "Carregando atividades...")
        
        resposta = api_client.listar_atividades_aluno(self.id_aluno)
        
        self.listbox.delete(0, END)
        if "erro" in resposta:
            self.listbox.insert(END, f"ERRO: {resposta['erro']}")
        elif not resposta:
            self.listbox.insert(END, "Nenhuma atividade disponível no momento.")
        else:
            self.listbox.insert(END, "--- Minhas Atividades (Selecione uma para entregar) ---")
            for ativ in resposta:
                self.atividades_carregadas[ativ['id_atividade']] = ativ
                self.listbox.insert(END, f"ID: {ativ['id_atividade']} | Título: {ativ['titulo']} | Entrega: {ativ['data_entrega']}")
                self.listbox.insert(END, f"    Descrição: {ativ['descricao']}")
                
                # --- INÍCIO DA CORREÇÃO ---
                anexo = ativ.get('caminho_anexo')
                if anexo:
                    self.listbox.insert(END, f"    ANEXO: {anexo}")

    def get_selected_id(self):
        try:
            selection = self.listbox.curselection()
            if not selection:
                return None
            selected_text = self.listbox.get(selection[0])

            # Pega o ID (ex: "ID: 5 | ...")
            return int(selected_text.split('|')[0].replace('ID:', '').strip())
        except Exception:
            return None

    def abrir_form_entrega(self):
        if self.modo_lista != 'atividades':
            messagebox.showerror(
                "Erro", "Por favor, liste as atividades e selecione uma primeiro.")
            return

        id_atividade_sel = self.get_selected_id()
        if not id_atividade_sel:
            messagebox.showerror("Erro", "Nenhuma atividade selecionada.")
            return

        campos = ["id_atividade", "id_aluno", "arquivo (ex: C:/trabalho.pdf)"]
        dados_preenchidos = {
            "id_atividade": id_atividade_sel,
            "id_aluno": self.id_aluno
        }
        FormularioPopup(self, "Enviar Atividade", campos,
                        self.salvar_entrega, dados_preenchidos)

    def salvar_entrega(self, dados):
        resposta = api_client.enviar_atividade(dados)
        if "erro" in resposta:
            messagebox.showerror("Erro", resposta["erro"])
        else:
            messagebox.showinfo("Sucesso", "Atividade enviada com sucesso!")
            self.carregar_atividades()  # Recarrega a lista


# === PAINEL DO PROFESSOR (ATUALIZADO ÉPICO 4) ===
class ProfessorPanel(Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.id_professor = usuario['id_professor']
        self.title(f"Painel Professor - Bem-vindo, {usuario['nome']}")
        self.geometry("900x600")  # Mais largo

        Label(self, text=f"Usuário: {usuario['email']} (ID Professor: {self.id_professor})", font=(
            "Arial", 10)).pack(pady=5)

        # --- Frames ---
        action_frame = Frame(self)
        action_frame.pack(pady=10)

        list_frame = Frame(self)
        list_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # --- Botões de Ação ---
        Button(action_frame, text="Listar Minhas Turmas",
               command=self.carregar_turmas).pack(side=tk.LEFT, padx=5)
        Button(action_frame, text="Criar Atividade (p/ Turma Sel.)",
               command=self.abrir_form_atividade).pack(side=tk.LEFT, padx=5)
        Button(action_frame, text="Lançar Nota (p/ Aluno Sel.)",
               command=self.abrir_form_nota).pack(side=tk.LEFT, padx=5)
        Button(action_frame, text="Registrar Falta (p/ Aluno Sel.)",
               command=self.abrir_form_falta).pack(side=tk.LEFT, padx=5)

        # --- Listboxes (Duas listas Lado a Lado) ---
        self.listbox_turmas = Listbox(list_frame, width=60, height=25)
        self.listbox_turmas.pack(side=tk.LEFT, pady=10, padx=10, fill='y')

        self.listbox_alunos = Listbox(list_frame, width=60, height=25)
        self.listbox_alunos.pack(side=tk.RIGHT, pady=10, padx=10, fill='y')

        # --- Variáveis de Estado ---
        self.turmas_carregadas = {}  # Guarda os dados das turmas
        self.id_turma_selecionada_cache = None  # Guarda o ID da última turma clicada
        self.id_aluno_selecionado_cache = None  # Guarda o ID do último aluno clicado

        # --- Bindings (Eventos de Clique) ---
        self.listbox_turmas.bind('<<ListboxSelect>>', self.on_turma_select)
        self.listbox_alunos.bind('<<ListboxSelect>>', self.on_aluno_select)

    def carregar_turmas(self):
        self.listbox_turmas.delete(0, END)
        self.listbox_alunos.delete(0, END)
        self.turmas_carregadas = {}
        self.id_turma_selecionada_cache = None  # Limpa o cache
        self.id_aluno_selecionado_cache = None  # Limpa o cache
        self.listbox_turmas.insert(END, "Carregando turmas...")

        resposta = api_client.listar_turmas_professor(self.id_professor)

        self.listbox_turmas.delete(0, END)
        if "erro" in resposta:
            self.listbox_turmas.insert(END, f"ERRO: {resposta['erro']}")
        elif not resposta:
            self.listbox_turmas.insert(END, "Nenhuma turma encontrada.")
        else:
            self.listbox_turmas.insert(
                END, "--- Minhas Turmas (Selecione uma) ---")
            for turma in resposta:
                self.turmas_carregadas[turma['id_turma']
                                       ] = turma  # Salva o objeto
                self.listbox_turmas.insert(
                    END, f"ID: {turma['id_turma']} | {turma['nome_disciplina']} ({turma['codigo']})")


# Em /client_desktop/app.py (na classe ProfessorPanel)


    def on_turma_select(self, event):
        """Chamado quando o professor clica em uma turma."""
        selected_id = self.get_selected_turma_id()  # Lê do listbox

        # Se a seleção for inválida (None), não faz NADA.
        if not selected_id:
            return

        # SÓ recarrega se a seleção da turma MUDOU
        if selected_id == self.id_turma_selecionada_cache:
            return  # Não faz nada se o clique for na mesma turma

        # A seleção é válida e é nova. Limpa o cache do aluno.
        self.id_aluno_selecionado_cache = None

        self.id_turma_selecionada_cache = selected_id  # ATUALIZA O CACHE

        turma = self.turmas_carregadas[selected_id]

        self.listbox_alunos.delete(0, END)  # Limpa a lista da direita

        # --- INÍCIO DA CORREÇÃO ---
        atividades = turma.get("atividades", [])
        alunos = turma.get("alunos_matriculados", [])

        if not atividades and not alunos:
            self.listbox_alunos.insert(
                END, "(Nenhuma atividade ou aluno nesta turma)")
            return

        # 1. MOSTRA AS ATIVIDADES
        self.listbox_alunos.insert(END, "--- Atividades da Turma ---")
        if not atividades:
            self.listbox_alunos.insert(END, "(Nenhuma atividade criada)")
        for ativ in atividades:
            self.listbox_alunos.insert(
                END, f"  Ativ ID: {ativ['id_atividade']} | {ativ['titulo']} (Peso: {ativ['peso']})")

        self.listbox_alunos.insert(END, "")  # Espaçador

        # 2. MOSTRA OS ALUNOS
        self.listbox_alunos.insert(
            END, "--- Alunos Matriculados (Selecione um) ---")
        if not alunos:
            self.listbox_alunos.insert(END, "(Nenhum aluno matriculado)")
        for aluno in alunos:
            self.listbox_alunos.insert(
                END, f"  Aluno ID: {aluno['id_aluno']} | {aluno['nome']} (RA: {aluno['ra']})")
        # --- FIM DA CORREÇÃO ---

    def on_aluno_select(self, event):
        """Chamado quando o professor clica em um aluno."""
        id_aluno_sel = self.get_selected_aluno_id()  # Lê do listbox
        id_turma_sel = self.id_turma_selecionada_cache

        if not id_aluno_sel:  # Se clicou em um header, não faz nada
            return

        # SÓ atualiza o cache do aluno se a seleção for válida
        self.id_aluno_selecionado_cache = id_aluno_sel

        # --- NOVA FUNCIONALIDADE: MOSTRAR DETALHES ---
        self.listbox_alunos.delete(0, END)
        self.listbox_alunos.insert(
            END, f"Carregando detalhes do Aluno ID: {id_aluno_sel}...")

        resposta = api_client.get_detalhes_aluno(id_turma_sel, id_aluno_sel)

        self.listbox_alunos.delete(0, END)
        if "erro" in resposta:
            self.listbox_alunos.insert(END, f"ERRO: {resposta['erro']}")
            return

        detalhes = resposta.get("detalhes", {})
        notas = detalhes.get("notas", [])
        faltas = detalhes.get("faltas", [])

        self.listbox_alunos.insert(
            END, f"--- Detalhes do Aluno ID: {id_aluno_sel} ---")

        self.listbox_alunos.insert(END, "")
        self.listbox_alunos.insert(END, f"--- Notas ({len(notas)}) ---")
        if not notas:
            self.listbox_alunos.insert(END, "(Nenhuma nota lançada)")
        for nota in notas:
            nome_ativ = nota.get('nome_atividade', 'N/A')
            self.listbox_alunos.insert(
                END, f"  Valor: {nota['valor']} (Atividade: {nome_ativ})")

        self.listbox_alunos.insert(END, "")
        self.listbox_alunos.insert(END, f"--- Faltas ({len(faltas)}) ---")
        if not faltas:
            self.listbox_alunos.insert(END, "(Nenhuma falta registrada)")
        for falta in faltas:
            self.listbox_alunos.insert(
                END, f"  Data: {falta['data_aula']} (Justificada: {falta['justificada']})")

        # Adiciona um "botão" para voltar
        self.listbox_alunos.insert(END, "")
        self.listbox_alunos.insert(
            END, "--- (Clique em 'Listar Minhas Turmas' para voltar) ---")

    def get_selected_turma_id(self):
        try:
            selection = self.listbox_turmas.curselection()
            if not selection:  # Se nada estiver selecionado
                return None
            selected_text = self.listbox_turmas.get(
                selection[0])  # Pega o índice 0

            return int(selected_text.split('|')[0].replace('ID:', '').strip())
        except Exception as e:
            # print(f"Erro em get_selected_turma_id: {e}")
            return None

    def get_selected_aluno_id(self):
        try:
            selection = self.listbox_alunos.curselection()
            if not selection:  # Se nada estiver selecionado
                return None
            selected_text = self.listbox_alunos.get(
                selection[0])  # Pega o índice 0

            if "Aluno ID:" not in selected_text:
                return None
            return int(selected_text.split('|')[0].replace('Aluno ID:', '').strip())
        except Exception as e:
            # print(f"Erro em get_selected_aluno_id: {e}")
            return None
    # --- FIM DA CORREÇÃO ---

    def abrir_form_atividade(self):
        id_turma_sel = self.id_turma_selecionada_cache # <-- Lê do cache
        if not id_turma_sel:
            messagebox.showerror("Erro", "Nenhuma turma selecionada.")
            return

        # --- CORREÇÃO ---
        campos = ["id_turma", "titulo", "descricao", "data_entrega (YYYY-MM-DD)", "peso", "caminho_anexo (opcional)"]
        # --- FIM DA CORREÇÃO ---
        dados_preenchidos = {"id_turma": id_turma_sel}
        FormularioPopup(self, "Criar Nova Atividade", campos, self.salvar_atividade, dados_preenchidos)

    def salvar_atividade(self, dados):
        # --- CORREÇÃO ---
        # Renomeia a chave do formulário para a chave da API
        if 'caminho_anexo (opcional)' in dados:
            dados['caminho_anexo'] = dados.pop('caminho_anexo (opcional)')
        # --- FIM DA CORREÇÃO ---

        resposta = api_client.criar_nova_atividade(dados)
        if "erro" in resposta: messagebox.showerror("Erro", resposta["erro"])
        else: messagebox.showinfo("Sucesso", "Atividade criada!"); self.carregar_turmas() # Recarrega

    def abrir_form_nota(self):
        id_turma_sel = self.id_turma_selecionada_cache  # <-- Lê do cache
        id_aluno_sel = self.id_aluno_selecionado_cache  # <-- Lê do cache

        if not id_turma_sel or not id_aluno_sel:
            messagebox.showerror(
                "Erro", "Selecione uma Turma e um Aluno primeiro.")
            return

        campos = ["id_aluno", "id_turma", "id_atividade (opcional)", "valor"]
        dados_preenchidos = {
            "id_aluno": id_aluno_sel,
            "id_turma": id_turma_sel
        }
        FormularioPopup(self, "Lançar Nota", campos,
                        self.salvar_nota, dados_preenchidos)

    def abrir_form_falta(self):
        id_turma_sel = self.id_turma_selecionada_cache  # <-- Lê do cache
        id_aluno_sel = self.id_aluno_selecionado_cache  # <-- Lê do cache

        if not id_turma_sel or not id_aluno_sel:
            messagebox.showerror(
                "Erro", "Selecione uma Turma e um Aluno primeiro.")
            return

        campos = ["id_aluno", "id_turma", "data_aula (YYYY-MM-DD)"]
        dados_preenchidos = {
            "id_aluno": id_aluno_sel,
            "id_turma": id_turma_sel
        }
        FormularioPopup(self, "Registrar Falta", campos,
                        self.salvar_falta, dados_preenchidos)

    def salvar_atividade(self, dados):
        resposta = api_client.criar_nova_atividade(dados)
        if "erro" in resposta:
            messagebox.showerror("Erro", resposta["erro"])
        else:
            messagebox.showinfo("Sucesso", "Atividade criada!")
            self.carregar_turmas()  # Recarrega

    def salvar_nota(self, dados):

        if 'id_atividade (opcional)' in dados:
            dados['id_atividade'] = dados.pop('id_atividade (opcional)')
        # --- FIM DA CORREÇÃO ---

        dados["id_professor"] = self.id_professor

        resposta = api_client.lancar_nota(dados)

        if "erro" in resposta:
            messagebox.showerror("Erro", resposta["erro"])
        else:
            messagebox.showinfo("Sucesso", "Nota lançada!")

    def salvar_falta(self, dados):
        resposta = api_client.registrar_falta(dados)
        if "erro" in resposta:
            messagebox.showerror("Erro", resposta["erro"])
        else:
            messagebox.showinfo("Sucesso", "Falta registrada!")


# === PAINEL DO ADMIN (ÉPICO 3) ===
# === PAINEL DO ADMIN (ATUALIZADO) ===
# Em /client_desktop/app.py

# === PAINEL DO ADMIN (ATUALIZADO) ===
# Em /client_desktop/app.py

# === PAINEL DO ADMIN (ATUALIZADO) ===
# Em /client_desktop/app.py

# === PAINEL DO ADMIN (ATUALIZADO) ===
class AdminPanel(Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.title(f"Painel Admin - Bem-vindo, {usuario['nome']}")
        self.geometry("900x600")

        Label(self, text=f"Usuário: {usuario['email']} (Tipo: {usuario['tipo']})", font=("Arial", 10)).pack(pady=5)

        # --- Frame de Ações de Listagem (GET) ---
        list_frame = Frame(self)
        list_frame.pack(pady=5, fill='x', padx=20)
        Label(list_frame, text="Listar Entidades:").pack(side=tk.LEFT, padx=5)
        self.btn_load_alunos = Button(list_frame, text="Alunos", command=self.carregar_alunos)
        self.btn_load_alunos.pack(side=tk.LEFT, padx=5)
        self.btn_load_prof = Button(list_frame, text="Professores", command=self.carregar_professores)
        self.btn_load_prof.pack(side=tk.LEFT, padx=5)
        self.btn_load_disciplinas = Button(list_frame, text="Disciplinas", command=self.carregar_disciplinas)
        self.btn_load_disciplinas.pack(side=tk.LEFT, padx=5)
        self.btn_load_turmas = Button(list_frame, text="Turmas", command=self.carregar_turmas)
        self.btn_load_turmas.pack(side=tk.LEFT, padx=5)

        # --- Frame de Ações de Criação (POST) ---
        create_frame = Frame(self)
        create_frame.pack(pady=5, fill='x', padx=20)
        Label(create_frame, text="Adicionar Entidades:").pack(side=tk.LEFT, padx=5)
        self.btn_add_aluno = Button(create_frame, text="Novo Aluno", command=self.abrir_form_aluno)
        self.btn_add_aluno.pack(side=tk.LEFT, padx=5)
        self.btn_add_prof = Button(create_frame, text="Novo Professor", command=self.abrir_form_professor)
        self.btn_add_prof.pack(side=tk.LEFT, padx=5)
        self.btn_add_disciplina = Button(create_frame, text="Nova Disciplina", command=self.abrir_form_disciplina)
        self.btn_add_disciplina.pack(side=tk.LEFT, padx=5)
        self.btn_add_turma = Button(create_frame, text="Nova Turma", command=self.abrir_form_turma)
        self.btn_add_turma.pack(side=tk.LEFT, padx=5)
        self.btn_add_matricula = Button(create_frame, text="Matricular Aluno", command=self.abrir_form_matricula)
        self.btn_add_matricula.pack(side=tk.LEFT, padx=5)
        
        # --- Frame de Ações de Modificação (PUT/DELETE) ---
        modify_frame = Frame(self)
        modify_frame.pack(pady=5, fill='x', padx=20)
        Label(modify_frame, text="Modificar Entidades:").pack(side=tk.LEFT, padx=5)
        # Botões de Edição (PUT)
        self.btn_edit_aluno = Button(modify_frame, text="Editar Aluno Sel.", command=self.abrir_form_editar_aluno, bg="#DDEEFF")
        self.btn_edit_aluno.pack(side=tk.LEFT, padx=5)
        self.btn_edit_prof = Button(modify_frame, text="Editar Prof. Sel.", command=self.abrir_form_editar_professor, bg="#DDEEFF")
        self.btn_edit_prof.pack(side=tk.LEFT, padx=5)
        self.btn_edit_disc = Button(modify_frame, text="Editar Disc. Sel.", command=self.abrir_form_editar_disciplina, bg="#DDEEFF")
        self.btn_edit_disc.pack(side=tk.LEFT, padx=5)
        self.btn_edit_turma = Button(modify_frame, text="Editar Turma Sel.", command=self.abrir_form_editar_turma, bg="#DDEEFF")
        self.btn_edit_turma.pack(side=tk.LEFT, padx=5)
        
        # --- Frame de Ações de Exclusão (DELETE) ---
        delete_frame = Frame(self)
        delete_frame.pack(pady=5, fill='x', padx=20)
        Label(delete_frame, text="Excluir Entidades:").pack(side=tk.LEFT, padx=5)
        self.btn_del_aluno = Button(delete_frame, text="Excluir Aluno Sel.", command=self.abrir_form_excluir_aluno, bg="#FFDDDD")
        self.btn_del_aluno.pack(side=tk.LEFT, padx=5)
        self.btn_del_prof = Button(delete_frame, text="Excluir Prof. Sel.", command=self.abrir_form_excluir_professor, bg="#FFDDDD")
        self.btn_del_prof.pack(side=tk.LEFT, padx=5)
        self.btn_del_disc = Button(delete_frame, text="Excluir Disc. Sel.", command=self.abrir_form_excluir_disciplina, bg="#FFDDDD")
        self.btn_del_disc.pack(side=tk.LEFT, padx=5)
        self.btn_del_turma = Button(delete_frame, text="Excluir Turma Sel.", command=self.abrir_form_excluir_turma, bg="#FFDDDD")
        self.btn_del_turma.pack(side=tk.LEFT, padx=5)
        self.btn_del_matr = Button(delete_frame, text="Desmatricular Aluno", command=self.abrir_form_desmatricular, bg="#FFDDDD")
        self.btn_del_matr.pack(side=tk.LEFT, padx=5)
        
        self.listbox = Listbox(self, width=120, height=25)
        self.listbox.pack(pady=10, padx=20, fill='both', expand=True)
        
        # --- Cache de estado ---
        self.modo_lista_atual = None 
        self.id_item_para_editar = None # ID genérico para edição

    def _limpar_e_mostrar_carregando(self, msg):
        self.listbox.delete(0, END)
        self.listbox.insert(END, msg)
        self.update_idletasks()

    def _processar_resposta_lista(self, resposta, tipo, format_func):
        self.listbox.delete(0, END)
        if "erro" in resposta:
            self.listbox.insert(END, f"ERRO: {resposta['erro']}")
        elif not resposta:
            self.listbox.insert(END, f"Nenhum(a) {tipo} encontrado(a).")
        else:
            self.listbox.insert(END, f"--- {len(resposta)} {tipo}(s) Encontrados ---")
            for item in resposta:
                self.listbox.insert(END, format_func(item))
                
    def carregar_turmas(self):
        self.modo_lista_atual = 'turmas'
        self._limpar_e_mostrar_carregando("Carregando turmas e matrículas...")
        resposta = api_client.listar_turmas()
        self.listbox.delete(0, END)
        if "erro" in resposta:
            self.listbox.insert(END, f"ERRO: {resposta['erro']}")
        elif not resposta:
            self.listbox.insert(END, "Nenhuma turma encontrada.")
        else:
            self.listbox.insert(END, f"--- {len(resposta)} Turma(s) Encontrada(s) ---")
            for turma in resposta:
                linha_turma = (f"ID: {turma['id_turma']} | Código: {turma['codigo']} | (Prof ID: {turma['id_professor']}, Disc ID: {turma['id_disciplina']})")
                self.listbox.insert(END, linha_turma)
                alunos = turma.get("alunos_matriculados", [])
                if not alunos:
                    self.listbox.insert(END, "    -> (Nenhum aluno matriculado nesta turma)")
                else:
                    for aluno in alunos:
                        linha_aluno = f"    -> Aluno: {aluno['nome']} (ID: {aluno['id_aluno']}, RA: {aluno['ra']})"
                        self.listbox.insert(END, linha_aluno)
                self.listbox.insert(END, "") 

    def carregar_alunos(self):
        self.modo_lista_atual = 'alunos'
        self._limpar_e_mostrar_carregando("Carregando alunos...")
        resposta = api_client.listar_alunos()
        self._processar_resposta_lista(resposta, "aluno", lambda al: f"ID: {al['id_aluno']} | Nome: {al['nome']} | RA: {al['ra']} | Curso: {al['curso']}")
    
    def carregar_professores(self):
        self.modo_lista_atual = 'professores'
        self._limpar_e_mostrar_carregando("Carregando professores...")
        resposta = api_client.listar_professores()
        self._processar_resposta_lista(resposta, "professor", lambda p: f"ID: {p['id_professor']} | Nome: {p['nome']} | Formação: {p['formacao']}")
    
    def carregar_disciplinas(self):
        self.modo_lista_atual = 'disciplinas'
        self._limpar_e_mostrar_carregando("Carregando disciplinas...")
        resposta = api_client.listar_disciplinas()
        self._processar_resposta_lista(resposta, "disciplina", lambda d: f"ID: {d['id_disciplina']} | Nome: {d['nome']} | Carga: {d['carga_horaria']}h")

    # --- Funções HELPER de Seleção ---
    def _get_selected_id_from_list(self, tipo_esperado, prefixo):
        if self.modo_lista_atual != tipo_esperado:
            messagebox.showerror("Erro", f"Por favor, liste os {tipo_esperado} primeiro.")
            return None
        try:
            selection = self.listbox.curselection()
            if not selection: return None
            selected_text = self.listbox.get(selection[0])
            if prefixo not in selected_text: return None
            return int(selected_text.split('|')[0].replace(prefixo, '').strip())
        except Exception as e:
            print(f"Erro em _get_selected_id: {e}")
            return None

    def _get_selected_aluno_id_from_turma_list(self):
        if self.modo_lista_atual != 'turmas':
            messagebox.showerror("Erro", "Por favor, liste as turmas primeiro.")
            return None
        try:
            selection = self.listbox.curselection()
            if not selection: return None
            selected_text = self.listbox.get(selection[0])
            if "-> Aluno:" not in selected_text: return None
            id_str = selected_text.split('(ID:')[1].split(',')[0]
            return int(id_str.strip())
        except Exception as e:
            print(f"Erro em _get_selected_aluno_id_from_turma_list: {e}")
            return None

    # --- Funções de Abrir Formulário (POST) ---
    def abrir_form_aluno(self):
        campos = ["nome", "email", "senha", "ra", "curso"]
        FormularioPopup(self, "Adicionar Novo Aluno", campos, self.salvar_aluno)
    def abrir_form_professor(self):
        campos = ["nome", "email", "senha", "formacao"]
        FormularioPopup(self, "Adicionar Novo Professor", campos, self.salvar_professor)
    def abrir_form_disciplina(self):
        campos = ["nome", "descricao", "carga_horaria"]
        FormularioPopup(self, "Adicionar Nova Disciplina", campos, self.salvar_disciplina)
    def abrir_form_turma(self):
        campos = ["codigo", "semestre", "id_disciplina", "id_professor"]
        FormularioPopup(self, "Adicionar Nova Turma", campos, self.salvar_turma)
    def abrir_form_matricula(self):
        campos = ["id_aluno", "id_turma"]
        FormularioPopup(self, "Matricular Aluno na Turma", campos, self.salvar_matricula)

    # --- Funções de Abrir Formulário (PUT) ---
    def abrir_form_editar_aluno(self):
        id_sel = self._get_selected_id_from_list('alunos', 'ID:')
        if not id_sel: messagebox.showerror("Erro", "Nenhum aluno selecionado."); return
        self.id_item_para_editar = id_sel
        
        resposta = api_client.get_aluno(id_sel)
        if "erro" in resposta: messagebox.showerror("Erro", f"Não foi possível buscar dados: {resposta['erro']}"); return
            
        campos = ["nome", "email", "ra", "curso", "senha (deixe em branco para não alterar)"]
        dados_preenchidos = {
            "nome": resposta.get('nome'), "email": resposta.get('email'),
            "ra": resposta.get('ra'), "curso": resposta.get('curso'),
            "senha (deixe em branco para não alterar)": ""
        }
        FormularioPopup(self, f"Editando Aluno ID: {id_sel}", campos, self.salvar_edicao_aluno, dados_preenchidos)

    def abrir_form_editar_professor(self):
        id_sel = self._get_selected_id_from_list('professores', 'ID:')
        if not id_sel: messagebox.showerror("Erro", "Nenhum professor selecionado."); return
        self.id_item_para_editar = id_sel
        
        resposta = api_client.get_professor(id_sel)
        if "erro" in resposta: messagebox.showerror("Erro", f"Não foi possível buscar dados: {resposta['erro']}"); return
            
        campos = ["nome", "email", "formacao", "senha (deixe em branco para não alterar)"]
        dados_preenchidos = {
            "nome": resposta.get('nome'), "email": resposta.get('email'),
            "formacao": resposta.get('formacao'),
            "senha (deixe em branco para não alterar)": ""
        }
        FormularioPopup(self, f"Editando Professor ID: {id_sel}", campos, self.salvar_edicao_professor, dados_preenchidos)
        
    def abrir_form_editar_disciplina(self):
        id_sel = self._get_selected_id_from_list('disciplinas', 'ID:')
        if not id_sel: messagebox.showerror("Erro", "Nenhuma disciplina selecionada."); return
        self.id_item_para_editar = id_sel
        
        resposta = api_client.get_disciplina(id_sel)
        if "erro" in resposta: messagebox.showerror("Erro", f"Não foi possível buscar dados: {resposta['erro']}"); return
            
        campos = ["nome", "descricao", "carga_horaria"]
        dados_preenchidos = {
            "nome": resposta.get('nome'),
            "descricao": resposta.get('descricao'),
            "carga_horaria": resposta.get('carga_horaria')
        }
        FormularioPopup(self, f"Editando Disciplina ID: {id_sel}", campos, self.salvar_edicao_disciplina, dados_preenchidos)

    def abrir_form_editar_turma(self):
        id_sel = self._get_selected_id_from_list('turmas', 'ID:')
        if not id_sel: messagebox.showerror("Erro", "Nenhuma turma selecionada."); return
        self.id_item_para_editar = id_sel
        
        resposta = api_client.get_turma(id_sel)
        if "erro" in resposta: messagebox.showerror("Erro", f"Não foi possível buscar dados: {resposta['erro']}"); return
            
        campos = ["codigo", "semestre", "id_disciplina", "id_professor"]
        dados_preenchidos = {
            "codigo": resposta.get('codigo'),
            "semestre": resposta.get('semestre'),
            "id_disciplina": resposta.get('id_disciplina'),
            "id_professor": resposta.get('id_professor')
        }
        FormularioPopup(self, f"Editando Turma ID: {id_sel}", campos, self.salvar_edicao_turma, dados_preenchidos)

    # --- Funções de Confirmação (DELETE) ---
    def _confirmar_exclusao(self, tipo, id_selecionado, callback_api, callback_lista):
        if not id_selecionado:
            messagebox.showerror("Erro", f"Nenhum(a) {tipo} selecionado(a) na lista.")
            return
        
        confirm = messagebox.askyesno(
            f"Confirmar Exclusão",
            f"Tem certeza que deseja excluir o(a) {tipo} ID: {id_selecionado}?\n"
            "Esta ação pode ser irreversível."
        )
        if confirm:
            print(f"Excluindo {tipo} ID: {id_selecionado}")
            resposta = callback_api(id_selecionado)
            if "erro" in resposta:
                messagebox.showerror("Erro ao Excluir", resposta["erro"])
            else:
                messagebox.showinfo("Sucesso", resposta.get("mensagem", f"{tipo} excluído(a)!"))
                callback_lista() # Atualiza a lista

    def abrir_form_excluir_aluno(self):
        id_sel = self._get_selected_id_from_list('alunos', 'ID:')
        self._confirmar_exclusao('Aluno', id_sel, api_client.excluir_aluno, self.carregar_alunos)
    def abrir_form_excluir_professor(self):
        id_sel = self._get_selected_id_from_list('professores', 'ID:')
        self._confirmar_exclusao('Professor', id_sel, api_client.excluir_professor, self.carregar_professores)
    def abrir_form_excluir_disciplina(self):
        id_sel = self._get_selected_id_from_list('disciplinas', 'ID:')
        self._confirmar_exclusao('Disciplina', id_sel, api_client.excluir_disciplina, self.carregar_disciplinas)
    def abrir_form_excluir_turma(self):
        id_sel = self._get_selected_id_from_list('turmas', 'ID:')
        self._confirmar_exclusao('Turma', id_sel, api_client.excluir_turma, self.carregar_turmas)
    def abrir_form_desmatricular(self):
        if self.modo_lista_atual != 'turmas':
            messagebox.showerror("Erro", "Por favor, liste as turmas primeiro.")
            return
        id_aluno_sel = self._get_selected_aluno_id_from_turma_list()
        if not id_aluno_sel:
            messagebox.showerror("Erro", "Selecione um aluno (linha '-> Aluno:') da lista de turmas.")
            return
        id_turma_sel = None
        try:
            indice_aluno = self.listbox.curselection()[0]
            for i in range(indice_aluno, -1, -1):
                linha = self.listbox.get(i)
                if "ID:" in linha and "Código:" in linha:
                    id_turma_sel = int(linha.split('|')[0].replace('ID:', '').strip())
                    break
        except Exception: pass
        if not id_turma_sel:
            messagebox.showerror("Erro Interno", "Não foi possível identificar a turma do aluno selecionado.")
            return
        confirm = messagebox.askyesno(
            f"Confirmar Exclusão",
            f"Tem certeza que deseja desmatricular o Aluno ID: {id_aluno_sel} da Turma ID: {id_turma_sel}?"
        )
        if confirm:
            resposta = api_client.desmatricular_aluno(id_turma_sel, id_aluno_sel)
            if "erro" in resposta: messagebox.showerror("Erro ao Desmatricular", resposta["erro"])
            else: messagebox.showinfo("Sucesso", resposta.get("mensagem", "Aluno desmatriculado!")); self.carregar_turmas()

    # --- Funções de Callback (POST) ---
    def _processar_resposta_criacao(self, resposta, tipo_sucesso, callback_lista):
        if "erro" in resposta:
            messagebox.showerror("Erro ao Salvar", resposta["erro"])
        else:
            messagebox.showinfo("Sucesso", resposta.get("mensagem", f"{tipo_sucesso} criado(a)!"))
            callback_lista() 
    def salvar_aluno(self, dados):
        resposta = api_client.criar_novo_aluno(dados)
        self._processar_resposta_criacao(resposta, "Aluno", self.carregar_alunos) 
    def salvar_professor(self, dados):
        resposta = api_client.criar_novo_professor(dados)
        self._processar_resposta_criacao(resposta, "Professor", self.carregar_professores) 
    def salvar_disciplina(self, dados):
        try: dados['carga_horaria'] = int(dados['carga_horaria'])
        except ValueError: messagebox.showerror("Erro de Formato", "Carga horária deve ser um número."); return
        resposta = api_client.criar_nova_disciplina(dados)
        self._processar_resposta_criacao(resposta, "Disciplina", self.carregar_disciplinas)
    def salvar_turma(self, dados):
        try:
            dados['id_disciplina'] = int(dados['id_disciplina']); dados['id_professor'] = int(dados['id_professor'])
        except ValueError: messagebox.showerror("Erro de Formato", "IDs devem ser números."); return
        resposta = api_client.criar_nova_turma(dados)
        self._processar_resposta_criacao(resposta, "Turma", self.carregar_turmas)
    def salvar_matricula(self, dados):
        try:
            dados['id_aluno'] = int(dados['id_aluno']); dados['id_turma'] = int(dados['id_turma'])
        except ValueError: messagebox.showerror("Erro de Formato", "IDs devem ser números."); return
        resposta = api_client.matricular_aluno(dados)
        if "erro" in resposta: messagebox.showerror("Erro ao Salvar", resposta["erro"])
        else: messagebox.showinfo("Sucesso", resposta.get("mensagem", "Aluno matriculado!")); self.carregar_turmas()

    # --- Funções de Callback (PUT) ---
    def salvar_edicao_aluno(self, dados):
        dados['senha'] = dados.pop('senha (deixe em branco para não alterar)', None)
        resposta = api_client.editar_aluno(self.id_item_para_editar, dados)
        if "erro" in resposta: messagebox.showerror("Erro ao Editar", resposta["erro"])
        else: messagebox.showinfo("Sucesso", resposta.get("mensagem", "Aluno atualizado!")); self.carregar_alunos()
        self.id_item_para_editar = None 

    def salvar_edicao_professor(self, dados):
        dados['senha'] = dados.pop('senha (deixe em branco para não alterar)', None)
        resposta = api_client.editar_professor(self.id_item_para_editar, dados)
        if "erro" in resposta: messagebox.showerror("Erro ao Editar", resposta["erro"])
        else: messagebox.showinfo("Sucesso", resposta.get("mensagem", "Professor atualizado!")); self.carregar_professores()
        self.id_item_para_editar = None 

    def salvar_edicao_disciplina(self, dados):
        try: dados['carga_horaria'] = int(dados['carga_horaria'])
        except ValueError: messagebox.showerror("Erro de Formato", "Carga horária deve ser um número."); return
        resposta = api_client.editar_disciplina(self.id_item_para_editar, dados)
        if "erro" in resposta: messagebox.showerror("Erro ao Editar", resposta["erro"])
        else: messagebox.showinfo("Sucesso", resposta.get("mensagem", "Disciplina atualizada!")); self.carregar_disciplinas()
        self.id_item_para_editar = None 

    def salvar_edicao_turma(self, dados):
        try:
            dados['id_disciplina'] = int(dados['id_disciplina']); dados['id_professor'] = int(dados['id_professor'])
        except ValueError: messagebox.showerror("Erro de Formato", "IDs devem ser números."); return
        resposta = api_client.editar_turma(self.id_item_para_editar, dados)
        if "erro" in resposta: messagebox.showerror("Erro ao Editar", resposta["erro"])
        else: messagebox.showinfo("Sucesso", resposta.get("mensagem", "Turma atualizada!")); self.carregar_turmas()
        self.id_item_para_editar = None

# === CLASSE DE LOGIN (ATUALIZADA) ===
class AppLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cliente Desktop - Sistema Acadêmico")
        self.geometry("300x200")

        tk.Label(self, text="Email:").pack(pady=5)
        self.entry_email = tk.Entry(self, width=30)
        self.entry_email.pack()
        self.entry_email.insert(0, "admin@sistema.com")

        tk.Label(self, text="Senha:").pack(pady=5)
        self.entry_senha = tk.Entry(self, width=30, show="*")
        self.entry_senha.pack()
        self.entry_senha.insert(0, "admin123")

        self.btn_login = tk.Button(
            self, text="Login", command=self.fazer_login)
        self.btn_login.pack(pady=20)

    def fazer_login(self):
        email = self.entry_email.get()
        senha = self.entry_senha.get()
        if not email or not senha:
            messagebox.showerror("Erro", "Preencha email e senha.")
            return

        print(f"Tentando login como {email}...")
        resposta = api_client.tentar_login(email, senha)
        print(f"Resposta do servidor: {resposta}")

        if "erro" in resposta:
            messagebox.showerror("Falha no Login", resposta["erro"])
        elif "usuario" in resposta:
            self.abrir_painel_principal(resposta["usuario"])

    def abrir_painel_principal(self, usuario):
        self.withdraw()
        painel = None

        tipo = usuario.get('tipo')

        if tipo == 'D':  # Admin
            painel = AdminPanel(self, usuario)
        elif tipo == 'P':  # Professor
            if 'id_professor' not in usuario:
                messagebox.showerror(
                    "Erro de Login", "Conta de Professor incompleta (sem id_professor).")
                self.deiconify()
                return
            painel = ProfessorPanel(self, usuario)
        elif tipo == 'A':  # Aluno
            if 'id_aluno' not in usuario:
                messagebox.showerror(
                    "Erro de Login", "Conta de Aluno incompleta (sem id_aluno).")
                self.deiconify()
                return
            painel = AlunoPanel(self, usuario)
        else:
            messagebox.showerror("Erro", "Tipo de usuário desconhecido.")
            self.deiconify()
            return

        painel.protocol("WM_DELETE_WINDOW", self.on_painel_fechado)

    def on_painel_fechado(self):
        self.deiconify()


if __name__ == "__main__":
    app = AppLogin()
    app.mainloop()
