import os
from typing import Literal, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from state import MultiAgentState
from logger import get_agent_logger

load_dotenv()

logger = get_agent_logger()

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-3-flash-preview")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MAX_ITERATIONS = 5


class RouterResponse(BaseModel):
    next_agent: Literal["researcher", "analyst", "FINISH"] = Field(
        description="Siguiente agente que debe intervenir. Si ya se investigó y analizó para dar la respuesta final, responder 'FINISH'."
    )
    reasoning: str = Field(
        description="Explicación breve de por qué se toma esta decisión de ruteo."
    )


SUPERVISOR_PROMPT = (
    "Sos el Supervisor Orquestador del sistema multi-agente de investigación y análisis.\n"
    "Tu tarea es evaluar el estado actual de la conversación y decidir cuál es el siguiente paso lógico.\n\n"
    "AGENTES DISPONIBLES:\n"
    "1. `researcher`: Agente de Búsqueda/Investigación. Encargado de buscar información en la base de datos documental (Vector DB).\n"
    "2. `analyst`: Agente de Análisis/Síntesis. Encargado de analizar los datos obtenidos, sintetizarlos y redactar la respuesta final en el idioma destino requerido.\n"
    "3. `FINISH`: Señal para finalizar la ejecución cuando la respuesta final ya ha sido generada por el analista y la tarea está completa.\n\n"
    "REGLAS DE FLUJO Y SUPERVISIÓN:\n"
    "- Si la pregunta del usuario recién ingresa y no hay reportes de investigación, debes delegar a `researcher`.\n"
    "- Si el `researcher` ya aportó la información o reportó que no la encontró, el siguiente paso DEBE ser `analyst` para que procese los hallazgos y redacte la respuesta final.\n"
    "- Si el `analyst` ya ha elaborado la respuesta final en el idioma correspondiente (o ya hay un mensaje de respuesta final), debes seleccionar `FINISH`.\n"
    "- No permitas bucles repetidos entre agentes a menos que la información sea contradictoria o insuficiente y requiera un reintento específico.\n"
    "- Límite de seguridad: Si ya se han realizado múltiples iteraciones sin concluir, selecciona `FINISH`."
)


def run_supervisor_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Nodo Supervisor que actúa como router inteligente utilizando Salida Estructurada (Structured Output).
    """
    iterations = state.get("iterations", 0) + 1
    logger.info(f"--- NODO SUPERVISOR INICIADO (Iteración #{iterations}) ---")

    if iterations >= MAX_ITERATIONS:
        logger.warning(f"Alcanzado el límite máximo de iteraciones ({MAX_ITERATIONS}). Forzando 'FINISH'.")
        return {
            "next": "FINISH",
            "iterations": iterations
        }

    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0.0
    )

    structured_llm = llm.with_structured_output(RouterResponse)

    messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + list(state["messages"])

    logger.info("Invocando LLM Supervisor para evaluación de flujo...")
    decision: RouterResponse = structured_llm.invoke(messages)

    logger.info(f"Decisión Supervisor: Next='{decision.next_agent}' | Razonamiento: {decision.reasoning}")

    return {
        "next": decision.next_agent,
        "iterations": iterations
    }
