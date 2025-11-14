import subprocess
import os
import sys  # <--- IMPORTAR SYS
import shlex

# Define os caminhos base
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BIN_DIR = os.path.join(BASE_DIR, 'c_modules', 'bin')
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'data'))

# Caminhos para os executáveis C
AUTH_EXEC = os.path.join(BIN_DIR, 'auth')
PERSIST_EXEC = os.path.join(BIN_DIR, 'persist')

# --- INÍCIO DA CORREÇÃO ---
# Adiciona .exe automaticamente se estiver no Windows
if sys.platform == "win32":
    AUTH_EXEC += ".exe"
    PERSIST_EXEC += ".exe"
# --- FIM DA CORREÇÃO ---


def _run_c_command(command_args):
    """Função auxiliar para rodar comandos C e capturar a saída."""
    try:
        # Garante que todos os argumentos são strings
        command_args = [str(arg) for arg in command_args]

        result = subprocess.run(
            command_args, capture_output=True, text=True, check=True, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Imprime stdout E stderr em caso de erro.
        print(f"--- Erro ao executar C ---")
        print(f"Comando: {' '.join(command_args)}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        print(f"--------------------------")
        return None
    except FileNotFoundError:
        print(f"Erro: Executável C não encontrado em {command_args[0]}")
        print("Certifique-se de que você compilou os módulos C (veja as instruções).")
        return None


def hash_senha_c(senha):
    """Chama o auth.c para gerar um hash."""
    return _run_c_command([AUTH_EXEC, 'hash', senha])


def verificar_senha_c(senha, hash_correto):
    """Chama o auth.c para verificar uma senha."""
    result = _run_c_command([AUTH_EXEC, 'verify', senha, hash_correto])
    return result == "true"


def salvar_linha_c(nome_arquivo, linha_dados_csv):
    """Chama o persist.c para salvar uma linha em um arquivo CSV."""
    caminho_arquivo_csv = os.path.join(DATA_DIR, nome_arquivo)
    caminho_arquivo_csv = caminho_arquivo_csv.replace("\\", "/")

    # Agora o persist.c será chamado corretamente
    result = _run_c_command(
        [PERSIST_EXEC, caminho_arquivo_csv, linha_dados_csv])
    return result == "true"

