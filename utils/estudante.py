from dataclasses import dataclass, field
from disciplina_cursada import DisciplinaCursada
from datetime import date, datetime
from typing import List
from enum import Enum
import traceback

class StatusEstudante(Enum):
    DESISTENTE = "Desistente"
    FORMADO = "Formado"
    REGULAR = "Regular"
    TRANCADO = "Trancado"
    MUDOU_CURSO = "Mudou de Curso"
    SEM_CURSAR = "Desistente (sem Cursar)"
    JUBILADO = "Jubilado"
    FALECIDO = "Falecido"
    TRANSFERIDO = "Transferido"
    ERRO_DE_CADASTRO = "Erro de cadastro"
    AFASTADO = "Afastado"


"""
Cada estudante possui um id anonimo, data de ingresso, cr, status e uma lista de disciplinas cursadas
"""
@dataclass
class Estudante:
    id: int
    ingresso: date
    cr: float
    status: StatusEstudante
    disciplinas: List[DisciplinaCursada] = field(default_factory=lambda: [])

    def add_disciplina(self, disciplina: DisciplinaCursada):
        self.disciplinas.append(disciplina)

    def add_disciplina_from_dict(self, disciplina: dict):
        self.disciplinas.append(DisciplinaCursada.from_dict(disciplina))

    @classmethod
    def from_dict(cls, data: dict):
        try:
            return cls(
                id=int(data["ID_ANONIMO"]),
                ingresso=datetime.strptime(data["INGRESSO"][:8], "%d/%m/%y"),
                cr=float(data["CR"].replace(",", ".")),
                status=StatusEstudante(data["SITUACAOALUNO"])
            )
        except:
            print(data)
            traceback.print_exc()
            print( "Returing None")
            return None

    def sort_disciplinas(self, reverse: bool = False):
        self.disciplinas.sort(key=lambda x: (x.ano, x.periodo), reverse=reverse)
