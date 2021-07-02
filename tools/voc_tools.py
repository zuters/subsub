#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Janis Zuters

from collections import Counter
from .char_tools import wordendsymbol, linksymbol, isalpha_dash, isalpha_dash_apo

def alpha_preprocess(word):
    """ splits away non-alpha symbols from alpha symbols,
        and non-alpha symbols are split symbol by symbol,
        word-end-symbol put after alpha sequences,
        all sequences within word linked by linksymbol
        e.g., "alpha1.2beta" split into
        ['alpha¶', '⇔', '1', '⇔', '.', '⇔', '2', '⇔', 'beta¶']
        with word-end-symbol='¶' and linksymbol="⇔"
    """
    res = []
    lastalpha = False
    for pos in range(len(word)):
        w = word[pos]
        if w.isalpha():
            if lastalpha:
                res[-1]+=w
            else:
                if len(res)>0:
                    res.append(linksymbol)
                res.append(w)
            lastalpha = True
        else:
            if lastalpha:
                res[-1]+=wordendsymbol
            if len(res)>0:
                res.append(linksymbol)
            res.append(w)
            lastalpha = False
    if lastalpha:
        res[-1]+=wordendsymbol
    return res

def extract_frequent_vocabulary(fin,alphaonly=0,tolower=False,addwordend=True):
     # 0-process all, 1-process alpha only, 11-alpha+dash, 11-alpha+dash+apostrophe, 2-non-alpha special preprocessing
    lopen = False
    if isinstance(fin,str): 
        fin = open(fin, 'r', encoding='utf-8')
        lopen = True
    vocab = Counter()
    for line in fin:
        if tolower: line = line.lower()
        for word in line.split():
            if alphaonly==2:
                for w in alpha_preprocess(word):
                    if w!=linksymbol:
                        vocab[w] += 1
            else:
                if alphaonly==1 and word.isalpha()==False: continue
                elif alphaonly==11 and isalpha_dash(word)==False: continue
                elif alphaonly==111 and isalpha_dash_apo(word)==False: continue
                if addwordend: word+=wordendsymbol
                vocab[word] += 1
    if lopen:
        fin.close()
    return vocab

def load_frequent_vocabulary(inname):
    fin = open(inname, 'r', encoding='utf-8')
    vocab = Counter()
    for line in fin:
        item = line.split()
        word = item[0]
        num = int(item[1])
        vocab[word] = num
    fin.close()
    return vocab

def save_frequent_vocab(fvocab,foutname,sortcol=1,rev=True,post=False):
    # sortcol: 0-word, 1-freq
    fout = open(foutname, 'w', encoding='utf-8')
    for w in sorted(fvocab.items(),key=lambda x: x[sortcol],reverse=rev):
        if post:
            ww = w[0][::-1]
        else:
            ww = w[0]
        fout.write(" {0} {1}\n".format(ww,w[1]))
    fout.close()

def get_required_frequency(fvocab,rate0rel,rate0):
    # sortcol: 0-word, 1-freq
    goodcount = max(rate0,int(len(fvocab)*rate0rel))
    cnt=0
    for w in sorted(fvocab.items(),key=lambda x: x[1],reverse=True):
        if cnt==goodcount:
            return w[1]
        cnt+=1
    return 1

def max_frequency_vocab(fvocab):
    for w in sorted(fvocab.items(),key=lambda x: x[1],reverse=True):
        return w[1]

def get_most_frequent_vocabulary(fvocab,amount):
    mfvocab = {}
    for item in sorted(fvocab.items(),key=lambda x: x[1],reverse=True)[:amount]:
        mfvocab[item[0]] = 1
    return mfvocab

def get_most_frequent_avocabulary(avocab,amount):
    mfvocab = {}
    for item in sorted(avocab.items(),key=lambda x: x[1][0],reverse=True)[:amount]:
        mfvocab[item[0]] = 1
    return mfvocab

def extract_frequent_vocabulary_postfix(vocin,maxpost=7):
    vocab = Counter()
    for word in vocin:
        if word.isalpha():
            for postnum in range(1,min(maxpost,len(word)-2)):
                post = word[-postnum:]
                vocab[post] += 1
    return vocab

def add_to_vocab_multi(word,vocab,freq):
    for pos in range(len(word)):
        if not word[pos].isalpha(): return
        vocab[word[:pos+1]] += freq

def add_to_vocab_multi_reverse(word,vocab,postmaxlen,minrootlen,freq):
    """ Adds one tuple-word to tree structure - one node per symbol
        word end in the tree characterized by node[0]>0
    """
    pos = 0
    while pos<len(word)-minrootlen and pos<postmaxlen:
        vocab[word[:pos+1]] += freq
        pos+=1
    