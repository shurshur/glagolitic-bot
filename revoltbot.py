#!/usr/bin/env python3
import sys
import os
import json
import asyncio
from time import time, localtime, strftime

import common
import config

common.load_tabs(config.all_tabs)

import asyncio
import aiohttp
import revolt

class Client(revolt.Client):
    async def on_message(self, message: revolt.Message):
        print (f"{message.created_at}: [{message.server.name}] [{message.channel.name}] <{message.author.name}> {message.content}")
        if message.author.bot: return
        msgtr = common.process_message(message.content, config.default_tabs, config.min_levenshtein_ratio, "[TEST MODE] " if config.test_mode else False)
        if msgtr:
            await message.reply(msgtr)

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, config.revolt_bot_token)
        await client.start()

asyncio.run(main())
