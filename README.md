# Actividad de Clonación de Voz con Qwen-3 TTS

## Descripción del proyecto
Este proyecto implementa una aplicación interactiva para clonar una voz y sintetizar texto usando el modelo **Qwen3-TTS**.

El flujo principal es descrito por lo siguiente:

- Subir un audio base con la voz que se quiere clonar.
- Escribir la transcripción del audio base.
- Cargar el modelo de clonación.
- Escribir un texto nuevo para sintetizarlo con la voz clonada.
- Escuchar el resultado generado en formato de audio.

La interfaz está construida con **Gradio**, mientras que la lógica de clonación e inferencia se implementa en Python con **PyTorch** y **qwen_tts**.

---

## Objetivo de la actividad
### Objetivo general
Desarrollar una solución práctica de clonación de voz que permita comprender un flujo completo de IA generativa de audio: entrada de referencia, creación de prompt de voz clonada e inferencia de texto a voz.

### Objetivos específicos
- Integrar un modelo de TTS/clonación de voz en una app local.
- Aplicar un flujo guiado en 3 pasos para reducir errores de uso.
- Permitir la aceleración por hardware cuando exista una GPU compatible (CUDA o MPS en Apple Silicon).
- Generar y reproducir un archivo de salida de audio (`synthesized_audio.wav`).

---

## Requisitos técnicos
### Entorno
- Python 3.10+
- pip actualizado
- Conexión a internet para descargar el modelo en la primera ejecución

### Dependencias principales
- gradio
- torch
- soundfile
- qwen_tts
- accelerate

Instalación sugerida:

```bash
pip install -U pip
pip install gradio torch soundfile qwen_tts accelerate
```

### Aceleración por GPU
El proyecto selecciona automáticamente el mejor dispositivo disponible:

1. `mps` para Apple Silicon (Mac M1/M2/M3/M4)
2. `cuda` para NVIDIA
3. `cpu` como fallback

En macOS con Apple Silicon, verifica que PyTorch detecte MPS:

```bash
python -c "import torch; print(torch.backends.mps.is_available())"
```

---

## Uso y personalización
### 1) Ejecutar la aplicación
En la carpeta raíz del proyecto:

```bash
python main.py
```

Luego abre en el navegador la URL local que imprime Gradio (normalmente `http://127.0.0.1:7860`).

### 2) Flujo de uso
1. **Step 1**: subir audio base (`.wav`, `.mp3`, etc.).
2. **Step 2**: ingresar transcripción del audio base.
3. **Step 3**:
   - presionar **Load Model** para crear el prompt de voz clonada.
   - escribir el texto a sintetizar.
   - presionar **Synthesize Cloned Voice**.

La salida se guarda como `synthesized_audio.wav` y se reproduce en la interfaz.

### 3) Personalización rápida
- Texto por defecto a sintetizar: editar `defaultTextToSynthesize` en `main.py`.
- Idioma de inferencia: cambiar el parámetro `language` en `performVoiceInference` dentro de `voiceClonning.py`.
- Etiquetas de interfaz y placeholders: editar `inputsGenerator.py` y `main.py`.
- Nombre/ruta de audio de salida: editar la llamada a `sf.write(...)` en `voiceClonning.py`.

### 4) Recomendaciones
- Usar archivos de audio base limpios y con poco ruido para mejores resultados.
- Mantener una transcripción fiel al audio de referencia.
- Si se usa CPU, considerar textos cortos para reducir tiempo de inferencia.
