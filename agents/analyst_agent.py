import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from state import MultiAgentState
from logger import get_agent_logger

load_dotenv()

logger = get_agent_logger()

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-3-flash-preview")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "Español")


def run_analyst_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Nodo wrapper para el Agente de Análisis/Síntesis.
    Procesa la información recolectada por el Investigador, valida la coherencia
    y redacta la respuesta final rigurosamente en el `idioma_destino`.
    """
    logger.info("--- NODO ANALYST INICIADO ---")

    idioma_destino = state.get("idioma_destino") or DEFAULT_LANGUAGE

    logger.info(f"Idioma destino configurado: '{idioma_destino}'")

    system_prompt = (
        f"Sos un Agente Especialista en Análisis, Síntesis y Redacción.\n"
        f"Tu objetivo principal es tomar los datos de investigación recopilados por el investigador, "
        f"analizarlos en profundidad y redactar una respuesta final clara, completa y bien estructurada.\n\n"
        f"REGLA DE ORO DE IDIOMA:\n"
        f"Debes redactar la respuesta FINAL EXCLUSIVAMENTE en el siguiente idioma: **{idioma_destino}**.\n"
        f"Incluso si los datos de investigación recopilados están en Español o en otro idioma, tu síntesis final "
        f"debe traducirse y adaptarse culturalmente al idioma de destino: **{idioma_destino}**.\n\n"
        f"SI LOS DATOS SON INSUFICIENTES O NO SE ENCONTRÓ INFORMACIÓN:\n"
        f"Explica amablemente en idioma **{idioma_destino}** que la base de datos documental del sistema no contiene "
        f"información para responder la pregunta realizada."
    )

    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0.2
    )

    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

    logger.info(f"Invocando LLM Analista para síntesis en '{idioma_destino}'...")
    response = llm.invoke(messages)

    analyst_message = AIMessage(
        content=f"[RESPUESTA FINAL - ANALISTA]\n{response.content}",
        name="analista"
    )

    logger.info("--- NODO ANALYST FINALIZADO ---")
    return {
        "messages": [analyst_message]
    }
