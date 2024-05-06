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
    
    for item in dados:
        dados[item]['CR'] = dados[item]['CR'].apply(lambda x: float(str(x).replace(',','.')))
        dados[item]['NOTA'] = dados[item]['NOTA'].apply(lambda x: float(str(x).replace(',','.')))
        dados[item]['ID_ANONIMO'] = dados[item]['ID_ANONIMO'].apply(lambda x: float(str(x).replace(',','.')))

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

from collections import defaultdict
from typing import List
import re

class Disciplina:
    def __init__(self, ch : int = 0, periodo : int = 0, nome : str = 'default', codigo : str = 'default', trilha : str = 'optativa', equivalentes = []):
        self.ch = ch
        self.periodo = periodo
        self.nome = nome
        self.codigo = codigo
        self.trilha = trilha
        self.equivalentes = equivalentes

def load_disciplinas() -> List:
    disciplinas = defaultdict()

    data = load_student_data() 
    with open('input/dependencias.txt', 'r') as file:
        for line in file:
            entry = line.split(';')
            if re.search('P[1-9]', entry[0]) != None and entry[1].split('\n')[0] not in disciplinas:
                disc_code = entry[1].split('\n')[0]
                disc_CH = data['todos'][data['todos']['CODIGO'] == disc_code].values[0][8] if len(data['todos'][data['todos']['CODIGO'] == disc_code].values) > 0 else 0
                disc_periodo = int(entry[0][1].split('\n')[0])
                disciplinas[entry[1].split('\n')[0]] = Disciplina(ch = int(disc_CH), periodo = disc_periodo, nome = entry[1].split('\n')[0], codigo = entry[1].split('\n')[0], trilha = 'Optativas Isoladas' if disc_periodo != 10 else 'obrigatoria')
            elif re.search('P[1-9]', entry[1]) != None:
                disc_code = entry[0]
                disc_CH = data['todos'][data['todos']['CODIGO'] == disc_code].values[0][8] if len(data['todos'][data['todos']['CODIGO'] == disc_code].values) > 0 else 0
                disc_periodo = int(entry[1][1].split('\n')[0]) - 1
                disciplinas[entry[0].split('\n')[0]] = Disciplina(ch = int(disc_CH), periodo = disc_periodo, nome = entry[0].split('\n')[0], codigo = entry[0].split('\n')[0], trilha = 'obrigatoria')


    with open('input/trilhas.txt', 'r') as file:
        for line in file:
            trilha = line.split('\n')[0].split(';')
            for item in trilha[1:]:
                if item in disciplinas:
                    disciplinas[item].trilha = trilha[0]
                else:
                    disc_code = item
                    disc_CH = data['todos'][data['todos']['CODIGO'] == disc_code].values[0][8] if len(data['todos'][data['todos']['CODIGO'] == disc_code].values) > 0 else 0
                    disc_periodo = 8
                    disciplinas[disc_code] = Disciplina(ch = int(disc_CH), periodo = disc_periodo, nome = item, codigo = item)

    matriz = pd.read_csv('input/matriz_844.csv', sep=',')
    for disc in matriz.itertuples():
        #print(disc[3])
        if disc[3] in disciplinas.keys():
            disciplinas[disc[3]].periodo = disc[1]
        if(len(str(disc[16]).split(' ')) > 1):
            print(disciplinas[disc[3]].codigo)
            disciplinas[disc[3]].equivalentes = disc[16].split(' ')
            print(disciplinas[disc[3]].equivalentes)

    

    return disciplinas

def get_matriz():
    return pd.read_csv('input/matriz_844.csv', sep=',')
