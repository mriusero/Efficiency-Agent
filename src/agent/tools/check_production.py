import json
from src.agent.utils.tooling import tool

@tool
def get_production_status() -> str:
    """
    This tool retrieves the current production status including various metrics such as operating time, unplanned stops, quality rates, availability, and performance indicators. Useful for understanding the overall production health and efficiency.
    """
    try:
        with open("data/status.json", "r") as f:
            json_string = f.read()

        data = json.loads(json_string)

        if data == {}:
            result = "'production has not started yet.'"

        elif data["opening_time"] == "0 days 00:00:00":
            result = "'Production has not started yet.'"
        else:
            result = "##### Production status:\n\n"
            result += json_string

        return result

    except Exception as e:
        print(f"Error getting production status: {e}")
        return None