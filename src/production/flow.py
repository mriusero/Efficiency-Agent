import os
import time
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from .downtime import machine_errors
from .processing import process

PRODUCTION = False
PROD_STATE = {
    "current_time": None,
    "part_id": None,
    "data": None
}

def synthetic_data():
    """
    Generate synthetic production data for a manufacturing process.
    """
    global PROD_STATE
    data = PROD_STATE["data"] if PROD_STATE["data"] else []
    current_time = PROD_STATE["current_time"] if PROD_STATE["current_time"] else datetime.now()
    part_id = PROD_STATE["part_id"] if PROD_STATE["part_id"] else 1
    non_compliance_rates = {
        1: 0.05,
        2: 0.10,
        3: 0.03,
        4: 0.07
    }

    for _ in range(1000):
        if not PRODUCTION:
            break

        if random.random() < 0.2:
            error_key = random.choice(list(machine_errors.keys()))
            error = machine_errors[error_key]
            downtime = error["downtime"]

            data.append({
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

            data.append({
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

    PROD_STATE["data"] = data
    PROD_STATE["current_time"] = current_time
    PROD_STATE["part_id"] = part_id

    return data

def compile(data):
    """
    Update production data in real-time.
    """
    raw_data = []
    for row in data:
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
    return pd.DataFrame(raw_data)


def play_fn():
    """
    Start the production simulation and generate synthetic data.
    """
    print("=== STARTING PRODUCTION ===")
    global PRODUCTION
    PRODUCTION = True
    while PRODUCTION:
        data = synthetic_data()
        raw_data = compile(data)
        tools_dfs, machine_json = process(raw_data)
        yield [tools_dfs[key] for key in tools_dfs.keys()] + [machine_json]


def stop_fn():
    """
    Pause the production simulation.
    """
    print("--- PAUSE ---")
    global PRODUCTION
    PRODUCTION = False


def reset_fn():
    """
    Reset the production state and clear the data.
    """
    os.system('clear')
    print("=== RESET DONE ===")
    global PRODUCTION, PROD_STATE
    PRODUCTION = False
    PROD_STATE = {
        "current_time": None,
        "part_id": None,
        "data": None
    }