from loops import initialization_loop

recent_response = None
recent_question = None


def on_message(message, say):
    global recent_response
    global recent_question

    recent_response = message["text"]
    recent_question = initialization_loop.on_message(recent_question, recent_response, say)
