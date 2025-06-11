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
        gr.Markdown("### *Efficiency Across Industries*")
        gr.Markdown(
            """
This is a demo of an AI agent designed to assist industries and service providers in understanding and interpreting their operational metrics. The agent has access to real-time telemetry data that measures quality, downtime, and operational performance.
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
        with gr.Tab("Readme"):
            gr.Markdown(
                """
## Design

The agent is implemented using **Mistral AI** via the `mistral-large-2411` LLM. Its capabilities have been enhanced with a chain-of-thought reasoning process, allowing it to `think`, `act`, `observe`, and `respond` effectively to user queries. The agent is presented through a **Gradio interface**, which is well-suited for both real-time visualization and LLM interaction. 

[See video overview](https://drive.google.com/file/d/1Bv1uF3-4EeR1HePSafZN1yzInr7YcQXZ/view?usp=share_link)

---

## Purposes  
I took inspiration from my experience in the manufacturing industry, where understanding operational metrics is crucial for efficiency. More specifically, gaining precise insights from over 30 real-time telemetry metrics is a game changer, allowing teams to focus on critical areas for improvement and optimization.  

Also, as the know-how is embedded in the agent, the risk of knowledge loss is minimized, ensuring that valuable insights are retained and can be shared across the organization.  Of course, this type of agent can be quickly adapted to various industry and service use cases such as manufacturing, cloud services, logistics, healthcare, and more.

---

## Personal Quote  
I believe that continuous improvement and efficiency are key to success in any industry.  Two years ago, I made a career shift from manufacturing to data science with a specific goal in mind: to leverage AI for operational excellence across various industries.

Today, I'm looking for opportunities to apply my expertise in AI, coupled with my passion for technology and operational excellence.  Looking for a collaborator? I’d love to connect and see how we can create something great together!  

[Send Mail](mailto:mriusero@icloud.com)
                """
            )

if __name__ == "__main__":
    demo.launch()