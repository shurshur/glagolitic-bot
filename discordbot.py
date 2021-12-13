#!/usr/bin/env python3
import sys
import os
import re
import json
from time import time, localtime, strftime, sleep

import disnake as discord
from disnake.ext import commands

import logging
logger = logging.getLogger('disnake')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='debug.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

try:
    from Levenshtein import distance as levenshtein_distance
except ImportError:
    from distance import levenshtein as levenshtein_distance
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

db = Sqlite3Worker("bot.db")

class ChatConfig:
    def __init__(self, guild_id=None, channel_id=None):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.tabs = config.default_tabs[:]
        self.lock = False

    def __str__(self):
        return f"<ChatConfig(guild_id={self.guild_id}, channel_id={self.channel_id}, tabs={self.tabs}, lock={self.lock})>"

chat_configs = {}

def get_chat_config(guild, channel):
    global chat_configs
    guild_id = guild.id if guild else None
    channel_id = channel.id if channel else None
    chat_key = f'{guild.id if guild else ""}:{channel.id if channel else ""}'
    chat_config = chat_configs.get(chat_key, None)
    if not chat_config:
        if guild:
            chat_config = chat_configs.get(f"{guild_id}:", None)
            if not chat_config:
                chat_config = ChatConfig(guild_id)
                chat_config.tabs = config.default_tabs[:]
                chat_configs[f"{guild_id}:"] = chat_config
        elif channel and str(channel.type) == "private":
            chat_config = ChatConfig(None, channel_id)
            chat_config.tabs = config.default_pm_tabs[:]
            chat_configs[f":{channel_id}"] = chat_config
        else:
            raise BaseException("Something impossible")
    assert chat_config
    return chat_config

def save_chat_config(guild, channel):
    guild_id = guild.id if guild else ""
    channel_id = channel.id if channel else ""
    chat_key = f"{guild_id}:{channel_id}"
    chat_config = get_chat_config(guild, channel)
    db.execute("INSERT INTO discord_chat_config (chat_key, tabs, lock) VALUES (?,?,?) ON CONFLICT(chat_key) DO UPDATE SET tabs=excluded.tabs,lock=excluded.lock",
        (chat_key, ",".join(chat_config.tabs), chat_config.lock))

def init_table(table, sql):
    res = db.execute("SELECT * FROM sqlite_master where tbl_name=?",(table,))
    if len(res) < 1:
        db.execute(sql)

init_table("discord_chat_config","""CREATE TABLE discord_chat_config (
    chat_key VARCHAR(256) NOT NULL UNIQUE,
    tabs TEXT VARCHAR(256),
    lock BOOLEAN
)""")

def load_chat_configs():
    global chat_configs
    res = db.execute("SELECT chat_key,tabs,lock FROM discord_chat_config")
    chat_configs = {}
    for row in res:
        chat_config = ChatConfig()
        chat_key, tabs, lock = row
        guild_id, channel_id = chat_key.split(":")
        chat_config.guild_id = guild_id if guild_id else None
        chat_config.channel_id = channel_id if channel_id else None
        tabs = tabs.split(",")
        for code in tabs[:]:
            if code not in config.all_tabs:
                tabs.remove(code)
        chat_config.tabs = tabs
        chat_config.lock = True if lock else False
        chat_configs[chat_key] = chat_config

def do_config(guild, channel, arg):
    #print (f"DO_CONFIG {guild} {channel} {arg}")
    chat_config = get_chat_config(guild, channel)
    if arg == "enable":
        chat_config.lock = False
    elif arg == "disable":
        chat_config.lock = True
    elif arg.startswith("tabs+"):
        chat_config.tabs.append(arg.split("+")[1])
    elif arg.startswith("tabs-"):
        chat_config.tabs.remove(arg.split("-")[1])
    save_chat_config(guild, channel)

menu = None

def load_menu():
    global menu
    menu = json.load(open("discordmenu/menu.json","r"))
    for _, item in menu.items():
        msg = item["message"]
        if re.match('[-_\w]+\.(?:txt|md|html)', msg):
            with open(os.path.join("discordmenu", msg), "r") as f:
                item["message"] = f.read()

class MenuButton(discord.ui.Button['Menu']):
    def __init__(self, *, name, action, link=None, row=None):
        super().__init__(style=discord.ButtonStyle.secondary, label=name, row=row)
        self.action = action
        self.name = name
        self.link = link

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        channel_type = str(interaction.channel.type)
        #print (f"CALLBACK guild_id={interaction.guild_id} channel_id={interaction.channel_id} channel_type={channel_type}")
        assert channel_type in ['text','private']
        if self.action == "config":
            do_config(interaction.guild, interaction.channel, self.link)
            view = Menu(node="config", guild=interaction.guild, channel=interaction.channel)
            await interaction.response.edit_message(content=menu["config"]["message"], view=view)
            return
        view = Menu(node=self.link, guild=interaction.guild, channel=interaction.channel)
        item = menu[self.link]
        att = []
        emb = None
        if "photo" in item:
            att.append(discord.File(os.path.join("discordmenu", item["photo"])))
        elif "file" in item:
            att.append(discord.File(os.path.join("discordmenu", item["file"])))
        if self.action in ["link","inline_link"]:
            await interaction.response.edit_message(content=menu[self.link]["message"], view=view, files=att)
        else:
            await interaction.response.send_message(content="Странное значение action :(")

class Menu(discord.ui.View):
    def __init__(self, *, node='root', guild=None, channel=None):
        super().__init__()
        self.__row = 0
        self.__col = 0
        item = menu[node]
        if isinstance(item["buttons"], list):
            for b in item["buttons"]:
                if b["action"] in ["link","inline_link","close"] and b.get("discord", True):
                    if b["action"] == "close":
                        self.add_button(b["caption"], b["action"])
                    else:
                        self.add_button(b["caption"], b["action"], b["link"])
        elif item["buttons"] == "config_buttons":
            assert guild or channel
            chat_config = get_chat_config(guild, channel)
            for code in config.all_tabs:
                if code in chat_config.tabs:
                    self.add_button(f"Выключить {code}", "config", f"tabs-{code}")
                else:
                    self.add_button(f"Включить {code}", "config", f"tabs+{code}")
            if chat_config.lock:
                self.add_button(f"Включить бота в чате", "config", "enable")
            else:
                self.add_button(f"Выключить бота в чате", "config", "disable")
            if not guild:
                self.add_button("В начало", "link", "root")

    def add_button(self, name, action, link=None):
        self.add_item(MenuButton(name=name, action=action, link=link, row=self.__row))
        self.__col += 1
        if self.__col > 4:
            self.__col = 1
            self.__row += 1

#test_guilds = [716373583982493697]
test_guilds = None
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), sync_commands_debug=True, test_guilds=test_guilds)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.bot:
        return

    await bot.process_commands(message)

    if message.type != discord.MessageType.default:
        return

    chat_config = get_chat_config(message.guild, message.channel)
    if chat_config.lock: return

    msg = message.content
    if len(msg) == 0:
        logger.debug ("OOPS, zero-length message...")
        logger.debug (message)
        return
    msgtr = common.process_message(msg, chat_config.tabs, config.min_levenshtein_ratio, "[TEST MODE] " if config.test_mode else False)
    if msgtr:
        em = discord.Embed(description=msgtr)
        await message.channel.send(embed=em)

@bot.command(name="menu")
@commands.dm_only()
async def show_menu(ctx: commands.Context):
    await ctx.send(content=menu["root"]["message"], view=Menu(node="root", guild=ctx.guild, channel=ctx.channel))

@bot.command(name="config")
async def show_config(ctx: commands.Context):
    if ctx.guild:
        if not ctx.author.guild_permissions.administrator:
            return
    await ctx.send(content=menu["config"]["message"], view=Menu(node="config", guild=ctx.guild, channel=ctx.channel))

@bot.slash_command(name="menu", description="Glagolitic Bot menu")
async def show_menu(interaction):
    if interaction.guild:
        await interaction.response.send_message(content="Эта команда должна использоваться только в приватных сообщениях с ботом", ephemeral=True)
        return
    await interaction.response.send_message(content=menu["root"]["message"], view=Menu(node="root", guild=interaction.guild, channel=interaction.channel), ephemeral=True)

@bot.slash_command(name="config", description="Glagolitic Bot configuration")
async def slash_config(interaction):
    if interaction.guild:
        if not interaction.author.guild_permissions.administrator:
            await interaction.response.send_message(content="Вы должны быть администратором сервера для использования этой команды", ephemeral=True)
            return
    await interaction.response.send_message(content=menu["config"]["message"], view=Menu(node="config", guild=interaction.guild, channel=interaction.channel), ephemeral=True)

load_chat_configs()
load_menu()

bot.run(config.discord_bot_token)
