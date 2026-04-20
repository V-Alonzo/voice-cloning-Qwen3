import gradio as gr

def generateCheckbox(label, defaultValue, onChangeFunction):
    checkbox = gr.Checkbox(label = label, value = defaultValue)

    if onChangeFunction:
        checkbox.change(fn = onChangeFunction, inputs = [checkbox], outputs = [])

    return checkbox

def generateMultilineTextInput(onUploadFunction, label):
    text_input = gr.Textbox(
        lines = 5,
        placeholder = "Enter text here...",
        label = label,
    )

    if onUploadFunction:
        text_input.change(fn = onUploadFunction, inputs = [text_input], outputs = [])

    return text_input

def generateAudioInput(onUploadFunction):
    audio_input = gr.Audio(sources = ["upload"], type = "filepath")

    if onUploadFunction:
        audio_input.change(fn = onUploadFunction, inputs = [audio_input], outputs = [])

    return audio_input

def generatePDFInput(onUploadFunction):
    pdf_input = gr.File(file_types = [".pdf"])

    if onUploadFunction:
        pdf_input.change(fn = onUploadFunction, inputs = [pdf_input], outputs = [])

    return pdf_input