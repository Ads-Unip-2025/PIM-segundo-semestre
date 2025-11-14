class Atividade:
    def __init__(self, id_atividade, id_turma, titulo, descricao, data_postagem, data_entrega, peso, caminho_anexo=None):
        self.id_atividade = int(id_atividade)
        self.id_turma = int(id_turma)
        self.titulo = titulo
        self.descricao = descricao
        self.data_postagem = data_postagem
        self.data_entrega = data_entrega
        self.peso = float(peso)
        self.caminho_anexo = caminho_anexo

    def to_dict(self):
        data = self.__dict__
        return data


class EntregaAtividade:
    def __init__(self, id_entrega, id_atividade, id_aluno, arquivo, data_envio, status):
        self.id_entrega = int(id_entrega)
        self.id_atividade = int(id_atividade)
        self.id_aluno = int(id_aluno)
        self.arquivo = arquivo  # Caminho ou link
        self.data_envio = data_envio
        self.status = status  # Enviado, Corrigido

    def to_dict(self):
        return self.__dict__
