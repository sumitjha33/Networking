from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client.WebWave

async def check_db_connection() -> None:
    try:
        await client.admin.command("ping")
        print("MongoDB connected")
    except Exception as e:
        print("MongoDB connection failed:", e)

if __name__ == "__main__":
    import asyncio

    asyncio.run(check_db_connection())
