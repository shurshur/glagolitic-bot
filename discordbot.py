#!/usr/bin/env python3
import sys
import re
from time import time, localtime, strftime, sleep
import discord
from discord.ext import commands
try:
  from Levenshtein import distance as levenshtein_distance
except ImportError:
  from distance import levenshtein as levenshtein_distance
import common
import config

common.load_tabs(config.all_tabs)

import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='debug.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if message.author.bot:
    return

  await bot.process_commands(message)

  if message.type != discord.MessageType.default:
    return

  msg = message.content
  if len(msg) == 0:
    logger.debug ("OOPS, zero-length message...")
    logger.debug (message)
    return
  msgtr = common.process_message(msg, config.default_tabs, config.min_levenshtein_ratio, "[TEST MODE] " if config.test_mode else False)
  if msgtr:
    em = discord.Embed(description=msgtr)
    await message.channel.send(embed=em)
    return

bot.run(config.discord_bot_token)
