import os
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from ai import chains
from model.startie import Startie
from services import db_service

load_dotenv(override=True)

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

async def find_startie_by_id(user_id) -> Startie:
    print(f"slack_service | find_startie_by_id | {user_id}")
    response = await app.client.users_info(user=user_id)
    return Startie(
        slack_id=response["user"]["id"],
        name=response["user"]["real_name"]
    )

@app.event("message")
async def on_message(message, say):
    print("slack_service | on_message")
    user_id = message["user"]
    cv_upload = None

    if message.get("files", []):
        url_private_download = message["files"][0]["url_private_download"]
        print("URL Private:", url_private_download)
        cv_upload = await db_service.add_startie_by_cv(_id=user_id, cv_path=url_private_download)

    await chains.on_message(message, say, cv_upload)

@app.event("file_shared")
async def handle_file_shared_events(body, logger):
    print("slack_service | handle_file_shared_events")

async def start():
    print("slack_service | start")
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()