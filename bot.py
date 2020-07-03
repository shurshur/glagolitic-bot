#!/usr/bin/env python3
import sys
import re
from time import localtime, strftime
import telebot
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

load_dict("gl2cyr","gl2cyr.tab")

bot = telebot.TeleBot(config.bot_token)

@bot.message_handler(content_types=['text'])
def translate_message(message):
  msg = message.text
  print ("%s <%s %s> %s" % (strftime("%Y-%m-%d %H:%M:%S", localtime(message.date)), message.from_user.first_name, message.from_user.last_name, msg))
  for code in dictmap:
    msgtr = translate(code, msg)
    dist = levenshtein_distance(msg, msgtr)
    ratio = dist/len(msg)
    if ratio > config.min_levenshtein_ratio:
      print (" code=%s ratio=%lf => %s" % (code, ratio, msgtr))
      bot.send_message(message.chat.id, msgtr, reply_to_message_id=message.message_id)
      return

bot.polling()
