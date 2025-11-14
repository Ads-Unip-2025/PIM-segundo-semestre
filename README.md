# Sistema Acadêmico Colaborativo (PIM II - UNIP)

[cite_start]Este é um Sistema Acadêmico Colaborativo desenvolvido como Projeto Integrado Multidisciplinar (PIM II) para o curso de Análise e Desenvolvimento de Sistemas da UNIP [cite: 46-51]. O objetivo foi criar um sistema cliente-servidor completo para gerenciamento acadêmico, integrando Python para a lógica de alto nível e C para módulos de performance crítica, tudo isso sem o uso de um banco de dados tradicional.

O sistema é 100% funcional e opera em uma arquitetura de API, com um backend (Flask) servindo dados para um cliente desktop (Tkinter).

## 📸 Screenshots

*(Adicione aqui os screenshots do seu sistema em funcionamento, como os que você me enviou)*

| Painel de Login | Painel do Administrador | Painel do Professor | Painel do Aluno |
| :---: | :---: | :---: | :---: |
| [Tela de Login] | [Painel Admin] | [Painel Professor] | [Painel Aluno] |

---

## 🌟 Principais Funcionalidades

[cite_start]O sistema é dividido em três perfis de usuário com diferentes níveis de acesso[cite: 38]:

### 👤 Administrador
* [cite_start]**CRUD Completo:** Cadastrar, Listar, **Editar** e **Excluir** (Logicamente) Alunos e Professores[cite: 5, 43].
* [cite_start]**CRUD Completo:** Cadastrar, Listar, **Editar** e **Excluir** (Fisicamente) Disciplinas e Turmas[cite: 5, 10, 43].
* **Gerenciamento:** Matricular alunos em turmas e desmatriculá-los.
* [cite_start]**Visualização:** Ver detalhes da turma, incluindo a lista de alunos matriculados[cite: 9].

### 👨‍🏫 Professor
* **Gestão de Turmas:** Listar apenas as turmas que lhe foram atribuídas.
* **Gestão de Alunos:** Visualizar os alunos matriculados em suas turmas.
* [cite_start]**Avaliação:** Lançar Notas (com ou sem ID de atividade) e registrar Faltas para os alunos[cite: 11, 13].
* [cite_start]**Atividades:** Criar atividades avaliativas, com opção de anexar um caminho de rede (link) para arquivos[cite: 14].
* **Consulta:** Visualizar o histórico de notas e faltas de um aluno específico.

### 🎓 Aluno
* [cite_start]**Boletim:** Consultar suas notas, faltas e situação final (Aprovado/Reprovado), calculada automaticamente com base nas regras de negócio[cite: 15, 16, 35].
* **Atividades:** Listar todas as atividades propostas pelos seus professores, incluindo links de anexos.
* [cite_start]**Entregas:** Registrar a entrega de uma atividade (simulada)[cite: 18].

---

## 🛠️ Arquitetura e Tecnologias Utilizadas

[cite_start]Este projeto foi desenhado para atender aos requisitos técnicos específicos do PIM [cite: 89-91, 99].

* **Backend:** **Python (Flask)**
    * Serve uma API RESTful (JSON) para toda a lógica de negócios.
    * [cite_start]Configurado para rodar em rede local (`host='0.0.0.0'`), permitindo acesso de múltiplos clientes[cite: 85].

* **Frontend:** **Python (Tkinter)**
    * [cite_start]Um cliente desktop "pesado" que consome a API Flask[cite: 171].
    * A comunicação é feita pela biblioteca `requests`.

* **Persistência (Base de Dados):** **Arquivos `.csv`**
    * O sistema não utiliza um SGBD. Todos os dados são persistidos em arquivos CSV na pasta `/data/`.
    * A lógica de "join" (ex: mostrar nome do aluno na turma) é feita em tempo de execução pelo Python.

* **Módulos Críticos:** **Linguagem C**
    * **`auth.c`**: Compilado para `auth.exe`, este módulo é chamado pelo Python (via `subprocess`) para gerar hashes de senha e verificar logins. [cite_start]Isso atende ao RNF05 (senhas criptografadas)[cite: 23, 26].
    * **`persist.c`**: Compilado para `persist.exe`, este módulo é chamado para operações de `INSERT` (anexar novas linhas aos arquivos `.csv`), garantindo performance.
    * **Lógica de CRUD em Python:** As operações de Edição (Update) e Exclusão (Delete) são feitas em Python. Elas atualizam os dados na memória e, em seguida, **reescrevem** os arquivos `.csv` de forma segura (lidando com caracteres especiais), uma operação que se mostrou mais robusta do que a manipulação de arquivos em C.

---

## 🚀 Guia de Instalação e Execução

Siga estes passos para rodar o projeto.

### 1. Requisitos
* Python 3.10+
* `pip` (Gerenciador de pacotes Python)
* Compilador C (`gcc`). Para Windows, é recomendado o **MinGW-w64**.

### 2. Configuração do Ambiente

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  Instale as dependências Python:
    ```bash
    pip install flask requests
    ```

3.  **Compile os Módulos C (Obrigatório):**
    Abra um terminal na pasta `/backend/c_modules/src/` e execute:
    ```bash
    # Compila o módulo de autenticação
    gcc -std=c99 auth.c -o ../bin/auth.exe
    
    # Compila o módulo de persistência (cadastro)
    gcc persist.c -o ../bin/persist.exe
    ```
    *(Sem os arquivos `.exe` na pasta `/bin/`, o sistema não funcionará.)*

### 3. Configuração dos Dados

O sistema é iniciado com um conjunto de dados limpo. A pasta `/data/` contém os arquivos `.csv` apenas com seus cabeçalhos. O primeiro usuário (Admin) já vem cadastrado no `pessoas.csv`.

* **Usuário Admin Padrão:**
    * **Email:** `admin@sistema.com`
    * **Senha:** `admin123`

### 4. Executando o Sistema

Você precisará de **dois terminais** abertos na pasta raiz do projeto (`/sistema_academico_pim/`).

**Terminal 1: Iniciar o Servidor (Backend)**
```bash
python -m backend.server
```
*(Deixe este terminal rodando. Você verá o log "In
iciando servidor Flask...")*

**Terminal 2: Iniciar o Cliente (Frontend)**

```bash
python -m client_desktop.app
```
## 🖥️ Demonstração Multiusuário (Requisito PIM)
Para demonstrar o funcionamento em rede local (LAN) com múltiplos usuários:

1.  **Encontre seu IP:** No Windows, abra um CMD e digite `ipconfig`. Anote seu "Endereço IPv4" (ex: `192.168.0.10`).
2.  **Configure o Cliente:** Abra o arquivo `/client_desktop/api_client.py` e altere a `BASE_URL`:
    * **De:** `BASE_URL = "http://127.0.0.1:5000"`
    * **Para:** `BASE_URL = "http://SEU_IP_AQUI:5000"` (ex: `http://192.168.0.10:5000`)
3.  **Execute:**
    * Rode o `backend.server` (Terminal 1).
    * Rode o `client_desktop.app` (Terminal 2) e logue como **Admin**.
    * Rode o `client_desktop.app` (Terminal 3) e logue como **Professor**.

Você terá dois clientes rodando simultaneamente, acessando o mesmo servidor pela rede, validando o requisito.

---
## 📄 Licença
Distribuído sob a licença MIT.