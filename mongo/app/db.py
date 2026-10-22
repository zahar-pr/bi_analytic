import os
import time

from pymongo import MongoClient


def env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)).strip("'\""))


CHUNK_SIZE = env_int("CHUNK_SIZE", 1000)
MAX_RETRIES = env_int("MAX_RETRIES", 3)
RETRY_DELAY = env_int("RETRY_DELAY", 5)


def get_db():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = MongoClient(
                host=os.getenv("MONGO_HOST", "localhost"),
                port=env_int("MONGO_PORT", 27017),
                username=os.getenv("MONGO_USER", "bi"),
                password=os.getenv("MONGO_PASSWORD", "bi"),
                connectTimeoutMS=env_int("CONNECT_TIMEOUT", 60) * 1000,
                serverSelectionTimeoutMS=env_int("CONNECT_TIMEOUT", 60) * 1000,
                socketTimeoutMS=env_int("NET_TIMEOUT", 3600) * 1000,
            )
            client.admin.command("ping")
            return client[os.getenv("MONGO_DB", "bi")]
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            print(f"MongoDB недоступна ({e}), попытка {attempt}/{MAX_RETRIES}, ждём {RETRY_DELAY} с")
            time.sleep(RETRY_DELAY)
    return None
