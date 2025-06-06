import json
import pandas as pd
import gradio as gr

from src.chat import respond
from src.production.flow import play_fn, pause_fn, reset_fn

custom_theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="green",
    neutral_hue="gray",
    font=[gr.themes.GoogleFont("Open Sans"), "sans-serif"],
)

with gr.Blocks(theme=custom_theme) as demo:

    gr.Markdown("# IndustryMind AI ⚡️")
    gr.Markdown("## An industrial production intelligence (WIP)")

    with gr.Tab("Demo"):
        gr.Markdown(
            """
            This demo showcases the capabilities of IndustryMind AI.
            You can interact with the chatbot to get insights and assistance on production-related queries.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                chatbot = gr.ChatInterface(respond)
                with gr.Row():
                    with gr.Column(scale=2):
                        with gr.Group():
                            play = gr.Button("▶️ Play")
                            pause = gr.Button("⏸️ Pause")
                            reset = gr.Button("🔄 Reset")

            with gr.Column(scale=3):
                df_outputs = {
                    "DataFrame 1": pd.DataFrame(),
                    "DataFrame 2": pd.DataFrame(),
                    "DataFrame 3": pd.DataFrame(),
                    "DataFrame 4": pd.DataFrame(),
                    "DataFrame 5": pd.DataFrame(),
                }
                json_output = {}

                df_components = [gr.DataFrame(label=df_name, visible=False) for df_name in df_outputs.keys()]
                json_component = gr.JSON(label="Machine JSON", value=json_output, visible=False)

                play.click(
                        fn=play_fn,
                        inputs=None,
                        outputs=df_components + [json_component]
                )
                pause.click(
                    fn=pause_fn,
                    inputs=None,
                    outputs=None
                )
                reset.click(
                    fn=reset_fn,
                    inputs=None,
                    outputs=None
                )


    with gr.Tab("Description"):
        gr.Markdown(
            """
            IndustryMind AI is an AI-powered chatbot designed to assist with industrial production processes. 
            It can help you manage production lines, monitor equipment, and optimize workflows.
            """
        )

if __name__ == "__main__":
    demo.launch()