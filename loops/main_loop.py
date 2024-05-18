from loops import initialization_loop, looking_for_starties_loop

recent_response = None
recent_question = None
initialization_complete = False 


def on_message(message, say):
    global recent_response
    global recent_question
    global initialization_complete


    print(message)
    recent_response = message["text"]
    user_id = message["user"]

     # Check if initialization is complete
    if not initialization_complete:
        recent_question = initialization_loop.on_message(user_id, recent_question, recent_response, say)

        # If initialization loop is done, set the flag to True
        if initialization_loop.counter > len(initialization_loop.questions):
            initialization_complete = True
            recent_question = None  # Reset the recent question for the next loop

    if initialization_complete:
        recent_question = looking_for_starties_loop.on_message(user_id, recent_question, recent_response, say)
