import os
from typing import Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from state import MultiAgentState
from supervisor import run_supervisor_node
from agents.research_agent import run_research_node
from agents.analyst_agent import run_analyst_node
from logger import get_agent_logger

load_dotenv()

logger = get_agent_logger()


def route_supervisor(state: MultiAgentState) -> Literal["researcher", "analyst", "__end__"]:
    """
    Arista condicional que dirige el flujo según la decisión del Supervisor.
    """
    next_node = state.get("next")
    logger.info(f"Ruteo de Supervisor a: {next_node}")
    if next_node == "researcher":
        return "researcher"
    elif next_node == "analyst":
        return "analyst"
    else:
        return END


def create_orchestrator_graph():
    """
    Construye y regresa el StateGraph orquestador multi-agente.
    """
    logger.info("Construyendo Grafo Multi-Agente...")
    builder = StateGraph(MultiAgentState)

    # Definir Nodos
    builder.add_node("supervisor", run_supervisor_node)
    builder.add_node("researcher", run_research_node)
    builder.add_node("analyst", run_analyst_node)

    # Flujo de entrada al Supervisor
    builder.add_edge(START, "supervisor")

    # Aristas condicionales desde el Supervisor hacia los agentes especialistas
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            END: END
        }
    )

    # Tras ejecutar un agente especialista, el control regresa al Supervisor
    builder.add_edge("researcher", "supervisor")
    builder.add_edge("analyst", "supervisor")

    graph = builder.compile()
    logger.info("Grafo Multi-Agente construido exitosamente.")
    return graph


# Instancia del grafo compilado
graph = create_orchestrator_graph()
