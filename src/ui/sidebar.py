import gradio as gr
import json
from gradio import ChatMessage

from src.agent.inference import MistralAgent

agent = MistralAgent()

async def respond(message, history=None):

    if history is None:
        history = []
    history.append(ChatMessage(role="user", content=message))

    thinking_msg = ChatMessage(
        role="assistant",
        content="",
        metadata={"title": "Thinking", "status": "pending"}
    )
    history.append(thinking_msg)
    yield history

    with open("./prompt.md", encoding="utf-8") as f:
        prompt = f.read()

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message},
        #{
        #    "role": "assistant",
        #    "content": "THINKING:\nLet's tackle this problem",
        ##    "prefix": True
        #},
    ]
    payload = {
        "agent_id": agent.agent_id,
        "messages": messages,
        "stream": True,
        "max_tokens": None,
        "tools": agent.tools,
        "tool_choice": "auto",
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "n": 1
    }

    response = await agent.client.agents.stream_async(**payload)

    full = ""
    thinking = ""
    final = ""

    async for chunk in response:
        delta = chunk.data.choices[0].delta
        content = delta.content or ""
        full += content

        if "FINAL ANSWER:" in full:
            parts = full.split("FINAL ANSWER:", 1)
            thinking = parts[0].replace("THINKING:", "").strip()
            final = parts[1].strip()
        else:
            thinking = full.strip()
            final = ""

        history[-1] = ChatMessage(
            role="assistant",
            content=thinking,
            metadata={"title": "Thinking", "status": "pending"}
        )
        yield history

    history[-1] = ChatMessage(
        role="assistant",
        content=thinking,
        metadata={"title": "Thinking", "status": "done"}
    )

    history.append(ChatMessage(role="assistant", content=final))
    yield history



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
                                ["How is the production process going?"],
                                ["What are the common issues faced in production?"],
                               # ["What is the status of the current production line?"],
                               # ["Can you provide insights on equipment performance?"],
                               # ["How can I optimize the workflow in the production area?"],
                               # ["How do I troubleshoot a specific piece of equipment?"],
                               # ["What are the best practices for maintaining production efficiency?"]
                            ],
                            cache_examples=False  # désactive le cache si les réponses varient
                        )
                    with gr.TabItem("Documentation", visible=True):
                        md_output = gr.Markdown("📄 La documentation s'affichera ici.")

            #textbox=gr.MultimodalTextbox(file_types=[".png", ".pdf"], sources=["upload", "microphone"]),
            #additional_inputs=[gr.Textbox("Système", label="System prompt"), gr.Slider(0, 1)],
            #additional_inputs_accordion="Options avancées",
            #flagging_mode="manual",
            #flagging_options=["👍", "👎"],
            #title="Mon Chatbot",
            #description="Testez un modèle multimodal",

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