import requests

# IP do servidor. Troque '127.0.0.1' pelo IP do servidor na rede local
BASE_URL = "http://26.222.53.193:5000/" 

def _handle_request(method, endpoint, json_data=None):
    """Função auxiliar para tratar todas as requisições e erros."""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=json_data)
        elif method == 'DELETE':
            response = requests.delete(url)
        elif method == 'PUT':
            response = requests.put(url, json=json_data)
        
        response.raise_for_status() # Lança um erro se a resposta for 4xx ou 5xx
        return response.json()
    
    except requests.exceptions.ConnectionError:
        return {"erro": f"Não foi possível conectar ao servidor em {BASE_URL}"}
    except requests.exceptions.HTTPError as e:
        try:
            return e.response.json()
        except:
            return {"erro": str(e)}
    except Exception as e:
        return {"erro": f"Ocorreu um erro inesperado: {e}"}

# --- Login ---
def tentar_login(email, senha):
    payload = {"email": email, "senha": senha}
    return _handle_request('POST', '/login', json_data=payload)

# --- Admin (GET) ---
def listar_alunos():
    return _handle_request('GET', '/alunos')
def listar_disciplinas():
    return _handle_request('GET', '/disciplinas')
def listar_professores():
    return _handle_request('GET', '/professores')
def listar_turmas():
    return _handle_request('GET', '/turmas')

# GET por ID (para Editar)
def get_aluno(id_aluno):
    return _handle_request('GET', f'/aluno/{id_aluno}')
def get_professor(id_professor):
    return _handle_request('GET', f'/professor/{id_professor}')
def get_disciplina(id_disciplina):
    return _handle_request('GET', f'/disciplina/{id_disciplina}')
def get_turma(id_turma):
    return _handle_request('GET', f'/turma/{id_turma}')

# --- Admin (POST - Criar) ---
def criar_novo_aluno(dados_aluno):
    return _handle_request('POST', '/admin/aluno', json_data=dados_aluno)
def criar_nova_disciplina(dados_disciplina):
    return _handle_request('POST', '/admin/disciplina', json_data=dados_disciplina)
def criar_novo_professor(dados_professor):
    return _handle_request('POST', '/admin/professor', json_data=dados_professor)
def criar_nova_turma(dados_turma):
    return _handle_request('POST', '/admin/turma', json_data=dados_turma)
def matricular_aluno(dados_matricula):
    return _handle_request('POST', '/admin/matricula', json_data=dados_matricula)

# --- Admin (PUT - Editar) ---
def editar_aluno(id_aluno, dados_aluno):
    return _handle_request('PUT', f'/admin/aluno/{id_aluno}', json_data=dados_aluno)
def editar_professor(id_professor, dados_professor):
    return _handle_request('PUT', f'/admin/professor/{id_professor}', json_data=dados_professor)
def editar_disciplina(id_disciplina, dados_disciplina):
    return _handle_request('PUT', f'/admin/disciplina/{id_disciplina}', json_data=dados_disciplina)
def editar_turma(id_turma, dados_turma):
    return _handle_request('PUT', f'/admin/turma/{id_turma}', json_data=dados_turma)

# --- Admin (DELETE) ---
def excluir_aluno(id_aluno):
    return _handle_request('DELETE', f'/admin/aluno/{id_aluno}')
def excluir_professor(id_professor):
    return _handle_request('DELETE', f'/admin/professor/{id_professor}')
def excluir_disciplina(id_disciplina):
    return _handle_request('DELETE', f'/admin/disciplina/{id_disciplina}')
def excluir_turma(id_turma):
    return _handle_request('DELETE', f'/admin/turma/{id_turma}')
def desmatricular_aluno(id_turma, id_aluno):
    return _handle_request('DELETE', f'/admin/turma/{id_turma}/aluno/{id_aluno}')

# --- Professor (GET) ---
def listar_turmas_professor(id_professor):
    return _handle_request('GET', f'/professor/turmas/{id_professor}')
def get_detalhes_aluno(id_turma, id_aluno):
    return _handle_request('GET', f'/professor/turma/{id_turma}/aluno/{id_aluno}')

# --- Professor (POST) ---
def criar_nova_atividade(dados_atividade):
    return _handle_request('POST', '/professor/atividade', json_data=dados_atividade)
def lancar_nota(dados_nota):
    return _handle_request('POST', '/professor/nota', json_data=dados_nota)
def registrar_falta(dados_falta):
    return _handle_request('POST', '/professor/falta', json_data=dados_falta)

# --- Aluno (GET) ---
def get_boletim(id_aluno):
    return _handle_request('GET', f'/aluno/boletim/{id_aluno}')
def listar_atividades_aluno(id_aluno):
    return _handle_request('GET', f'/aluno/atividades/{id_aluno}')

# --- Aluno (POST) ---
def enviar_atividade(dados_entrega):
    return _handle_request('POST', '/aluno/entrega', json_data=dados_entrega)