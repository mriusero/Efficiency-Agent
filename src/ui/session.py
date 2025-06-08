import gradio as gr

def show_toast(text):
    gr.Info(text, duration=1.5)
    return "Toast displayed"

def play_fn(state):
    state['running'] = True
    print("\n\n===== Production started =====")
    show_toast("Production started !")
    return state

def stop_fn(state):
    state['running'] = False
    print("----- Production stopped -----")
    show_toast("Production paused !")
    return  state

def reset_fn(state):
    state['running'] = False
    state['current_time'] = None
    state['part_id'] = None
    state['data'] = {}
    state['machine'] = {}
    print("----- Production rested -----\n\n")
    show_toast("Production reset !")
    return state

def session_state(state):
    """
    Session state management for production simulation controls.
    """
    with gr.Row():
        play = gr.Button("▶️ Play")
        stop = gr.Button("⏸️ Pause")
        reset = gr.Button("🔄 Reset")
    play.click(
        fn=play_fn,
        inputs=state,
        outputs=state
    )
    stop.click(
        fn=stop_fn,
        inputs=state,
        outputs=state
    )
    reset.click(
        fn=reset_fn,
        inputs=state,
        outputs=state
    )