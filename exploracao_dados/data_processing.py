import pandas as pd
import numpy as np
from typing import Dict

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

# Funções para escolha e obtenção de dados de estudantes

def select_random_student(data : pd.DataFrame, max_tries : int, minimum_entry_year : int) -> int:
    id = 0
    tries = 0

    minimum_entry_year -= 2000
    
    while id == 0 and tries < max_tries:
        try:
            id = data[[int(x[3].split('/')[2].split(' ')[0]) >= minimum_entry_year for x in data.values]].sample()
            return int(id.ID_ANONIMO.iloc[0])
        except:
            id = 0
            tries += 1
    return 0

def get_all_data_from_student(student_id : int, data : pd.DataFrame):
    return data[[x == student_id for x in data['ID_ANONIMO']]]
    pass

# Funções para recomendação

from typing import List
from collections import defaultdict

def centralized_cosine(user_array):
    vec_med = sum(user_array.values())/len(user_array.values())
    for key in user_array:
        user_array[key] -= vec_med
    return user_array

def get_user_array(student_id : int, data : pd.DataFrame, centralize_cosine = True):
    student_data = get_all_data_from_student(student_id, data)

    student_array : Dict[str, float] = defaultdict(lambda : 0)
    
    for course in student_data.values:
        if student_array[course[4]] == 0:
            #print([course[4], float(str(course[7]).replace(',','.')),(course[5] - 2000)*2 + course[6]])
            student_array[course[4]] = float(str(course[7]).replace(',','.'))
            if student_array[course[4]] != student_array[course[4]]:
                student_array[course[4]] = 0
        else:
            nota = float(str(course[7]).replace(',','.'))
            student_array[course[4]] = nota if nota < student_array[course[4]] else student_array[course[4]]
    
    if centralize_cosine and len(student_array) != 0:
        student_array = centralized_cosine(student_array)
    
    return student_array

from numpy import dot
from numpy.linalg import norm
import math

def cos_sim(a : List[int], b : List[int]) -> int:
    return dot(a, np.transpose(b))/(norm(a)*norm(b))

# O cache deve ser criado com os mesmos dados utilizados nas funções
def create_cache_user_arrays(data,  centralize_cosine = True):
    return {int(identifier): get_user_array(identifier, data, centralize_cosine = centralize_cosine) for identifier in data["ID_ANONIMO"].unique() if identifier == identifier}
        
def most_similar_students_to(user_id : int, student_ids : List[int], user_data, rec_data, centralize_cosine = True, include_self = False,
                            cache = None):
    pairs = []

    user_array = get_user_array(user_id, user_data, centralize_cosine = centralize_cosine)
    user_list = []
    for course in user_array:
        user_list.append(user_array[course] if user_array[course] > 0 else 0)

    for id in student_ids:
        if include_self or id != user_id:
            if cache != None:
                student_array = cache[id]
            else:
                student_array = get_user_array(id, rec_data, centralize_cosine = centralize_cosine)
            
            student_list = []

            for course in user_array:
                #print(student_array[course] if student_array[course] > 0 else 1)
                student_list.append(student_array[course] if student_array[course] > 0 else 0)


            if norm(user_list)*norm(student_list) != 0 and cos_sim(user_list, student_list) == cos_sim(user_list, student_list):
                pairs.append((int(id), cos_sim(user_list, student_list)))
    
    return sorted(pairs, key = lambda pair: pair[-1], reverse = True)

# Sugestões por filtragem colaborativa

def user_based_suggestions(user_id: int, include_user_interests: bool = False, 
                           only_optionals = True, data_rec = None, data_user = None,
                           disciplinas_optativas = optativas, centralize_cosine = True, reduce_popularity_weight = True, cache = None):
    # Some as semelhanças
    suggestions : Dict[str, float] = defaultdict(float)
    times_coursed : Dict[str, float] = defaultdict(int)

    if cache != None:
        for other_user_id, similarity in most_similar_students_to(user_id, data_rec["ID_ANONIMO"].unique(), data_user, data_rec, centralize_cosine = centralize_cosine, cache = cache):
            for interest in get_all_data_from_student(other_user_id, data_rec)["CODIGO"].values:
                suggestions[interest] += similarity
                times_coursed[interest] += 1
    else:
        for other_user_id, similarity in most_similar_students_to(user_id, data_rec["ID_ANONIMO"].unique(), data_user, data_rec, centralize_cosine = centralize_cosine):
            for interest in get_all_data_from_student(other_user_id, data_rec)["CODIGO"].values:
                suggestions[interest] += similarity
                times_coursed[interest] += 1
    
    if reduce_popularity_weight:
        for codigo in suggestions:
            suggestions[codigo] = suggestions[codigo]/times_coursed[codigo]
    
    # Converta em uma lista classificada 
    suggestions = sorted(suggestions.items(),
                        key = lambda pair: pair[-1],
                        reverse = True)

    # Exclua nao optativas
    if only_optionals:
        suggestions = [(suggestion, weight)
                for suggestion, weight in suggestions
                if suggestion in disciplinas_optativas]
    
    # Exclua interesses existentes
    if include_user_interests:
        return suggestions
    else:
        return [(suggestion, weight)
                for suggestion, weight in suggestions
                if suggestion not in get_all_data_from_student(user_id, data_user)["CODIGO"].values]
    
def trim_user_data(user_data, num_materias):
    trimmed_data = user_data.copy()

    trimmed_data = trimmed_data.sort_values(by=['ANO','PERIODO.1'])
    # Dropping last n rows using drop
    trimmed_data.drop(trimmed_data.tail(num_materias).index,
            inplace = True)

    return trimmed_data

def get_course_list(user_data):
    return user_data[user_data['NOTA'] > 6]['CODIGO'].unique()

def select_random_student(data : pd.DataFrame, max_tries : int, minimum_entry_year : int) -> int:
    id = 0
    tries = 0

    minimum_entry_year -= 2000
    
    while id == 0 and tries < max_tries:
        try:
            id = data[[int(x[3].split('/')[2].split(' ')[0]) >= minimum_entry_year for x in data.values]].sample()
            return int(id.ID_ANONIMO.iloc[0])
        except:
            id = 0
            tries += 1
    return 0