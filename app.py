import gradio as gr
from datetime import datetime

from src.ui import sidebar_ui, dashboard_ui
from src.ui.session import session_state

custom_theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="green",
    neutral_hue="gray",
    font=[gr.themes.GoogleFont("Open Sans"), "sans-serif"],
)

STATE = {
    "running": False,
    "date": datetime.now(),
    "part_id": 0,
    "status": {},
    "data": {},
}

with gr.Blocks(theme=custom_theme) as demo:

        # HEADER
        gr.Markdown("# Efficiency Agent ⚡️️")
        gr.Markdown("### *Smarter Efficiency. Across Industries & Services !*")
        gr.Markdown(
            """
            This demo showcases the capabilities of an AI-Agent designed to assist in production processes.  
            You can interact with the chatbot to get insights and assistance on production-related queries.
            """
        )

        state = gr.State(STATE)

        # CHAT INTERFACE
        sidebar_ui(state, width=700, visible=True)

        # DASHBOARD
        with gr.Tab("Dashboard"):
            session_state(state)
            dashboard_ui(state)

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