import os
from typing import Annotated, Sequence, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class MultiAgentState(TypedDict):
    """
    Estado compartido estructurado para el orquestador multi-agente.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: str
    idioma_destino: str
    task_completed: bool
    iterations: int
