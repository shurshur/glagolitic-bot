from PIL import Image, ImageDraw, ImageFont
from math import floor,ceil
import common
from common import tabmap
import re

cols = 3
tab = "rus2hebr"
abc_filename = "cyrl"
font1_filename = "NotoSans-Regular.ttf"
font2_filename = "NotoSansHebrew-Regular.ttf"
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

def load_tab(code,fn=None):
  tabmap[code] = {}
  if not fn:
    fn = code + '.tab'
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
      #m1 = re.sub(r'_','(\\\\b|[^\\\\w])',m1)
      #m2 = re.sub(r'_','\\\\1',m2,1)
      #m2 = re.sub(r'_','\\\\2',m2,1)
      #m2 = re.sub(r'_','\\\\3',m2,1)
      if m2 == "!": m2 = ""
      tabmap[code][m1] = m2

load_tab(tab)

rows = ceil(len(abc)/cols)
width = 4*lsize*cols+hpad*(cols-1)+left+right
height = rows*lsize+(rows-1)*vpad+top+bottom

font1 = ImageFont.truetype(font1_filename, lsize)
font2 = ImageFont.truetype(font2_filename, lsize)

im = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(im)

header_text = "Ивритица"
w, h = draw.textsize(header_text, font=font1)
draw.text((width/2-w/2,0), text=header_text, font=font1, fill='black')

for i, a in enumerate(abc):
    row = floor(i/cols)
    col = i%cols
    print (i)
    print ((row, col))
    a = a.lower()
    a2 = common.tabmap[tab][a]
    a_ = a+"_"
    if a_ in common.tabmap[tab]:
        a2 = common.tabmap[tab][a_].replace("_", "") + "  " + a2
    #a2 = common.translate(tab, a.lower())
    #if a.lower()+"_" in common.tabmap[tab]:
    #    a2 = common.tabmap[tab][a.lower()] + " / " + common.tabmap[tab][a.lower()+"_"]
    #print ((a, a2))
    draw.text((left+col*(4*lsize+hpad),top+row*(lsize+vpad)), text=a, font=font1, fill='black')
    if a2 != '%%%':
        draw.text((left+col*(4*lsize+hpad)+2*lsize,top+row*(lsize+vpad)), text=a2, font=font2, fill='black')

im.save("hebrew.png")
