from services import chat_service

initialization_message = """Initialising Starties looking for Starties Programm... \n
Hi there 🙋‍♀️, looks like you are using me for the first time. I would love to get to know you a little before I can match potentially helpful people for you (because you might be helpful to others 😉)."
"""

questions = [
    "In which area would you say you have fairly good expertise?",
    "What projects or experiences have you already had in which you applied or built up this expertise?",
    "On a scale from 1-10, how would you rate your expertise in this field?}"
]


def run():
    chat_service.write_message(initialization_message)
    user_inputs = []

    for i in range(len(questions)):
        user_inputs.append(chat_service.get_answer(questions[i]))

    print(f"Conversation done: user inputs -> {user_inputs}")

