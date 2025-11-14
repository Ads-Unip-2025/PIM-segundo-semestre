#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// Chave "pim2"
const char* CHAVE = "pim2";

/**
 * Gera um "hash" simples e imprimível.
 * Em vez de XOR, ele SOMA os valores ASCII e os mantém 
 * na faixa de caracteres imprimíveis (ASCII 33 '!' a 126 '~').
 */
void simple_printable_hash(const char* input, char* output) {
    int key_len = strlen(CHAVE);
    int input_len = strlen(input);
    
    for (int i = 0; i < input_len; i++) {
        // Soma o caractere da senha com o caractere da chave
        int hashed_char = ((unsigned char)input[i] + (unsigned char)CHAVE[i % key_len]);
        
        // Garante que o resultado esteja na faixa imprimível [33, 126]
        // (94 é o tamanho dessa faixa: 126 - 33 + 1)
        hashed_char = (hashed_char % 94) + 33;
        
        output[i] = (char)hashed_char;
    }
    output[input_len] = '\0';
}

int main(int argc, char *argv[]) {
    // argv[1] = "hash" ou "verify"
    // argv[2] = senha
    // argv[3] = hash_para_verificar (apenas no "verify")

    if (argc < 3) {
        printf("Erro: argumentos insuficientes.\n");
        return 1;
    }

    if (strcmp(argv[1], "hash") == 0) {
        char hash_result[256];
        simple_printable_hash(argv[2], hash_result);
        printf("%s", hash_result); // Retorna o "hash"
        return 0;
    }

    if (strcmp(argv[1], "verify") == 0) {
        if (argc < 4) {
            printf("Erro: 'verify' precisa de senha e hash.\n");
            return 1;
        }
        
        char hash_da_senha[256];
        simple_printable_hash(argv[2], hash_da_senha);
        
        // Compara o hash gerado com o hash esperado
        if (strcmp(hash_da_senha, argv[3]) == 0) {
            printf("true"); // Match
            return 0;
        } else {
            printf("false"); // No match
            return 1;
        }
    }

    printf("Erro: comando invalido.\n");
    return 1;
}