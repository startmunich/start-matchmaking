import asyncio
from services import slack_service, db_service

async def main():
    try:
        await db_service.init_db()
        await slack_service.start()
    except Exception as e:
        print(f"An error occurred during initialization: {e}")

if __name__ == '__main__':
    asyncio.run(main())