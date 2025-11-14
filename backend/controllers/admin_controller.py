import datetime
from backend.persistence import data_manager, c_bridge
from backend.persistence.data_manager import _build_csv_line
from backend.models.pessoa import Pessoa
from backend.models.aluno import Aluno
from backend.models.professor import Professor
from backend.models.disciplina import Disciplina
from backend.models.turma import Turma
from backend.models.matricula import Matricula

# ---
# --- GERENCIAMENTO (POST)
# ---
def criar_novo_aluno(nome, email, senha, ra, curso):
    try:
        hash_senha = c_bridge.hash_senha_c(senha)
        if not hash_senha: return (False, "Erro ao gerar hash da senha.", None)

        id_pessoa = data_manager.get_next_id("pessoas")
        id_aluno = data_manager.get_next_id("alunos")

        linha_pessoa = _build_csv_line([id_pessoa, nome, email, hash_senha, 'A', 'true'])
        linha_aluno = _build_csv_line([id_aluno, id_pessoa, ra, curso])

        if not c_bridge.salvar_linha_c("pessoas.csv", linha_pessoa):
            return (False, "Erro ao salvar pessoa no disco.", None)
        if not c_bridge.salvar_linha_c("alunos.csv", linha_aluno):
            return (False, "Erro ao salvar aluno no disco.", None)

        pessoa_obj = Pessoa(id_pessoa, nome, email, hash_senha, 'A', True)
        aluno_obj = Aluno(pessoa_obj, id_aluno, ra, curso)
        aluno_obj.ativo = True # Sincroniza estado
        
        data_manager.add_pessoa_to_memory(pessoa_obj)
        data_manager.add_aluno_to_memory(aluno_obj)

        return (True, "Aluno criado com sucesso.", aluno_obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def criar_novo_professor(nome, email, senha, formacao):
    try:
        hash_senha = c_bridge.hash_senha_c(senha)
        if not hash_senha: return (False, "Erro ao gerar hash da senha.", None)

        id_pessoa = data_manager.get_next_id("pessoas")
        id_professor = data_manager.get_next_id("professores")

        linha_pessoa = _build_csv_line([id_pessoa, nome, email, hash_senha, 'P', 'true'])
        linha_professor = _build_csv_line([id_professor, id_pessoa, formacao])

        if not c_bridge.salvar_linha_c("pessoas.csv", linha_pessoa):
            return (False, "Erro ao salvar pessoa no disco.", None)
        if not c_bridge.salvar_linha_c("professores.csv", linha_professor):
            return (False, "Erro ao salvar professor no disco.", None)

        pessoa_obj = Pessoa(id_pessoa, nome, email, hash_senha, 'P', True)
        prof_obj = Professor(pessoa_obj, id_professor, formacao)
        prof_obj.ativo = True # Sincroniza estado
        
        data_manager.add_pessoa_to_memory(pessoa_obj)
        data_manager.add_professor_to_memory(prof_obj)

        return (True, "Professor criado com sucesso.", prof_obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def criar_nova_disciplina(nome, descricao, carga_horaria):
    try:
        id_disciplina = data_manager.get_next_id("disciplinas")
        linha_csv = _build_csv_line([id_disciplina, nome, descricao, carga_horaria])
        if not c_bridge.salvar_linha_c("disciplinas.csv", linha_csv):
            return (False, "Erro ao salvar disciplina no disco.", None)
        disc_obj = Disciplina(id_disciplina, nome, descricao, carga_horaria)
        data_manager.add_disciplina_to_memory(disc_obj)
        return (True, "Disciplina criada com sucesso.", disc_obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def criar_nova_turma(codigo, semestre, id_disciplina, id_professor):
    try:
        id_turma = data_manager.get_next_id("turmas")
        linha_csv = _build_csv_line([id_turma, codigo, semestre, id_disciplina, id_professor])
        if not c_bridge.salvar_linha_c("turmas.csv", linha_csv):
            return (False, "Erro ao salvar turma no disco.", None)
        turma_obj = Turma(id_turma, codigo, semestre, id_disciplina, id_professor)
        data_manager.add_turma_to_memory(turma_obj)
        return (True, "Turma criada com sucesso.", turma_obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def matricular_aluno(id_aluno, id_turma):
    try:
        id_matricula = data_manager.get_next_id("matriculas")
        data_hoje = datetime.date.today().isoformat()
        status = "Ativa"
        linha_csv = _build_csv_line([id_matricula, id_aluno, id_turma, data_hoje, status])
        if not c_bridge.salvar_linha_c("matriculas.csv", linha_csv):
            return (False, "Erro ao salvar matrícula no disco.", None)
        mat_obj = Matricula(id_matricula, id_aluno, id_turma, data_hoje, status)
        data_manager.add_matricula_to_memory(mat_obj)
        return (True, "Aluno matriculado com sucesso.", mat_obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

# ---
# --- GERENCIAMENTO (PUT)
# ---

def editar_aluno(id_aluno, novos_dados):
    """Edita os dados de um aluno (Pessoa e Aluno)."""
    try:
        id_aluno = int(id_aluno)
        aluno = data_manager.DB["alunos"].get(id_aluno)
        if not aluno: return (False, "Aluno não encontrado.", None)
        pessoa = data_manager.DB["pessoas"].get(aluno.id_pessoa)
        if not pessoa: return (False, "Objeto Pessoa do aluno não encontrado.", None)

        # 1. Atualiza os dados na memória (ambos os objetos)
        novo_nome = novos_dados.get('nome', pessoa.nome)
        novo_email = novos_dados.get('email', pessoa.email)
        pessoa.nome = novo_nome
        aluno.nome = novo_nome 
        pessoa.email = novo_email
        aluno.email = novo_email 

        aluno.ra = novos_dados.get('ra', aluno.ra)
        aluno.curso = novos_dados.get('curso', aluno.curso)
        
        nova_senha = novos_dados.get('senha')
        if nova_senha: 
            pessoa.senha_hash = c_bridge.hash_senha_c(nova_senha)
            if not pessoa.senha_hash:
                return (False, "Erro ao gerar hash da nova senha.", None)

        # 2. Reescreve os arquivos CSV usando Python
        if not data_manager.rewrite_pessoas_csv():
            return (False, "Erro ao reescrever pessoas.csv.", None)
        if not data_manager.rewrite_alunos_csv():
            return (False, "Erro ao reescrever alunos.csv.", None)

        return (True, "Aluno atualizado com sucesso.", aluno.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def editar_professor(id_professor, novos_dados):
    try:
        id_professor = int(id_professor)
        professor = data_manager.DB["professores"].get(id_professor)
        if not professor: return (False, "Professor não encontrado.", None)
        pessoa = data_manager.DB["pessoas"].get(professor.id_pessoa)
        if not pessoa: return (False, "Objeto Pessoa do professor não encontrado.", None)

        # Atualiza dados (Pessoa)
        novo_nome = novos_dados.get('nome', pessoa.nome)
        novo_email = novos_dados.get('email', pessoa.email)
        pessoa.nome = novo_nome
        professor.nome = novo_nome # Sincroniza cache
        pessoa.email = novo_email
        professor.email = novo_email # Sincroniza cache
        # Atualiza dados (Professor)
        professor.formacao = novos_dados.get('formacao', professor.formacao)
        
        nova_senha = novos_dados.get('senha')
        if nova_senha:
            pessoa.senha_hash = c_bridge.hash_senha_c(nova_senha)
            if not pessoa.senha_hash:
                return (False, "Erro ao gerar hash da nova senha.", None)

        if not data_manager.rewrite_pessoas_csv():
            return (False, "Erro ao reescrever pessoas.csv.", None)
        if not data_manager.rewrite_professores_csv():
            return (False, "Erro ao reescrever professores.csv.", None)

        return (True, "Professor atualizado com sucesso.", professor.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def editar_disciplina(id_disciplina, novos_dados):
    try:
        id_disciplina = int(id_disciplina)
        disciplina = data_manager.DB["disciplinas"].get(id_disciplina)
        if not disciplina: return (False, "Disciplina não encontrada.", None)

        # Atualiza dados (Disciplina)
        disciplina.nome = novos_dados.get('nome', disciplina.nome)
        disciplina.descricao = novos_dados.get('descricao', disciplina.descricao)
        disciplina.carga_horaria = int(novos_dados.get('carga_horaria', disciplina.carga_horaria))
        
        if not data_manager.rewrite_disciplinas_csv():
            return (False, "Erro ao reescrever disciplinas.csv.", None)

        return (True, "Disciplina atualizada com sucesso.", disciplina.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def editar_turma(id_turma, novos_dados):
    try:
        id_turma = int(id_turma)
        turma = data_manager.DB["turmas"].get(id_turma)
        if not turma: return (False, "Turma não encontrada.", None)

        # Atualiza dados (Turma)
        turma.codigo = novos_dados.get('codigo', turma.codigo)
        turma.semestre = novos_dados.get('semestre', turma.semestre)
        turma.id_disciplina = int(novos_dados.get('id_disciplina', turma.id_disciplina))
        turma.id_professor = int(novos_dados.get('id_professor', turma.id_professor))
        
        if not data_manager.rewrite_turmas_csv():
            return (False, "Erro ao reescrever turmas.csv.", None)

        return (True, "Turma atualizada com sucesso.", turma.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

# ---
# --- GERENCIAMENTO (DELETE)
# ---

def excluir_aluno(id_aluno):
    """Exclusão lógica de um aluno (Soft Delete) usando Python."""
    try:
        id_aluno = int(id_aluno)
        aluno = data_manager.DB["alunos"].get(id_aluno)
        if not aluno: return (False, "Aluno não encontrado.", None)
        
        pessoa = data_manager.DB["pessoas"].get(aluno.id_pessoa)
        if not pessoa: return (False, "Objeto Pessoa do aluno não encontrado.", None)

        # 1. Seta AMBOS os objetos como inativos
        pessoa.ativo = False
        aluno.ativo = False 
        
        # 2. Seta as Matrículas como inativas
        for matricula in data_manager.DB["matriculas"].values():
            if matricula.id_aluno == aluno.id_aluno:
                matricula.status = "Inativa"
        
        # 3. Reescreve os arquivos CSV usando Python
        if not data_manager.rewrite_pessoas_csv():
            return (False, "Erro ao reescrever pessoas.csv.", None)
        if not data_manager.rewrite_matriculas_csv():
            return (False, "Erro ao reescrever matriculas.csv.", None)

        return (True, "Aluno excluído (inativado) com sucesso.", None)
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def excluir_professor(id_professor):
    try:
        id_professor = int(id_professor)
        professor = data_manager.DB["professores"].get(id_professor)
        if not professor: return (False, "Professor não encontrado.", None)
        pessoa = data_manager.DB["pessoas"].get(professor.id_pessoa)
        if not pessoa: return (False, "Objeto Pessoa do professor não encontrado.", None)

        turmas_associadas = [t for t in data_manager.DB["turmas"].values() if t.id_professor == id_professor]
        if turmas_associadas:
            return (False, "Erro: Professor está vinculado a uma ou mais turmas. Reatribua as turmas antes de excluir.", None)

        pessoa.ativo = False
        professor.ativo = False
        
        if not data_manager.rewrite_pessoas_csv():
            return (False, "Erro ao reescrever pessoas.csv.", None)

        return (True, "Professor excluído (inativado) com sucesso.", None)
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def excluir_disciplina(id_disciplina):
    try:
        id_disciplina = int(id_disciplina)
        if id_disciplina not in data_manager.DB["disciplinas"]:
            return (False, "Disciplina não encontrada.", None)

        turmas_associadas = [t for t in data_manager.DB["turmas"].values() if t.id_disciplina == id_disciplina]
        if turmas_associadas:
            return (False, "Erro: Disciplina está vinculada a uma ou mais turmas.", None)
            
        data_manager.DB["disciplinas"].pop(id_disciplina)
        
        if not data_manager.rewrite_disciplinas_csv():
            return (False, "Erro ao reescrever disciplinas.csv.", None)

        return (True, "Disciplina excluída com sucesso.", None)
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def excluir_turma(id_turma):
    try:
        id_turma = int(id_turma)
        if id_turma not in data_manager.DB["turmas"]:
            return (False, "Turma não encontrada.", None)

        if any(m.id_turma == id_turma for m in data_manager.DB["matriculas"].values()):
            return (False, "Erro: Turma possui alunos matriculados.", None)
        if any(a.id_turma == id_turma for a in data_manager.DB["atividades"].values()):
            return (False, "Erro: Turma possui atividades cadastradas.", None)
        if any(n.id_turma == id_turma for n in data_manager.DB["notas"].values()):
            return (False, "Erro: Turma possui notas lançadas.", None)
        if any(f.id_turma == id_turma for f in data_manager.DB["faltas"].values()):
            return (False, "Erro: Turma possui faltas registradas.", None)

        data_manager.DB["turmas"].pop(id_turma)
        
        if not data_manager.rewrite_turmas_csv():
            return (False, "Erro ao reescrever turmas.csv.", None)

        return (True, "Turma excluída com sucesso.", None)
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

def desmatricular_aluno(id_aluno, id_turma):
    try:
        id_aluno = int(id_aluno)
        id_turma = int(id_turma)
        
        matricula_para_excluir = None
        for matricula in data_manager.DB["matriculas"].values():
            if matricula.id_aluno == id_aluno and matricula.id_turma == id_turma:
                matricula_para_excluir = matricula
                break
        
        if not matricula_para_excluir:
            return (False, "Matrícula não encontrada.", None)

        data_manager.DB["matriculas"].pop(matricula_para_excluir.id_matricula)
        
        if not data_manager.rewrite_matriculas_csv():
            return (False, "Erro ao reescrever matriculas.csv.", None)

        return (True, "Aluno desmatriculado com sucesso.", None)
    except Exception as e:
        return (False, f"Erro interno: {e}", None)