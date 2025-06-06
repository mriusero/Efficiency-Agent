import gradio as gr

from src.chat import respond

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
                            button1 = gr.Button("Start Production")
                            button2 = gr.Button("Restart Production")
                            button3 = gr.Button("Stop Production")

                            output1 = gr.Textbox(label="Sortie", visible=False)
                            output2 = gr.Textbox(label="Sortie", visible=False)
                            output3 = gr.Textbox(label="Sortie", visible=False)

                            button1.click(fn=None, outputs=output1)
                            button2.click(fn=None, outputs=output2)
                            button3.click(fn=None, outputs=output3)

            with gr.Column(scale=2):
                with gr.Group():
                    gr.Markdown('### Display Graphs here')

    with gr.Tab("Description"):
        gr.Markdown(
            """
            IndustryMind AI is an AI-powered chatbot designed to assist with industrial production processes. 
            It can help you manage production lines, monitor equipment, and optimize workflows.
            """
        )

if __name__ == "__main__":
    demo.launch()