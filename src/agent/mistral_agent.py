import os
from dotenv import load_dotenv
from mistralai import Mistral

from src.agent.utils.tooling import generate_tools_json
from src.agent.tools import (
    calculate_sum,
    retrieve_knowledge,
    visit_webpage,
    get_production_status,
)

load_dotenv()

class MistralAgent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        self.client = Mistral(api_key=self.api_key)
        self.model = "mistral-large"
        self.prompt = None
        self.names_to_functions = {
            "calculate_sum": calculate_sum,
            "retrieve_knowledge": retrieve_knowledge,
            "visit_webpage": visit_webpage,
            "get_production_status": get_production_status,
        }
        self.tools = self.get_tools()

    @staticmethod
    def get_tools():
        """Generate the tools.json file with the tools to be used by the agent."""
        return generate_tools_json(
            [
                calculate_sum,
                retrieve_knowledge,
                visit_webpage,
                get_production_status,
            ]
        ).get('tools')