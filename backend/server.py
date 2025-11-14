import sys
import os

# Adiciona a pasta raiz (sistema_academico_pim) ao "caminho" do Python
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

from flask import Flask, request, jsonify
from backend.persistence import data_manager
from backend.controllers import auth_controller, admin_controller, prof_controller, aluno_controller

# Inicializa o Flask
app = Flask(__name__)

# Carrega todos os dados (CSVs/JSON) para a memória ANTES de iniciar o servidor
data_manager.load_all_data()

@app.route('/')
def index():
    return "Servidor do Sistema Acadêmico PIM II no ar!"

# === ENDPOINTS DE AUTENTICAÇÃO ===
@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or 'email' not in dados or 'senha' not in dados:
        return jsonify({"erro": "Email e Senha são obrigatórios"}), 400
    sucesso, mensagem, dados_usuario = auth_controller.fazer_login(email=dados['email'], senha=dados['senha'])
    if not sucesso:
        return jsonify({"erro": mensagem}), 401
    return jsonify({"mensagem": mensagem, "usuario": dados_usuario}), 200

# === ENDPOINTS DE LEITURA GERAL (GET) ===
@app.route('/configuracao', methods=['GET'])
def get_configuracao():
    config = data_manager.get_config()
    return jsonify(config), 200

@app.route('/alunos', methods=['GET'])
def get_alunos():
    alunos = data_manager.get_all_alunos()
    return jsonify(alunos), 200

@app.route('/professores', methods=['GET'])
def get_professores():
    professores = data_manager.get_all_professores()
    return jsonify(professores), 200

@app.route('/disciplinas', methods=['GET'])
def get_disciplinas():
    disciplinas = data_manager.get_all_disciplinas()
    return jsonify(disciplinas), 200

@app.route('/turmas', methods=['GET'])
def get_turmas():
    turmas = data_manager.get_all_turmas()
    return jsonify(turmas), 200

# Rotas GET por ID (para preencher formulários de edição)
@app.route('/aluno/<int:id_aluno>', methods=['GET'])
def get_aluno(id_aluno):
    aluno = data_manager.get_aluno_by_id(id_aluno)
    if not aluno: return jsonify({"erro": "Aluno não encontrado"}), 404
    return jsonify(aluno.to_dict()), 200

@app.route('/professor/<int:id_professor>', methods=['GET'])
def get_professor(id_professor):
    prof = data_manager.get_professor_by_id(id_professor)
    if not prof: return jsonify({"erro": "Professor não encontrado"}), 404
    return jsonify(prof.to_dict()), 200
    
@app.route('/disciplina/<int:id_disciplina>', methods=['GET'])
def get_disciplina(id_disciplina):
    disc = data_manager.get_disciplina_by_id(id_disciplina)
    if not disc: return jsonify({"erro": "Disciplina não encontrada"}), 404
    return jsonify(disc.to_dict()), 200
    
@app.route('/turma/<int:id_turma>', methods=['GET'])
def get_turma(id_turma):
    turma = data_manager.get_turma_by_id(id_turma)
    if not turma: return jsonify({"erro": "Turma não encontrada"}), 404
    return jsonify(turma.to_dict()), 200


# === ENDPOINTS DE ADMIN (POST - Criar) ===
@app.route('/admin/aluno', methods=['POST'])
def post_aluno():
    dados = request.get_json()
    sucesso, msg, data = admin_controller.criar_novo_aluno(
        dados.get('nome'), dados.get('email'), dados.get('senha'),
        dados.get('ra'), dados.get('curso')
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "aluno": data}), 201

@app.route('/admin/professor', methods=['POST'])
def post_professor():
    dados = request.get_json()
    sucesso, msg, data = admin_controller.criar_novo_professor(
        dados.get('nome'), dados.get('email'), dados.get('senha'),
        dados.get('formacao')
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "professor": data}), 201

@app.route('/admin/disciplina', methods=['POST'])
def post_disciplina():
    dados = request.get_json()
    sucesso, msg, data = admin_controller.criar_nova_disciplina(
        dados.get('nome'), dados.get('descricao'), dados.get('carga_horaria')
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "disciplina": data}), 201
    
@app.route('/admin/turma', methods=['POST'])
def post_turma():
    dados = request.get_json()
    sucesso, msg, data = admin_controller.criar_nova_turma(
        dados.get('codigo'), dados.get('semestre'),
        dados.get('id_disciplina'), dados.get('id_professor')
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "turma": data}), 201

@app.route('/admin/matricula', methods=['POST'])
def post_matricula():
    dados = request.get_json()
    sucesso, msg, data = admin_controller.matricular_aluno(
        dados.get('id_aluno'), dados.get('id_turma')
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "matricula": data}), 201

# === ENDPOINTS DE ADMIN (PUT - Editar) ===
@app.route('/admin/aluno/<int:id_aluno>', methods=['PUT'])
def update_aluno(id_aluno):
    dados = request.get_json()
    sucesso, msg, data = admin_controller.editar_aluno(id_aluno, dados)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "aluno": data}), 200

@app.route('/admin/professor/<int:id_professor>', methods=['PUT'])
def update_professor(id_professor):
    dados = request.get_json()
    sucesso, msg, data = admin_controller.editar_professor(id_professor, dados)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "professor": data}), 200

@app.route('/admin/disciplina/<int:id_disciplina>', methods=['PUT'])
def update_disciplina(id_disciplina):
    dados = request.get_json()
    sucesso, msg, data = admin_controller.editar_disciplina(id_disciplina, dados)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "disciplina": data}), 200
    
@app.route('/admin/turma/<int:id_turma>', methods=['PUT'])
def update_turma(id_turma):
    dados = request.get_json()
    sucesso, msg, data = admin_controller.editar_turma(id_turma, dados)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "turma": data}), 200

# === ENDPOINTS DE ADMIN (DELETE) ===
@app.route('/admin/aluno/<int:id_aluno>', methods=['DELETE'])
def delete_aluno(id_aluno):
    sucesso, msg, data = admin_controller.excluir_aluno(id_aluno)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg}), 200

@app.route('/admin/professor/<int:id_professor>', methods=['DELETE'])
def delete_professor(id_professor):
    sucesso, msg, data = admin_controller.excluir_professor(id_professor)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg}), 200

@app.route('/admin/disciplina/<int:id_disciplina>', methods=['DELETE'])
def delete_disciplina(id_disciplina):
    sucesso, msg, data = admin_controller.excluir_disciplina(id_disciplina)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg}), 200

@app.route('/admin/turma/<int:id_turma>', methods=['DELETE'])
def delete_turma(id_turma):
    sucesso, msg, data = admin_controller.excluir_turma(id_turma)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg}), 200

@app.route('/admin/turma/<int:id_turma>/aluno/<int:id_aluno>', methods=['DELETE'])
def delete_matricula(id_turma, id_aluno):
    sucesso, msg, data = admin_controller.desmatricular_aluno(id_aluno, id_turma)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg}), 200

# === ENDPOINTS DE PROFESSOR (ÉPICO 4) ===
@app.route('/professor/turmas/<int:id_professor>', methods=['GET'])
def get_turmas_professor(id_professor):
    turmas = data_manager.get_turmas_by_professor(id_professor)
    return jsonify(turmas), 200

@app.route('/professor/atividade', methods=['POST'])
def post_atividade():
    dados = request.get_json()
    sucesso, msg, data = prof_controller.criar_atividade(
        dados.get('id_turma'), dados.get('titulo'), dados.get('descricao'),
        dados.get('data_entrega'), dados.get('peso'),
        dados.get('caminho_anexo') # <-- ADICIONADO
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "atividade": data}), 201

@app.route('/professor/nota', methods=['POST'])
def post_nota():
    dados = request.get_json()
    sucesso, msg, data = prof_controller.lancar_nota(
        dados.get('id_aluno'), dados.get('id_turma'), dados.get('id_atividade'),
        dados.get('valor'), dados.get('id_professor')
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "nota": data}), 201

@app.route('/professor/falta', methods=['POST'])
def post_falta():
    dados = request.get_json()
    sucesso, msg, data = prof_controller.registrar_falta(
        dados.get('id_aluno'), dados.get('id_turma'), dados.get('data_aula')
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "falta": data}), 201
    
@app.route('/professor/turma/<int:id_turma>/aluno/<int:id_aluno>', methods=['GET'])
def get_detalhes_aluno_turma(id_turma, id_aluno):
    sucesso, msg, data = prof_controller.consultar_detalhes_aluno(id_aluno, id_turma)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "detalhes": data}), 200

# === ENDPOINTS DE ALUNO (ÉPICO 4) ===
@app.route('/aluno/boletim/<int:id_aluno>', methods=['GET'])
def get_boletim(id_aluno):
    sucesso, msg, data = aluno_controller.consultar_boletim(id_aluno)
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "boletim": data}), 200

@app.route('/aluno/atividades/<int:id_aluno>', methods=['GET'])
def get_atividades_aluno(id_aluno):
    atividades = data_manager.get_atividades_by_aluno(id_aluno)
    return jsonify(atividades), 200

@app.route('/aluno/entrega', methods=['POST'])
def post_entrega():
    dados = request.get_json()
    sucesso, msg, data = aluno_controller.enviar_atividade(
        dados.get('id_atividade'), dados.get('id_aluno'), dados.get('arquivo')
    )
    if not sucesso: return jsonify({"erro": msg}), 400
    return jsonify({"mensagem": msg, "entrega": data}), 201


if __name__ == '__main__':
    # 'host="0.0.0.0"' faz o servidor ser acessível na sua rede local (LAN)
    print("Iniciando servidor Flask em http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)