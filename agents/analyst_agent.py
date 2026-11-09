from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from tools import calcular_costos_beneficios
from state import MultiAgentState

_llm = ChatOllama(model="qwen2.5:3b", temperature=0)
_llm_with_tool = _llm.bind_tools([calcular_costos_beneficios])

SYSTEM_PROMPT = """Eres el Especialista en Análisis Financiero y Métricas de Rapanui.
Tu tarea es realizar cálculos numéricos, estimaciones de costos laborales y proyecciones usando tu herramienta.
Presenta las cifras de forma prolija y estructurada."""


def analyst_node(state: MultiAgentState):
    """Nodo especialista en procesamiento cuantitativo y proyecciones."""
    mensajes = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    respuesta = _llm_with_tool.invoke(mensajes)
    
    if respuesta.tool_calls:
        tool_call = respuesta.tool_calls[0]
        argumentos = tool_call["args"]
        resultado = calcular_costos_beneficios.invoke(argumentos)
        
        mensajes_con_contexto = mensajes + [
            respuesta,
            HumanMessage(content=f"Resultado del cálculo:\n{resultado}\nPresenta el reporte:")
        ]
        respuesta_final = _llm.invoke(mensajes_con_contexto)
        contenido = respuesta_final.content
    else:
        contenido = respuesta.content

    return {
        "messages": [HumanMessage(content=contenido, name="analista")],
        "datos_analisis": contenido,
        "step_count": state.get("step_count", 0) + 1,
    }
