#!/usr/bin/env python3
import sys
import re
from time import time, localtime, strftime, sleep
import discord
from discord.ext import commands
from Levenshtein import distance as levenshtein_distance
import config

dictmap = {}

def load_dict(code,fn):
  dictmap[code] = [] 
  with open(fn,"r") as f:
    for l in f:
      if l.startswith('#') or l.startswith(' '):
        continue
      m = re.search(r'^(\S+)\s(\S+)', l)
      if not m:
        print ("ERROR: [%s]" % l)
        continue
      m1 = m.group(1)
      m2 = m.group(2)
      dictmap[code].append((m1, m2))

def translate(code, text):
  for k,v in dictmap[code]:
    text = re.sub(k, v, text)
  return text

load_dict("glag2cyrl","glag2cyrl.tab")
load_dict("tfng2cyrl","tfng2cyrl.tab")
load_dict("cyrl2glag","cyrl2glag.tab")
load_dict("cyrl2tfng","cyrl2tfng.tab")

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
  for code in config.default_tabs:
    msgtr = translate(code, msg)
    dist = levenshtein_distance(msg, msgtr)
    ratio = dist/len(msg)
    if ratio > config.min_levenshtein_ratio:
      logger.debug (msg)
      logger.debug (" code=%s ratio=%lf => %s" % (code, ratio, msgtr))
      if config.test_mode:
        msgtr = "[TEST MODE] "+msgtr
      em = discord.Embed(description=msgtr)
      await message.channel.send(embed=em)
      return

bot.run(config.discord_bot_token)
