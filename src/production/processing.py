import json
import numpy as np

from .metrics.tools import get_tools_metrics
from .metrics.machine import get_machine_metrics

def process(raw_data):
    """
    Process the raw production data to extract metrics.
    """
    print("=== TOOLS METRICS ===\n")
    tools_dfs = get_tools_metrics(raw_data)
    tools_dfs = {tool: df for tool, df in tools_dfs.items() if not df.empty}

    for tool, df in tools_dfs.items():
        print(tool)
        print(df.head())
        print("\n")

    print("=== MACHINE METRICS ===")
    machine_results = get_machine_metrics(raw_data)
    machine_json = json.dumps(machine_results, indent=4)
    print(machine_json)

    return tools_dfs, machine_json