import gradio as gr

from src.ui import sidebar_ui, dashboard_ui

custom_theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="green",
    neutral_hue="gray",
    font=[gr.themes.GoogleFont("Open Sans"), "sans-serif"],
)

with gr.Blocks(theme=custom_theme) as demo:

        # HEADER
        gr.Markdown("# AI Industrial Efficiency Helper ⚡️")
        gr.Markdown("### *AI for efficiency in Industries & Services*")
        gr.Markdown(
            """
            This demo showcases the capabilities of IndustryMind AI.
            You can interact with the chatbot to get insights and assistance on production-related queries.
            """
        )
        # CHAT INTERFACE
        sidebar_ui(width=700, visible=True)

        # DASHBOARD
        dashboard_ui()

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