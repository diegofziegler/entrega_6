import os
import asyncio
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from tracing import setup_phoenix_tracing
setup_phoenix_tracing()

from graph import graph
from logger import get_agent_logger, get_rag_logger

load_dotenv()

agent_logger = get_agent_logger()
rag_logger = get_rag_logger()


async def run_query(query: str, idioma_destino: str = None):
    print("\n" + "="*80)
    print(f"CONSULTA: {query}")
    if idioma_destino:
        print(f"IDIOMA DESTINO SOLICITADO: {idioma_destino}")
    print("="*80 + "\n")

    agent_logger.info(f"=== NUEVA EJECUCIÓN DEL ORQUESTADOR ===")
    agent_logger.info(f"Consulta: {query} | Idioma Destino: {idioma_destino}")

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "idioma_destino": idioma_destino or os.getenv("DEFAULT_LANGUAGE", "Español"),
        "iterations": 0
    }

    print("Iniciando orquestador multi-agente...\n")

    try:
        async for event in graph.astream(initial_state, stream_mode="updates"):
            for node_name, state_update in event.items():
                print(f"--- NODO EJECUTADO: [{node_name.upper()}] ---")
                if "next" in state_update:
                    print(f"  > Decisión de ruteo siguiente: {state_update['next']}")
                if "messages" in state_update:
                    for msg in state_update["messages"]:
                        sender = getattr(msg, "name", "desconocido")
                        print(f"  > Mensaje de ({sender}):\n{msg.content}\n")

    except Exception as e:
        agent_logger.error(f"Excepción no capturada en ejecución streaming: {e}", exc_info=True)
        from supervisor import extract_error_code, build_error_message
        err_code = extract_error_code(e)
        print(f"--- ERROR TÉCNICO EN ORQUESTADOR ---")
        print(build_error_message(err_code))
        print()

    print("="*80)
    print("EJECUCIÓN FINALIZADA")
    print("="*80 + "\n")


async def main():
    print("=== ORQUESTADOR MULTI-AGENTE DE ANÁLISIS E INVESTIGACIÓN (RAG) ===")

    # Ejemplo 1: Pregunta válida con respuesta en la base de datos (Español)
    q1 = "¿Quién fue Kanbun Uechi y qué estilo de Karate desarrolló?"
    await run_query(q1, idioma_destino="Español")

    # Ejemplo 2: Pregunta válida en otro idioma de respuesta (ej. Francés)
    q2 = "¿Cuáles son las tres formas/katas principales traídas de China por Kanbun Uechi?"
    await run_query(q2, idioma_destino="Francés")

    # Ejemplo 3: Pregunta trampa (sin respuesta en la base de datos)
    q3 = "¿En qué año se firmó la Declaración de Independencia de los Estados Unidos y quién la redactó?"
    await run_query(q3, idioma_destino="Español")


if __name__ == "__main__":
    asyncio.run(main())
