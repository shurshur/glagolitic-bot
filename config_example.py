# токен бота
bot_token = '12345:ABCDEF'

# токен discord-бота
discord_bot_token = 'gCYquNipNiq4zMfoT4LqEnXh.qRv3zK.gRgw9jaEq4tVHnUyXfTNprhNtMi'

# процент levenshtein distance от длины текста, выше которого выполнять транслитерацию
# сделано для того, чтобы бот не копировал длинные сообщения с незначительным употреблением глаголицы
min_levenshtein_ratio = 0.3

# максимальное количество секунд отставания от текущего времени для исключения флуда при
# офлайне бота
max_timediff = 300

# список всех таблиц
all_tabs = ["glag2cyrl","tfng2cyrl","cyrl2glag","cyrl2tfng","glag2ukr","glag2ukrilk"]
# список таблиц по умолчанию
default_tabs = ["glag2cyrl","tfng2cyrl"]
# список таблиц по умолчанию для привата с ботом
default_pm_tabs = ["glag2cyrl","tfng2cyrl","cyrl2glag"]
# список таблиц для inline mode
inline_tabs = ["cyrl2glag","cyrl2tfng"]

# список ботов, чьи сообщения будут игнорироваться или удаляться при inline_policy=1 или 2
blacklist_inline_bots = ["glagolitic_bot", "glagolitic_test_bot"]

# тестовый режим: бот будет дописывать во все сообщения [TEST MODE]
# сделано из-за того, что тестового бота иногда подключают в реальные чаты
test_mode = True
