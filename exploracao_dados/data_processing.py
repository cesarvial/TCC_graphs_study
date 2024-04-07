import pandas as pd
import numpy as np

dados_formados_path = 'input/dados_formados.csv'
dados_regulares_path = 'input/dados_regulares.csv'
dados_trancados_path = 'input/dados_trancados.csv'
dados_desistentes_path = 'input/dados_desistentes.csv'


def load_student_data() -> dict:
    dados = {
        "formados": pd.read_csv(dados_formados_path, delimiter=';'),
        "regulares": pd.read_csv(dados_regulares_path, delimiter=';'),
        "desistentes": pd.read_csv(dados_desistentes_path, delimiter=';'),
        "trancados": pd.read_csv(dados_trancados_path, delimiter=';')
    }

    dados.update(todos = pd.concat([dados["desistentes"], dados["regulares"], dados["formados"], dados["trancados"]]))

    dados['desistentes'] = dados['desistentes'].dropna()
    dados['regulares'] = dados['regulares'].dropna()
    dados['formados'] = dados['formados'].dropna()
    dados['trancados'] = dados['trancados'].dropna()
    dados['todos'] = dados['todos'].dropna()

    return dados


disciplinas = []
with open('input/dependencias.txt') as f:
    for line in f:
        curr = line.split(';')
        if 'P8' in curr:
            curr = curr[1].split('\n')[0]
            disciplinas.append(curr)

disciplinas_obrigatorias = ['GE70D', 'EEC31', 'CSS30','EEX23']
optativas = np.array(disciplinas)
optativas = optativas[[disc not in disciplinas_obrigatorias for disc in optativas]]

def get_optativas() -> list:

    return optativas