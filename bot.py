#!/usr/bin/env python3
import sys
import os
import re
import json
from time import time, localtime, strftime, sleep
import telebot
from telebot import types
import requests
try:
  from Levenshtein import distance as levenshtein_distance
except ImportError:
  from distance import levenshtein as levenshtein_distance
import signal
import common
import config
try:
  __import__('pysqlite3')
  import sys
  sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ModuleNotFoundError:
  pass
from sqlite3worker import Sqlite3Worker

common.load_tabs(config.all_tabs)

bot = telebot.TeleBot(config.bot_token, skip_pending=True, threaded=False)

db = Sqlite3Worker("bot.db")

class ChatConfig:
  def __init__(self, chat_id=None):
    self.chat_id = chat_id
    self.tabs = config.default_tabs[:]
    self.inline_policy = 0
    self.lock = False

  def __str__(self):
    return f"<ChatConfig(chat_id={self.chat_id}, tabs={self.tabs}, inline_policy={self.inline_policy}, lock={self.lock})>"

chat_configs = {}

def get_chat_config(chat):
  global chat_configs
  chat_config = chat_configs.get(chat.id, None)
  if not chat_config:
    chat_config = ChatConfig(chat.id)
    if chat.type == "private":
      chat_config.tabs = config.default_pm_tabs[:]
    chat_configs[chat.id] = chat_config
  return chat_config

def save_chat_config(chat):
  chat_config = get_chat_config(chat)
  db.execute("INSERT INTO chat_config (chat_id, tabs, inline_policy, lock) VALUES (?,?,?,?) ON CONFLICT(chat_id) DO UPDATE SET tabs=excluded.tabs,inline_policy=excluded.inline_policy,lock=excluded.lock",
    (chat.id, ",".join(chat_config.tabs), chat_config.inline_policy, chat_config.lock))

def init_table(table, sql):
  res = db.execute("SELECT * FROM sqlite_master where tbl_name=?",(table,))
  if len(res) < 1:
    db.execute(sql)

init_table("chat_config","""CREATE TABLE chat_config (
  chat_id INT NOT NULL UNIQUE,
  tabs TEXT VARCHAR(256),
  inline_policy INT,
  lock BOOLEAN
)""")

init_table("files","""CREATE TABLE files (
  file_name TEXT VARCHAR(256) UNIQUE,
  file_id TEXT VARCHAR(256)
)""")

def load_chat_configs():
  global chat_configs
  res = db.execute("SELECT chat_id,tabs,inline_policy,lock FROM chat_config")
  chat_configs = {}
  for row in res:
    chat_config = ChatConfig()
    chat_config.chat_id, tabs, chat_config.inline_policy, lock = row
    tabs = tabs.split(",")
    for code in tabs[:]:
      if code not in config.all_tabs:
        tabs.remove(code)
    chat_config.tabs = tabs
    chat_config.lock = True if lock else False
    chat_configs[chat_config.chat_id] = chat_config

files = {}

def load_files():
  global files
  res = db.execute("SELECT file_name,file_id FROM files")
  files = {}
  for row in res:
    file_name, file_id = row
    files[file_name] = file_id

def save_file(file_name, file_id):
  global files
  db.execute("INSERT INTO files (file_name,file_id) VALUES (?,?) ON CONFLICT(file_name) DO UPDATE SET file_id=excluded.file_id", (file_name, file_id))
  files[file_name] = file_id

menu = None

def load_menu():
  global menu
  menu = json.load(open("menu/menu.json","r"))
  for _, item in menu.items():
    msg = item["message"]
    if re.match('[-_\w]+\.(?:md|html)', msg):
      with open(os.path.join("menu", msg), "r") as f:
        item["message"] = f.read()

def make_menu(item, chat):
  chat_config = get_chat_config(chat)
  item = menu[item]
  keyboard = types.InlineKeyboardMarkup()
  if type(item["buttons"]) is list:
    for b in item["buttons"]:
      if b["action"] == "link":
        keyboard.add(types.InlineKeyboardButton(text=b["caption"], callback_data=f"link:{b['link']}"))
      elif b["action"] == "url":
        keyboard.add(types.InlineKeyboardButton(text=b["caption"], url=b['url']))
  elif item["buttons"] == "config_buttons":
    for code in config.all_tabs:
      if code in chat_config.tabs:
        keyboard.add(types.InlineKeyboardButton(text=f"Выключить {code}", callback_data=f"config:tabs-{code}"))
      else:
        keyboard.add(types.InlineKeyboardButton(text=f"Включить {code}", callback_data=f"config:tabs+{code}"))
    if chat_config.lock:
      keyboard.add(types.InlineKeyboardButton(text="Включить бота в чате", callback_data="config:enable"))
    else:
      keyboard.add(types.InlineKeyboardButton(text="Выключить бота в чате", callback_data="config:disable"))
    keyboard.add(types.InlineKeyboardButton(text=f"Дополнительно", callback_data=f"link:config-extra"))
    if chat.type == "private":
      keyboard.add(types.InlineKeyboardButton(text="В начало", callback_data="link:root"))
  elif item["buttons"] == "config_extra_buttons":
    for inline_policy in [0,1,2]:
      mark = ""
      if inline_policy == chat_config.inline_policy:
        mark = "✓"
      keyboard.add(types.InlineKeyboardButton(text=f"Установить inline_policy {inline_policy}{mark}", callback_data=f"config:inline_policy={inline_policy}"))
    keyboard.add(types.InlineKeyboardButton(text=f"Назад", callback_data=f"link:config"))
    if chat.type == "private":
      keyboard.add(types.InlineKeyboardButton(text="В начало", callback_data="link:root"))
  return item["message"], item.get("parse_mode", None), keyboard

def do_config(chat, arg):
  print (f"DO_CONFIG {chat.id} {arg}")
  chat_config = get_chat_config(chat)
  if arg == "enable":
    chat_config.lock = False
  elif arg == "disable":
    chat_config.lock = True
  elif arg.startswith("inline_policy="):
    chat_config.inline_policy = int(arg.split("=")[1])
  elif arg.startswith("tabs+"):
    chat_config.tabs.append(arg.split("+")[1])
  elif arg.startswith("tabs-"):
    try:
      chat_config.tabs.remove(arg.split("-")[1])
    except ValueError:
      pass
  save_chat_config(chat)

@bot.message_handler(commands=['menu','start'])
def show_menu(message):
  if message.chat.type != 'private': return
  msg, parse_mode, keyboard = make_menu('root', message.chat)
  bot.send_message(message.chat.id, msg, reply_markup=keyboard, parse_mode=parse_mode, message_thread_id=message.message_thread_id, disable_web_page_preview=True)

@bot.message_handler(commands=['config'])
def show_config(message):
  if message.chat.type in ['group', 'supergroup']:
    if message.from_user.id not in map(lambda x:x.user.id, bot.get_chat_administrators(message.chat.id)):
      return
  elif message.chat.type != 'private':
    return
  msg, parse_mode, keyboard = make_menu('config', message.chat)
  bot.send_message(message.chat.id, msg, reply_markup=keyboard, parse_mode=parse_mode, message_thread_id=message.message_thread_id, disable_web_page_preview=True)

@bot.callback_query_handler(func=lambda call: call.message is not None)
def menu_callback(call):
  print ("callback %s|%s|%s|%s <%s %s> %s" % (call.message.chat.type, str(call.message.chat.id), call.message.chat.title, strftime("%Y-%m-%d %H:%M:%S", localtime()), call.from_user.first_name, call.from_user.last_name, call.data))
  action, link = call.data.split(":")
  if action == "config":
    if call.message.chat.type in ['group', 'supergroup']:
      if call.from_user.id not in map(lambda x:x.user.id, bot.get_chat_administrators(call.message.chat.id)):
        return
    do_config(call.message.chat, link)
    if link.startswith("inline_policy"):
      next_menu = "config-extra"
    else:
      next_menu = "config"
    msg, parse_mode, keyboard = make_menu(next_menu, call.message.chat)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=keyboard, parse_mode=parse_mode, disable_web_page_preview=True)
  elif link in menu:
    msg, parse_mode, keyboard = make_menu(link, call.message.chat)
    item = menu[link]
    if action == "inline_link":
      bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=keyboard, parse_mode=parse_mode, disable_web_page_preview=True)
    elif action == "link":
      if "photo" in item:
        if item["photo"] in files:
          file_id = files[item["photo"]]
          print (f" send photo file_name={item['photo']} file_id={file_id}")
          bot.send_photo(call.message.chat.id, file_id, message_thread_id=call.message.message_thread_id)
        else:
          with open(os.path.join("menu", item["photo"]), "rb") as f:
            bot.send_chat_action(call.message.chat.id, "upload_photo", message_thread_id=call.message.message_thread_id)
            r = bot.send_photo(call.message.chat.id, f, message_thread_id=call.message.message_thread_id)
            file_id = r.photo[0].file_id
            save_file(item["photo"], file_id)
            print (f" uploaded photo file_name={item['photo']} file_id={file_id}")
      if "file" in item:
        if item["file"] in files:
          file_id = files[item["file"]]
          print (f" send document file_name={item['file']} file_id={file_id}")
          bot.send_document(call.message.chat.id, file_id, message_thread_id=call.message.message_thread_id)
        else:
          with open(os.path.join("menu", item["file"]), "rb") as f:
            bot.send_chat_action(call.message.chat.id, "upload_document", message_thread_id=call.message.message_thread_id)
            r = bot.send_document(call.message.chat.id, f, message_thread_id=call.message.message_thread_id)
            file_id = r.document.file_id
            save_file(item["file"], file_id)
            print (f" uploaded document file_name={item['file']} file_id={file_id}")
      bot.send_message(chat_id=call.message.chat.id, text=msg, reply_markup=keyboard, parse_mode=parse_mode, message_thread_id=call.message.message_thread_id, disable_web_page_preview=True)

@bot.message_handler(content_types=['text'])
def translate_message(message):
  msg = message.text
  print ("%s|%s <%s %s> %s" % (str(message.chat.id), strftime("%Y-%m-%d %H:%M:%S", localtime(message.date)), message.from_user.first_name, message.from_user.last_name, msg))
  chat_config = get_chat_config(message.chat)
  if "via_bot" in message.json and message.json["via_bot"]["username"] in config.blacklist_inline_bots:
    if chat_config.inline_policy == 2:
      print (f" inline bot {message.json['via_bot']['username']} blacklisted")
      try:
        bot.delete_message(message.chat.id, message.message_id)
      except telebot.apihelper.ApiException:
        print (f" delete failed")
      return
    elif chat_config.inline_policy == 1:
      return
  reply_to_message_id = message.message_id
  if chat_config.lock: return
  if time() > message.date+config.max_timediff:
    print (" message time too old :(")
    return
  msgtr = common.process_message(msg, chat_config.tabs, config.min_levenshtein_ratio, "[TEST MODE] " if config.test_mode else False)
  if msgtr:
    try:
      bot.send_message(message.chat.id, msgtr, reply_to_message_id=reply_to_message_id, message_thread_id=message.message_thread_id)
    except telebot.apihelper.ApiException:
      print (" Exception occured!")
  return

@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(inline_query):
  print (inline_query)
  keyboard = []
  for code in config.inline_tabs:
    msgtr = common.translate(code, inline_query.query)
    if config.test_mode:
      msgtr = "[TEST MODE] "+msgtr
    keyboard.append(telebot.types.InlineQueryResultArticle(code, f'{code}: {msgtr}', telebot.types.InputTextMessageContent(msgtr)))
  bot.answer_inline_query(inline_query.id, keyboard, is_personal=True)

# shutdown on SIGINT to allow quit by Ctrl-C (usally just causes requests.exceptions.ConnectionError exception)
def signal_handler(sig, frame):
  print ("Shutdown bot...")
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

load_chat_configs()
load_files()
load_menu()

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
