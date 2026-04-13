# Actividad de Clonacion de Voz con Qwen-3 TTS

## Descripcion del proyecto
Este proyecto implementa una aplicacion interactiva en Gradio para:

1. Clonar una voz a partir de un audio de referencia.
2. Sintetizar texto con la voz clonada.
3. Cargar contexto desde un PDF y datos de una persona.
4. Chatear con un agente que responde en texto y, cuando es posible, tambien en audio sintetizado.

La interfaz vive en `main.py` y la logica se divide principalmente entre:

- `voiceClonning.py`: clonacion e inferencia de voz.
- `informationExtraction.py`: carga de contexto, generacion de respuestas por LLM y evaluacion.
- `inputsGenerator.py`: componentes de entrada para la UI.

## Funcionalidades actuales
- Flujo guiado en 5 pasos con pestañas.
- Clonacion de voz usando audio + transcripcion base.
- Sintesis de texto a voz desde UI.
- Carga de PDF, nombre y resumen para contextualizar un agente conversacional.
- Chat con respuestas en:
  - texto (siempre), y
  - audio (si la inferencia de voz se genera correctamente).
- Manejo de fallback: si la sintesis falla en el chat, se devuelve solo texto.

## Flujo de uso (UI)
1. **Step 1**: subir audio base (`.wav`, `.mp3`, etc.).
2. **Step 2**: ingresar transcripcion del audio base.
3. **Step 3**:
   - clic en **Load Model** para preparar la voz clonada.
   - escribir texto en **Text to Synthesize**.
   - clic en **Synthesize Cloned Voice** para escuchar el resultado.
4. **Step 4**: 
   - Subir PDF del que se podrá extraer información.
   - Ingresar `Person Name` (nombre del agente) y `Person Summary` (quién es el agente). 
5. **Step 5**:
   - clic en **Load Chat** para inicializar el contexto del agente.
   - conversar en el chat.

## Requisitos
### Entorno
- Python 3.10+
- pip actualizado
- Conexion a internet para descarga de modelos y uso de APIs

### Dependencias principales
- gradio
- torch
- soundfile
- qwen_tts
- accelerate
- python-dotenv
- openai
- pypdf
- pydantic

Instalacion sugerida:

```bash
pip install -U pip
pip install gradio torch soundfile qwen_tts accelerate python-dotenv openai pypdf pydantic
```

## Variables de entorno
Configura un archivo `.env` en la raiz del proyecto con al menos:

- `OPENAI_API_KEY`: clave para llamadas OpenAI usadas en `informationExtraction.py`.
- `GEMINI_API_KEY`: clave para evaluacion via endpoint compatible en Gemini.
- `SYSTEM_PROMPT`: plantilla del prompt del agente. Debe incluir los placeholders:
  - `{nombre}`
  - `{resumen}`
  - `{perfil}`

Ejemplo minimo:

```env
OPENAI_API_KEY=tu_clave_openai
GEMINI_API_KEY=tu_clave_gemini
SYSTEM_PROMPT=Eres {nombre}. Usa este resumen: {resumen}. Usa este perfil: {perfil}.
```

## Ejecucion
Desde la carpeta raiz:

```bash
python main.py
```

Luego abre la URL local que imprime Gradio (normalmente `http://127.0.0.1:7860`).

