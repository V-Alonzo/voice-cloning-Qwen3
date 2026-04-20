# Actividad de Clonacion de Voz con Qwen-3 TTS

## Descripcion del proyecto
Esta aplicacion en Gradio permite:

1. Clonar una voz a partir de un audio de referencia y su transcripcion.
2. Sintetizar texto con la voz clonada.
3. Cargar contexto desde un PDF y configurar una personalidad al agente.
4. Chatear con un agente contextualizado.
5. Generar respuestas en audio (opcional) y activar un modo de razonamiento iterativo (opcional).

La interfaz principal esta en `main.py` y la logica se divide en:

- `voiceClonning.py`: clonacion de voz e inferencia TTS con Qwen.
- `informationExtraction.py`: lectura de PDF, configuracion de prompts, generacion de respuestas y evaluacion iterativa.
- `inputsGenerator.py`: componentes reutilizables para entradas de la UI.
- `audioPlayer.py`: utilitario para reproductor de audio en Gradio.

## Novedades incorporadas
- Toggle **Generate with Voice Cloning** en el chat:
   - activado: intenta generar audio de cada respuesta.
   - desactivado: responde solo en texto.
- Toggle **Activate Reasoning** en el chat:
   - activado: la respuesta se evalua con un segundo modelo y se regenera hasta que sea aceptable.
   - desactivado: genera una respuesta directa.
- Flujo de fallback robusto:
   - si falla la sintesis de voz, el chat no se rompe y entrega la respuesta en texto.
- Seleccion automatica de dispositivo para inferencia:
   - Apple Silicon (`mps`), CUDA (`cuda`) o CPU.

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

Instalacion sugerida:

```bash
pip install -U pip
pip install gradio torch soundfile qwen_tts accelerate python-dotenv openai pypdf pydantic
```

## Variables de entorno
Configura un archivo `.env` en la raiz del proyecto.

Variables requeridas para generacion y evaluacion:

- `OPENAI_API_KEY`: clave para generar respuestas del agente.
- `GPT_MODEL`: modelo para generacion principal (ejemplo: `gpt-4o-mini`).
- `GEMINI_API_KEY`: clave para el evaluador.
- `GEMINI_BASE_URL`: URL base compatible con el endpoint de Gemini.
- `GEMINI_MODEL`: modelo usado para evaluar calidad de la respuesta.
- `SYSTEM_PROMPT`: prompt base del agente. Debe incluir:
   - `{nombre}`
   - `{resumen}`
   - `{perfil}`

Ejemplo:

```env
OPENAI_API_KEY=tu_clave_openai
GPT_MODEL=gpt-4o-mini

GEMINI_API_KEY=tu_clave_gemini
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.0-flash

SYSTEM_PROMPT=Eres {nombre}. Usa este resumen: {resumen}. Usa este perfil: {perfil}.
```

## Ejecucion
Desde la carpeta raiz del proyecto:

```bash
python main.py
```

Luego abre la URL local que imprime Gradio (normalmente `http://127.0.0.1:7860`).

## Notas importantes
- Antes de usar el chat, debes ejecutar **Load Chat** (Step 5).
- Para generar audio en chat, primero debes haber cargado el modelo de voz en **Step 3**.
- El archivo de salida de TTS se guarda como `synthesized_audio.wav` en la raiz del proyecto.

