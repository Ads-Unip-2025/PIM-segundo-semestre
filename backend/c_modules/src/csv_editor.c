#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_LINE_LEN 2048

// Constantes para as colunas
#define PESSOAS_COL_ID 0
#define PESSOAS_COL_ATIVO 5
#define MATRICULAS_COL_ID_ALUNO 1
#define MATRICULAS_COL_STATUS 4

/**
 * Função principal para soft delete (marca como inativo).
 * Lê um arquivo, encontra a linha pelo ID, muda o valor de uma coluna,
 * e reescreve o arquivo.
 */
int soft_delete(const char* filepath, int target_id, int id_col, int target_col, const char* new_value) {
    FILE *file_in, *file_out;
    char line[MAX_LINE_LEN];
    char temp_filepath[256];
    
    // Cria o nome do arquivo temporário
    sprintf(temp_filepath, "%s.tmp", filepath);

    file_in = fopen(filepath, "r");
    if (file_in == NULL) {
        fprintf(stderr, "Erro: Nao foi possivel abrir o arquivo original %s\n", filepath);
        return 1;
    }

    file_out = fopen(temp_filepath, "w");
    if (file_out == NULL) {
        fprintf(stderr, "Erro: Nao foi possivel criar o arquivo temporario %s\n", temp_filepath);
        fclose(file_in);
        return 1;
    }

    // 1. Ler e copiar o cabeçalho
    if (fgets(line, MAX_LINE_LEN, file_in) != NULL) {
        fprintf(file_out, "%s", line);
    } else {
        fprintf(stderr, "Erro: Arquivo original vazio.\n");
        fclose(file_in);
        fclose(file_out);
        return 1;
    }

    // 2. Ler e processar o resto do arquivo
    while (fgets(line, MAX_LINE_LEN, file_in) != NULL) {
        char original_line[MAX_LINE_LEN];
        strcpy(original_line, line); // Salva a linha original

        char* token;
        int current_col = 0;
        int current_id = -1;
        
        // Pega o ID da linha
        token = strtok(line, ",");
        while (token != NULL && current_col < id_col) {
            token = strtok(NULL, ",");
            current_col++;
        }
        
        if (token != NULL) {
            current_id = atoi(token);
        }

        // 3. Compara o ID
        if (current_id == target_id) {
            // ID bateu! Vamos reescrever a linha
            char new_line_buffer[MAX_LINE_LEN] = "";
            
            // Recomeça a "tokenização" da linha original
            strcpy(line, original_line); 
            current_col = 0;
            token = strtok(line, ",\n");
            
            while (token != NULL) {
                if (current_col == target_col) {
                    // Esta é a coluna que queremos mudar
                    strcat(new_line_buffer, new_value);
                } else {
                    // Apenas copia o valor antigo
                    strcat(new_line_buffer, token);
                }
                
                // Adiciona a vírgula (exceto no final)
                strcat(new_line_buffer, ",");
                
                token = strtok(NULL, ",\n");
                current_col++;
            }
            // Remove a última vírgula e adiciona quebra de linha
            new_line_buffer[strlen(new_line_buffer) - 1] = '\0'; 
            fprintf(file_out, "%s\n", new_line_buffer);

        } else {
            // ID não bateu, apenas copia a linha original
            fprintf(file_out, "%s", original_line);
        }
    }

    fclose(file_in);
    fclose(file_out);

    // 4. Substitui o arquivo original pelo temporário
    if (remove(filepath) != 0) {
        fprintf(stderr, "Erro: Falha ao deletar o arquivo original.\n");
        return 1;
    }
    if (rename(temp_filepath, filepath) != 0) {
        fprintf(stderr, "Erro: Falha ao renomear o arquivo temporario.\n");
        return 1;
    }

    return 0; // Sucesso
}


int main(int argc, char *argv[]) {
    // Exemplo: csv_editor.exe soft_delete_pessoa <path/pessoas.csv> <id_pessoa>
    // Exemplo: csv_editor.exe soft_delete_matriculas <path/matriculas.csv> <id_aluno>

    if (argc < 4) {
        fprintf(stderr, "Erro: Argumentos insuficientes.\n");
        return 1;
    }

    char* comando = argv[1];
    char* filepath = argv[2];
    int id = atoi(argv[3]);

    if (strcmp(comando, "soft_delete_pessoa") == 0) {
        // Altera pessoas.csv: ID na col 0, 'ativo' na col 5, novo valor 'false'
        return soft_delete(filepath, id, PESSOAS_COL_ID, PESSOAS_COL_ATIVO, "false");
    }

    if (strcmp(comando, "soft_delete_matriculas") == 0) {
        // Altera matriculas.csv: ID_ALUNO na col 1, 'status' na col 4, novo valor 'Inativa'
        return soft_delete(filepath, id, MATRICULAS_COL_ID_ALUNO, MATRICULAS_COL_STATUS, "Inativa");
    }

    fprintf(stderr, "Erro: Comando '%s' desconhecido.\n", comando);
    return 1;
}