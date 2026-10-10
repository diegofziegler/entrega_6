import os
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

from logger import get_agent_logger

logger = get_agent_logger()


def get_llm(temperature: float = 0.0):
    """
    Fábrica de LLM dinámica que selecciona entre 'gemini' o 'groq' según la variable LLM_PROVIDER.
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "groq":
        groq_api_key = os.getenv("GROQ_API_KEY")
        model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

        logger.info(f"Instanciando LLM Groq ({model_name}) temp={temperature}")
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=model_name,
            groq_api_key=groq_api_key,
            temperature=temperature
        )

    else:
        # Proveedor predeterminado: Google Gemini
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_NAME", os.getenv("LLM_MODEL_NAME", "gemini-3-flash-preview"))

        logger.info(f"Instanciando LLM Google Gemini ({model_name}) temp={temperature}")
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=gemini_api_key,
            temperature=temperature
        )
