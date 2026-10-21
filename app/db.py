import os
import time

import clickhouse_connect


def env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)).strip("'\""))


CHUNK_SIZE = env_int("CHUNK_SIZE", 1000)
MAX_RETRIES = env_int("MAX_RETRIES", 3)
RETRY_DELAY = env_int("RETRY_DELAY", 5)


def get_client():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return clickhouse_connect.get_client(
                host=os.getenv("CLICKHOUSE_HOST", "localhost"),
                port=env_int("CLICKHOUSE_PORT", 8123),
                username=os.getenv("CLICKHOUSE_USER", "bi"),
                password=os.getenv("CLICKHOUSE_PASSWORD", "bi"),
                database=os.getenv("CLICKHOUSE_DB", "bi"),
                secure=os.getenv("CLICKHOUSE_SECURE", "false").lower() == "true",
                connect_timeout=env_int("CONNECT_TIMEOUT", 60),
                send_receive_timeout=env_int("NET_TIMEOUT", 3600),
                autogenerate_session_id=False,
            )
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            print(f"ClickHouse недоступен ({e}), попытка {attempt}/{MAX_RETRIES}, ждём {RETRY_DELAY} с")
            time.sleep(RETRY_DELAY)
    return None
