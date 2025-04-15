# токен бота
bot_token = '12345:ABCDEF'

# токен discord-бота
discord_bot_token = 'gCYquNipNiq4zMfoT4LqEnXh.qRv3zK.gRgw9jaEq4tVHnUyXfTNprhNtMi'

# реквизиты matrix-бота, их можно получить с помощью скрипта matrix-get-token.py
matrix_homeserver = "https://matrix.org"
matrix_user_id = "myawesomebot:matrix.org"
matrix_device_id = "MOO_DEVICE"
matrix_access_token = "syt_ZjBiYTNlOWJmNT_jOTJkZjk0NmQyNmE3NzViOTcgIC"

# токен бота для revolt
revolt_bot_token = "XYZ_***"

# токен бота для guilded
guilded_bot_token = "gapi_***"

# процент levenshtein distance от длины текста, выше которого выполнять транслитерацию
# сделано для того, чтобы бот не копировал длинные сообщения с незначительным употреблением глаголицы
min_levenshtein_ratio = 0.3

# максимальное количество секунд отставания от текущего времени для исключения флуда при
# офлайне бота
max_timediff = 30

# список всех таблиц
all_tabs = ["glag2rus","tfng2rus","rus2glag","rus2tfng","glag2ukr","ukr2glag","hebr2rus","rus2hebr","copt2rus","rus2copt","rus2hira","rus2kana","rus2jamo","rus2hang"]
# список таблиц по умолчанию
default_tabs = ["glag2rus","tfng2rus"]
# список таблиц по умолчанию для привата с ботом
default_pm_tabs = ["glag2rus","tfng2rus","hebr2rus","copt2rus","rus2glag"]
# список таблиц для inline mode
inline_tabs = ["rus2glag","rus2tfng","ukr2glag","rus2hebr","rus2copt","rus2hira","rus2kana","rus2jamo","rus2hang"]

# список ботов, чьи сообщения будут игнорироваться или удаляться при inline_policy=1 или 2
blacklist_inline_bots = ["glagolitic_bot", "glagolitic_test_bot"]

# тестовый режим: бот будет дописывать во все сообщения [TEST MODE]
# сделано из-за того, что тестового бота иногда подключают в реальные чаты
test_mode = True
