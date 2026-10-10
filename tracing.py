import os
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

from logger import get_agent_logger

logger = get_agent_logger()

_is_instrumented = False


def setup_phoenix_tracing():
    """
    Configura el exportador OpenInference / OpenTelemetry apuntando al servidor Arize Phoenix local.
    Instrumenta las ejecuciones de LangChain (LLM, RAG y Agent Chains).
    """
    global _is_instrumented
    if _is_instrumented:
        return

    collector_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
    project_name = os.getenv("PHOENIX_PROJECT_NAME", "orquestador-multi-agente")

    try:
        logger.info(f"Configurando telemetría Arize Phoenix hacia endpoint '{collector_endpoint}' (Proyecto: '{project_name}')")

        from phoenix.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor

        # Registrar el tracer provider de Phoenix
        tracer_provider = register(
            project_name=project_name,
            endpoint=collector_endpoint,
            auto_instrument=False
        )

        # Instrumentar LangChain y cadenas asociadas
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

        _is_instrumented = True
        logger.info("Instrumentación Arize Phoenix / OpenInference activada exitosamente.")

    except Exception as e:
        logger.error(f"Error configurando trazabilidad Arize Phoenix: {e}", exc_info=True)


if __name__ == "__main__":
    setup_phoenix_tracing()
