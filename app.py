import gradio as gr

def hello():
    return "Smart Home Dashboard Running"

demo = gr.Interface(
    fn=hello,
    inputs=[],
    outputs="text"
)

demo.launch()