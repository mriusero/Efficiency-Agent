import json
import pandas as pd
import gradio as gr

from src.chat import respond
from src.production.flow import play_fn, stop_fn, reset_fn

custom_theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="green",
    neutral_hue="gray",
    font=[gr.themes.GoogleFont("Open Sans"), "sans-serif"],
)

with gr.Blocks(theme=custom_theme) as demo:

        # CHAT_INTERFACE
        gr.Markdown("# AI Industrial Efficiency Helper ⚡️")
        gr.Markdown("### *A production efficiency intelligence, for industries & services (WIP)*")
        gr.Markdown(
            """
            This demo showcases the capabilities of IndustryMind AI.
            You can interact with the chatbot to get insights and assistance on production-related queries.
            """
        )
        with gr.Sidebar(width=700, visible=True):
            gr.Markdown("# Ask Agent")
            gr.HTML("<div style='margin-bottom: 20px;'></div>")
            gr.Markdown(
                """
                Ask questions about production processes, equipment, and workflows.
                The chatbot will provide insights and assistance based on the current production data.
                """
            )
            gr.HTML("<div style='margin-bottom: 20px;'></div>")
            gr.Markdown(
                """
                1. **Play** - Start the production simulation and generate synthetic data.
                2. **Ask Questions** - Interact with the chatbot to get insights on production processes.
                3. **Ask for Help** - Get assistance with any issues or queries related to production.

                Note: you can click on `stop` or `reset` to control the production simulation.
                """
            )
            gr.HTML("<div style='margin-bottom: 40px;'></div>")
            chatbot = gr.ChatInterface(respond, type='messages')

        # DASHBOARD
        with gr.Tab("Dashboard"):
            with gr.Row():
                    with gr.Blocks():
                        play = gr.Button("▶️ Play")
                        stop = gr.Button("⏸️ Pause")
                        reset = gr.Button("🔄 Reset")

            with gr.Row():
                with gr.Column(scale=3):
                    df_outputs = {
                        "DataFrame 1": pd.DataFrame(),
                        "DataFrame 2": pd.DataFrame(),
                        "DataFrame 3": pd.DataFrame(),
                        "DataFrame 4": pd.DataFrame(),
                        "DataFrame 5": pd.DataFrame(),
                    }
                    json_output = {}

                    df_components = [gr.DataFrame(label=df_name, visible=True) for df_name in df_outputs.keys()]
                    json_component = gr.JSON(label="Machine JSON", value=json_output, visible=True)

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

        # DESCRIPTION
        with gr.Tab("Description"):
            gr.Markdown(
                """
                IndustryMind AI is an AI-powered chatbot designed to assist with industrial production processes. 
                It can help you manage production lines, monitor equipment, and optimize workflows.
                """
            )

if __name__ == "__main__":
    demo.launch()