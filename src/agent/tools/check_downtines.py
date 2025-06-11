import json
from src.agent.utils.tooling import tool

@tool
def get_downtimes() -> str:
    """
    This tool provide the production downtimes which is useful for understanding production issues and causes.
    Data contains :
    - Timestamps of downtimes starts and endings,
    - Event, Error Code and Error Description
    """
    try:
        with open("data/downtimes.json", "r") as f:
            json_string = f.read()

        data = json.loads(json_string)

        if data is None or len(data) == 0 or data == "[]":
            result = "'No downtimes recorded yet. Please check the production status or wait for downtimes to occur.'"
        else:
            result = "##### Downtimes:\n\n"
            result += json_string

        return result

    except Exception as e:
        print(f"Error getting production status: {e}")
        return None