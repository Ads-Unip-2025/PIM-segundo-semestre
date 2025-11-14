from backend.models.pessoa import Pessoa


class Professor(Pessoa):
    def __init__(self, pessoa: Pessoa, id_professor, formacao):
        # Chama o construtor da classe pai (Pessoa)
        super().__init__(
            pessoa.id_pessoa,
            pessoa.nome,
            pessoa.email,
            pessoa.senha_hash,
            pessoa.tipo,
            pessoa.ativo
        )
        self.id_professor = int(id_professor)
        self.formacao = formacao

    def __repr__(self):
        return f"<Professor {self.nome} (Formação: {self.formacao})>"

    # --- INÍCIO DA CORREÇÃO ---
    def to_dict(self):
        """Retorna um dicionário com os dados do Professor e da Pessoa."""
        return {
            "id_pessoa": self.id_pessoa,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
            "ativo": self.ativo,
            "id_professor": self.id_professor,
            "formacao": self.formacao
        }
    # --- FIM DA CORREÇÃO ---
