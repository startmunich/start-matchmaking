import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from loops import main_loop
from services import db_service

load_dotenv(override=True)

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])



@app.event("message")
def on_message(message, say):
    print("message event handler: ", message)
    user_id = message["user"]
    url_private_download = message["files"][0]["url_private_download"]

    main_loop.on_message(message, say)

    if "url_private_download" in message["files"][0]:
        print("URL Private:", url_private_download)
        db_service.add_user_by_cv(_id=user_id, cv_path=url_private_download)
        

@app.event("file_shared")
def handle_file_shared_events(body, logger):
    # logger.info(body)
    print("file_shared event handler: ", body)



def start():
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
