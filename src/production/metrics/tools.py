import numpy as np
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor

def stats_metrics(data, column, usl, lsl):
    rolling_mean = data[column].expanding().mean()
    rolling_std = data[column].expanding().std()
    cp = (usl - lsl) / (6 * rolling_std)
    cpk = np.minimum(
        (usl - rolling_mean) / (3 * rolling_std),
        (rolling_mean - lsl) / (3 * rolling_std)
    )
    cpk[rolling_std == 0] = 0
    return rolling_mean, rolling_std, cp, cpk

def process_unique_tool(tool, tool_data):
    tool_data['pos_rolling_mean'], tool_data['pos_rolling_std'], tool_data['pos_rolling_cp'], tool_data['pos_rolling_cpk'] = stats_metrics(tool_data, 'Position', 0.5, 0.3)
    tool_data['ori_rolling_mean'], tool_data['ori_rolling_std'], tool_data['ori_rolling_cp'], tool_data['ori_rolling_cpk'] = stats_metrics(tool_data, 'Orientation', 0.6, 0.2)
    return tool, tool_data

async def tools_metrics(raw_data):
    filtered_data = raw_data[raw_data['Tool ID'] != 'N/A']
    tools = filtered_data['Tool ID'].unique()

    loop = asyncio.get_running_loop()
    metrics = {}

    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(
                executor,
                process_unique_tool,
                tool,
                filtered_data[filtered_data['Tool ID'] == tool].copy()
            )
            for tool in tools
        ]

        results = await asyncio.gather(*tasks)

    for tool, tool_data in results:
        metrics[f"tool_{tool}"] = tool_data

    all_tools_data = filtered_data.copy()
    all_tools_data['pos_rolling_mean'], all_tools_data['pos_rolling_std'], all_tools_data['pos_rolling_cp'], all_tools_data['pos_rolling_cpk'] = stats_metrics(all_tools_data, 'Position', 0.5, 0.3)
    all_tools_data['ori_rolling_mean'], all_tools_data['ori_rolling_std'], all_tools_data['ori_rolling_cp'], all_tools_data['ori_rolling_cpk'] = stats_metrics(all_tools_data, 'Orientation', 0.6, 0.2)
    metrics['all'] = all_tools_data

    return metrics