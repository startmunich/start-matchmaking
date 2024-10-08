import os
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from ai import chains
from model.startie import Startie
from services import db_service
import asyncio

load_dotenv(override=True)

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])


async def find_startie_by_id(user_id) -> Startie:
    print(f"slack_service | find_startie_by_id | {user_id}")
    response = await app.client.users_info(user=user_id)
    return Startie(slack_id=response["user"]["id"], name=response["user"]["real_name"])

@app.event("message")
async def on_message(message, say):
    print("slack_service | on_message")
    user_id = message["user"]
    cv_upload = None

    if message.get("files", []):
        url_private_download = message["files"][0]["url_private_download"]
        print("URL Private:", url_private_download)
        try:
            print("Before add_startie_by_cv")
            # Process CV and create/update user in DB
            cv_upload = await db_service.add_startie_by_cv(
                _id=user_id, cv_path=url_private_download
            )

            chunks = await db_service.get_chunks_for_startie(user_id)
            if chunks:
                print("slack_service | chunk check successful")
                await say(
                    "Thanks for uploading your CV! I've processed it successfully and stored it in our database."
                )
            else:
                print("slack_service | No chunks found after CV upload")
                await say(
                    "Your CV was received, but there might have been an issue processing it. Our team will look into it."
                )

        except Exception as e:
            print(f"Error processing CV: {type(e).__name__}, {str(e)}")
            import traceback
            traceback.print_exc()
            await say(
                "There was an error processing your CV. Our team has been notified. Please try again later."
            )

    if message.get("text"):
        await chains.on_message(message, say, cv_upload)

# @app.event("message")
# async def on_message(message, say):
#     print("slack_service | on_message")
#     user_id = message["user"]
#     cv_upload = None

#     if message.get("files", []):
#         url_private_download = message["files"][0]["url_private_download"]
#         print("URL Private:", url_private_download)
#         try:
#             print("Before add_startie_by_cv")
#             # Process CV and create/update user in DB
#             cv_upload = await db_service.add_startie_by_cv(
#                 _id=user_id, cv_path=url_private_download
#             )

#             if cv_upload:
#                 # Check if chunks were created for the user
#                 chunks = await db_service.get_chunks_for_startie(user_id)
#                 if chunks:
#                     print("slack_service | chunk check successful")
#                     await say(
#                         "Thanks for uploading your CV! I've processed it successfully and stored it in our database."
#                     )
#                 else:
#                     print("slack_service | chunks not created. retrying...")
#                     # If no chunks were created, retry the process
#                     cv_upload = await db_service.add_startie_by_cv(
#                         _id=user_id, cv_path=url_private_download
#                     )
#                     chunks = await db_service.get_chunks_for_startie(user_id) 
#                     if chunks:
#                         await say(
#                             "Thanks for uploading your CV! I've processed it successfully and stored it in our database."
#                         )
#                     else:
#                         print("slack_service | CV upload failed on the retry")
#                         await say(
#                             "I received your CV, but there was an issue processing it. Our team has been notified. Please try again later."
#                         )
#             else:
#                 print("slack_service | CV upload failed on the first time")
#                 await say(
#                     "I received your CV, but there was an issue processing it. Our team has been notified. Please try again later."
#                 )
#         except Exception as e:
#             print(f"Error processing CV: {e}")
#             await say(
#                 "There was an error processing your CV. Our team has been notified. Please try again later."
#             )

#     if message.get("text"):
#         await chains.on_message(message, say, cv_upload)


@app.event("file_shared")
async def handle_file_shared_events(body, logger):
    print("slack_service | handle_file_shared_events")
    # You might want to process the file here as well


async def start():
    print("slack_service | start")
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()
