import gradio as gr
import pandas as pd
import asyncio

from src.production.flow import generate_data
from src.production.metrics.tools import tools_metrics
from src.production.metrics.machine import machine_metrics, fetch_issues
from src.ui.graphs.tools_graphs import ToolMetricsDisplay

async def dataflow(state):
    if 'tools' not in state['data']:
        state['data']['tools'] = {}

    if 'issues' not in state['data']:
        state['data']['issues'] = {}

    if state['running']:
        if 'gen_task' not in state or state['gen_task'] is None or state['gen_task'].done():
            print("Launching generate_data in background")
            state['gen_task'] = asyncio.create_task(generate_data(state))

    raw_data = state['data'].get('raw_df', pd.DataFrame())
    if raw_data.empty:
        return pd.DataFrame()

    tools_data = await tools_metrics(raw_data)
    tools_data = {tool: df for tool, df in tools_data.items() if not df.empty}
    for tool, df in tools_data.items():
        state['data']['tools'][tool] = df

    machine_data = await machine_metrics(raw_data)
    state['efficiency'] = machine_data
    issues = await fetch_issues(raw_data)
    state['data']['issues'] = issues

    df1 = pd.DataFrame(state['data']['tools'].get('tool_1', pd.DataFrame()))
    return df1

def dashboard_ui(state):
    display = ToolMetricsDisplay()
    plots = display.tool_block(df=pd.DataFrame(), id=1)

    async def on_tick(state):
        df1 = await dataflow(state)
        updated = [
            display.normal_curve(df1, cote='pos'),
            display.gauge(df1, type='cp', cote='pos'),
            display.gauge(df1, type='cpk', cote='pos'),

            display.normal_curve(df1, cote='ori'),
            display.gauge(df1, type='cp', cote='ori'),
            display.gauge(df1, type='cpk', cote='ori'),

            display.control_graph(df1),
        ]
        return updated + [state]

    timer = gr.Timer(1)
    timer.tick(
        fn=on_tick,
        inputs=[state],
        outputs=plots + [state]
    )