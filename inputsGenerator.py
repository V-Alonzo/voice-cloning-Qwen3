import gradio as gr

def generateMultilineTextInput(onUploadFunction):
    text_input = gr.Textbox(
        lines = 5,
        placeholder = "Enter text here...",
        label = "Base Audio Transcription",
    )

    if onUploadFunction:
        text_input.change(fn = onUploadFunction, inputs = [text_input], outputs = [])

    return text_input

def generateAudioInput(onUploadFunction):
    audio_input = gr.Audio(sources = ["upload"], type = "filepath")

    if onUploadFunction:
        audio_input.change(fn = onUploadFunction, inputs = [audio_input], outputs = [])

    return audio_input