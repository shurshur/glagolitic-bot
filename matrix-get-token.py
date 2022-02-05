import sys
import os
import json
import asyncio
import getpass

from nio import AsyncClient, AsyncClientConfig, LoginResponse

async def main() -> None:
    matrix_homeserver = "https://matrix.org"
    matrix_user_id = "@myawesomebot:matrix.org"
    matrix_password = getpass.getpass(f"Enter password for {matrix_user_id}: ")

    client = AsyncClient(matrix_homeserver, matrix_user_id, config=AsyncClientConfig(encryption_enabled=True), store_path="./store")
    resp = await client.login(matrix_password, device_name="glagolitic-bot")
    if isinstance(resp, LoginResponse):
        print (f"""Add these parameters to config.py:

matrix_homeserver = '{matrix_homeserver}'
matrix_user_id = '{resp.user_id}'
matrix_device_id = '{resp.device_id}'
matrix_access_token = '{resp.access_token}'
""")

    else:
        print (f"Login failed: {resp}")
    await client.close()

asyncio.run(main())
