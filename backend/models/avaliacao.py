# Em /backend/models/avaliacao.py

class Nota:
    def __init__(self, id_nota, id_aluno, id_turma, id_atividade, valor, data_lancamento, id_professor):
        self.id_nota = int(id_nota)
        self.id_aluno = int(id_aluno)
        self.id_turma = int(id_turma)

        # --- INÍCIO DA CORREÇÃO ---
        # Garante que Nulo, Vazio, ou a string "None" sejam tratados
        if id_atividade is None or id_atividade == "" or str(id_atividade).lower() == "none":
            self.id_atividade = None  # Armazena como None
        else:
            # Se não for nulo, converte para int
            self.id_atividade = int(id_atividade)
        # --- FIM DA CORREÇÃO ---

        self.valor = float(valor)
        self.data_lancamento = data_lancamento
        self.id_professor = int(id_professor)

    def to_dict(self):
        """Retorna um dicionário com os dados da Nota."""
        # Garante que o to_dict (que vai para o JSON) esteja correto
        return {
            "id_nota": self.id_nota,
            "id_aluno": self.id_aluno,
            "id_turma": self.id_turma,
            "id_atividade": self.id_atividade,
            "valor": self.valor,
            "data_lancamento": self.data_lancamento,
            "id_professor": self.id_professor
        }


class Falta:
    def __init__(self, id_falta, id_aluno, id_turma, data_aula, justificada):
        self.id_falta = int(id_falta)
        self.id_aluno = int(id_aluno)
        self.id_turma = int(id_turma)
        self.data_aula = data_aula
        self.justificada = bool(justificada)

    def to_dict(self):
        return self.__dict__
