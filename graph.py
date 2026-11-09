from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import MultiAgentState
from agents.supervisor import supervisor_node
from agents.research_agent import research_node
from agents.analyst_agent import analyst_node


def router(state: MultiAgentState):
    """Función de enrutamiento basada en la decisión del supervisor."""
    siguiente = state.get("next")
    if siguiente == "investigador":
        return "investigador"
    elif siguiente == "analista":
        return "analista"
    else:
        return END


def create_multi_agent_graph():
    """Compila el grafo jerárquico orquestado por el Supervisor."""
    builder = StateGraph(MultiAgentState)

    # 1. Definición de nodos
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("investigador", research_node)
    builder.add_node("analista", analyst_node)

    # 2. Flujo inicial: Entrada siempre al supervisor
    builder.add_edge(START, "supervisor")

    # 3. Aristas condicionales desde el supervisor
    builder.add_conditional_edges(
        "supervisor",
        router,
        {
            "investigador": "investigador",
            "analista": "analista",
            END: END,
        },
    )

    # 4. Los especialistas devuelven el control al supervisor (ciclo)
    builder.add_edge("investigador", "supervisor")
    builder.add_edge("analista", "supervisor")

    # 5. Checkpointer para trazabilidad y memoria
    memory = MemorySaver()
    app = builder.compile(checkpointer=memory)
    return app
