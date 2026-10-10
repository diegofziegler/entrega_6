import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from state import MultiAgentState
from rag import search_context_sync
from supervisor import extract_error_code, build_error_message
from logger import get_agent_logger

load_dotenv()

logger = get_agent_logger()

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-3-flash-preview")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


@tool
def buscar_en_vectorstore(query: str) -> str:
    """
    Busca información en la base de datos vectorial de documentos históricos (Karate Uechi-Ryu, Pangai-noon, etc.).
    Las consultas a la base deben realizarse siempre en ESPAÑOL.
    """
    logger.info(f"Tool buscar_en_vectorstore ejecutada con query: '{query}'")
    result = search_context_sync(query, k=4)
    return f"RESULTADOS DE BÚSQUEDA (Fuentes: {result['sources']}):\n{result['context']}"


RESEARCHER_SYSTEM_PROMPT = (
    "Eres un Agente Especialista en Búsqueda e Investigación documental.\n"
    "Tu ÚNICA función es consultar la base de datos vectorial mediante la herramienta `buscar_en_vectorstore` "
    "para extraer información precisa en español relacionada con la consulta.\n"
    "IMPORTANTE:\n"
    "1. Siempre debes realizar las búsquedas en ESPAÑOL, ya que los documentos están redactados en español.\n"
    "2. Presenta de forma clara y objetiva los hallazgos encontrados, citando las fuentes si las hay.\n"
    "3. Si la base de datos no contiene información sobre el tema, acláralo explícitamente.\n"
    "4. No realices análisis finales ni traducciones complejas de idioma; concéntrate en recolectar y resumir la evidencia documental."
)


def run_research_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Nodo wrapper para el Agente de Investigación con manejo elegante de excepciones.
    """
    logger.info("--- NODO RESEARCHER INICIADO ---")

    try:
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL_NAME,
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )

        agent = create_react_agent(
            model=llm,
            tools=[buscar_en_vectorstore],
            prompt=RESEARCHER_SYSTEM_PROMPT
        )

        input_messages = list(state["messages"])
        logger.info(f"Invocando Agente de Investigación con {len(input_messages)} mensajes...")
        result = agent.invoke({"messages": input_messages})

        last_message = result["messages"][-1]

        researcher_message = AIMessage(
            content=f"[REPORTE DE INVESTIGACIÓN]\n{last_message.content}",
            name="investigador"
        )

        logger.info("--- NODO RESEARCHER FINALIZADO ---")
        return {
            "messages": [researcher_message]
        }

    except Exception as e:
        logger.error(f"Excepción en nodo Researcher: {e}", exc_info=True)
        error_code = extract_error_code(e)
        error_msg = build_error_message(error_code)

        error_message = AIMessage(
            content=error_msg,
            name="investigador"
        )

        logger.info("--- NODO RESEARCHER FINALIZADO CON ERROR ---")
        return {
            "messages": [error_message]
        }
