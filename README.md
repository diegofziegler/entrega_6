# Entrega 6: Orquestador Multi-Agente de Análisis e Investigación con RAG

Este proyecto implementa un **Orquestador Multi-Agente de Análisis e Investigación** utilizando **LangGraph** y un sistema de recuperación semántica local (**RAG con ChromaDB y HuggingFace Embeddings**).

El sistema cuenta con una arquitectura jerárquica gobernada por un nodo **Supervisor** que actúa como router inteligente y controlador de flujo, delegando tareas de forma dinámica a sub-agentes especialistas en investigación y análisis/síntesis.

---

## 📐 Topología del Grafo

El flujo del sistema se basa en el **Patrón Supervisor (Supervisor Pattern)** con estado compartido estructurado (`MultiAgentState`).

### Diagrama Mermaid del Grafo

```mermaid
graph TD
    START([Inicio / Usuario]) --> Supervisor[Supervisor / Router]
    
    Supervisor -- decision == "researcher" --> Researcher[Agente Investigador]
    Supervisor -- decision == "analyst" --> Analyst[Agente Analista / Sintetizador]
    Supervisor -- decision == "FINISH" --> END([Fin / Respuesta Final])
    
    Researcher -- Búsqueda RAG finalizada --> Supervisor
    Analyst -- Síntesis y Traducción finalizada --> Supervisor
```

![Diagrama del Grafo](graph.png)

### Explicación de la Topología Elegida

1. **Nodo Supervisor (Router Inteligente)**:
   - Utiliza **Salida Estructurada (`Structured Output` con Pydantic)** para garantizar decisiones probabilísticas seguras (`researcher`, `analyst`, o `FINISH`).
   - Evalúa el historial de la conversación y decide cuál especialista debe actuar o si la tarea se ha completado.
   - Cuenta con un contador de iteraciones y límites para **prevenir bucles infinitos**.

2. **Agente Investigador (`researcher`)**:
   - Posee en exclusiva la herramienta `buscar_en_vectorstore` (Aislamiento de Herramientas).
   - Realiza consultas en **Español** sobre la base de datos vectorial ChromaDB que contiene la documentación histórica de `./data`.
   - Genera reportes objetivos etiquetados con atribución clara (`name="investigador"`).

3. **Agente Analista / Sintetizador (`analyst`)**:
   - Recibe la evidencia recopilada por el investigador y la procesa.
   - Redacta la respuesta final **exclusivamente en el `idioma_destino`** configurado en el estado compartible (por ejemplo, Español, Francés, Inglés), permitiendo la separación entre el idioma de almacenamiento/búsqueda y el idioma de entrega al usuario.
   - Genera el reporte final etiquetado con atribución clara (`name="analista"`).

---

## 🛠️ Requisitos Previos e Instalación

### 1. Clonar el repositorio e instalar dependencias con `uv`

Este proyecto utiliza **`uv`** como gestor de entornos y dependencias rápido.

```bash
# Crear el entorno virtual con uv
uv venv .venv

# Activar el entorno virtual
# En Linux/macOS:
source .venv/bin/activate
# En Windows (PowerShell / CMD):
.venv\Scripts\activate

# Instalar dependencias
uv pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno (`.env`)

Crea un archivo `.env` tomando como base `.env.example`:

```bash
cp .env.example .env
```

Edita `.env` y coloca tu API Key de Gemini:

```ini
GEMINI_API_KEY=tu_gemini_api_key_aqui
LLM_MODEL_NAME=gemini-3-flash-preview
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
DEFAULT_LANGUAGE=Español
VECTORSTORE_DIR=./vectorstore
DATA_DIR=./data
LOG_DIR=./log
```

---

## 🚀 Ejecución

### Ejecución de Scripts e Ingesta

El sistema verifica automáticamente si la Vector DB existe en `./vectorstore`. Si no existe, realiza la ingesta de forma automática desde `./data`.

También puedes forzar o ejecutar la ingesta manualmente:

**En Linux / macOS (con entorno activado):**
```bash
python3 ingest.py
```

**En Windows (usando el ejecutable del entorno virtual directamente):**
```cmd
.venv\Scripts\python.exe ingest.py
```

**O usando `uv` (multiplataforma):**
```bash
uv run ingest.py
```

### Ejecutar el Orquestador por CLI

**En Linux / macOS:**
```bash
python3 main.py
```

**En Windows:**
```cmd
.venv\Scripts\python.exe main.py
```

**O mediante `uv`:**
```bash
uv run main.py
```

El script `main.py` ejecutará 3 pruebas representativas:
1. Consulta sobre la historia del Karate Uechi-Ryu (Respuesta en Español).
2. Consulta sobre katas traídas de China (Respuesta en Francés).
3. Pregunta trampa sobre historia de EE.UU. no contenida en los documentos (Respuesta controlada "No dispongo de esa información").

---

## 📓 Demostración interactiva (Jupyter Notebook)

Se incluye el archivo **`demo.ipynb`** que muestra el flujo de delegación nodo por nodo, las llamadas a las herramientas y los logs del sistema.

Para iniciarlo:
```bash
# Con entorno activado
jupyter notebook demo.ipynb

# O con uv:
uv run jupyter notebook demo.ipynb
```

---

## 📝 Sistema de Logging y Trazabilidad

Los eventos del sistema se registran de forma aislada en la carpeta `./log`:
- **`log/agentes.log`**: Registra las decisiones del Supervisor, ruteo y ejecuciones de los agentes especialistas.
- **`log/rag.log`**: Registra la ingesta de documentos, chunking, embeddings y búsquedas vectoriales sobre ChromaDB.

---

## 🛡️ Criterios de Calidad y Buenas Prácticas Aplicadas

- **Structured Output**: Control estricto de decisiones del Supervisor con esquemas Pydantic.
- **Atribución de Mensajes (`name`)**: Identificación clara de respuestas por agente (`investigador`, `analista`).
- **Aislamiento de Herramientas y Estado**: Sub-agentes encapsulados que previenen contaminación de contexto (`context bloating`).
- **Ejecución Asíncrona Streaming (`astream`)**: Procesamiento asíncrono no bloqueante para seguimiento nodo a nodo.
