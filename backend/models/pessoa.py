class Pessoa:
    def __init__(self, id_pessoa, nome, email, senha_hash, tipo, ativo):
        self.id_pessoa = int(id_pessoa)
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.tipo = tipo  # 'A', 'P', 'D'
        self.ativo = bool(ativo)

    def __repr__(self):
        return f"<Pessoa {self.nome} ({self.tipo})>"
