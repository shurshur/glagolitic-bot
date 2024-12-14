#!/usr/bin/env python3
import sys
import os
import re
import json
from time import time, localtime, strftime, sleep

import guilded
from guilded.ext import commands

import logging
logger = logging.getLogger('guilded')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='guildedbot-debug.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

try:
    from Levenshtein import distance as levenshtein_distance
except ImportError:
    from distance import levenshtein as levenshtein_distance
import common
import config

import urllib.request

print (urllib.request.getproxies())
sys.exit()

common.load_tabs(config.all_tabs)

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    for guild in bot.guilds:
        print (f' ` joined to guild {guild.id} ({guild.name})')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.bot:
        return

    await bot.process_commands(message)

    if message.type != guilded.MessageType.default:
        return

    msg = message.content
    if len(msg) == 0:
        logger.debug ("OOPS, zero-length message...")
        logger.debug (message)
        return
    msgtr = common.process_message(msg, config.default_tabs, config.min_levenshtein_ratio, "[TEST MODE] " if config.test_mode else False)
    if msgtr:
        em = guilded.Embed(description=msgtr)
        await message.channel.send(embed=em)

bot.run(config.guilded_bot_token)
