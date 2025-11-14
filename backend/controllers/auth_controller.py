from backend.persistence import data_manager, c_bridge


# Em /backend/controllers/auth_controller.py

def fazer_login(email, senha):
    """
    Controlador para lógica de login.
    Retorna (True/False, mensagem, dados_usuario)
    """
    # 1. Busca o usuário na memória
    pessoa = data_manager.get_pessoa_by_email(email)

    if not pessoa or not pessoa.ativo:
        return (False, "Usuário não encontrado ou inativo.", None)

    # 2. Chama a bridge C para verificar a senha
    senha_correta = c_bridge.verificar_senha_c(senha, pessoa.senha_hash)

    if not senha_correta:
        return (False, "Senha incorreta.", None)

    # 3. Sucesso! Monta o payload do usuário
    dados_usuario = {
        "id_pessoa": pessoa.id_pessoa,
        "nome": pessoa.nome,
        "email": pessoa.email,
        "tipo": pessoa.tipo
    }

    # --- INÍCIO DA ATUALIZAÇÃO (ÉPICO 4) ---
    # Se for Aluno ou Professor, adiciona o ID específico
    if pessoa.tipo == 'A':
        aluno = data_manager.get_aluno_by_pessoa_id(pessoa.id_pessoa)
        if aluno:
            dados_usuario['id_aluno'] = aluno.id_aluno

    elif pessoa.tipo == 'P':
        professor = data_manager.get_professor_by_pessoa_id(pessoa.id_pessoa)
        if professor:
            dados_usuario['id_professor'] = professor.id_professor
    # --- FIM DA ATUALIZAÇÃO ---

    return (True, "Login bem-sucedido!", dados_usuario)
