import gradio as gr
import pandas as pd
import asyncio

from src.production.flow import generate_data
from src.production.metrics.tools import tools_metrics
from src.production.metrics.machine import machine_metrics, fetch_issues
from src.ui.graphs.tools_graphs import ToolMetricsDisplay


async def dataflow(state):
    """
    Main dataflow function that processes raw production data and updates the state with tool metrics, machine efficiency, and issues.
    """
    if 'tools' not in state['data']:
        state['data']['tools'] = {}

    if 'issues' not in state['data']:
        state['data']['issues'] = {}

    if state['running']:
        if 'gen_task' not in state or state['gen_task'] is None or state['gen_task'].done():
            state['gen_task'] = asyncio.create_task(generate_data(state))

    raw_data = state['data'].get('raw_df', pd.DataFrame())
    if raw_data.empty:
        return [pd.DataFrame()] * 4

    tools_data = await tools_metrics(raw_data)
    tools_data = {tool: df for tool, df in tools_data.items() if not df.empty}
    for tool, df in tools_data.items():
        state['data']['tools'][tool] = df

    machine_data = await machine_metrics(raw_data)
    state['efficiency'] = machine_data

    issues = await fetch_issues(raw_data)
    state['data']['issues'] = issues

    return [
        pd.DataFrame(state['data']['tools'].get(f'tool_{i}', pd.DataFrame()))
        for i in range(1, 5)
    ]


def create_display_and_plots(df):
    """
    Create a ToolMetricsDisplay instance and generate plots for the provided DataFrame.
    """
    display = ToolMetricsDisplay()
    plots = [
        display.normal_curve(df, cote='pos'),
        display.gauge(df, type='cp', cote='pos'),
        display.gauge(df, type='cpk', cote='pos'),
        display.normal_curve(df, cote='ori'),
        display.gauge(df, type='cp', cote='ori'),
        display.gauge(df, type='cpk', cote='ori'),
        display.control_graph(df),
    ]
    return display, plots


def init_displays_and_blocks(n=4):
    """
    Initialize a list of ToolMetricsDisplay instances and their corresponding blocks.
    """
    displays = []
    blocks = []
    for i in range(1, n + 1):
        display = ToolMetricsDisplay()
        displays.append(display)
        blocks.extend(display.tool_block(df=pd.DataFrame(), id=i))
    return displays, blocks


def dashboard_ui(state):
    """
    Create the Gradio UI for the dashboard, initializing displays and setting up the dataflow.
    """
    displays, initial_plots = init_displays_and_blocks()

    async def on_tick(state):
        dfs = await dataflow(state)
        all_plots = []
        for df in dfs:
            _, plots = create_display_and_plots(df)
            all_plots.extend(plots)
        return all_plots + [state]

    timer = gr.Timer(0.1)
    timer.tick(
        fn=on_tick,
        inputs=[state],
        outputs=initial_plots + [state]
    )