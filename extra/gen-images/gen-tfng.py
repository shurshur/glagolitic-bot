from PIL import Image, ImageDraw, ImageFont
from math import floor,ceil
import common

cols = 3
tab = "rus2tfng"
abc_filename = "cyrl"
font1_filename = "NotoSans-Regular.ttf"
font2_filename = "NotoSansTifinagh-Regular.ttf"
lsize = 24 # letter size
hpad = 20
vpad = 5
top = 50
bottom = 15
left = 10
right = 10

abc = []

with open(abc_filename, "r") as f:
    for l in f:
        abc.append(l.strip().upper())

common.load_tab(tab)

rows = ceil(len(abc)/cols)
width = 4*lsize*cols+hpad*(cols-1)+left+right
height = rows*lsize+(rows-1)*vpad+top+bottom

font1 = ImageFont.truetype(font1_filename, lsize)
font2 = ImageFont.truetype(font2_filename, lsize)

im = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(im)

header_text = "Тифинагица"
w, h = draw.textsize(header_text, font=font1)
draw.text((width/2-w/2,0), text=header_text, font=font1, fill='black')

for i, a in enumerate(abc):
    row = floor(i/cols)
    col = i%cols
    print (i)
    print ((row, col))
    a2 = common.translate(tab, a)
    print ((a, a2))
    draw.text((left+col*(4*lsize+hpad),top+row*(lsize+vpad)), text=a, font=font1, fill='black')
    if a2 != '%%%':
        draw.text((left+col*(4*lsize+hpad)+2*lsize,top+row*(lsize+vpad)), text=a2, font=font2, fill='black')

im.save("tifinagh.png")
