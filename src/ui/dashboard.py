import gradio as gr
import pandas as pd
import asyncio
from functools import partial

from src.production.flow import generate_data
from src.production.metrics.tools import tools_metrics
from src.production.metrics.machine import machine_metrics, fetch_issues
from src.ui.graphs.tools_graphs import ToolMetricsDisplay
from src.ui.graphs.general_graphs import GeneralMetricsDisplay

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
    state.setdefault('efficiency', {})

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
            state['efficiency']
        ]
    state['last_hash'] = current_hash

    # Process data
    tools_data = await tools_metrics(raw_data)
    tools_data = {tool: df for tool, df in tools_data.items() if not df.empty}
    for tool, df in tools_data.items():
        state['data']['tools'][tool] = df

    machine_data = await machine_metrics(raw_data)
    state['efficiency'] = machine_data

    issues = await fetch_issues(raw_data)
    state['data']['issues'] = issues

    return (
        [
            pd.DataFrame(state['data']['tools'].get(f'tool_{i}', pd.DataFrame()))
            for i in range(1, TOOLS_COUNT + 1)
        ] + [
            pd.DataFrame(state['data']['tools'].get('all', pd.DataFrame()))
        ] + [
            pd.DataFrame(state['data']['issues'])
        ] + [
            state['efficiency']
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
    displays = []
    tool_plots = []
    general_plots = []

    # General metrics display and its plots
    main_display = GeneralMetricsDisplay()
    displays.append(main_display)
    general_plots.extend(
            main_display.block(
            all_tools_df=pd.DataFrame(),
            issues_df=pd.DataFrame(),
            efficiency_data={}
        )
    )
    # Tool metrics displays and their plots
    for i in range(1, n + 1):
        display = ToolMetricsDisplay()
        displays.append(display)
        tool_plots.extend(display.tool_block(df=pd.DataFrame(), id=i))

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
        efficiency_data = data[-1]       # efficiency dict

        # Update general plots
        general_plots = []
        general_display = displays[0]
        general_plots.extend(
                general_display.update(
                all_tools_df=all_tools_df,
                issues_df=issues_df,
                efficiency_data=efficiency_data
            )
        )
        # Update tool-specific plots
        tool_plots = []
        for df, display in zip(tool_dfs, displays[1:]):
            tool_plots.extend(
                [
                    display.normal_curve(df, cote='pos'),
                    display.gauge(df, type='cp', cote='pos'),
                    display.gauge(df, type='cpk', cote='pos'),
                    display.normal_curve(df, cote='ori'),
                    display.gauge(df, type='cp', cote='ori'),
                    display.gauge(df, type='cpk', cote='ori'),
                    display.control_graph(df),
                ]
            )
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