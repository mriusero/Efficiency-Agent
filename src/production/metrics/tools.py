import numpy as np
from concurrent.futures import ThreadPoolExecutor

def stats_metrics(data, column, usl, lsl):
    """
    Calculate rolling mean, standard deviation, Cp, and Cpk for a given column.
    Args:
        data (pd.DataFrame): DataFrame containing the production data.
        column (str): The column for which to calculate metrics.
        usl (float): Upper specification limit.
        lsl (float): Lower specification limit.
    """
    rolling_mean = data[column].expanding().mean()
    rolling_std = data[column].expanding().std()
    cp = (usl - lsl) / (6 * rolling_std)
    cpk = np.minimum(
        (usl - rolling_mean) / (3 * rolling_std),
        (rolling_mean - lsl) / (3 * rolling_std)
    )
    cpk[rolling_std == 0] = 0
    return rolling_mean, rolling_std, cp, cpk


def process_unique_tool(tool, raw_data, file_id=None):
    """
    Process data for a single tool and save the results to a CSV file.
    Args:
        tool (str): Tool ID to process.
        raw_data (pd.DataFrame): DataFrame containing the raw production data.
    """
    tool_data = raw_data[raw_data['Tool ID'] == tool].copy()
    tool_data['pos_rolling_mean'], tool_data['pos_rolling_std'], tool_data['pos_rolling_cp'], tool_data['pos_rolling_cpk'] = stats_metrics(tool_data, 'Position', 0.5, 0.3)
    tool_data['ori_rolling_mean'], tool_data['ori_rolling_std'], tool_data['ori_rolling_cp'], tool_data['ori_rolling_cpk'] = stats_metrics(tool_data, 'Orientation', 0.6, 0.2)
    tool_data.to_csv(f'./data/tool_{file_id}.csv', index=False)


def tools_metrics(raw_data):
    """
    Process the raw production data to extract tool metrics in parallel.
    """
    tools = raw_data['Tool ID'].unique()

    with ThreadPoolExecutor() as executor:
        executor.map(lambda tool: process_unique_tool(tool, raw_data, file_id=tool), tools)

    # Calculate metrics for all tools together
    all_tools_data = raw_data.copy()
    all_tools_data = all_tools_data[all_tools_data['Tool ID'] != 'N/A']

    all_tools_data['pos_rolling_mean'], all_tools_data['pos_rolling_std'], all_tools_data['pos_rolling_cp'], all_tools_data['pos_rolling_cpk'] = stats_metrics(all_tools_data, 'Position', 0.5, 0.3)
    all_tools_data['ori_rolling_mean'], all_tools_data['ori_rolling_std'], all_tools_data['ori_rolling_cp'], all_tools_data['ori_rolling_cpk'] = stats_metrics(all_tools_data, 'Orientation', 0.6, 0.2)
    all_tools_data.to_csv('./data/tool_all.csv', index=False)