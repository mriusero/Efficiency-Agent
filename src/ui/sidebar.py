import gradio as gr
from src.chat import respond


def sidebar_ui(state, width=700, visible=True):
    with gr.Sidebar(width=width, visible=visible):
        gr.Markdown("# Ask Agent")
        gr.Markdown(
            """
            Ask questions about production processes, equipment, and workflows.
            The chatbot will provide insights and assistance based on the current production data.
            """
        )
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
        sessions_state = gr.JSON(
            label="Sessions State",
            visible=True,
            value=state.value,
        )
        state.change(
            fn=lambda x: x,
            inputs=state,
            outputs=sessions_state,
        )