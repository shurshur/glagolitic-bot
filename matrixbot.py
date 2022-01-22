#!/usr/bin/env python3
import sys
import os
import json
import asyncio
from time import time, localtime, strftime

import common
import config

common.load_tabs(config.all_tabs)

from nio import AsyncClient, LoginResponse, MatrixRoom, RoomMessageText, InviteMemberEvent

class MatrixBot:
    def __init__(self):
        self.client = None

    async def on_message(self, room: MatrixRoom, event: RoomMessageText) -> None:
        print (f"{strftime('%Y-%m-%d %H:%M:%S', localtime(event.server_timestamp/1000))}: {room.room_id}({room.display_name})|<{event.sender}({room.user_name(event.sender)})> {event.body}")
        if time() - event.server_timestamp/1000 > config.max_timediff:
            print (" ` skip old message")
            return
        msg = event.body
        msgtr = common.process_message(msg, config.default_tabs, config.min_levenshtein_ratio, "[TEST MODE] " if config.test_mode else False)
        if msgtr:
            content = {
                "msgtype": "m.text",
                "body": msgtr,
            }
            m_relates_to = event.source["content"].get("m.relates_to", None)
            if m_relates_to and m_relates_to.get("rel_type", None) == "io.element.thread":
                content["m.relates_to"] = {
                    "rel_type": "io.element.thread",
                    "event_id": m_relates_to.get("event_id", None),
                }
            await self.client.room_send(
                room_id=room.room_id,
                message_type="m.room.message",
                content=content
            )

    async def on_invite(self, room: MatrixRoom, event: InviteMemberEvent) -> None:
        print (f"{strftime('%Y-%m-%d %H:%M:%S', localtime())}: <<< Invited to {room.room_id} by {event.sender} >>>")
        await self.client.join(room.room_id)

    async def run(self) -> None:
        self.client = AsyncClient(config.matrix_homeserver)

        self.client.access_token = config.matrix_access_token
        self.client.user_id = config.matrix_user_id
        self.client.device_id = config.matrix_device_id

        self.client.add_event_callback(self.on_message, RoomMessageText)
        self.client.add_event_callback(self.on_invite, InviteMemberEvent)

        await self.client.sync_forever(timeout=30000)
        await self.client.close()

bot = MatrixBot()
asyncio.run(bot.run())
