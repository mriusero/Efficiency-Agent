import asyncio
from functools import partial

import gradio as gr
import pandas as pd

from src.production.flow import generate_data
from src.production.metrics.machine import machine_metrics, fetch_issues
from src.production.metrics.tools import tools_metrics
from src.ui.graphs.general_graphs import GeneralMetricsDisplay
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
    # Initialize state
    state.setdefault('data', {}).setdefault('tools', {})
    state['data']['tools'].setdefault('all', pd.DataFrame())

    for i in range(1, TOOLS_COUNT + 1):
        state['data']['tools'].setdefault(f'tool_{i}', pd.DataFrame())

    state['data'].setdefault('issues', {})
    state.setdefault('status', {})

    # Check running state
    if state.get('running'):
        if 'gen_task' not in state or state['gen_task'] is None or state['gen_task'].done():
            state['gen_task'] = asyncio.create_task(generate_data(state))

    raw_data = state['data'].get('raw_df', pd.DataFrame())

    # Cold start
    if raw_data.empty:
        return (
                [pd.DataFrame()] * TOOLS_COUNT +    # outils
                [pd.DataFrame()] +                  # all
                [pd.DataFrame()] +                  # issues
                [{}]                                # efficiency
        )

    # Limit MAX_ROWS
    if len(raw_data) > MAX_ROWS:
        raw_data = raw_data.tail(MAX_ROWS)

    # Check if data has changed
    current_hash = hash_dataframe(raw_data)
    if state.get('last_hash') == current_hash:
        return [
            pd.DataFrame(state['data']['tools'].get(f'tool_{i}', pd.DataFrame()))
            for i in range(1, TOOLS_COUNT+1)
        ] + [
            pd.DataFrame(state['data']['tools'].get('all', pd.DataFrame()))
        ] + [
            pd.DataFrame(state['data']['issues'])
        ] + [
            state['status']
        ]
    state['last_hash'] = current_hash

    # Process data
    tools_data = await tools_metrics(raw_data)
    tools_data = {tool: df for tool, df in tools_data.items() if not df.empty}
    for tool, df in tools_data.items():
        state['data']['tools'][tool] = df

    # Get machine metrics
    machine_data = await machine_metrics(raw_data)
    state['status'] = machine_data

    # Get tools stats
    for tool in ['tool_1', 'tool_2', 'all']:
        df = state['data']['tools'].get(tool, pd.DataFrame())
        if df.empty or 'Timestamp' not in df.columns:
            continue

        df = df.copy()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df.dropna(subset=['Timestamp'], inplace=True)

        if df.empty:
            continue

        idx = df['Timestamp'].idxmax()

        for cote in ['pos', 'ori']:
            for metric_type in ['cp', 'cpk']:
                column = f"{cote}_rolling_{metric_type}"
                if column in df.columns:
                    value = df.at[idx, column]
                    key = f"{tool}_{metric_type}_{cote}"
                    state['status'][key] = round(value, 4)

    # Get issues
    issues = await fetch_issues(raw_data)
    state['data']['issues'] = issues

    # Update situation
    return (
        [
            pd.DataFrame(state['data']['tools'].get(f'tool_{i}', pd.DataFrame()))
            for i in range(1, TOOLS_COUNT + 1)
        ] + [
            pd.DataFrame(state['data']['tools'].get('all', pd.DataFrame()))
        ] + [
            pd.DataFrame(state['data']['issues'])
        ] + [
            state['status']
        ]
    )


def init_components(n=TOOLS_COUNT):
    """
    Initializes the graphical objects (ToolMetricsDisplay and GeneralMetricsDisplay)
    and returns:
    - displays: list of display objects [GeneralMetricsDisplay, ToolMetricsDisplay1, ToolMetricsDisplay2, ...]
    - tool_plots: list of tool-related Gradio components
    - general_plots: list of general-related Gradio components
    """
    print("Initializing components...")

    displays = []
    tool_plots = []
    general_plots = []

    for i in range(1, n + 1):                   # Tool metrics displays
        display = ToolMetricsDisplay()
        displays.append(display)
        tool_plots.extend(display.tool_block(df=pd.DataFrame(), id=i))

    main_display = GeneralMetricsDisplay()      # General metrics display
    displays.append(main_display)
    general_plots.extend(
            main_display.general_block(
            all_tools_df=pd.DataFrame(),
            issues_df=pd.DataFrame(),
            status={}
        )
    )
    return displays, tool_plots, general_plots


async def on_tick(state, displays):
    """
    Tick function called periodically to update plots if data has changed.
    Handles:
    - Tool-specific plots (tool_1, tool_2, ..., tool_n)
    - General plots (all tools, issues, efficiency)
    Returns two lists of plots separately for tools and general metrics, plus state.
    """
    async with state.setdefault('lock', asyncio.Lock()):

        data = await dataflow(state)
        tool_dfs = data[:-3]             # all individual tool DataFrames
        all_tools_df = data[-3]          # 'all' tools DataFrame
        issues_df = data[-2]             # issues DataFrame
        status = data[-1]                # status dict

        general_display = displays[-1]                      # General plots
        general_plots = general_display.refresh(
            all_tools_df=all_tools_df,
            issues_df=issues_df,
            status=status
        )

        tool_plots = []                                     # Tool-specific plots
        for df, display in zip(tool_dfs, displays[:-1]):
            tool_plots.extend(display.refresh(df=df))

        return tool_plots + general_plots + [state]

def dashboard_ui(state):
    """
    Creates the Gradio interface and sets a refresh every second.
    The outputs are separated into two groups for tools and general metrics to
    preserve layout order and grouping.
    """
    displays, tool_plots, general_plots = init_components()

    timer = gr.Timer(1.0)
    timer.tick(
        fn=partial(on_tick, displays=displays),
        inputs=[state],
        outputs=tool_plots + general_plots + [state]
    )