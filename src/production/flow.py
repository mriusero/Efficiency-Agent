import time
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from .downtime import machine_errors

def generate_data(state):
    """
    Generate synthetic production data for a manufacturing process.
    """
    current_time = state["current_time"] if state["current_time"] else datetime.now()
    part_id = state["part_id"] if state["part_id"] else 0
    if 'raw' not in state['data']:
        state['data']['raw'] = []
    non_compliance_rates = {
        1: 0.05,
        2: 0.10,
        3: 0.03,
        4: 0.07
    }

    for _ in range(1000):
        if not state["running"]:
            break

        if random.random() < 0.2:
            error_key = random.choice(list(machine_errors.keys()))
            error = machine_errors[error_key]
            downtime = error["downtime"]

            state['data']['raw'].append({
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "event": "Machine Error",
                "error_code": error_key,
                "error_description": error["description"],
                "downtime_start": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "downtime_end": (current_time + downtime).strftime("%Y-%m-%d %H:%M:%S")
            })

            current_time += downtime
        else:
            position = np.random.normal(loc=0.4, scale=0.03)
            orientation = np.random.normal(loc=0.4, scale=0.06)
            tool_id = (part_id % 4) + 1

            if random.random() < non_compliance_rates[tool_id]:
                position = np.random.normal(loc=0.4, scale=0.2)
                orientation = np.random.normal(loc=0.4, scale=0.3)

            compliance = 'OK' if (0.3 <= position <= 0.5) and (0.2 <= orientation <= 0.6) else 'NOK'

            state['data']['raw'].append({
                "part_id": part_id,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "position": round(position, 4),
                "orientation": round(orientation, 4),
                "tool_id": tool_id,
                "compliance": compliance
            })

            print(f"     - part {part_id} data generated")
            part_id += 1
            time.sleep(0.5)

        current_time += timedelta(seconds=1)

    state["current_time"] = current_time
    state["part_id"] = part_id

    raw_data = []
    for row in state['data']['raw']:
        raw_data.append({
            "Part ID": row.get("part_id", "N/A"),
            "Timestamp": row.get("timestamp", "N/A"),
            "Position": row.get("position", "N/A"),
            "Orientation": row.get("orientation", "N/A"),
            "Tool ID": row.get("tool_id", "N/A"),
            "Compliance": row.get("compliance", "N/A"),
            "Event": row.get("event", "N/A"),
            "Error Code": row.get("error_code", "N/A"),
            "Error Description": row.get("error_description", "N/A"),
            "Downtime Start": row.get("downtime_start", "N/A"),
            "Downtime End": row.get("downtime_end", "N/A")
        })

    state['data']['raw_df'] = pd.DataFrame(raw_data)