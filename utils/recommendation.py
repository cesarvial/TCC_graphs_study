import sys
from mapa_estudantes import get_disciplinas_matriz_844
import networkx as nx
import sys
from itertools import combinations
from datetime import datetime
import pandas as pd
import numpy as np
import random
import csv
import igraph as ig

files = [
    "../excel/dados_historicos_alunos_de_EngComputacaoCuritiba formados.csv",
    "../excel/dados_historicos_alunos_de_EngComputacaoCuritiba regulares.csv",
]

# ================================================================================== DADOS DE DISCIPLINAS ==========================================================================
# inicia as variáveis globais de acesso a disciplinas
def get_disciplinas_variables():
    dfs = []
    for file in files:
        dfs.append(pd.read_csv(file, delimiter=";"))

    df = pd.concat(dfs, ignore_index=True)
    df.rename(
        columns={"PERIODO": "PERIODO_CURSO", "PERIODO.1": "PERIODO_ANO"}, inplace=True
    )
    # df["INGRESSO"] = pd.to_datetime(df["INGRESSO"], format="%d/%m/%y")
    df["INGRESSO"] = pd.to_datetime(df["INGRESSO"], format="mixed")
    df["SEMESTRE"] = df["ANO"].astype(str) + "." + df["PERIODO_ANO"].astype(str)
    pd.set_option("display.width", 1000)
    # Obter os dados da matriz 844
    disciplinas_844 = get_disciplinas_matriz_844()
    # Dada uma disciplinas, busca o seu tipo
    def get_tipo_disciplina(disciplina):
        eletivas = pd.read_csv("../excel/Eletivas.csv", delimiter=",")
        mapa_eletivas = {}
        for index, row in eletivas.iterrows():
            mapa_eletivas[row["CODIGO"]] = row["DISCIPLINA"]
        if disciplina in disciplinas_844:
            return (
                disciplinas_844[disciplina].trilha
                if disciplinas_844[disciplina].trilha
                else "OBRIGATÓRIA"
            )
        elif disciplina in mapa_eletivas:
            return "ELETIVA"
        else:
            return "NÃO MAPEADA"
    # Obter um mapeamento de disciplinas equivalentes
    mapeamento_equivalentes = {}
    for disciplina in disciplinas_844.values():
        for equivalente in disciplina.disciplinas_equivalentes.keys():
            mapeamento_equivalentes[equivalente] = disciplina.codigo
    # Obter nome de disciplinas eletivas
    eletivas = pd.read_csv("../excel/Eletivas.csv", delimiter=",")
    mapa_eletivas = {}
    for index, row in eletivas.iterrows():
        mapa_eletivas[row["CODIGO"]] = row["DISCIPLINA"]
    df = df.replace({"CODIGO": mapeamento_equivalentes})
    df["DISCIPLINA"] = df["CODIGO"].apply(
        lambda x: disciplinas_844[x].disciplina if x in disciplinas_844 else None
    )
    df["TRILHA"] = df["CODIGO"].apply(get_tipo_disciplina)
    df_844 = df.loc[
    (df["INGRESSO"] >= datetime(2017, 1, 1)) & (df["INGRESSO"] <= datetime(2023, 1, 1))
    ]
    # Disciplinas eletivas de alunos da matriz 844
    eletivas = list(df_844.loc[df_844["DISCIPLINA"].isna()]["CODIGO"].unique())
    # Remover disciplinas com trilha NÃO MAPEADA ou ELETIVA
    df_844_curso = df_844.loc[
        (df_844["TRILHA"] != "NÃO MAPEADA") & (df_844["TRILHA"] != "ELETIVA")
    ]
    df_844_optativas = df_844_curso.loc[(df_844["TRILHA"] != "OBRIGATÓRIA")]
    return disciplinas_844, df_844_curso, df_844_optativas

# variáveis globais
disciplinas_844, df_844_curso, df_844_optativas = get_disciplinas_variables()

# Função auxiliar para verificar se os semestres são consecutivos
def semestres_consecutivos(semestre1, semestre2):
    ano1, periodo1 = map(int, semestre1.split("."))
    ano2, periodo2 = map(int, semestre2.split("."))
    
    if ano1 == ano2:
        return periodo1 + 1 == periodo2
    elif ano1 + 1 == ano2:
        return periodo1 == 2 and periodo2 == 1
    return False

# ================================================================================== DADOS DE ESTUDANTES ==========================================================================
# classe estudante para adicionar as trilhas
class estudante:
    def __init__(self, id_anonimo, status, ano_ingresso):
        self.id_anonimo = id_anonimo
        self.status = status
        self.ano_ingresso = ano_ingresso
        self.trilhas = []
        self.disciplinas = []

    def add_disciplina(self, d):
        self.disciplinas.append(d)
    
    def add_trilha(self, t):
        self.trilhas.append(t)

# função para verificar se um aluno teve seu ingresso antes ou depois de 2014
def beforeClasses(date):
    year = date.split('/')[2]
    if (int(year) < 14):
        return True
    return False

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

# função auxiliar para criar o grafo completo de relação de estudantes
def create_student_relation_graph_trilhas():
    hist = []
    # preenche as listas iniciais
    for file in files:
        print(file)
        with open(file, 'r') as csvfile:   
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                hist.append(row)
    # Remove todos os alunos que ingressaram antes de 2014 
    for i in range(len(hist)):
        if (i == len(hist)):
            break
        if (beforeClasses(hist[i]['INGRESSO'].split(" ")[0])):
            hist.pop(i)
            i = 0

    # Remove todos dados de reprovações (matérias repetidas)
    for i in range(len(hist)):
        for j in range(i, len(hist)):
            if (j == len(hist)):
                break
            if (hist[i]["ID_ANONIMO"] != hist[j]["ID_ANONIMO"]):
                break
            if (j < len(hist) and (i != j and (hist[i]["ID_ANONIMO"] == hist[j]["ID_ANONIMO"] and hist[i]["CODIGO"] == hist[j]["CODIGO"]))):
                hist.pop(j)
                j -= 5

    G = nx.Graph()
    # Adiciona todos os nós, que são os alunos
    # Sem colocar nenhum aluno pré-2014
    for line in hist:
        if (not beforeClasses(line['INGRESSO'].split(" ")[0])):
            if not G.has_node(line["ID_ANONIMO"]):
                G.add_node(line["ID_ANONIMO"])
    # Verifica quais são as matérias obrigatórias, que não serão levadas em conta
    optional = []
    with open('../texts/optativas.txt', 'r') as f:   
        lines = f.readlines()
        for l in lines:
            optional.append(l.split(" ")[0])
    trilhas = []
    with open("../texts/trilhas.txt") as f:
        for line in f.readlines():
            trilhas.append(line.split("\n")[0].split(";"))
    estudantes = []
    # adiciona todos os estudantes na lista
    for i in range(len(hist)):
        # o estudante deve estar no grafo
        if G.has_node(hist[i]["ID_ANONIMO"]):
            # verifica se o estudante já está na lista de estudantes, se não cria um novo
            e = next((x for x in estudantes if x.id_anonimo == hist[i]["ID_ANONIMO"]), None)
            if e == None:
                e = estudante(hist[i]["ID_ANONIMO"], hist[i]["SITUACAOALUNO"], hist[i]["INGRESSO"].split("/")[2])
                estudantes.append(e)
    # adiciona todas as disciplinas de estudantes na lista
    for i in range(len(hist)):
        for j in range(len(estudantes)):
            if (hist[i]["ID_ANONIMO"] == estudantes[j].id_anonimo):
                if (hist[i]["CODIGO"] in optional):
                    estudantes[j].add_disciplina(hist[i]["CODIGO"])
    # Adiciona as trilhas de cada estudante
    for e in estudantes:
        for t in trilhas:
            if (len(intersection(e.disciplinas, t)) >= 2):
                e.add_trilha(t[0])
    # Adiciona as arestas
    for i in range(len(estudantes)):
        for j in range(i, len(estudantes)):
            w = len(intersection(estudantes[i].trilhas, estudantes[j].trilhas))
            if (w > 0):
                G.add_edge(estudantes[i].id_anonimo, estudantes[j].id_anonimo, weight = w)
    # Remover as arestas com peso pequeno
    edges_remove = []
    for u, v, a in G.edges(data=True):
        if a["weight"] < 0:
            edges_remove.append([u, v])
    G.remove_edges_from(edges_remove)
    remove = [node for node, degree in dict(G.degree()).items() if degree == 0]
    G.remove_nodes_from(remove)
    H = ig.Graph.from_networkx(G)
    H.is_weighted()
    # retorna o grafo do networkx, o grafo do igraph, e a lista de estudantes
    return G, H, estudantes

# variáveis globais relacionadas ao grafo de estudantes
G, H, estudantes = create_student_relation_graph_trilhas()
# variável global com lista de trilhas e suas disciplinas
# Lista de trilhas com suas disciplinas
trilhas_map = []
with open("../texts/trilhas.txt") as f:
    for line in f.readlines():
        trilhas_map.append(line.split("\n")[0].split(";"))

def get_student_by_id(id):
    for e in estudantes:
        if (e.id_anonimo == id):
            return e.id_anonimo, e.trilhas, e.disciplinas
        
# ======================================================================================= FUNÇÕES PARA PARTIÇÃO ================================================================
# Comunidades utilizando o algoritmo de Leiden
def get_leiden_partition():
    partition = H.community_leiden(weights='weight', objective_function='modularity')
    comunidades = []
    for com in enumerate(partition.membership):
        if (len(comunidades) <= com[1]):
            comunidades.append([])
        comunidades[com[1]].append(H.vs()[com[0]]["_nx_name"])
    comunidades_trilhas = []
    for c in comunidades:
        comm = {"estudantes":[],
                "trilhas":[]}
        comm["estudantes"] = c
        em_trilha = []
        for trilha in trilhas_map:
            est_in_trilha = 0
            for e_id in range(len(c)-1):
                e_trilhas = get_student_by_id(c[e_id])[1]
                if (trilha[0] in e_trilhas):
                    est_in_trilha += 1
            if (est_in_trilha > 0):
                em_trilha.append([trilha[0], est_in_trilha])
        comm["trilhas"] = sorted(em_trilha, key=lambda t: t[1], reverse=True)
        comunidades_trilhas.append(comm)
    return comunidades_trilhas


# Comunidades utilizando o algoritmo dos kcliques
def get_kclique_partition():
    # função para buscar um único K-clique
    def get_kcliques_communities(G, k):
        g = G.copy()
        # remove as arestas com peso menor que 2
        to_remove = [(a,b) for a, b, attrs in g.edges(data=True) if attrs["weight"] < 2]
        g.remove_edges_from(to_remove)
        k_cliques = list(nx.community.k_clique_communities(g, k))
        k_cliques_list = []
        for set in k_cliques:
            k_cliques_list.append(list(set))
        # são os mesmos cliques presentes na análise do igraph (amém)
        return k_cliques_list
    all_k_cliques = []
    for k in range(3, 10):
        k_cliques = get_kcliques_communities(G, k)
        all_k_cliques.append({"k":k, "k_cliques":k_cliques})
    # Define uma estrutura de comunidades que possui uma lista de ids (os alunos) e uma lista de trilhas (ordenada e com o número de estudantes)
    # para cada k_clique
    k_cliques_comunidades = []
    for k_clique in all_k_cliques:
        complete_k_clique = {"k": k_clique["k"], "k_cliques":[]}
        for clique in k_clique["k_cliques"]:
            comm = {"estudantes":[],
                    "trilhas":[]}
            comm["estudantes"] = clique
            em_trilha = []
            for trilha in trilhas_map:
                est_in_trilha = 0
                for e_id in range(len(clique)-1):
                    e_trilhas = get_student_by_id(clique[e_id])[1]
                    if (trilha[0] in e_trilhas):
                        est_in_trilha += 1
                if (est_in_trilha > 0):
                    em_trilha.append([trilha[0], est_in_trilha])
            comm["trilhas"] = sorted(em_trilha, key=lambda t: t[1], reverse=True)
            complete_k_clique["k_cliques"].append(comm)
        k_cliques_comunidades.append(complete_k_clique)
    return k_cliques_comunidades

# passa como parâmetro a posição do vértice no grafo
def get_student_by_clique_pos(pos):
    return get_student_by_id(H.vs[pos]['_nx_name'])

# Partição utilizando o algoritmo dos cliques maximais
def get_max_cliques_partition():
    # Utilizando o mesmo grafo H, passa pelas arestas e procura os cliques
    H_cliques = H.copy()
    # remoção de arestas de peso 1
    H_cliques.es.select(weight=1).delete()
    cliques = H_cliques.maximal_cliques(min=3)
    # Define uma estrutura de cliques que possui uma lista de ids (os alunos) e uma lista de trilhas (ordenada e com número de alunos)
    cliques_trilhas = []
    for clique in cliques:
        cliq = {"estudantes":[],
                "trilhas":[],
                "disciplinas":[]}
        em_trilha = []  
        all_dis = [] 
        n_estudantes = 0    
        for c in clique:
            e_id = get_student_by_clique_pos(c)[0]
            n_estudantes += 1
            cliq["estudantes"].append(e_id)
            e = [e for e in estudantes if e.id_anonimo == e_id][0]
            # Adiciona todas as disciplinas que fazem parte das trilhas do estudante dentro da lista de discplinas do clique
            for t in e.trilhas:
                trilha = [tri for tri in trilhas_map if tri[0] == t][0]
                for d in e.disciplinas:
                    if (d in trilha):
                        all_dis.append(d)
        for trilha in trilhas_map:
            est_in_trilha = 0
            for c in clique:
                e_trilhas = get_student_by_clique_pos(c)[1]
                if (trilha[0] in e_trilhas):
                    est_in_trilha += 1
            if (est_in_trilha > 0):
                em_trilha.append([trilha[0], est_in_trilha])
        cliq["trilhas"] = sorted(em_trilha, key=lambda t: t[1], reverse=True)
        n_apperances = len(all_dis)
        # a 1a posição da disciplina mostra o número total de optativas realizadas
        cliq["disciplinas"].append(n_apperances)
        for d in all_dis:
            if d != "-":
                n_times = all_dis.count(d)
                # disciplina seguido pelo n de alunos que a realizou no clique
                cliq["disciplinas"].append([d, n_times])
                # evita inserções repetidas no futuro
                for idx, item in enumerate(all_dis):
                    if item == d:
                        all_dis[idx] = '-'
            
        cliques_trilhas.append(cliq)
    return cliques_trilhas

# ======================================================================================== FUNÇÕES PARA RECOMENDAÇÃO ========================================================================
# Dado um Ra, cria o grafo do caminho completo do estuante
def create_full_student_graph(csv_path):
    hist = []
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            hist.append(row)
    student_G = nx.DiGraph()
    # disciplinas 
    for line in hist:
        if not student_G.has_node(line["CODIGO"]):
            student_G.add_node(line["CODIGO"])
    # arestas        
    for i in range(len(hist)):
        course = hist[i]["CODIGO"]
        year = hist[i]["ANO"]
        semester = hist[i]["PERIODO.1"]
        # começou a análise de outro estudante
        j_init = i
        for j in range(j_init, len(hist)):
            # cria a aresta/adiciona peso nela
            edge1 = course
            edge2 = hist[j]["CODIGO"]
            if (semester == '1'):
                # deve ser no mesmo ano e no 2o periodo
                if hist[j]["ANO"] == year and hist[j]["PERIODO.1"] == '2':
                    if student_G.has_edge(edge1, edge2):
                        student_G[edge1][edge2]['weight'] += 1
                    else:
                        student_G.add_edge(edge1, edge2, weight = 1)
            else:
                # deve ser no próx ano e no 1o período
                if hist[j]["ANO"] == str(int(year)+1) and hist[j]["PERIODO.1"] == '1':
                    if student_G.has_edge(edge1, edge2):
                        student_G[edge1][edge2]['weight'] += 1
                    else:
                        student_G.add_edge(edge1, edge2, weight = 1)
    return student_G


# Dado uma disciplina, retorna uma lista de cliques nos quais ela pertence
def get_course_cliques(codigo, cliques_trilhas):
    cs = []
    for clique in cliques_trilhas:
        for d in clique['disciplinas'][1:]:
            if codigo == d[0]:
                cs.append(clique)
                break
    
    return cs

# Dado uma lista de disciplinas, retorna a melhor comunidade para ela
def get_course_community(disciplinas, comunidades_trilhas):
    # vetor para guardar as comunidades junto com a quantidade de estudantes nas trilhas de interesse
    comunidades_count = []
    for c in comunidades_trilhas:
        count = 0
        for node in disciplinas:
            for t in c['trilhas']:
                for full_t in trilhas_map:
                    if full_t[0] == t[0]:
                        if node in full_t:
                            count += t[1]
        comunidades_count.append({"community": c, "count": count})
    best_c = comunidades_count[0]
    for c in comunidades_count:
        if c["count"] > best_c["count"]:
            best_c = c
    return best_c

# Dado uma lista de disciplinas, retorna a melhor comunidade para ela
def get_course_k_clique(disciplinas, k_cliqes):
    # vetor para guardar as comunidades junto com a quantidade de estudantes nas trilhas de interesse
    comunidades_count = []
    for c in k_cliqes:
        count = 0
        for node in disciplinas:
            for t in c['trilhas']:
                for full_t in trilhas_map:
                    if full_t[0] == t[0]:
                        if node in full_t:
                            count += t[1]
        comunidades_count.append({"community": c, "count": count})
    best_c = comunidades_count[0]
    for c in comunidades_count:
        if c["count"] > best_c["count"]:
            best_c = c
    return best_c

# retorna as disciplinas resultantes como um único conjunto, levando em conta todos os cliques
def get_recommended_courses_all_cliques(e_cliques, opt_nodes_with_edges):
    all_rec_dis = []
    n_dis = 0
    # para buscar a recomendação divide a quantidade de vezes que uma disciplina apareceu em todos os cliques pela quantidade total de disciplinas
    # Conta o número total de disciplinas
    for clique in e_cliques:
        n_dis += clique['disciplinas'][0]
    # Adiciona todas as disicplinas em um vetor
    for clique in e_cliques:
        for d in clique['disciplinas'][1:]:
            if d[0] not in opt_nodes_with_edges:
                for i in range(d[1]):
                    all_rec_dis.append(d[0])
    # Pega o valor das disciplinas
    rec_dis = []
    for d in all_rec_dis:
        if d != '-':
            nd = all_rec_dis.count(d)
            rec_dis.append([d, 10*(nd/n_dis)])
            all_rec_dis[:] = [x if x != d else '-' for x in all_rec_dis]
    return rec_dis

# retorna as disciplinas resultantes 
def get_recommended_courses_cliques(e_cliques, opt_nodes_with_edges):
    rec_dis = []
    n_dis = 0
    # Para cada clique, divide a quantidade de vezes que uma disciplina apareceu nele pela quantidade total de disciplinas
    for clique in e_cliques:
        clique_rec_dis = []
        curr_clique_rec_dis = []
        n_dis = clique['disciplinas'][0]
        for d in clique['disciplinas'][1:]:
            if d[0] not in opt_nodes_with_edges:
                for i in range(d[1]):
                    clique_rec_dis.append(d[0])
        # calcula o valor de cada disciplina para esse clique
        for d in clique_rec_dis:
            if d != '-':
                nd = clique_rec_dis.count(d)
                curr_clique_rec_dis.append([d, nd/n_dis])
                clique_rec_dis[:] = [x if x != d else '-' for x in clique_rec_dis]
        rec_dis.append(curr_clique_rec_dis)
    return rec_dis

# Dado um grafo, retorna uma lista de disciplinas recomendadas com a sua probabilidade de ser realizada
# Utilizando dados dos cliques encontrados
def get_recommended_courses_from_cliques(g, cliques_trilhas, join_cliques=True):
    # pega as disciplinas optativas existentes
    disciplinas = df_844_optativas["CODIGO"].unique()
    nodes_with_edges = [node for node in g.nodes() if g.degree[node] > 0]
    opt_nodes_with_edges = [node for node in disciplinas
                            if node in nodes_with_edges]
    # caso não tenham disciplinas optativas existentes, roda com base no interesse
    # TODO: no momento iremos apenas ignorar esse caso
    if (len(opt_nodes_with_edges) == 0):
        print("Sem disciplinas optativas já realizadas. Sem recomendações.")
        return []
    # Caso tenham disciplinas, busca os cliques de cada uma delas
    e_cliques = []
    for node in opt_nodes_with_edges:
        course_cliques = get_course_cliques(node, cliques_trilhas)
        if (len(course_cliques) > 0):
            e_cliques.append(get_course_cliques(node, cliques_trilhas))
    if len(e_cliques) == 0:
        return []
    if (join_cliques):
        return get_recommended_courses_all_cliques(e_cliques[0], opt_nodes_with_edges)
    else:
        return get_recommended_courses_cliques(e_cliques[0], opt_nodes_with_edges)
    
# Dado um grafo, retoruna uma lista de disciplinas recomendadas com a sua probabilidade de ser realizada
# Utilizando dados das comunidades encontradas
def get_recommended_courses_from_communities(g, comunidades_trilhas):
    # pega as disciplinas optativas existentes
    disciplinas = df_844_optativas["CODIGO"].unique()
    nodes_with_edges = [node for node in g.nodes() if g.degree[node] > 0]
    opt_nodes_with_edges = [node for node in disciplinas
                            if node in nodes_with_edges]
    # caso não tenham disciplinas optativas existentes, roda com base no interesse
    # TODO: no momento iremos apenas ignorar esse caso
    if (len(opt_nodes_with_edges) == 0):
        print("Sem disciplinas optativas já realizadas. Sem recomendações.")
        return []
    # Busca a comunidade em que o estudante se encaixa
    community = get_course_community(opt_nodes_with_edges, comunidades_trilhas)
    n_dis = 0
    all_dis_count = []
    for e in community['community']['estudantes']:
        ds = get_student_by_id(e)[2]
        for d in ds:
            all_dis_count.append(d)
            n_dis += 1
    # calcula o valor de cada disciplina
    rec_dis = []
    for d in all_dis_count:
        if d != '-':
            nd = all_dis_count.count(d)
            rec_dis.append([d, nd/n_dis])
            all_dis_count[:] = [x if x != d else '-' for x in all_dis_count]
    return rec_dis

# Dado um grafo, retoruna uma lista de disciplinas recomendadas com a sua probabilidade de ser realizada
# Utilizando dados das comunidades encontradas
def get_recommended_courses_from_k_cliques(g, pos, k_cliques_comunidades):
    curr_cliques = k_cliques_comunidades[pos]["k_cliques"]
    # pega as disciplinas optativas existentes
    disciplinas = df_844_optativas["CODIGO"].unique()
    nodes_with_edges = [node for node in g.nodes() if g.degree[node] > 0]
    opt_nodes_with_edges = [node for node in disciplinas
                            if node in nodes_with_edges]
    # caso não tenham disciplinas optativas existentes, roda com base no interesse
    # TODO: no momento iremos apenas ignorar esse caso
    if (len(opt_nodes_with_edges) == 0):
        print("Sem disciplinas optativas já realizadas. Sem recomendações.")
        return []
    # Busca a comunidade em que o estudante se encaixa
    community = get_course_k_clique(opt_nodes_with_edges, curr_cliques)
    n_dis = 0
    all_dis_count = []
    for e in community['community']['estudantes']:
        ds = get_student_by_id(e)[2]
        for d in ds:
            all_dis_count.append(d)
            n_dis += 1
    # calcula o valor de cada disciplina
    rec_dis = []
    for d in all_dis_count:
        if d != '-':
            nd = all_dis_count.count(d)
            rec_dis.append([d, nd/n_dis])
            all_dis_count[:] = [x if x != d else '-' for x in all_dis_count]
    return rec_dis

# Dado uma lista de disciplinas optativas que um estudante fez e o resultado de uma recomendação
# Retorna os valores de precision and recall
def calc_precision_and_recall(opts, recom, k=-1):
    if (len(opts) == 0 or len(recom) == 0):
        return 0.0, 0.0
    # Result: os elementos que foram recomendados pelo algoritmo
    result = []
    for r in recom:
        result.append(r[0])
    # Relevant elements: os elementos relevantes para o resultado (as disciplinas que o estudante efetivamente pegou)
    relevant_elements = opts
    # True Positives intersecção entre o resultado e os elementos relevantes:
    if (k == -1):
        true_positives = list(set(result[0:k]) & set(relevant_elements))
    else:
        true_positives = list(set(result[0:k]) & set(relevant_elements))
    # Precision: número de verdadeiros positivos pelo número de valores recomendados
    precision = len(true_positives) / len(result)
    # Recall: número de verdadeiros positivos pelo número de valores nos recomendados
    recall = len(true_positives) / len(relevant_elements)
    return precision, recall

# =============================================================================================== MAIN ==============================================================================

# Função que dado um dataset do percurso de um estudante, retorna uma lista de discplinas recomendadas
def recommend_dis(csv_path, alg_sel):
    print("CSV path:", csv_path)
    print("Alg selecionado:", alg_sel)
    # Inicialmente cria o grafo do estudante
    student_G = create_full_student_graph(csv_path)
    print(student_G)
    # Depois, busca as partições do algoritmo selecionado
    # Caso leiden
    if alg_sel == 'Comunidades':
        partitions = get_leiden_partition()
        rec_dis = get_recommended_courses_from_communities(student_G, partitions)
        return sorted(rec_dis, key=lambda x: x[1], reverse=True)
    elif alg_sel == 'Kcliques':
        partitions = get_kclique_partition()
        rec_dis = get_recommended_courses_from_k_cliques(student_G, 3, partitions)
        return sorted(rec_dis, key=lambda x: x[1], reverse=True)
    elif alg_sel == 'CliquesMaximais':
        partitions = get_max_cliques_partition()
        rec_dis = get_recommended_courses_from_cliques(student_G, partitions, True)
        return sorted(rec_dis, key=lambda x: x[1], reverse=True)
    else:
        print("Tipo de algoritmo inválido. Inputs possíveis são:")
        print("'Comunidades';")
        print("'Kcliques';")
        print("'CliquesMaximais';")
        return

def help():
    print("Argumentos para execução:")
    print("Caminho para excel com dados de um aluno. Deve ser um percurso de um estudante incompleto;")
    print("Tipo de algoritmo que será executado. Inputs possíveis são: ")
    print("'Comunidades';")
    print("'Kcliques';")
    print("'CliquesMaximais';")

def main():
    print(sys.argv)
    if (len(sys.argv) < 3):
        help()
        return
    rec = recommend_dis(sys.argv[1], sys.argv[2])
    print("Disciplinas recomendadas:")
    print(rec)

if __name__ == '__main__':
    main()