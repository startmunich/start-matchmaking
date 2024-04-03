from loops import main_loop


def start():
    while True:
        question = input("Q: ")
        main_loop.on_message({"user": "console user", "text": question}, print)