import re
try:
  from Levenshtein import distance as levenshtein_distance
except ImportError:
  from distance import levenshtein as levenshtein_distance

tabmap = {}

def load_tab(code,fn=None):
  tabmap[code] = []
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
      m1 = re.sub(r'_','(\\\\b|[^\\\\w])',m1)
      m2 = re.sub(r'_','\\\\1',m2,1)
      m2 = re.sub(r'_','\\\\2',m2,1)
      m2 = re.sub(r'_','\\\\3',m2,1)
      if m2 == "!": m2 = ""
      tabmap[code].append((m1, m2))

def load_tabs(tabs):
  global tabmap
  tabmap = {}
  for tab in tabs:
    load_tab(tab)

def translate(code, text):
  for k,v in tabmap[code]:
    text = re.sub(k, v, text)
  # в тифинагице текст из одних "ь" может превратиться в пустую строку, это нехорошо
  if text == "":
    text = "%%%"
  return text

def process_message(msg, tabs, min_levenshtein_ratio, test_mode_prefix=False):
  for code in tabs:
    msgtr = translate(code, msg)
    dist = levenshtein_distance(msg, msgtr)
    ratio = dist/len(msg)
    if ratio > min_levenshtein_ratio:
      print (" code=%s ratio=%lf => %s" % (code, ratio, msgtr))
      if test_mode_prefix:
        msgtr = test_mode_prefix+msgtr
      return msgtr
  return None
