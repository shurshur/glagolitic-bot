#!/usr/bin/env python3
import sys
import re
from time import time, localtime, strftime, sleep
import telebot
import requests
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

bot = telebot.TeleBot(config.bot_token)

@bot.message_handler(content_types=['text'])
def translate_message(message):
  msg = message.text
  print ("%s|%s <%s %s> %s" % (str(message.chat.id), strftime("%Y-%m-%d %H:%M:%S", localtime(message.date)), message.from_user.first_name, message.from_user.last_name, msg))
  if time() > message.date+config.max_timediff:
    print (" message time too old :(")
    return
  for code in config.default_tabs:
    msgtr = translate(code, msg)
    dist = levenshtein_distance(msg, msgtr)
    ratio = dist/len(msg)
    if ratio > config.min_levenshtein_ratio:
      print (" code=%s ratio=%lf => %s" % (code, ratio, msgtr))
      try:
        if config.test_mode:
          msgtr = "[TEST MODE] "+msgtr
        bot.send_message(message.chat.id, msgtr, reply_to_message_id=message.message_id)
      except telebot.apihelper.ApiException:
        print (" Exception occured!")
      return

# команда /rules для @mikitkinabeseda
@bot.message_handler(commands=["rules"])
def rules(message):
  if message.chat.type in ['group','supergroup'] and message.chat.id == -1001199017575:
    with open("rules.md", "r") as f:
      rules = f.read()
    bot.send_message(message.chat.id, rules, parse_mode="Markdown")

# inline-режим, у боевого бота выключен, так как нельзя запретить использовать его в конкретном чате
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(inline_query):
  print (inline_query)
  msgtr_glag = translate('cyrl2glag', inline_query.query)
  msgtr_tfng = translate('cyrl2tfng', inline_query.query)
  if config.test_mode:
    msgtr_glag = "[TEST MODE] "+msgtr_glag
    msgtr_tfng = "[TEST MODE] "+msgtr_tfng
  r_glag = telebot.types.InlineQueryResultArticle('GLAG', f'{inline_query.query} -> {msgtr_glag}', telebot.types.InputTextMessageContent(msgtr_glag))
  r_tfng = telebot.types.InlineQueryResultArticle('TFNG', f'{inline_query.query} -> {msgtr_tfng}', telebot.types.InputTextMessageContent(msgtr_tfng))
  bot.answer_inline_query(inline_query.id, [r_glag, r_tfng])

while True:
  try:
    bot.polling()
  except requests.exceptions.ConnectionError:
    print (" ConnectionError exception occured while polling, restart in 1 second...")
    sleep(1)
    continue
  except telebot.apihelper.ApiException:
    print (" ApiException exception occured while polling, restart in 1 second...")
    sleep(1)
    continue
  except requests.exceptions.ReadTimeout:
    print (" ReadTimeout exception occured while polling, restart in 1 second...")
    sleep(1)
    continue
