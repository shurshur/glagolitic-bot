#!/usr/bin/env python
import sys
import csv
import re

VERBOSE = False
REVERSE_TRANSLATE = False

conv_tab = {}
jap_tab = {}
words_tab = {}

def load_conv_tab():
    if conv_tab: return
    with open("rus2jap.csv", "r") as f:
        csvin = csv.reader(f, delimiter=',', quotechar='"')
        first = True
        for r in csvin:
            if first:
                first = False
                continue
            src = r[0]
            if src == "": continue
            if src[0] == "#": continue
            conv = r[1]
            assert src.strip() == src
            assert conv.strip() == conv
            assert src not in conv_tab
            conv_tab[src] = conv

def load_jap_tab():
    if jap_tab: return
    with open("jap.csv", "r") as f:
        csvin = csv.reader(f, delimiter=',', quotechar='"')
        first = True
        for r in csvin:
            if first:
                first = False
                continue
            conv = r[0]
            if conv == "": continue
            if conv[0] == "#": continue
            jap_tab[conv] = {
               "conventional": conv+"-",
               "polivanov": r[1],
               "hepburn": r[2],
               "kunrei": r[3],
               "hiragana": r[4],
               "katakana": r[5],
            }

def rus2conv(s):
    c = []
    while s:
        #print (s)
        for src, conv in conv_tab.items():
            #print (s, src)
            if s.startswith(src):
                if VERBOSE:
                    print (f" ` FOUND {src}")
                s = s[len(src):]
                if conv != "":
                    c.extend(conv.split(" "))
                break
    return c

def rus2jap(s, target=None):
    RE_RUS = "^[а-яё]+$"
    RE_TOKENS = "[а-яё]+|[^а-яё]+"
    RE_DUP = '([бвгджзйклмнпрстфхцчшщ])\\1+'
    s = s.lower()
    s = re.sub(RE_DUP, '\\1', s)
    tokens = re.findall(RE_TOKENS, s)
    out = []
    for t in tokens:
        if re.match(RE_RUS, t):
            if VERBOSE:
                print (f"PROCESS rus token {t}")
            conv = rus2conv(t)
            conv_delimited = "-".join(conv)
            if target:
                conv = [jap_tab[x][target] for x in conv]
            conv_str = "".join(conv)
            if VERBOSE:
                print (f" * RESULT {t} -> {conv_str} ({conv_delimited})")
            if target == "conventional": conv_str = conv_str.rstrip("-")
            out.append(conv_str)
        else:
            if VERBOSE:
                print (f"PASS token {t}")
            out.append(t)
    out = "".join(out)
    return out

def load_all():
    load_conv_tab()
    load_jap_tab()

