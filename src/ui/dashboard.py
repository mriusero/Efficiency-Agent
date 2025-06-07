import time
import json
import gradio as gr

from src.production.flow import generate_data#, compile
from src.production.metrics.tools import get_tools_metrics
from src.production.metrics.machine import get_machine_metrics

def dashboard_ui(state):

    def update_dashboard(state):
        if state['running']:
            generate_data(state)

            raw_data = state['data']['raw_df']
            print(raw_data)


            tools_dfs = get_tools_metrics(raw_data)
            tools_dfs = {tool: df for tool, df in tools_dfs.items() if not df.empty}

            for tool, df in tools_dfs.items():
                print(tool)
                print(df.columns.tolist())
                print("\n")

            machine_results = get_machine_metrics(raw_data)
            machine_json = json.dumps(machine_results, indent=4)
            print(machine_json)

        return state





    timer = gr.Timer(0.1)
    timer.tick(
        fn=update_dashboard,
        inputs=state,
        outputs=state
    )



#        # ----------------   TOOLS METRICS DISPLAY   ----------------
#        tools_count = 4
#        visualizers = [ToolMetricsDisplay() for _ in range(tools_count)]
#        for id, display in enumerate(visualizers, start=1):
#            with gr.Row():
#                df = datalist.value['data'][id - 1][0]
#                header = f"Tool {id}"
#                html_content = f"""
#                                    <div style="display: flex; align-items: center; justify-content: flex-start; width: 100%;">
#                                        <div style="flex: 0 0 2%; border-top: 1px solid white;"></div>
#                                        <h2 style="flex: 0 0 auto; margin: 0 10px;">{header}</h2>
#                                        <div style="flex: 1; border-top: 1px solid white;"></div>
#                                </div>
#                                """
#                gr.HTML(html_content)
#            with gr.Row():
#                with gr.Column(scale=1):
#                    gr.Markdown("### `Position`")
#                    with gr.Group():
#                        with gr.Row(height=250):
#                            pos_normal_plot = gr.Plot(display.normal_curve(df=df, cote='pos'))
#                        with gr.Row(height=150):
#                            pos_cp_gauge = gr.Plot(display.gauge(df=df, type='cp', cote='pos'))
#                            pos_cpk_gauge = gr.Plot(display.gauge(df=df, type='cpk', cote='pos'))
#
#                with gr.Column(scale=1):
#                    gr.Markdown("### `Orientation`")
#                    with gr.Group():
#                        with gr.Row(height=250):
#                            ori_normal_plot = gr.Plot(display.normal_curve(df=df, cote='ori'))
#                        with gr.Row(height=150):
#                            ori_cp_gauge = gr.Plot(display.gauge(df=df, type='cp', cote='ori'))
#                            ori_cpk_gauge = gr.Plot(display.gauge(df=df, type='cpk', cote='ori'))
#
#                with gr.Column(scale=2):
#                    gr.Markdown("### `Control card`")
#                    with gr.Row(height=400):
#                        control_plot = gr.Plot(display.control_graph(df=df))
#
#            timer = gr.Timer(1)
#            timer.tick(
#                lambda : [
#                    display.normal_curve(df=df, cote='pos'),
#                    display.gauge(df=df, type='cp', cote='pos'),
#                    display.gauge(df=df, type='cpk', cote='pos'),
#                    display.normal_curve(df=df, cote='ori'),
#                    display.gauge(df=df, type='cp', cote='ori'),
#                    display.gauge(df=df, type='cpk', cote='ori'),
#                    display.control_graph(df=df)
#                ],
#                outputs=[pos_normal_plot, pos_cp_gauge, pos_cpk_gauge, ori_normal_plot, ori_cp_gauge, ori_cpk_gauge,
#                         control_plot]
#            )