#!/usr/bin/env python3
import sys
import re
from time import time, localtime, strftime, sleep
import telebot
import requests
try:
  from Levenshtein import distance as levenshtein_distance
except ImportError:
  from distance import levenshtein as levenshtein_distance
import signal
import common
import config

common.load_dicts()

bot = telebot.TeleBot(config.bot_token)

# команда /rules для @mikitkinabeseda
@bot.message_handler(commands=["rules"])
def rules(message):
  if message.chat.type in ['group','supergroup'] and message.chat.id == -1001199017575:
    with open("rules.md", "r") as f:
      rules = f.read()
    bot.send_message(message.chat.id, rules, parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def translate_message(message):
  msg = message.text
  print ("%s|%s <%s %s> %s" % (str(message.chat.id), strftime("%Y-%m-%d %H:%M:%S", localtime(message.date)), message.from_user.first_name, message.from_user.last_name, msg))
  if time() > message.date+config.max_timediff:
    print (" message time too old :(")
    return
  msgtr = common.process_message(msg, config.default_tabs, config.min_levenshtein_ratio, "[TEST MODE] " if config.test_mode else False)
  if msgtr:
    try:
      bot.send_message(message.chat.id, msgtr, reply_to_message_id=message.message_id)
    except telebot.apihelper.ApiException:
      print (" Exception occured!")
  return

# inline-режим, у боевого бота выключен, так как нельзя запретить использовать его в конкретном чате
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(inline_query):
  print (inline_query)
  msgtr_glag = common.translate('cyrl2glag', inline_query.query)
  msgtr_tfng = common.translate('cyrl2tfng', inline_query.query)
  if config.test_mode:
    msgtr_glag = "[TEST MODE] "+msgtr_glag
    msgtr_tfng = "[TEST MODE] "+msgtr_tfng
  r_glag = telebot.types.InlineQueryResultArticle('GLAG', f'{inline_query.query} -> {msgtr_glag}', telebot.types.InputTextMessageContent(msgtr_glag))
  r_tfng = telebot.types.InlineQueryResultArticle('TFNG', f'{inline_query.query} -> {msgtr_tfng}', telebot.types.InputTextMessageContent(msgtr_tfng))
  bot.answer_inline_query(inline_query.id, [r_glag, r_tfng])

# shutdown on SIGINT to allow quit by Ctrl-C (usally just causes requests.exceptions.ConnectionError exception)
def signal_handler(sig, frame):
  print ("Shutdown bot...")
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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
