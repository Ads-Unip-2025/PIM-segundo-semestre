class Disciplina:
    def __init__(self, id_disciplina, nome, descricao, carga_horaria):
        self.id_disciplina = int(id_disciplina)
        self.nome = nome
        self.descricao = descricao
        self.carga_horaria = int(carga_horaria)

    def __repr__(self):
        return f"<Disciplina {self.nome}>"

    def to_dict(self):
        return self.__dict__
