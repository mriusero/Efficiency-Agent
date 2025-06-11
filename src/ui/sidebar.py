import gradio as gr

from src.agent.stream import respond

def sidebar_ui(state, width=700, visible=True):
    with gr.Sidebar(width=width, visible=visible):
        gr.Markdown("# Ask Agent")
        gr.Markdown(
            """
            Ask questions about production quality, efficiency, or issues.  
            The chatbot will provide insights and assistance based on the current production data.
            """
        )
        gr.Markdown(
            """
            1. **Play** - Start the production simulation and generate synthetic data.
            2. **Ask Agent** - Interact with the chatbot to get insights on production process, any issues and more.

            Note: you can click on `Pause` or `Reset` to control the production simulation.
            """
        )

        with gr.Blocks():
            with gr.Row(height=800):
                with gr.Tabs():
                    with gr.TabItem("Agent"):
                        chatbot = gr.ChatInterface(
                            fn=respond,
                            type="messages",
                            multimodal=False,
                            chatbot=gr.Chatbot(
                                placeholder="⚡️ How can I help you today ?",
                                type="messages",
                                height=600,
                                show_copy_button=True,
                            ),
                            show_progress='full',
                            stop_btn=True,
                            save_history=True,
                            examples=[
                              #  ["What is the sum of 1+1 ?"],
                                ["How is the production health now?"],
                                ["What is the most critical issue in the production right now?"],
                                ["What are the common downtimes faced in production?"],
                                ["Can you explain me Cp & Cpk KPIs ?"],
                                ["Which tool have the worst quality rate ?"],
                                ["On what metrics should I focus to improve global efficiency?"],
                               # ["Can you provide insights on equipment performance?"],
                               # ["How can I optimize the workflow in the production area?"],
                               # ["How do I troubleshoot a specific piece of equipment?"],
                               # ["What are the best practices for maintaining production efficiency?"]
                            ],
                            additional_inputs=[state],
                            cache_examples=False
                        )
        sessions_state = gr.JSON(
            label="Sessions State",
            visible=False,
            value=state.value,
        )
        state.change(
            fn=lambda x: x,
            inputs=state,
            outputs=sessions_state,
        )