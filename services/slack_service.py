import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from loops import main_loop

load_dotenv(override=True)

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.message()
def on_message(message, say):
    main_loop.on_message(message, say)


def start():
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
