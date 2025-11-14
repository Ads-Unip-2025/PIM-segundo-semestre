#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    // argv[1] = caminho do arquivo
    // argv[2] = linha de dados

    if (argc < 3) {
        // Agora imprime no stderr
        fprintf(stderr, "Erro: Caminho do arquivo ou dados ausentes.\n");
        return 1;
    }

    FILE *arquivo;
    char* caminho_arquivo = argv[1];
    
    // "a+" = modo Append (adicionar ao final)
    arquivo = fopen(caminho_arquivo, "a+"); 

    if (arquivo == NULL) {
        fprintf(stderr, "Erro: Nao foi possivel abrir o arquivo %s.\n", caminho_arquivo);
        return 1;
    }

    // Escreve a nova linha de dados (argv[2]) e uma quebra de linha
    fprintf(arquivo, "%s\n", argv[2]);
    
    fclose(arquivo);
    printf("true"); // Sucesso
    return 0;
}