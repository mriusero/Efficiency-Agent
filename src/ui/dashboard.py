import time
import json
import gradio as gr
import pandas as pd

from src.production.flow import generate_data
from src.production.metrics.tools import tools_metrics
from src.production.metrics.machine import machine_metrics, fetch_issues

from src.ui.graphs.tools_graphs import ToolMetricsDisplay

def dashboard_ui(state):

    display1 = ToolMetricsDisplay()

    def dataflow(state):

        # --- INIT ---
        if 'tools' not in state['data']:
            state['data']['tools'] = {}

        if 'issues' not in state['data']:
            state['data']['issues'] = {}

        # --- DATA FLOW ---
        if state['running']:

            # Generation
            generate_data(state)
            raw_data = state['data']['raw_df']

            # Process tools metrics
            tools_data = tools_metrics(raw_data)
            tools_data = {tool: df for tool, df in tools_data.items() if not df.empty}
            for tool, df in tools_data.items():
                state['data']['tools'][tool] = df

            # Process machine metrics
            machine_data = machine_metrics(raw_data)
            state['machine'] = machine_data
            issues = fetch_issues(raw_data)
            state['data']['issues'] = issues

        # --- UPDATE UI ---
        df1 = pd.DataFrame(state['data']['tools'].get('tool_1', pd.DataFrame()))
        return display1.tool_block(df=df1, id=1)

    plots = display1.tool_block(df=pd.DataFrame(), id=1)
    timer = gr.Timer(1)
    timer.tick(
        fn=dataflow,
        inputs=state,
        outputs=plots
    )