import gradio as gr
import pandas as pd
import asyncio
from functools import partial

from src.production.flow import generate_data
from src.production.metrics.tools import tools_metrics
from src.production.metrics.machine import machine_metrics, fetch_issues
from src.ui.graphs.tools_graphs import ToolMetricsDisplay

MAX_ROWS = 1000
TOOLS_COUNT = 2

def hash_dataframe(df):
    """Computes a simple hash to detect changes in the DataFrame."""
    return pd.util.hash_pandas_object(df).sum()

async def dataflow(state):
    """
    Main function that updates data if necessary.
    Avoids processing if the raw data hasn't changed.
    """
    state.setdefault('data', {}).setdefault('tools', {})
    state['data'].setdefault('issues', {})

    if state.get('running'):
        if 'gen_task' not in state or state['gen_task'] is None or state['gen_task'].done():
            state['gen_task'] = asyncio.create_task(generate_data(state))

    raw_data = state['data'].get('raw_df', pd.DataFrame())
    if raw_data.empty:
        return [pd.DataFrame()] * TOOLS_COUNT

    if len(raw_data) > MAX_ROWS:
        raw_data = raw_data.tail(MAX_ROWS)

    current_hash = hash_dataframe(raw_data)
    if state.get('last_hash') == current_hash:
        return [
            pd.DataFrame(state['data']['tools'].get(f'tool_{i}', pd.DataFrame()))
            for i in range(1, TOOLS_COUNT+1)
        ]
    state['last_hash'] = current_hash

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
        for i in range(1, TOOLS_COUNT+1)
    ]

def update_display_and_plots(df, display):
    """
    Uses an existing instance of ToolMetricsDisplay to generate plots.
    """
    return [
        display.normal_curve(df, cote='pos'),
        display.gauge(df, type='cp', cote='pos'),
        display.gauge(df, type='cpk', cote='pos'),
        display.normal_curve(df, cote='ori'),
        display.gauge(df, type='cp', cote='ori'),
        display.gauge(df, type='cpk', cote='ori'),
        display.control_graph(df),
    ]

def init_displays_and_blocks(n=TOOLS_COUNT):
    """
    Initializes the graphical objects (ToolMetricsDisplay) and their associated blocks.
    """
    displays = []
    blocks = []
    for i in range(1, n + 1):
        display = ToolMetricsDisplay()
        displays.append(display)
        blocks.extend(display.tool_block(df=pd.DataFrame(), id=i))
    return displays, blocks

async def on_tick(state, displays):
    """
    Tick function called periodically: updates plots only if data has changed.
    Uses a lock to prevent concurrent execution.
    """
    async with state.setdefault('lock', asyncio.Lock()):
        dfs = await dataflow(state)
        all_plots = []
        for df, display in zip(dfs, displays):
            plots = update_display_and_plots(df, display)
            all_plots.extend(plots)
        return all_plots + [state]

def dashboard_ui(state):
    """
    Creates the Gradio interface and sets a refresh every second.
    """
    displays, initial_plots = init_displays_and_blocks()
    timer = gr.Timer(1.0)
    timer.tick(
        fn=partial(on_tick, displays=displays),
        inputs=[state],
        outputs=initial_plots + [state]
    )