import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage

from state import MultiAgentState
from supervisor import extract_error_code, build_error_message
from logger import get_agent_logger
from llm import get_llm

load_dotenv()

logger = get_agent_logger()

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "Español")


def run_analyst_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Nodo wrapper para el Agente de Análisis/Síntesis con reglas estrictas de no-alucinación
    y manejo elegante de excepciones.
    """
    logger.info("--- NODO ANALYST INICIADO ---")

    idioma_destino = state.get("idioma_destino") or DEFAULT_LANGUAGE
    logger.info(f"Idioma destino configurado: '{idioma_destino}'")

    system_prompt = (
        f"Sos un Agente Especialista en Análisis, Síntesis y Redacción.\n"
        f"Tu objetivo principal es tomar ÚNICAMENTE los datos de investigación recopilados por el Agente Investigador, "
        f"analizarlos y redactar una respuesta final clara, completa y bien estructurada.\n\n"
        f"REGLA ESTRICTA DE GROUNDING (CERO CONOCIMIENTO INTERNO/EXTERNO):\n"
        f"1. Está ABSOLUTAMENTE PROHIBIDO utilizar tu propio conocimiento previo, cultura general o entrenamiento general para responder la pregunta.\n"
        f"2. Tu ÚNICA fuente de información permitida es el [REPORTE DE INVESTIGACIÓN] proporcionado por el investigador.\n"
        f"3. Si el [REPORTE DE INVESTIGACIÓN] especifica que no se encontró información en la base de datos documental, "
        f"DEBES responder EXCLUSIVAMENTE en el idioma **{idioma_destino}** que la base de datos documental del sistema no contiene "
        f"información sobre el tema consultado.\n"
        f"4. BAJO NINGUNA CIRCUNSTANCIA respondas preguntas de historia universal, ciencia o conocimiento general si la información no está en los hallazgos del investigador.\n\n"
        f"REGLA DE ORO DE IDIOMA:\n"
        f"Debes redactar la respuesta FINAL EXCLUSIVAMENTE en el siguiente idioma: **{idioma_destino}**.\n"
        f"Traduce y adapta culturalmente el contenido al idioma de destino: **{idioma_destino}**."
    )

    try:
        llm = get_llm(temperature=0.0)

        messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

        logger.info(f"Invocando LLM Analista para síntesis en '{idioma_destino}' con restricción estricta RAG...")
        response = llm.invoke(messages)

        analyst_message = AIMessage(
            content=f"[RESPUESTA FINAL - ANALISTA]\n{response.content}",
            name="analista"
        )

        logger.info("--- NODO ANALYST FINALIZADO ---")
        return {
            "messages": [analyst_message]
        }

    except Exception as e:
        logger.error(f"Excepción en nodo Analyst: {e}", exc_info=True)
        error_code = extract_error_code(e)
        error_msg = build_error_message(error_code)

        error_message = AIMessage(
            content=error_msg,
            name="analista"
        )

        logger.info("--- NODO ANALYST FINALIZADO CON ERROR ---")
        return {
            "messages": [error_message]
        }
