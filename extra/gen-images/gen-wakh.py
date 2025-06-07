from PIL import Image, ImageDraw, ImageFont
from math import floor,ceil
import common

data = {
    "cyrl": {
        "name": "Кириллица",
        "font": "NotoSans-Regular.ttf",
        "text": "Кириллица",
        "tab": None
    },
    "latn": {
        "name": "Латиница",
        "font": "NotoSans-Regular.ttf",
        "text": "Latinica",
        "tab": None
    },
    "copt": {
        "name": "Коптица",
        "font": "NotoSansCoptic-Regular.ttf",
        "text": "Коптица",
        "tab": "rus2copt"
    },
    "glag": {
        "name": "Глаголица",
        "font": "NotoSansGlagolitic-Regular.ttf",
        "text": "Глаголица",
        "tab": "rus2glag",
    },
    "hebr": {
        "name": "Ивритица",
        "font": "NotoSansHebrew-Regular.ttf",
        "text": "Ивритица",
        "tab": "rus2hebr",
    },
    "tfng": {
        "name": "Тифинагица",
        "font": "NotoSansTifinagh-Regular.ttf",
        "text": "Тифинагица",
        "tab": "rus2tfng",
    },
    "jamo": {
        "name": "Чамица",
        "font": "NotoSansCJK-Regular.ttc",
        "text": "Чамица",
        "tab": "rus2jamo",
    },
    "hang": {
        "name": "Хангылица",
        "font": "NotoSansCJK-Regular.ttc",
        "text": "Хангылица",
        "tab": "rus2hang",
    },
    "hira": {
        "name": "Хираганица",
        "font": "NotoSansCJK-Regular.ttc",
        "text": "Хираганица",
        "tab": "rus2hira",
    },
    "kana": {
        "name": "Катаканица",
        "font": "NotoSansCJK-Regular.ttc",
        "text": "Хангылица",
        "tab": "rus2kana",
    },
}

lsize = 24 # letter size
hpad = 20
vpad = 5
top = 50
bottom = 15
left = 10
right = 10

main_font = ImageFont.truetype("NotoSans-Regular.ttf", lsize)

rows = len(data)
#width = 4*lsize*cols+hpad*(cols-1)+left+right
height = rows*lsize+(rows-1)*vpad+top+bottom
width = 400

im = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(im)

header_text = "Славянские письмена"
#w, h = draw.textsize(header_text, font=main_font)
_, _, w, h = draw.textbbox((0,0), header_text, font=main_font)
draw.text((width/2-w/2,0), text=header_text, font=main_font, fill='black')

for row,v in enumerate(data.values()):
    print (row, v)
    if v["tab"] and v["tab"] != "rus2hang": common.load_tab(v["tab"])
    if v["tab"]: stext = common.translate(v["tab"], v["text"])
    else:        stext = v["text"]
    font = ImageFont.truetype(v["font"], lsize)

    draw.text((left, top+row*(lsize+vpad)), text=v["name"], font=main_font, fill="black")
    draw.text((int(width/2)+left, top+row*(lsize+vpad)), text=stext, font=font, fill="black")

im.save("wakh.png")
