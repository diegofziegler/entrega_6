# Pre-entrega 6: Orquestador multi-agente especializado

## ¿Qué debes construir?

Debes entregar un prototipo funcional de un **Orquestador Multi-Agente de Análisis e Investigación**. El sistema debe ser capaz de procesar una solicitud de usuario que requiera al menos dos dominios de especialización distintos y una fase de síntesis final.

### Requerimientos Técnicos:

1. **Topología Jerárquica**: Un nodo `Supervisor` que actúa como router inteligente y controlador de flujo.
2. **Mínimo de 2 Agentes Especialistas**:


- **Agente de Búsqueda/Investigación**: Con herramientas para consultar fuentes externas (puedes usar Tavily o una búsqueda simulada sobre tu Vector DB de pre-entregas anteriores).
- **Agente de Análisis/Cómputo**: Especializado en procesar los datos obtenidos (análisis de sentimiento, cálculos matemáticos o validación de esquemas).

1. **Estado Compartido Estructurado**: Un esquema de `State` en LangGraph que permita rastrear qué agente ha contribuido con qué información, evitando la pérdida de contexto en la comunicación asíncrona.
2. **Flujo de Supervisión**: El supervisor debe decidir si la tarea está completa o si algún especialista debe refinar su output antes de dar la respuesta final.


## Pasos Sugeridos

1. **Define tu Estado**: Diseña una clase `TypedDict` que herede de `MessagesState`. Piensa si necesitas campos extra como `next_agent` o `task_completed`.
2. **Crea los Agentes Especialistas**: Define funciones que utilicen `create_react_agent` de LangGraph o prompts específicos para cada rol. Asegúrate de que cada uno tenga herramientas acotadas.
3. **Implementa el Supervisor**: Este es el cerebro. Su prompt debe ser claro: "Dada la conversación actual, ¿quién debe intervenir ahora o es momento de finalizar?". Debe mapear sus respuestas a los nombres de los nodos del grafo.
4. **Construye el Grafo**: Une los puntos. Usa `add_node` para cada agente y para el supervisor. Define las `Conditional Edges` que conecten al supervisor con los especialistas.
5. **Prueba la Interacción**: Lanza una consulta que obligue al supervisor a enviar la tarea al Investigador, recibir el dato, enviarlo al Analista y finalmente cerrar la conversación.


## Errores Comunes a Evitar

- **El "Supervisor Infinito"**: No definir una condición de parada clara, haciendo que el supervisor y los agentes entren en un bucle de correcciones eternas. Tip: Implementa un contador de pasos o un criterio de "Suficiencia" estricto.
- **Contaminación de Contexto**: Pasar todo el historial a todos los agentes en cada turno. Para sistemas escalables, a veces es mejor que el especialista solo reciba la instrucción específica y el contexto necesario, no toda la metadata del sistema.

## Entregable

### Qué entregás y en qué formato

- **Tipo:** Código: usaremos el siguiente repo de github [https://github.com/diegofziegler/entrega_6.git](https://github.com/diegofziegler/entrega_6.git)
- **Artefacto concreto:** repositorio github con `state.py`, la carpeta `agents/` (investigación + análisis), el grafo con nodo Supervisor, y un `README.md` con el diagrama Mermaid del grafo, explicando la topología elegida.
- **Adicional:** Sumá un video corto o notebook que demuestre el flujo de delegación.

### Estructura del Repositorio:

1. Crea un archivo state.py para definir el esquema de datos compartido.
2. Crea un directorio agents/ con los especialistas (ej. research_agent.py, analyst_agent.py).
3. Define el grafo principal en main.py o graph.py.


### Implementación del Grafo:

- Utiliza StateGraph de LangGraph.
- Define al menos un nodo de "Supervisor" que decida dinámicamente el flujo usando Literal en el retorno para las aristas condicionales.
- Herramientas (Tools):- Los agentes deben tener al menos una herramienta funcional (puedes usar TavilySearchResults o una función propia que consulte una base de datos).
- Validación:
- Implementa un nodo de Validation o asegura que el Supervisor tenga una rúbrica personalizada en su prompt para validar los resultados de los especialistas antes de dar el END.
- Documentación:
- Tu [README](./README.md) debe incluir un diagrama del grafo (puedes generarlo con graph.get_graph().draw_mermaid_png()).
- Explica brevemente por qué elegiste esa topología y cómo manejas los posibles conflictos entre agentes.


### Idea que quiero implementar

El archivo [descripción de la idea](./descripcion_de_la_idea.md) tiene el detalle dell comportamiento que quiero implementar.

---

## Criterios de Aceptación

1. Documentación y Visualización:Claridad en la explicación de la topología y representación visual del grafo en el [README](./README.md). Valor 20%.
2. Arquitectura y Flujo del Grafo (Supervisor)Evaluación del diseño del StateGraph y la implementación del nodo Supervisor para la delegación dinámica. Valor 35%.
3. Especialización de Agentes y HerramientasCapacidad de los agentes para ejecutar tareas específicas mediante el uso de herramientas funcionales. Valor 25%.
4. Gestión de Estado y ValidaciónUso de state.py para la coherencia de datos y presencia de mecanismos de validación de resultados.Valor 20 %.


---

## Buenas prácticas

A continuación, te presento una lista clara y estructurada de las buenas prácticas para patrones de diseño de multi-agentes utilizando el Patrón Supervisor, ellas deben cumplirse en el desarrollo que vamos a generar:

- **Uso de Salida Estructurada (Structured Output) en el Supervisor:** Emplear modelos (como Pydantic) para forzar al supervisor a responder con un esquema predefinido, permitiéndole decidir de manera inteligente qué miembro del equipo debe actuar a continuación o si la tarea ha finalizado con la señal `FINISH`.
- **Atribución Clara de Mensajes (Name):** Al devolver mensajes desde un agente especialista hacia el estado compartido, es fundamental incluir el parámetro `name` (por ejemplo, `name="investigador"` o `name="redactor"`), lo que permite que el supervisor distinga claramente qué agente produjo cada respuesta.
- **Aislamiento de Herramientas:** Restringir las herramientas de cada sub-agente dándole únicamente las funciones que le competen de forma exclusiva (por ejemplo, aislar herramientas de búsqueda web de las de bases de datos), lo que previene alucinaciones cruzadas y mejora la modularidad.
- **Aislamiento de Estado (Encapsulación en Nodos Wrapper):** Tratar a cada sub-agente como un sub-grafo independiente o encapsularlo mediante funciones adaptadoras, evitando que los pasos intermedios, llamadas a herramientas en bruto o errores ensucien el estado global.
- **Prevención de Context Bloating y Colisión:** Evitar la contaminación del historial compartido (`messages`) y la sobreescritura de variables de control del supervisor (como `next`), asegurando que los sub-agentes solo expongan hacia afuera su resultado final sintetizado.
- **Implementación de Ejecución Paralela (Fan-out / Fan-in):** Utilizar ramas paralelas en el grafo (como en LangGraph) cuando dos o más agentes posean tareas independientes que puedan ejecutarse de manera concurrente antes de ser procesadas por un nodo sintetizador o consolidador.
- **Invocación Asistida o Asíncrona Streaming (`astream`):** Emplear mecanismos de ejecución asíncrona para no bloquear el bucle principal de eventos (ideal para APIs o interfaces), permitiendo recibir salidas nodo por nodo a medida que se van completando.

---

 
