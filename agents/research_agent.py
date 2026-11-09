from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from tools import buscar_datos_rapanui
from state import MultiAgentState

# Modelo local ligero para CPU
_llm = ChatOllama(model="qwen2.5:3b", temperature=0)
_llm_with_tool = _llm.bind_tools([buscar_datos_rapanui])

SYSTEM_PROMPT = """Eres el Especialista de Investigación de Rapanui.
Tu único objetivo es buscar información documental verídica usando la herramienta disponible.
Responde de forma clara y concisa, citando siempre las fuentes encontradas."""


def research_node(state: MultiAgentState):
    """Nodo especialista en consultar la base de conocimiento vectorial/híbrida."""
    mensajes = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    
    # 1. El modelo decide y ejecuta la búsqueda si hace falta
    respuesta = _llm_with_tool.invoke(mensajes)
    
    # Si generó una llamada a la herramienta, la ejecutamos directamente
    if respuesta.tool_calls:
        tool_call = respuesta.tool_calls[0]
        argumentos = tool_call["args"]
        resultado = buscar_datos_rapanui.invoke(argumentos)
        
        # Le pedimos la síntesis final de lo recuperado
        mensajes_con_contexto = mensajes + [
            respuesta,
            HumanMessage(content=f"Resultado de la búsqueda:\n{resultado}\nSintetiza la respuesta:")
        ]
        respuesta_final = _llm.invoke(mensajes_con_contexto)
        contenido = respuesta_final.content
    else:
        contenido = respuesta.content

    return {
        "messages": [HumanMessage(content=contenido, name="investigador")],
        "datos_investigacion": contenido,
        "step_count": state.get("step_count", 0) + 1,
    }
