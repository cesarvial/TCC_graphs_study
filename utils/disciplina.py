from dataclasses import dataclass
import traceback
from typing import Dict, List

trilhas = {
    960: "Controle",
    961: "Processamento Gráfico",
    962: "Sistemas Inteligentes",
    963: "Algoritmos E Complexidade",
    964: "Redes De Computadores",
    965: "Engenharia De Software",
    966: "Otim, Mod Analíticos E Simul",
    967: "Física",
    968: "Banco De Dados",
    969: "Interação Hum",
    970: "Engenharia Biomédica",
    971: "Sistemas Embarcados",
    972: "Desenv Bas Em Plataforma",
    973: "Optativas Isoladas"
}

def get_trilha(trilha: int) -> str:
    return trilhas.get(trilha, None)

@dataclass
class Disciplina:
    periodo: int
    trilha: str
    codigo: str
    disciplina: str
    modelo_disciplina: str
    aulas_teoricas_semanais: int
    aulas_praticas_semanais: int
    total_de_aulas_semanais: int
    total_de_aulas_de_aps: int  # Atividade Prática Supervisionada
    total_de_aulas_de_apcc: int  # Atividade Prática como Componente Curricular
    total_de_horas_de_ad: int  # Atividade a Distância
    carga_horaria_total: int
    pre_requisitos: List[str]
    disciplinas_equivalentes: Dict[str, int]

    @classmethod
    def from_dict(cls, data: dict):
        trilha = data["[OPT]"].strip().replace("[", "").replace("]", "")
        try:
            disciplina = cls(
                periodo=int(data["Período"]),
                trilha = int(trilha) if trilha else None,
                codigo=data["Código"],
                disciplina=data["Disciplina"],
                modelo_disciplina=data["Modelo de disciplina"],
                aulas_teoricas_semanais=int(data["Aulas teóricas semanais"]),
                aulas_praticas_semanais=int(data["Aulas práticas semanais"]),
                total_de_aulas_semanais=int(data["Total de aulas semanais"]),
                total_de_aulas_de_aps=int(data["Total de aulas de APS"]),
                total_de_aulas_de_apcc=int(data["Total de aulas de APCC"]),
                total_de_horas_de_ad=int(data["Total de horas de AD"]),
                carga_horaria_total=int(data["Carga horária total"]),
                pre_requisitos=list(filter(lambda x: x != "", data["Pré-requisito(s)"].strip().split(","))),
                disciplinas_equivalentes={},
            )
            disciplinas_eq = data["Disciplina_EQ"].strip()
            cht_eq = data["CHT_EQ"].strip()

            if disciplinas_eq != '':
                for d, c in zip(disciplinas_eq.split(" "), cht_eq.split(" ")):
                    disciplina.disciplinas_equivalentes[d] = int(c)

            return disciplina

        except:
            print(data)
            print(data["Disciplina_EQ"].split(" "))
            print(data["CHT_EQ"].split(" "))
            traceback.print_exc()
            return None
