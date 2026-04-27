# Actividad de Clonacion de Voz con Qwen-3 TTS

## Descripcion del proyecto
Esta aplicacion en Gradio permite:

1. Clonar una voz a partir de un audio de referencia y su transcripcion.
2. Sintetizar texto con la voz clonada.
3. Cargar contexto desde un PDF y configurar una personalidad al agente.
4. Chatear con un agente contextualizado.
5. Generar respuestas en audio (opcional) y activar un modo de razonamiento iterativo (opcional).
6. Cargar informacion de una agencia (texto libre) y chatear con una base de conocimiento RAG con salida en texto o audio.

La interfaz principal esta en `main.py` y la logica se divide en:

- `voiceClonning.py`: clonacion de voz e inferencia TTS con Qwen.
- `informationExtraction.py`: lectura de PDF, construccion de prompts dinamicos, chat con herramientas (function calling) y evaluacion iterativa.
- `informationExtraction2.py`: carga de informacion de agencia, indexacion RAG (FAISS) y respuestas contextualizadas.
- `inputsGenerator.py`: componentes reutilizables para entradas de la UI.
- `audioPlayer.py`: utilitario para reproductor de audio en Gradio.
- `agencia.txt`: contenido por defecto para inicializar la base de conocimiento de Step 6.

## Novedades incorporadas
- Toggle **Generate with Voice Cloning** en el chat:
   - activado: intenta generar audio de cada respuesta.
   - desactivado: responde solo en texto.
- Toggle **Activate Reasoning** en el chat:
   - activado: la respuesta se evalua con un segundo modelo y se regenera hasta que sea aceptable.
   - desactivado: genera una respuesta directa.
- Nuevo **Step 6: Chat with Agency Information**:
   - permite pegar o editar el contexto de la agencia.
   - precarga automaticamente el contenido de `agencia.txt`.
   - usa un boton de carga para construir la base RAG antes de conversar.
   - incluye checkbox **Generate with Voice Cloning** para responder en texto + audio cuando haya voz disponible.
- Flujo de fallback robusto:
   - si falla la sintesis de voz, el chat no se rompe y entrega la respuesta en texto.
- Seleccion automatica de dispositivo para inferencia:
   - Apple Silicon (`mps`), CUDA (`cuda`) o CPU.

## Detalle de informationExtraction.py
- Carga configuracion de entorno con `load_dotenv(dotenv_path=".env", override=True)`.
- Construye el perfil del agente a partir de un PDF con `PdfReader` en `initialConfiguration(pdfFilePath, personSummary, personName)`.
- Genera dos prompts dinamicos:
   - `systemPrompt` para responder como la persona configurada.
   - `evaluatorSystemPrompt` para evaluar calidad de respuesta cuando el razonamiento esta activo.
- Flujo principal de chat:
   - `chatGeneration(...)` delega en `chatear(...)`.
   - `getOpenAIResponse(...)` usa `gpt-4o-mini` e incluye herramientas (`tools`) para function calling.
   - Si el modelo solicita herramientas, ejecuta `manageToolCalls(...)` y retorna los mensajes resultantes.
- Modo de razonamiento (`reasoningActivated=True`):
   - Evalua cada respuesta con Gemini (`evaluate(...)`).
   - Si no es aceptable, regenera usando `rerun(...)` con la retroalimentacion hasta obtener una respuesta valida.
- Herramientas implementadas:
   - `registerDataUser(...)`: guarda contactos en `ToolsResults/contactos.txt`.
   - `registerUnknownQuestion(...)`: guarda preguntas no respondidas en `ToolsResults/preguntas_sin_respuesta.txt`.
- Validacion de evaluacion con `pydantic`:
   - Clase `Evaluacion` con `isAcceptable` y `feedback`.
   - Gemini responde en formato JSON (`response_format={"type": "json_object"}`).

## Flujo de uso (UI)
1. **Step 1**: subir audio base (`.wav`, `.mp3`, etc.).
2. **Step 2**: ingresar la transcripcion del audio base.
3. **Step 3**:
    - clic en **Load Model** para preparar el prompt de voz clonada.
    - escribir texto en **Text to Synthesize**.
    - clic en **Synthesize Cloned Voice** para escuchar el resultado.
4. **Step 4**:
    - subir un PDF desde el que se extraera contexto.
    - ingresar `Person Name` (nombre del agente/persona).
    - ingresar `Person Summary` (resumen corto de la persona).
5. **Step 5**:
    - clic en **Load Chat** para inicializar el sistema con el PDF y datos de la persona.
    - configurar toggles de chat:
       - **Generate with Voice Cloning**
       - **Activate Reasoning**
    - conversar en el chat.
6. **Step 6**:
   - pegar o editar la informacion de la agencia en **Agency Information**.
   - por defecto se carga el contenido de `agencia.txt`.
   - clic en **Load Agency Info** para indexar la informacion.
   - activar o desactivar **Generate with Voice Cloning** segun se desee.
   - conversar en el chat de agencia.

## Requisitos

### Entorno
- Python 3.10+
- `pip` actualizado
- Conexion a internet para descarga de modelos y llamadas a API

### Dependencias principales
- `gradio`
- `torch`
- `soundfile`
- `qwen_tts`
- `accelerate`
- `python-dotenv`
- `openai`
- `pypdf`
- `pydantic`
- `langchain-openai`
- `langchain-community`
- `langchain-text-splitters`
- `faiss-cpu`

Instalacion sugerida:

```bash
pip install -U pip
pip install gradio torch soundfile qwen_tts accelerate python-dotenv openai pypdf pydantic langchain-openai langchain-community langchain-text-splitters faiss-cpu
```

## Variables de entorno
Configura un archivo `.env` en la raiz del proyecto.

Variables requeridas para `informationExtraction.py`:

- `OPENAI_API_KEY`: clave para generar respuestas del agente.
- `GEMINI_API_KEY`: clave para el evaluador.

Configuracion fija dentro de `informationExtraction.py` (actualmente hardcodeada):
- Modelo de generacion principal: `gpt-4o-mini`.
- Modelo evaluador Gemini: `gemini-2.5-flash`.
- Base URL evaluador: `https://generativelanguage.googleapis.com/v1beta/openai/`.

Ejemplo:

```env
OPENAI_API_KEY=tu_clave_openai
GEMINI_API_KEY=tu_clave_gemini
```

## Ejecucion
Desde la carpeta raiz del proyecto:

```bash
python main.py
```

Luego abre la URL local que imprime Gradio (normalmente `http://127.0.0.1:7860`).

## Notas importantes
- Antes de usar el chat, debes ejecutar **Load Chat** (Step 5).
- Antes de usar el chat de agencia, debes ejecutar **Load Agency Info** (Step 6).
- Para generar audio en chat, primero debes haber cargado el modelo de voz en **Step 3**.
- El archivo de salida de TTS se guarda como `synthesized_audio.wav` en la raiz del proyecto.
- Cuando el modelo use herramientas en Step 5:
   - contactos registrados: `ToolsResults/contactos.txt`.
   - preguntas sin respuesta: `ToolsResults/preguntas_sin_respuesta.txt`.