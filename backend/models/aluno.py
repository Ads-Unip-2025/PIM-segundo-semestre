from backend.models.pessoa import Pessoa


class Aluno(Pessoa):
    def __init__(self, pessoa: Pessoa, id_aluno, ra, curso):
        # Chama o construtor da classe pai (Pessoa)
        super().__init__(
            pessoa.id_pessoa,
            pessoa.nome,
            pessoa.email,
            pessoa.senha_hash,
            pessoa.tipo,
            pessoa.ativo
        )
        self.id_aluno = int(id_aluno)
        self.ra = ra
        self.curso = curso

    def __repr__(self):
        return f"<Aluno {self.nome} (RA: {self.ra})>"

    # --- INÍCIO DA CORREÇÃO ---
    def to_dict(self):
        """Retorna um dicionário com os dados do Aluno e da Pessoa."""
        return {
            "id_pessoa": self.id_pessoa,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
            "ativo": self.ativo,
            "id_aluno": self.id_aluno,
            "ra": self.ra,
            "curso": self.curso
        }
    # --- FIM DA CORREÇÃO ---
