
arquivos = [
    "pessoas.csv",
    "alunos.csv",
    "professores.csv",
    "disciplinas.csv",
    "turmas.csv",
    "matriculas.csv",
    "atividades.csv",
    "entregas.csv",
    "notas.csv",
    "faltas.csv",
    "configuracao.json"
]


for x in arquivos:
    arquivo = open(f'{x}', "a")
