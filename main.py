from langchain_core.messages import HumanMessage
from graph import create_multi_agent_graph


def main():
    print("=" * 65)
    print("Iniciando Orquestador Multi-Agente de Rapanui (LangGraph)")
    print("=" * 65)

    app = create_multi_agent_graph()
    config = {"configurable": {"thread_id": "test-multi-agent-1"}}

    # Consulta compuesta que requiere investigación y cálculo
    consulta = (
        "¿Cuáles son los beneficios corporativos de Rapanui en cuanto a salud y gimnasio, "
        "y cuánto costaría cubrir ese paquete para 25 empleados?"
    )

    print(f"\nUsuario: {consulta}\n")
    print("-" * 65)
    print("Traza de ejecución de los agentes:\n")

    inputs = {"messages": [HumanMessage(content=consulta)], "step_count": 0}

    # Ejecución con streaming para ver qué agente actúa en cada paso
    for output in app.stream(inputs, config=config):
        for node_name, node_output in output.items():
            print(f"👉 [Nodo ejecutado]: {node_name}")
            if "next" in node_output:
                print(f"   Decisión del Supervisor: delegar a -> {node_output['next']}")
            if "messages" in node_output and node_output["messages"]:
                ultimo = node_output["messages"][-1]
                print(f"   Aporte de {getattr(ultimo, 'name', node_name)}:\n{ultimo.content}\n")
            print("-" * 65)


if __name__ == "__main__":
    main()
