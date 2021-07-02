#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Janis Zuters

wordendsymbol = '¶'
wordstartsymbol = ''
linksymbol = '⇔'

def isalpha_dash(text):
    for t in text:
        if t.isalpha()==False and t!='-': return False
    return True

def isalpha_dash_apo(text):
    for t in text:
        if t.isalpha()==False and t!='-' and t!="'": return False
    return True

def words_match(w1,w2):
    minlen = min(len(w1),len(w2))
    for i in range(minlen):
        if w1[i]!=w2[i]: return i
    return minlen

