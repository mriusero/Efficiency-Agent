from src.agent.utils.tooling import tool

@tool
def get_production_status() -> str:
    """
    This tool retrieves the current production status including various metrics such as operating time, unplanned stops, quality rates, availability, and performance indicators.
    """
    try:
        with open("data/status.json", "r") as f:
            json_string = f.read()

        result = "## Production status:\n\n"
        result += json_string
        result += "\n\n## Description:\n"
#       result += """
#   These data represent various performance and efficiency metrics related to a manufacturing or production process. They include time-based measurements such as total operating time, unplanned stops, and net productive time. Additionally, quality rates assess the percentage of products meeting specifications, often broken down by different tools or stations. Availability and operating rates indicate the proportion of scheduled production time that the equipment is actually running. Key performance indicators such as Overall Equipment Effectiveness (OEE), Mean Time Between Failures (MTBF), and Mean Time To Repair (MTTR) provide insights into equipment reliability and maintenance efficiency. Finally, process capability indices (Cp and Cpk) evaluate the precision and consistency of the tools used in production, considering both position and orientation parameters.
#       """
        result += "\n\nWARNING:\n If all metrics are null, it means that the production is not running or has not started yet."
        return result

    except Exception as e:
        print(f"Error getting production status: {e}")
        return None