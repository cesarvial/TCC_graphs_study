from dataclasses import dataclass
import traceback

"""
Cada disciplina cursada possui codigo, período, ano, nota e carga horária
"""
@dataclass
class DisciplinaCursada:
    codigo: str
    periodo: int
    ano: int
    nota: float
    carga_horaria: int

    @classmethod
    def from_dict(cls, data: dict):
        try:
            return cls(
                codigo=data["CODIGO"],
                periodo=int(data["PERIODO"]),
                ano=int(data["ANO"]),
                nota=float(data["NOTA"].replace(",", ".")) if data["NOTA"] else -1,
                carga_horaria=int(data["CH"]),
            )
        except:
            traceback.print_exc()
            return None

    def periodo_consecutivo(self, other: "DisciplinaCursada"):
        return (self.ano == other.ano and self.periodo == 1 and other.periodo == 2) or (
            (self.ano + 1 == other.ano) and self.periodo == 2 and other.periodo == 1
        )

