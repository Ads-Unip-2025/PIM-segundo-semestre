import datetime
from backend.persistence import data_manager, c_bridge
from backend.models.atividade import Atividade
from backend.models.avaliacao import Nota, Falta

# --- INÍCIO DA CORREÇÃO ---


def _csv_safe(field):
    """Garante que o campo seja seguro para CSV. Se contiver vírgula,
    quebra de linha ou aspas, envolve em aspas duplas."""
    field_str = str(field)
    if ',' in field_str or '"' in field_str or '\n' in field_str:
        # "Escapa" aspas duplas internas (substituindo por duas aspas duplas)
        escaped_field = field_str.replace('"', '""')
        return f'"{escaped_field}"'
    return field_str


def _build_csv_line(data_list):
    """Cria uma linha CSV sanitizada."""
    return ",".join(_csv_safe(field) for field in data_list)
# --- FIM DA CORREÇÃO ---


# Em /backend/controllers/prof_controller.py

def criar_atividade(id_turma, titulo, descricao, data_entrega, peso, caminho_anexo=""): # Adicionado
    """Cria uma nova Atividade (RF10)"""
    try:
        id_atividade = data_manager.get_next_id("atividades")
        data_postagem = datetime.date.today().isoformat()
        
        # id_atividade,id_turma,titulo,descricao,data_postagem,data_entrega,peso,caminho_anexo
        linha_csv = _build_csv_line([id_atividade, id_turma, titulo, descricao, data_postagem, data_entrega, peso, caminho_anexo]) # Adicionado
        
        if not c_bridge.salvar_linha_c("atividades.csv", linha_csv):
            return (False, "Erro ao salvar atividade no disco.", None)
        
        obj = Atividade(id_atividade, id_turma, titulo, descricao, data_postagem, data_entrega, peso, caminho_anexo) # Adicionado
        data_manager.add_to_memory("atividades", obj)
        
        return (True, "Atividade criada com sucesso.", obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)

# Em /backend/controllers/prof_controller.py


def lancar_nota(id_aluno, id_turma, id_atividade, valor, id_professor):
    """Lança uma nova Nota (RF08)"""
    try:
        id_nota = data_manager.get_next_id("notas")
        data_lancamento = datetime.date.today().isoformat()

        # --- INÍCIO DA CORREÇÃO ---
        # 'id_atividade' virá como string vazia ("") se o campo for
        # deixado em branco, ou None se a chave não existir.

        id_ativ_para_obj = None
        id_ativ_para_csv = ""  # Salva como string vazia no CSV

        if id_atividade is not None and str(id_atividade).strip() != "":
            id_ativ_para_obj = int(id_atividade)
            id_ativ_para_csv = id_ativ_para_obj
        # --- FIM DA CORREÇÃO ---

        # id_nota,id_aluno,id_turma,id_atividade,valor,data_lancamento,id_professor
        linha_csv = _build_csv_line(
            [id_nota, id_aluno, id_turma, id_ativ_para_csv, valor, data_lancamento, id_professor])

        if not c_bridge.salvar_linha_c("notas.csv", linha_csv):
            return (False, "Erro ao salvar nota no disco.", None)

        # Passa o 'id_ativ_para_obj' (que é None ou int) para o construtor
        obj = Nota(id_nota, id_aluno, id_turma, id_ativ_para_obj,
                   valor, data_lancamento, id_professor)
        data_manager.add_to_memory("notas", obj)

        return (True, "Nota lançada com sucesso.", obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)


def registrar_falta(id_aluno, id_turma, data_aula):
    """Registra uma Falta (RF09)"""
    try:
        id_falta = data_manager.get_next_id("faltas")
        justificada = False  # Padrão

        # id_falta,id_aluno,id_turma,data_aula,justificada
        linha_csv = _build_csv_line(
            [id_falta, id_aluno, id_turma, data_aula, justificada])

        if not c_bridge.salvar_linha_c("faltas.csv", linha_csv):
            return (False, "Erro ao salvar falta no disco.", None)

        obj = Falta(id_falta, id_aluno, id_turma, data_aula, justificada)
        data_manager.add_to_memory("faltas", obj)

        return (True, "Falta registrada com sucesso.", obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)
# Em /backend/controllers/prof_controller.py


def consultar_detalhes_aluno(id_aluno, id_turma):
    """Busca detalhes (notas/faltas) de um aluno em uma turma."""
    try:
        # Validação (RG03): Este professor pode ver esta turma?
        turma = data_manager.DB["turmas"].get(id_turma)
        # (Falta a lógica de verificar se o prof da turma é o prof logado)
        # (Vamos assumir que sim por enquanto)

        detalhes = data_manager.get_detalhes_aluno_na_turma(id_aluno, id_turma)
        return (True, "Detalhes carregados", detalhes)
    except Exception as e:
        return (False, f"Erro interno: {e}", None)
