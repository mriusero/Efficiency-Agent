from gradio import ChatMessage
import json
import asyncio
import re

from src.agent.mistral_agent import MistralAgent
from src.agent.utils.call import call_tool


agent = MistralAgent()
api_lock = asyncio.Lock()
tool_lock = asyncio.Lock()

with open("./prompt.md", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

def extract_phases(text):
    """Split streaming in THINK / ACT / OBSERVE / FINAL ANSWER"""
    phases = {'think': '', 'act': '', 'observe': '', 'final': ''}
    matches = list(re.finditer(r'(THINK:|ACT:|OBSERVE:|FINAL ANSWER:)', text))
    for i, match in enumerate(matches):
        phase = match.group(1).lower().replace(":", "").replace("final answer", "final")
        start = match.end()
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        phases[phase] = text[start:end].strip()
    return phases


async def respond(message, history=None, state=None):

    if history is None:
        history = []

    if state["cycle"] == 0:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
            {"role": "assistant", "content": "THINK: Let's tackle this query step by step, the user is asking", "prefix": True},
        ]
        history.append(ChatMessage(role="assistant", content="", metadata={"title": "Thinking...", "status": "pending", 'id': state["cycle"]}))
        yield history
    else:
        history = []
        messages = state["chat"] + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "THINK: Let's tackle this query step by step, the user is asking", "prefix": True}
        ]
        history.append(ChatMessage(role="assistant", content="", metadata={"title": "Thinking...", "status": "pending", 'id': state["cycle"]}))
        yield history

    phase_order = ["think", "act", "observe", "final"]
    phase_index = 0
    done = False
    final_full = ""

    while not done:
        current_phase = phase_order[phase_index]
        if current_phase != "final":
            full = ""
        else:
            full = final_full

        print('\n', '---' * 15)
        print(f">>> messages before payload [phase {phase_index}] :", json.dumps([m for m in messages if m.get("role") != "system"], indent=2))
        #print(f">>> messages: {json.dumps(messages, indent=2)}")
        payload = {
            "agent_id": agent.agent_id,
            "messages": messages,
            "stream": True,
            "max_tokens": None,
            "tools": agent.tools,
            "tool_choice": "auto",
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "n": 1
        }

        async with api_lock:
            response = await agent.client.agents.stream_async(**payload)

            async for chunk in response:
                delta = chunk.data.choices[0].delta
                content = delta.content or ""

                full += content
                if current_phase == "final":
                    final_full = full

                phases = extract_phases(full)
                buffer = phases.get(current_phase, "")

                if current_phase == "think":
                    history[-1] = ChatMessage(role="assistant", content=buffer, metadata={"title": "Thinking...", "status": "pending", "id": state['cycle']})

                #elif current_phase == "act":
                    #parent_message = next((msg for msg in history if msg.metadata.get("id") == state['cycle']), None)
                    #if parent_message:
                    #    parent_message.content += "\n\n" + buffer
                    #    parent_message.metadata["title"] = "Acting..."
                    #else:
                    #    history[-1] = ChatMessage(role="assistant", content=buffer, metadata={"title": "Acting...", "status": "pending", "id": state['cycle']+1, 'parent_id': state["cycle"]})

                elif current_phase == "observe":
                    parent_message = next((msg for msg in history if msg.metadata.get("id") == state['cycle']), None)
                    if parent_message:
                        parent_message.content += "\n\n" + buffer
                        parent_message.metadata["title"] = "Acting..."
                    else:
                        history[-1] = ChatMessage(role="assistant", content=buffer, metadata={"title": "Observing...", "status": "pending", "id": state['cycle']+2, 'parent_id': state["cycle"]})

                yield history

                if current_phase == "final":
                    delta_content = delta.content or ""
                    final_full += delta_content
                    phases = extract_phases(final_full)
                    buffer = phases.get("final", "")
                    yield history
                    if delta_content == "" and buffer:
                        done = True
                        break

        if phase_index == 0:
            messages = [msg for msg in messages if not msg.get("prefix")]
            if buffer:
                prefix_label = current_phase.upper() if current_phase != "final" else "FINAL ANSWER"
                messages.append({
                    "role": "assistant",
                    "content": f"{prefix_label}: {buffer}\n\nACT: Now, let's using some tools to answer this query.",
                    "prefix": True
                })

        elif phase_index == 1:
            for message in messages:
                if "prefix" in message:
                    del message["prefix"]

        if phase_index == 2:
            for message in messages:
                if "prefix" in message:
                    del message["prefix"]
            messages.append({
                "role": "assistant",
                "content": "OBSERVE: Based on the results, I can conclude that",
                "prefix": True
            })

        yield history

        if current_phase == "act":
            tool_calls = getattr(delta, "tool_calls", None)
            if tool_calls and tool_calls != [] and str(tool_calls) != "Unset()":

                for tool_call in tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                async with tool_lock:
                    messages = call_tool(
                        agent,
                        tool_calls,
                        messages,
                    )
                    last_tool_response = next((m for m in reversed(messages) if m["role"] == "tool"), None)
                    if last_tool_response and last_tool_response.get("content"):
                        output = last_tool_response["content"]

                        if fn_name == "retrieve_knowledge":
                        #    pattern1 = r"##### Knowledge for '.*' \n\n"
                            pattern2 = r"Fetched \d+ relevant documents.\n\n"
                            combined_pattern = re.compile(f"({pattern2})", re.DOTALL)
                            match = combined_pattern.search(output)
                            if match:
                                output = match.group(1)
                            else:
                                output = "No relevant data found."

                        parent_message = next((msg for msg in history if msg.metadata.get("id") == state['cycle']), None)
                        if parent_message:
                            parent_message.content += "\n\n" + buffer + f"\n\nTool: `{fn_name}`\nArgs: `{fn_args}`\n\n" + output + '\n\n'
                            parent_message.metadata["title"] = "Acting..."
                        else:
                            history[-1] = ChatMessage(role="assistant", content=buffer,  metadata={"title": "Acting...", "status": "pending", "id": state['cycle']+1, 'parent_id': state["cycle"]})
                yield history

        if not done:
            phase_index += 1
            if phase_index < len(phase_order):
                pass
            else:
                done = True

    observe_text = phases.get("observe", "")
    final_text = phases.get("final", "")

    if observe_text:
        messages = [msg for msg in messages if not msg.get("prefix")]
        messages.append({
            "role": "assistant",
            "content": observe_text,
        })
        parent_message = next((msg for msg in history if msg.metadata.get("id") == state['cycle']), None)
        if parent_message:
            parent_message.content += "\n\n" + observe_text
            parent_message.metadata["title"] = "Thoughts"
            parent_message.metadata["status"] = "done"
        else:
            history[-1] = ChatMessage(role="assistant", content=observe_text, metadata={"title": "Thoughts", "status": "done", "id": state['cycle']+2, 'parent_id': state["cycle"]})

    if final_text:
        history.append(ChatMessage(role="assistant", content=final_text))

        last_message = messages[-1]
        last_message["content"] += ' FINAL ANSWER: ' + final_text
        messages[-1] = last_message

        state["cycle"] += 1
        state["chat"] = messages

    yield history