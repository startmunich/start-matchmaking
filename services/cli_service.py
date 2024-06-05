from ai import chains


def start():
    print("cli_service | start")

    while True:
        question = input("Q: ")
        chains.on_message({"user": "console user", "text": question}, print)