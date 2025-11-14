import datetime
from backend.persistence import data_manager, c_bridge
from backend.models.atividade import EntregaAtividade

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


def enviar_atividade(id_atividade, id_aluno, arquivo):
    """Envia uma Atividade (RF13)"""
    try:
        id_entrega = data_manager.get_next_id("entregas")
        data_envio = datetime.date.today().isoformat()
        status = "Enviado"

        # id_entrega,id_atividade,id_aluno,arquivo,data_envio,status
        linha_csv = _build_csv_line(
            [id_entrega, id_atividade, id_aluno, arquivo, data_envio, status])

        if not c_bridge.salvar_linha_c("entregas.csv", linha_csv):
            return (False, "Erro ao salvar entrega no disco.", None)

        obj = EntregaAtividade(id_entrega, id_atividade,
                               id_aluno, arquivo, data_envio, status)
        data_manager.add_to_memory("entregas", obj)

        return (True, "Atividade enviada com sucesso.", obj.to_dict())
    except Exception as e:
        return (False, f"Erro interno: {e}", None)


def consultar_boletim(id_aluno):
    """Consulta o boletim (RF11)"""
    try:
        boletim = data_manager.get_boletim_aluno(id_aluno)
        return (True, "Boletim gerado com sucesso.", boletim)
    except Exception as e:
        return (False, f"Erro interno: {e}", None)
