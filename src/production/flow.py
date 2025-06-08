import random
import numpy as np
import pandas as pd
import asyncio
from datetime import datetime, timedelta

from .downtime import machine_errors

TOOLS_COUNT = 2

async def generate_data(state):
    """
    Generate synthetic production data for a manufacturing process.
    """
    current_time = state["current_time"] if state["current_time"] else datetime.now()
    part_id = state["part_id"] if state["part_id"] else 0

    non_compliance_rates = {
        1: 0.05,
        2: 0.10,
    }

    if 'raw_df' not in state['data']:
        state['data']['raw_df'] = pd.DataFrame(columns=[
            "Part ID", "Timestamp", "Position", "Orientation", "Tool ID",
            "Compliance", "Event", "Error Code", "Error Description",
            "Downtime Start", "Downtime End"
        ])

    for _ in range(1000):
        if not state["running"]:
            break

        if random.random() < 0.2:
            error_key = random.choice(list(machine_errors.keys()))
            error = machine_errors[error_key]
            downtime = error["downtime"]

            new_row = pd.DataFrame([{
                "Part ID": "N/A",
                "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Position": "N/A",
                "Orientation": "N/A",
                "Tool ID": "N/A",
                "Compliance": "N/A",
                "Event": "Machine Error",
                "Error Code": error_key,
                "Error Description": error["description"],
                "Downtime Start": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Downtime End": (current_time + downtime).strftime("%Y-%m-%d %H:%M:%S")
            }])

            state['data']['raw_df'] = pd.concat([state['data']['raw_df'], new_row], ignore_index=True)

            current_time += downtime
        else:
            position = np.random.normal(loc=0.4, scale=0.03)
            orientation = np.random.normal(loc=0.4, scale=0.06)
            tool_id = (part_id % TOOLS_COUNT) + 1

            if random.random() < non_compliance_rates[tool_id]:
                position = np.random.normal(loc=0.4, scale=0.2)
                orientation = np.random.normal(loc=0.4, scale=0.3)

            compliance = 'OK' if (0.3 <= position <= 0.5) and (0.2 <= orientation <= 0.6) else 'NOK'

            new_row = pd.DataFrame([{
                "Part ID": part_id,
                "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Position": round(position, 4),
                "Orientation": round(orientation, 4),
                "Tool ID": tool_id,
                "Compliance": compliance,
                "Event": "N/A",
                "Error Code": "N/A",
                "Error Description": "N/A",
                "Downtime Start": "N/A",
                "Downtime End": "N/A"
            }])

            if (
                    (not new_row.empty and not new_row.isna().all().all())
                and \
                    (not state['data']['raw_df'].empty and not state['data']['raw_df'].isna().all().all())
            ):
                state['data']['raw_df'] = pd.concat([state['data']['raw_df'], new_row], ignore_index=True)

            elif not new_row.empty and not new_row.isna().all().all():
                state['data']['raw_df'] = new_row.copy()

            #print(f"- part {part_id} data generated")
            part_id += 1
            await asyncio.sleep(0.2)

        current_time += timedelta(seconds=1)

    state["current_time"] = current_time
    state["part_id"] = part_id