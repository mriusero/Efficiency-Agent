import os
import json
import time
from dotenv import load_dotenv
from mistralai import Mistral

from src.agent.utils.tooling import generate_tools_json
from src.agent.tools import (
    calculate_sum,
)

load_dotenv()

class MistralAgent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        self.client = Mistral(api_key=self.api_key)
        self.model = "mistral-small"
        self.prompt = None
        self.names_to_functions = {
            "calculate_sum": calculate_sum,
        }
        self.tools = self.get_tools()

    @staticmethod
    def get_tools():
        """Generate the tools.json file with the tools to be used by the agent."""
        return generate_tools_json(
            [
                calculate_sum,
            ]
        ).get('tools')

    def make_initial_request(self, input):
        """Make the initial request to the agent with the given input."""
        with open("./prompt.md", 'r', encoding='utf-8') as file:
            self.prompt = file.read()
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": input},
            {
                "role": "assistant",
                "content": "THINKING:\nLet's tackle this problem, ",
                "prefix": True,
            },
        ]
        payload = {
            "agent_id": self.agent_id,
            "messages": messages,
            "max_tokens": None,
            "stream": False,
            "stop": None,
            "random_seed": None,
            "response_format": None,
            "tools": self.tools,
            "tool_choice": 'auto',
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "n": 1,
            "prediction": None,
            "parallel_tool_calls": None
        }
        return self.client.agents.complete(**payload), messages

    def run(self, input):
        """Run the agent with the given input and process the response."""
        print("\n===== Asking the agent =====\n")
        response, messages = self.make_initial_request(input)
        first_iteration = True

        while True:
            time.sleep(1)
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]

                if first_iteration:
                    messages = [message for message in messages if not message.get("prefix")]
                    messages.append(
                        {
                            "role": "assistant",
                            "content": choice.message.content,
                            "prefix": True,
                        },
                    )
                    first_iteration = False
                else:
                    if choice.message.tool_calls:
                        results = []

                        for tool_call in choice.message.tool_calls:
                            function_name = tool_call.function.name
                            function_params = json.loads(tool_call.function.arguments)

                            try:
                                function_result = self.names_to_functions[function_name](**function_params)
                                results.append((tool_call.id, function_name, function_result))

                            except Exception as e:
                                results.append((tool_call.id, function_name, None))

                        for tool_call_id, function_name, function_result in results:
                            messages.append({
                                "role": "assistant",
                                "tool_calls": [
                                    {
                                        "id": tool_call_id,
                                        "type": "function",
                                        "function": {
                                            "name": function_name,
                                            "arguments": json.dumps(function_params),
                                        }
                                    }
                                ]
                            })
                            messages.append(
                                {
                                    "role": "tool",
                                    "content": function_result if function_result is not None else f"Error occurred: {function_name} failed to execute",
                                    "tool_call_id": tool_call_id,
                                },
                            )
                            for message in messages:
                                if "prefix" in message:
                                    del message["prefix"]
                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": f"Based on the results, ",
                                    "prefix": True,
                                }
                            )
                    else:
                        for message in messages:
                            if "prefix" in message:
                                del message["prefix"]
                        messages.append(
                            {
                                "role": "assistant",
                                "content": choice.message.content,
                            }
                        )
                        if 'FINAL ANSWER:' in choice.message.content:
                            print("\n===== END OF REQUEST =====\n", json.dumps(messages, indent=2))
                            ans = choice.message.content.split('FINAL ANSWER:')[1].strip()

                            timestamp = time.strftime("%Y%m%d-%H%M%S")
                            output_file = f"chat_{timestamp}.json"
                            with open(output_file, "w", encoding="utf-8") as f:
                                json.dump(messages, f, indent=2, ensure_ascii=False)
                            print(f"Conversation enregistrée dans {output_file}")

                            return ans

                print("\n===== MESSAGES BEFORE API CALL =====\n", json.dumps(messages, indent=2))
                time.sleep(1)
                response = self.client.agents.complete(
                    agent_id=self.agent_id,
                    messages=messages,
                    tools=self.tools,
                    tool_choice='auto',
                )