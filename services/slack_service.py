import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from ai import chains
from model.startie import Startie
from services import db_service

load_dotenv(override=True)

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])


# Call the user.info method using the WebClient
def find_startie_by_id(user_id) -> Startie:
    print(f"slack_service | find_startie_by_id | {user_id}")
    response = app.client.users_info(user=user_id)

    return Startie(
        slack_id=response["user"]["id"],
        name=response["user"]["real_name"]
    )


@app.event("message")
def on_message(message, say):
    print("slack_service | on_message")

    user_id = message["user"]
    cv_upload = None

    if message.get("files", []):
        url_private_download = message["files"][0]["url_private_download"]
        print("URL Private:", url_private_download)
        cv_upload = db_service.add_startie_by_cv(_id=user_id, cv_path=url_private_download)

    chains.on_message(message, say, cv_upload)


@app.event("file_shared")
def handle_file_shared_events(body, logger):
    print("slack_service | handle_file_shared_events")


def start():
    print("slack_service | start")

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
