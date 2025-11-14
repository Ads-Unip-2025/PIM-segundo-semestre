import csv
import json
import os
from backend.models.pessoa import Pessoa
from backend.models.aluno import Aluno
from backend.models.professor import Professor
from backend.models.disciplina import Disciplina
from backend.models.turma import Turma
from backend.models.matricula import Matricula
from backend.models.atividade import Atividade, EntregaAtividade
from backend.models.avaliacao import Nota, Falta

# Caminho para a pasta de dados
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

# "Banco de dados" em memória
DB = {
    "config": {},
    "pessoas": {},
    "alunos": {},
    "professores": {},
    "disciplinas": {},
    "turmas": {},
    "matriculas": {},
    "atividades": {},
    "entregas": {},
    "notas": {},
    "faltas": {}
}

# ---
# --- FUNÇÕES DE CSV (Leitura e Escrita)
# ---
def _csv_safe(field):
    field_str = str(field)
    if field_str is None: return ""
    if ',' in field_str or '"' in field_str or '\n' in field_str:
        escaped_field = field_str.replace('"', '""')
        return f'"{escaped_field}"'
    return field_str

def _build_csv_line(data_list):
    return ",".join(_csv_safe(field) for field in data_list)

def _rewrite_csv(filename, header, data_rows):
    """Função genérica para reescrever qualquer arquivo CSV."""
    print(f"Reescrevendo {filename}...")
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            f.write(",".join(header) + "\n") # Escreve o cabeçalho
            for row in data_rows:
                f.write(row + "\n")
        return True
    except Exception as e:
        print(f"Erro ao reescrever {filename}: {e}")
        return False

# Funções de reescrita
def rewrite_pessoas_csv():
    header = ["id_pessoa", "nome", "email", "senha_hash", "tipo", "ativo"]
    rows = []
    for p in DB["pessoas"].values():
        ativo_str = str(p.ativo).lower()
        rows.append(_build_csv_line([p.id_pessoa, p.nome, p.email, p.senha_hash, p.tipo, ativo_str]))
    return _rewrite_csv("pessoas.csv", header, rows)

def rewrite_alunos_csv():
    header = ["id_aluno", "id_pessoa_fk", "ra", "curso"]
    rows = []
    for a in DB["alunos"].values():
        rows.append(_build_csv_line([a.id_aluno, a.id_pessoa, a.ra, a.curso]))
    return _rewrite_csv("alunos.csv", header, rows)

def rewrite_professores_csv():
    header = ["id_professor", "id_pessoa_fk", "formacao"]
    rows = []
    for p in DB["professores"].values():
        rows.append(_build_csv_line([p.id_professor, p.id_pessoa, p.formacao]))
    return _rewrite_csv("professores.csv", header, rows)

def rewrite_disciplinas_csv():
    header = ["id_disciplina", "nome", "descricao", "carga_horaria"]
    rows = []
    for d in DB["disciplinas"].values():
        rows.append(_build_csv_line([d.id_disciplina, d.nome, d.descricao, d.carga_horaria]))
    return _rewrite_csv("disciplinas.csv", header, rows)

def rewrite_turmas_csv():
    header = ["id_turma", "codigo", "semestre", "id_disciplina", "id_professor"]
    rows = []
    for t in DB["turmas"].values():
        rows.append(_build_csv_line([t.id_turma, t.codigo, t.semestre, t.id_disciplina, t.id_professor]))
    return _rewrite_csv("turmas.csv", header, rows)

def rewrite_matriculas_csv():
    header = ["id_matricula", "id_aluno", "id_turma", "data_matricula", "status"]
    rows = []
    for m in DB["matriculas"].values():
        rows.append(_build_csv_line([m.id_matricula, m.id_aluno, m.id_turma, m.data_matricula, m.status]))
    return _rewrite_csv("matriculas.csv", header, rows)

def _load_csv(nome_arquivo):
    """Função auxiliar para ler qualquer CSV usando DictReader."""
    path = os.path.join(DATA_DIR, nome_arquivo)
    data = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Aviso: Arquivo {nome_arquivo} não encontrado. Iniciando vazio.")
    except Exception as e:
        print(f"Erro ao ler {nome_arquivo}: {e}")
    return data

# ---
# --- FUNÇÕES DE CARREGAMENTO (INIT)
# ---
def load_config():
    path = os.path.join(DATA_DIR, 'configuracao.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            DB["config"] = json.load(f)
            print("Configuração carregada.")
    except Exception as e:
        print(f"Erro ao carregar configuracao.json: {e}")

def load_all_data():
    print("Carregando todos os dados...")
    load_config()
    
    # 1. Pessoas
    for p_data in _load_csv('pessoas.csv'):
        p_data['ativo'] = (p_data['ativo'].lower() == 'true')
        pessoa = Pessoa(**p_data)
        DB["pessoas"][pessoa.id_pessoa] = pessoa

    # 2. Professores
    for p_data in _load_csv('professores.csv'):
        id_pessoa_fk = int(p_data.pop('id_pessoa_fk'))
        pessoa_base = DB["pessoas"].get(id_pessoa_fk)
        if pessoa_base:
            professor = Professor(pessoa=pessoa_base, **p_data)
            professor.ativo = pessoa_base.ativo
            DB["professores"][professor.id_professor] = professor
            
    # 3. Alunos
    for a_data in _load_csv('alunos.csv'):
        id_pessoa_fk = int(a_data.pop('id_pessoa_fk'))
        pessoa_base = DB["pessoas"].get(id_pessoa_fk)
        if pessoa_base:
            aluno = Aluno(pessoa=pessoa_base, **a_data)
            aluno.ativo = pessoa_base.ativo
            DB["alunos"][aluno.id_aluno] = aluno
    
    # 4. Disciplinas
    for d_data in _load_csv('disciplinas.csv'):
        disciplina = Disciplina(**d_data)
        DB["disciplinas"][disciplina.id_disciplina] = disciplina

    # 5. Turmas
    for t_data in _load_csv('turmas.csv'):
        turma = Turma(**t_data)
        DB["turmas"][turma.id_turma] = turma

    # 6. Matrículas
    for m_data in _load_csv('matriculas.csv'):
        matricula = Matricula(**m_data)
        DB["matriculas"][matricula.id_matricula] = matricula
        
    # 7. Atividades
    for data in _load_csv('atividades.csv'):
        obj = Atividade(**data)
        DB["atividades"][obj.id_atividade] = obj
        
    # 8. Entregas
    for data in _load_csv('entregas.csv'):
        obj = EntregaAtividade(**data)
        DB["entregas"][obj.id_entrega] = obj
        
    # 9. Notas
    for data in _load_csv('notas.csv'):
        obj = Nota(**data)
        DB["notas"][obj.id_nota] = obj
        
    # 10. Faltas
    for data in _load_csv('faltas.csv'):
        data['justificada'] = (data['justificada'].lower() == 'true')
        obj = Falta(**data)
        DB["faltas"][obj.id_falta] = obj

    print(f"Carregamento concluído: {len(DB['pessoas'])} pessoas, {len(DB['alunos'])} alunos, {len(DB['notas'])} notas.")

# ---
# --- FUNÇÕES DE BUSCA (GET)
# ---
def get_config():
    return DB["config"]

def get_pessoa_by_email(email):
    for pessoa in DB["pessoas"].values():
        if pessoa.email == email:
            return pessoa
    return None

def get_aluno_by_pessoa_id(id_pessoa):
    for aluno in DB["alunos"].values():
        if aluno.id_pessoa == id_pessoa:
            return aluno
    return None

def get_professor_by_pessoa_id(id_pessoa):
    for professor in DB["professores"].values():
        if professor.id_pessoa == id_pessoa:
            return professor
    return None

def get_next_id(db_key):
    if not DB[db_key]:
        return 1
    max_id = max(DB[db_key].keys())
    return max_id + 1

# Funções GET By ID (para Edição)
def get_aluno_by_id(id_aluno):
    aluno = DB["alunos"].get(int(id_aluno))
    if aluno and aluno.ativo:
        return aluno
    return None

def get_professor_by_id(id_professor):
    prof = DB["professores"].get(int(id_professor))
    if prof and prof.ativo:
        return prof
    return None

def get_disciplina_by_id(id_disciplina):
    return DB["disciplinas"].get(int(id_disciplina))

def get_turma_by_id(id_turma):
    return DB["turmas"].get(int(id_turma))

# Funções GET All (Listagem)
def get_all_alunos():
    return [aluno.to_dict() for aluno in DB["alunos"].values() if aluno.ativo]
def get_all_professores():
    return [prof.to_dict() for prof in DB["professores"].values() if prof.ativo]
def get_all_disciplinas():
    return [disc.to_dict() for disc in DB["disciplinas"].values()]
def get_all_turmas():
    lista_turmas_enriquecida = []
    for turma in DB["turmas"].values():
        turma_dict = turma.to_dict()
        alunos_na_turma = []
        for matricula in DB["matriculas"].values():
            if matricula.id_turma == turma.id_turma:
                aluno = DB["alunos"].get(matricula.id_aluno)
                if aluno:
                    alunos_na_turma.append({
                        "id_aluno": aluno.id_aluno,
                        "nome": aluno.nome,
                        "ra": aluno.ra
                    })
        turma_dict["alunos_matriculados"] = alunos_na_turma
        lista_turmas_enriquecida.append(turma_dict)
    return lista_turmas_enriquecida

# Funções (ÉPICO 4)
def get_turmas_by_professor(id_professor):
    turmas_prof = []
    id_professor = int(id_professor)
    for turma in DB["turmas"].values():
        if turma.id_professor == id_professor:
            disciplina = DB["disciplinas"].get(turma.id_disciplina)
            turma_info = turma.to_dict()
            turma_info["nome_disciplina"] = disciplina.nome if disciplina else "N/A"
            
            atividades_da_turma = []
            for atividade in DB["atividades"].values():
                if atividade.id_turma == turma.id_turma:
                    atividades_da_turma.append(atividade.to_dict())
            turma_info["atividades"] = atividades_da_turma
            
            alunos_na_turma = []
            for matricula in DB["matriculas"].values():
                if matricula.id_turma == turma.id_turma:
                    aluno = DB["alunos"].get(matricula.id_aluno)
                    if aluno and aluno.ativo: # Só mostra alunos ativos na turma
                        alunos_na_turma.append({
                            "id_aluno": aluno.id_aluno,
                            "nome": aluno.nome,
                            "ra": aluno.ra
                        })
            turma_info["alunos_matriculados"] = alunos_na_turma
            
            turmas_prof.append(turma_info)
    return turmas_prof
    
def get_atividades_by_aluno(id_aluno):
    atividades_aluno = []
    id_aluno = int(id_aluno)
    matriculas_aluno = [m for m in DB["matriculas"].values() if m.id_aluno == id_aluno and m.status == "Ativa"]
    ids_turmas_aluno = {m.id_turma for m in matriculas_aluno}
    
    for atividade in DB["atividades"].values():
        if atividade.id_turma in ids_turmas_aluno:
            atividades_aluno.append(atividade.to_dict())
    return atividades_aluno

def get_boletim_aluno(id_aluno):
    boletim = []
    id_aluno = int(id_aluno)
    config = get_config()
    media_minima = config.get("media_minima", 7.0)
    limite_faltas_pct = config.get("limite_faltas", 25)

    matriculas_aluno = [m for m in DB["matriculas"].values() if m.id_aluno == id_aluno and m.status == "Ativa"]

    for matricula in matriculas_aluno:
        turma = DB["turmas"].get(matricula.id_turma)
        if not turma: continue
        disciplina = DB["disciplinas"].get(turma.id_disciplina)
        if not disciplina: continue
        
        notas_aluno_turma = [n for n in DB["notas"].values() if n.id_aluno == id_aluno and n.id_turma == turma.id_turma]
        media_final = 0.0
        if notas_aluno_turma:
            media_final = sum(n.valor for n in notas_aluno_turma) / len(notas_aluno_turma)
        
        faltas_aluno_turma = [f for f in DB["faltas"].values() if f.id_aluno == id_aluno and f.id_turma == turma.id_turma and not f.justificada]
        total_faltas = len(faltas_aluno_turma)
        pct_faltas = (total_faltas / disciplina.carga_horaria) * 100 if disciplina.carga_horaria > 0 else 0
        
        aprovado_nota = media_final >= media_minima
        aprovado_frequencia = pct_faltas <= limite_faltas_pct
        
        situacao = "Aprovado"
        if not aprovado_nota or not aprovado_frequencia:
            situacao = "Reprovado"
            if not aprovado_nota: situacao += " (Nota)"
            if not aprovado_frequencia: situacao += " (Frequência)"
        
        boletim.append({
            "nome_disciplina": disciplina.nome,
            "media_final": round(media_final, 2),
            "total_faltas": total_faltas,
            "pct_frequencia": round(100.0 - pct_faltas, 2),
            "situacao": situacao
        })
    return boletim
    
def get_detalhes_aluno_na_turma(id_aluno, id_turma):
    id_aluno = int(id_aluno)
    id_turma = int(id_turma)

    notas_obj = [n for n in DB["notas"].values() if n.id_aluno == id_aluno and n.id_turma == id_turma]
    notas_dict = []
    
    for nota in notas_obj:
        nota_data = nota.to_dict()
        id_ativ_nota = nota_data.get('id_atividade') # int ou None
        
        if id_ativ_nota is not None:
            ativ = DB["atividades"].get(id_ativ_nota) 
            nota_data['nome_atividade'] = ativ.titulo if ativ else f'ID Ativ. ({id_ativ_nota}) Nao Encontrado'
        else:
            nota_data['nome_atividade'] = 'Nota Avulsa'
        notas_dict.append(nota_data)
        
    faltas_dict = [f.to_dict() for f in DB["faltas"].values() if f.id_aluno == id_aluno and f.id_turma == id_turma]
    
    return {"notas": notas_dict, "faltas": faltas_dict}

# --- Funções de Adição (para POST) ---
def add_to_memory(db_key, obj):
    DB[db_key][obj.id_atividade if hasattr(obj, 'id_atividade') else
                obj.id_entrega if hasattr(obj, 'id_entrega') else
                obj.id_nota if hasattr(obj, 'id_nota') else
                obj.id_falta if hasattr(obj, 'id_falta') else
                obj.id_pessoa if hasattr(obj, 'id_pessoa') else
                obj.id_aluno if hasattr(obj, 'id_aluno') else
                obj.id_professor if hasattr(obj, 'id_professor') else
                obj.id_disciplina if hasattr(obj, 'id_disciplina') else
                obj.id_turma if hasattr(obj, 'id_turma') else
                obj.id_matricula] = obj

def add_pessoa_to_memory(pessoa_obj: Pessoa):
    DB["pessoas"][pessoa_obj.id_pessoa] = pessoa_obj
def add_aluno_to_memory(aluno_obj: Aluno):
    DB["alunos"][aluno_obj.id_aluno] = aluno_obj
def add_professor_to_memory(prof_obj: Professor):
    DB["professores"][prof_obj.id_professor] = prof_obj
def add_disciplina_to_memory(disc_obj: Disciplina):
    DB["disciplinas"][disc_obj.id_disciplina] = disc_obj
def add_turma_to_memory(turma_obj: Turma):
    DB["turmas"][turma_obj.id_turma] = turma_obj
def add_matricula_to_memory(mat_obj: Matricula):
    DB["matriculas"][mat_obj.id_matricula] = mat_obj