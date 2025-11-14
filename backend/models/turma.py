class Turma:
    def __init__(self, id_turma, codigo, semestre, id_disciplina, id_professor):
        self.id_turma = int(id_turma)
        self.codigo = codigo
        self.semestre = semestre
        self.id_disciplina = int(id_disciplina)  # FK para Disciplina
        self.id_professor = int(id_professor)  # FK para Professor

    def __repr__(self):
        return f"<Turma {self.codigo} ({self.semestre})>"

    def to_dict(self):
        return self.__dict__
