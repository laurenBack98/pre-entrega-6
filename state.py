from typing import Literal, Optional
from langgraph.graph import MessagesState


class MultiAgentState(MessagesState):
    """
    Estado compartido del sistema multi-agente jerárquico.
    Hereda 'messages' (Annotated[list[AnyMessage], add_messages]).
    """
    # Indica qué agente debe intervenir a continuación o si finaliza
    next: Literal["researcher", "analyst", "FINISH"]
    
    # Contexto estructurado o datos procesados entre agentes
    research_data: Optional[str] = None
    analysis_data: Optional[str] = None
    
    # Salvaguarda contra bucles infinitos (Supervisor Infinito)
    step_count: int = 0
