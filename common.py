import re
try:
  from Levenshtein import distance as levenshtein_distance
except ImportError:
  from distance import levenshtein as levenshtein_distance

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

def load_dicts():
  global dictmap
  dictmap = {}
  load_dict("glag2cyrl","glag2cyrl.tab")
  load_dict("tfng2cyrl","tfng2cyrl.tab")
  load_dict("cyrl2glag","cyrl2glag.tab")
  load_dict("cyrl2tfng","cyrl2tfng.tab")

def translate(code, text):
  for k,v in dictmap[code]:
    text = re.sub(k, v, text)
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
