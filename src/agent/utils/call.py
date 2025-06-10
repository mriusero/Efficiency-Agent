import json


def call_tool(agent, tool_calls, messages):
    """
    Calls the specified tools with the provided arguments and updates the messages accordingly.
    """
    for tool_call in tool_calls:
        output = []
        fn_name = tool_call.function.name
        fn_args = json.loads(tool_call.function.arguments)

        try:
            fn_result = agent.names_to_functions[fn_name](**fn_args)
            output.append((tool_call.id, fn_name, fn_args, fn_result))

        except Exception as e:
            output.append((tool_call.id, fn_name, fn_args, None))

        for tool_call_id, fn_name, fn_args, fn_result in output:
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": fn_name,
                            "arguments": json.dumps(fn_args),
                        }
                    }
                ]
            })
            messages.append(
                {
                    "role": "tool",
                    "content": fn_result if fn_result is not None else f"Error occurred: {fn_name} failed to execute",
                    "tool_call_id": tool_call_id,
                },
            )
    return messages