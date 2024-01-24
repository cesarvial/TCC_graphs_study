import csv
from typing import List
from estudante import Estudante
from disciplina_cursada import DisciplinaCursada
from disciplina import Disciplina

dados_estudantes = [
    "../excel/dados_historicos_alunos_de_EngComputacaoCuritiba desistentes mudancas curso.csv",
    "../excel/dados_historicos_alunos_de_EngComputacaoCuritiba formados.csv",
    "../excel/dados_historicos_alunos_de_EngComputacaoCuritiba regulares.csv",
    "../excel/dados_historicos_alunos_de_EngComputacaoCuritiba trancados.csv",
]

mapeamento_721_to_844_path = "../excel/mapeamento_disciplinas_721_to_844.csv"
matriz_844_path = "../excel/matriz_844.csv"


def get_disciplinas_matriz_844():
    disciplinas = {}
    with open(matriz_844_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            disciplinas[row["Código"]] = Disciplina.from_dict(row)
    return disciplinas


def get_mapeamento_844_equivalencias(disciplinas: dict):
    """
    Recebe um dicionário de disciplinas e retorna um dicionário
    com o mapeamneto entre as disciplinas equivalentes e as disciplinas da matriz 844

    Args:
        {<CODIGO-DISCIPLINA-DA-MATRIZ-844>: Disciplina}

    Returns:
        {<CODIGO-DISCIPLINA-EQUIVALENTE>": "<CODIGO-DISCIPLINA-DA-MATRIZ-844>"}
    """
    mapa = {}
    for d in disciplinas.values():
        for eq in d.disciplinas_equivalentes.keys():
            mapa[eq] = d.codigo
    return mapa


def get_mapeamento_721_to_844():
    mapa = {}
    with open(mapeamento_721_to_844_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        mapa = {row["721"]: row["844"] for row in reader}
    return mapa


def get_historico_completo() -> List:
    """
    Obtem o histórico completo de todos os estudantes
    """
    historico_completo = []
    # Obter os históricos de todos os estudantes
    for file in dados_estudantes:
        with open(file, "r") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                historico_completo.append(row)
    print(f"Carregando {len(historico_completo)} dados de estudantes")
    return historico_completo


def gerar_estudantes(historico):
    """
    Obtem um mapa de estudantes a partir de dados de histórico de estudantes
    """
    estudantes = {}
    for dado in historico:
        id = dado["ID_ANONIMO"]
        if not any(id == estudante for estudante in estudantes):
            estudantes[id] = Estudante.from_dict(dado)
        estudantes[id].add_disciplina_from_dict(dado)

    # Ordenar as disciplinas cursadas de cada estudante por ano e periodo
    for estudante in estudantes.values():
        estudante.sort_disciplinas()

    return estudantes


def carregar_estudantes_old():
    """
    Carrega os dados dos estudantes de Engenharia de Computação

    Retorna um dicionário com os estudantes, onde a chave é o id anonimo do estudante e o valor é um objeto da classe Estudante
    """
    get_historico_completo = get_historico_completo()

    # Obter o mapeamento de disciplinas
    # map_disciplinas = mapeamento_721_to_844()

    # Mapear as disciplinas para o nova grade
    # Note que para algumas disciplinas não existe mapeamento, TODO: tratar isso posteriormente
    # for dado in historico:
    #     if dado["CODIGO"] in map_disciplinas:
    #         dado["CODIGO"] = map_disciplinas[dado["CODIGO"]]

    # Mapear as disciplinas equivalentes
    # disciplinas_844 = carregar_disciplinas_844()
    # print(f"{len(disciplinas_844)} disciplinas encontradas na grade 844")
    # mapa_equivalencias = mapeamento_844_equivalencias(disciplinas_844)
    # for dado in historico_completo:
    #     if dado["CODIGO"] in mapa_equivalencias:
    #         dado["CODIGO"] = mapa_equivalencias[dado["CODIGO"]]

    # Remover disciplinas fora da grade 844
    # Note que pode haver estudantes que não são da grade 844 que cursaram disciplinas da grade 844
    # Isso pode ser um problema, TODO: tratar isso posteriormente
    # historico_grade_844 = list(filter(lambda x: x["CODIGO"] in disciplinas_844, historico_completo))
    # historico_desconhecido = list(filter(lambda x: x["CODIGO"] not in disciplinas_844, historico_completo))

    # print(historico_desconhecido)

    # historico_grade_844 = historico_completo
    print(f"{len(historico_grade_844)} dados de estudantes na grade 844")

    # Criar uma mapa de estudantes
    estudantes = {}
    disciplinas_cursadas = set()
    disciplinas_desconhecidas = set()
    for dado in historico_completo:
        id = dado["ID_ANONIMO"]
        if not any(id == estudante for estudante in estudantes):
            estudantes[id] = Estudante.from_dict(dado)
        estudantes[id].add_disciplina_from_dict(dado)

        if dado["CODIGO"] in disciplinas_844:
            disciplinas_cursadas.add(dado["CODIGO"])
        else:
            disciplinas_desconhecidas.add(dado["CODIGO"])

    # Ordenar as disciplinas cursadas de cada estudante por ano e periodo
    for estudante in estudantes.values():
        estudante.sort_disciplinas()

    return estudantes, disciplinas_cursadas, disciplinas_desconhecidas
