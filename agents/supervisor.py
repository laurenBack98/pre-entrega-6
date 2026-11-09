from typing import Literal
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from state import MultiAgentState

# Esquema estructurado para la decisión del Supervisor
class DecisionSupervisor(BaseModel):
    next: Literal["investigador", "analista", "FINISH"] = Field(
        description="Elige 'investigador' para buscar información, 'analista' para calcular costos/métricas, o 'FINISH' si la consulta está respondida."
    )
    razon: str = Field(description="Breve justificación de la delegación.")


_llm = ChatOllama(model="qwen2.5:7b", temperature=0)
_supervisor_llm = _llm.with_structured_output(DecisionSupervisor)

SUPERVISOR_PROMPT = """Eres el Supervisor de un sistema multi-agente en Rapanui.
Tu rol es coordinar a dos especialistas:
1. 'investigador': Busca políticas internas, beneficios, normas HACCP, ISO y franquicias.
2. 'analista': Realiza cálculos de costos, presupuestos de beneficios o proyecciones numéricas.

Reglas:
- Si la pregunta pide información documental, delega a 'investigador'.
- Si la pregunta pide cálculos numéricos o costos, delega a 'analista' (o a 'investigador' primero si faltan datos).
- Si los especialistas ya aportaron la información necesaria para responder la consulta inicial, responde 'FINISH'.
"""


def supervisor_node(state: MultiAgentState):
    """Nodo orquestador que toma la decisión de enrutamiento."""
    # Salvaguarda contra bucles infinitos (máximo 6 pasos)
    if state.get("step_count", 0) >= 6:
        return {"next": "FINISH"}

    mensajes = [SystemMessage(content=SUPERVISOR_PROMPT)] + state["messages"]
    decision = _supervisor_llm.invoke(mensajes)

    return {"next": decision.next}
