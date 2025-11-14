import datetime


class Matricula:
    def __init__(self, id_matricula, id_aluno, id_turma, data_matricula, status):
        self.id_matricula = int(id_matricula)
        self.id_aluno = int(id_aluno)  # FK para Aluno
        self.id_turma = int(id_turma)  # FK para Turma
        self.data_matricula = data_matricula
        self.status = status  # Ativa, Trancada, Concluída

    def __repr__(self):
        return f"<Matricula {self.id_aluno} em {self.id_turma}>"

    def to_dict(self):
        return {
            "id_matricula": self.id_matricula,
            "id_aluno": self.id_aluno,
            "id_turma": self.id_turma,
            "data_matricula": self.data_matricula,
            "status": self.status
        }
