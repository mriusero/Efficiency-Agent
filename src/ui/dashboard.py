import gradio as gr
import pandas as pd

from src.production.flow import play_fn, stop_fn, reset_fn

def dashboard_ui():
    with gr.Tab("Dashboard"):
        with gr.Row():
            with gr.Blocks():
                play = gr.Button("▶️ Play")
                stop = gr.Button("⏸️ Pause")
                reset = gr.Button("🔄 Reset")

        with gr.Row():
            with gr.Column(scale=3):
                json_output = {}
                json_component = gr.JSON(label="Machine JSON", value=json_output, visible=True)

                df_outputs = {
                    "DataFrame 1": pd.DataFrame(),
                    "DataFrame 2": pd.DataFrame(),
                    "DataFrame 3": pd.DataFrame(),
                    "DataFrame 4": pd.DataFrame(),
                    "DataFrame 5": pd.DataFrame(),
                }
                df_components = [gr.DataFrame(label=df_name, visible=False) for df_name in df_outputs.keys()]

                play.click(
                    fn=play_fn,
                    inputs=None,
                    outputs=df_components + [json_component]
                )
                stop.click(
                    fn=stop_fn,
                    inputs=None,
                    outputs=None
                )
                reset.click(
                    fn=reset_fn,
                    inputs=None,
                    outputs=None
                )