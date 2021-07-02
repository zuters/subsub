    #!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Janis Zuters
# SUBSUB word segmentation tool
# requires Python 3.6+

import os
import time
import pickle
from collections import Counter

#from tools.file_tools import parallel_files_reader, get_filenum_text
#from tools.splitlen import splitcorpora
from tools.wordtree_tools import noo
from tools.voc_tools import load_frequent_vocabulary, extract_frequent_vocabulary, save_frequent_vocab

#from copy import deepcopy

#def settostr(ss):
#    return "-".join(sorted([s for s in ss]))
#def strtoset(st):
#    return set(st.split('-'))
def listtostr(ss):
    return "-".join(sorted(ss))
#def strtolist(st):
#    return st.split('-')

class rlp:
    DEBUG = 0

    def get_vocabulary(corpusdir,vocdir,corpuscode,lang):
        pathvoc = vocdir+"/"+corpuscode+".lower.all."+lang+".voc"
        if os.path.exists(pathvoc)==False:
            pathcorpus = corpusdir+"/"+corpuscode+"."+lang
            print("Collecting vocabulary:",lang)
            fin = open(pathcorpus, 'r', encoding='utf-8')
            vocab = extract_frequent_vocabulary(fin,alphaonly=0,tolower=True,addwordend=False)
            save_frequent_vocab(vocab,pathvoc,sortcol=0,rev=False)
            fin.close()
        else:
            print("Loading vocabulary:",lang)
            vocab = load_frequent_vocabulary(pathvoc)
        return vocab

    @classmethod
    def init_coeffs(cls):
        cls.MAX_INITIAL_SUBWORD_FORMS = 10
        cls.BEST_ENDINGS = 300
        cls.FULLWORD_COEFF = 1.0
    
    @classmethod
    def init(cls):
        cls.START = time.perf_counter()
        cls.DEBUG = 1
        cls.RAW_FILE_DIRECT = True
        cls.statusmsg("Processing subsub segmentation...")
        cls.logfiles={}
        if cls.RAW_FILE_DIRECT:
            fin = open(cls.corpus_filename, 'r', encoding='utf-8')
            cls.statusmsg(f"Corpus: {cls.corpus_filename}")
            cls.vocab1 = extract_frequent_vocabulary(fin,alphaonly=0,tolower=True,addwordend=False)
            cls.statusmsg("Corpus OK")
        else:
            cls.vocab1 = cls.get_vocabulary(cls.corpusdir,cls.vocdir,cls.corpuscode,cls.lang1)
    
    @classmethod
    def statusmsg(cls,msg):
        if cls.DEBUG!=0:
            print("{0} (s): {1:.2f}".format(msg,time.perf_counter()-cls.START))
    
    @classmethod
    def log(cls,*msg,fid="",flush=False,sep=' ',end='\n'):
        if cls.DEBUG!=0:
            if fid[:1] == "@":
                fid = fid[1:]
            else:
                fid = "log" + fid
            if fid not in cls.logfiles:
                cls.logfiles[fid] = open (f"{cls.outdir}/{fid}.txt","w",encoding="utf-8")
            for pos,m in enumerate(msg):
                if pos==0:
                    mysep=''
                else:
                    mysep=sep
                print(mysep,m,file=cls.logfiles[fid],sep='',end='')
            print(file=cls.logfiles[fid],end=end)
            if flush:
                cls.logfiles[fid].flush()
    
    @classmethod
    def clear(cls):
        for f in cls.logfiles:
            cls.logfiles[f].close()
    
    def create_noodle_from_vocab(vocab,specialfunini=None,specialfun=None,specialdata=None,reverse=False):
        noodle = noo(specialfunini=specialfunini)
        for word in vocab:
            if reverse: w=word[::-1]
            else: w=word
            noodle.add_word(w,vocab[word],specialfunini=specialfunini,
                            specialfun=specialfun,specialdata=specialdata)
        return noodle

    @classmethod
    def init_data_info(cls):
        cls.lang1 = "en"
#        rlp.lang2 = "en"
        cls.corpuscode = "train"
#        rlp.corpuscode = "tune"
#        rlp.post = True
#        rlp.post = False
    
    @classmethod
    def init_paths(cls):
        cls.maindir = "d:/nmt"
        if os.path.exists(cls.maindir)==False:
            cls.maindir = "c"+cls.maindir[1:]
        cls.corpusdir = cls.maindir
        cls.outdir = cls.maindir + "/out"
        cls.splitdir = cls.maindir + "/split"
        cls.vocdir = cls.maindir + "/voc"
        cls.corpus_filename = cls.corpusdir+"/"+"train"+"."+"lv"
        cls.segseg_model_filename = cls.outdir+"/"+"treemodel.bin"

def calculate_initial_ending_info(nnn):
    # collect endings initial
    endings0 = Counter()
    for n in noo.iterate_nodes(nnn):
        if n.subword_forms>=2 and n.subword_forms<=rlp.MAX_INITIAL_SUBWORD_FORMS and n.pos>=1:
            for w,occ in noo.iterate_words_also_self(n):
                if w=="" or w.isalpha():
                    endings0[w]+=1
    
    # filter best endings
    endings2 = {}
    i = 0
    for w,f in sorted(endings0.items(),key=lambda wf: wf[1],reverse=True):
        endings2[w] = i
#        endings2x.append(w)
        i+=1
        if i>=rlp.BEST_ENDINGS:
            break
        
    # calculate ending link values
    endix = [[0 for _ in range(rlp.BEST_ENDINGS)] for _ in range(rlp.BEST_ENDINGS)]
    for n in noo.iterate_nodes(nnn):
        if n.pos>=1:
            ends = set()
            for w,occ in noo.iterate_words_also_self(n):
                if w in endings2:
                    ends.add(w)
            if len(ends)>1:
                for e in ends:
                    for f in ends:
                        if e!=f:
                            endix[endings2[e]][endings2[f]]+=1
#                            endixdict[e][f]+=1
#    save_frequent_vocab(endings0,rlp.outdir+"/"+"endings.txt",rev=True)                            
    return endings2,endix

def calculate_node_significance(nnn,endings2,endix):
    # calculate node values from words - 2nd-level statistics
    # 2.1. calculating significance of nodes to hold endings v.1. (subword_forms_plus)
    for n in noo.iterate_nodes(nnn):
        n.val1 = 0
        n.lendings1ext = set()
        n.lendings1neg = set()
        ends = set()
        for w,occ in noo.iterate_words_also_self(n):
            if w in endings2:
                ends.add(w)
        if len(ends)>1:
            mval = 0
            for e in ends:
                for f in ends:
                    if e!=f:
                        val = endix[endings2[e]][endings2[f]]
                        mval += val
            n.val1 += mval
    # 2.3. register best endings, v.0, with regard to the most significant for each word
    for n in noo.iterate_nodes(nnn):
        if n.pos>=1 and n.word_occ>0:
            nn = n
            cending = ""
#            nnext = None
            while nn.pos>=1 and (cending in endings2 or cending[1:] in endings2):
                if nn.val1>0:
                    if cending in endings2:
                        nn.lendings1ext.add(cending)
#                        nn.lendings1ext.add(cending)
#                    elif nnext is not None and nn.val1>nnext.val1:
#                        nn.lendings1ext.add(cending)
                cending = nn.char + cending
#                nnext = nn
                nn = nn.prev

def calculate_good_bad(nnn,dolog=False):
    for n in noo.iterate_nodes(nnn):
        n.bad_stem = False
        n.bad_stem2 = False
        n.good_stem2 = False
        if n.pos>=1:
            if n.val1>n.prev.val1:
                nok = True
                ncnt = 0
                for nn in n.next:
                    nnext = n.next[nn]
                    if nnext.subword_forms>1:
                        if nnext.val1<n.val1:
                            ncnt += 1
                        else:
                            nok = False
                if nok and ncnt>0:
                    n.good_stem2 = True
            if n.val1<n.prev.val1:
                nok = True
                ncnt = 0
                for nn in n.next:
                    nnext = n.next[nn]
                    if nnext.val1>n.val1:
                        ncnt += 1
                    else:
                        nok = False
                if nok and ncnt>0:
                    n.bad_stem2 = True
    for n in noo.iterate_nodes(nnn):
        nlen = len(n.lendings1ext)
        if n.pos>=1 and nlen>0:
            nprev = n.prev
            diff = 1
            while nprev.pos>=0:
                plen = len(nprev.lendings1ext)
                if plen>0:
                    local_endings_plus = set([n.subword[-diff:]+e for e in n.lendings1ext])
                    if nlen != plen:
                        if local_endings_plus.issubset(nprev.lendings1ext):
                            n.bad_stem = True
#                            rlp.log(f"{n.subword} {nprev.subword} {diff}",fid="_badstem")
                            break
                        elif nprev.lendings1ext.issubset(local_endings_plus):
                            nprev.bad_stem = True
#                            rlp.log(f"{n.subword} {nprev.subword} {diff} {local_endings_plus} {nprev.lendings1} {nprev.lendings1ext}",fid="_prevbadstem")
                            break
                    elif local_endings_plus==nprev.lendings1ext:
                        if n.val1>nprev.val1:
#                        n.bad_stem = True
                            nprev.bad_stem = True
                        break
                nprev = nprev.prev
                diff+=1      
                
    pars3good = {}
    pars3good['-'] = Counter()
    pars3bad = {}
    pars3bad['-'] = Counter()
    parads33 = (pars3good,pars3bad)
    for n in noo.iterate_nodes(nnn):
        chrx = [n.char]
        if n.subword.isalpha():
            pc = n.val1 * 0.001 / (len(n.lendings1ext)+1)
            if n.good_stem2:
                gb = 0
            elif n.bad_stem or n.bad_stem2:
                gb = 1
            else:
                gb = 0
            parads3local = parads33[gb]
            for e in n.lendings1ext:
                if e not in parads3local:
                    parads3local[e] = Counter()
            for e in n.lendings1neg:
                if e not in pars3bad:
                    pars3bad[e] = Counter()
            for prevcontext in chrx:
                parads3local['-'][prevcontext] += pc   
                for e in n.lendings1ext:
                    parads3local[e][prevcontext] += pc   
                for e in n.lendings1neg:
                    pars3bad[e][prevcontext] += 1   
    return pars3good,pars3bad

def calculate_val3(nnn,endings2,parads33):
    for n in noo.iterate_nodes(nnn):
        chrx = [n.char]
#        if len(n.subword)>=2:
#            chrx.append(n.subword[-2:])
        leset = set()
        for w,occ in noo.iterate_words_also_self(n):
#            if w in endings2:
#                n.cnt3 += 1
#            if w in endings2 or e.isalpha() and len(w)<=MAX_EXTRA_ENDING_LEN:
            if w in endings2: # or w[1:] in endings2:
                leset.add(w)
#        parads33 = (pars3good,pars3bad)
        n.val30 = [0.0,0.0,0.0]
        n.val3 = [0.0,0.0,0.0]
#        if len(leset)>1:
        for gb in range(2):
            parads33actual = parads33[gb]
            for prevcontext in chrx:
                n.val30[gb] += parads33actual['-'][prevcontext]
            for e in leset:
                if e in parads33actual:
                    for prevcontext in chrx:
                        n.val3[gb] += parads33actual[e][prevcontext] #* COEFFPREV[len(prevcontext)] #* COEFFPREV_BAD[gb]
        n.val3[2] = n.val3[0]                            
        if n.val3[1]>=1.0:
            n.val3[2] /= n.val3[1]                            
        n.val30[2] = n.val30[0]                            
        if n.val30[1]>=1.0:
            n.val30[2] /= n.val30[1]                            
    if rlp.DEBUG!=0:
        pars3good = parads33[0]
        pars3bad = parads33[1]
        for p,ccc in sorted(pars3good.items(), key=lambda x: x[0]):
            rlp.log(f" [{p}]",fid="@fparads3prev")
            for px,pxc in sorted(ccc.items(),key=lambda x: -x[1]):
                rlp.log(f"  * {pxc} {px} ",fid="@fparads3prev")
        for p,ccc in sorted(pars3bad.items(), key=lambda x: x[0]):
            rlp.log(f" [{p}]",fid="@fparads3badprev")
            for px,pxc in sorted(ccc.items(),key=lambda x: -x[1]):
                rlp.log(f"  * {pxc} {px} ",fid="@fparads3badprev")

          
def extend_local_endings(nnn,endings2):
    endings2ext = set()
    for n in noo.iterate_nodes(nnn):
        if n.word_occ>0 and n.subword.isalpha():
            nn = n
            cending = ""
            mxcvalstem = 0.0
            mxcstem = "-"
            mxnn = None
            while nn.pos>=1 and cending[1:] in endings2:
                if nn.val3[2]*nn.val30[2]>mxcvalstem:
#                if nn.val1>mxcvalstem:
                    mxcvalstem = nn.val3[2]*nn.val30[2]
#                    mxcvalstem = nn.val1
                    mxcstem = cending
                    mxnn = nn
                cending = nn.char + cending
                nn = nn.prev
            if mxnn is not None:
                mxnn.lendings1ext.add(mxcstem)
                if mxcstem not in endings2:
                    endings2ext.add(mxcstem)
    for n in noo.iterate_nodes(nnn):
        if n.word_occ>0 and n.subword.isalpha():
            nn = n
            cending = ""
            while nn.pos>=1 and cending[1:] in endings2:
                if cending in endings2ext and cending not in nn.lendings1ext:
                    nn.lendings1neg.add(cending)
                cending = nn.char + cending
                nn = nn.prev
#                    rlp.log(f"[{mxcstem}] {mxnn.subword}",fid="_extended")
    return endings2ext
                
def iterate_pairs(aa):
    for i in range(len(aa)):
        for j in range(i+1,len(aa)):
            yield aa[i],aa[j]

def iterate_triples(aa):
    for i in range(len(aa)):
        for j in range(i+1,len(aa)):
            for k in range(j+1,len(aa)):
                yield aa[i],aa[j],aa[k]
                
def calculate_local_endings3(nnn,endings2plus,parads33):
    for n in noo.iterate_nodes(nnn):
        n.lendings3 = Counter()
    for n in noo.iterate_nodes(nnn):
#        n.endvalues3 = []
        n.endvalues3x = []
        if n.word_occ>0:
            nn = n
            cending = ""
            mxcval = 0.0
            mxc = "-"
            while nn.pos>=1 and cending in endings2plus:
                chrx = [nn.char]
#                if len(nn.subword)>=2:
#                    chrx.append(nn.subword[-2:])
#                cendingstemval = [0.0,0.0,0.0]
                cendingval = [0.0,0.0,0.0]
                e = cending
                for gb in range(2):
                    parads33actual = parads33[gb]
                    if e in parads33actual:
                        for prevcontext in chrx:
                            cendingval[gb] += parads33actual[e][prevcontext] #* COEFFPREV[len(prevcontext)] #* COEFFPREV_BAD[gb]
                cendingval[2] = cendingval[0]
                if cendingval[1]>=1.0:
                    cendingval[2] /= cendingval[1]
                if cendingval[2]>mxcval:
                    mxcval = cendingval[2]
                    mxc = cending
                n.endvalues3x.append((cending,round(cendingval[2],3)))
                cending = nn.char + cending
                nn = nn.prev
            nn = n
            cending = ""
            for i in range(len(n.endvalues3x)):
                if mxcval>0.1:
                    val = n.endvalues3x[i][1] / mxcval
                    if val > 0.1:
                        nn.lendings3[cending] += n.endvalues3x[i][1] / mxcval
                        nn.lendings3[cending] = round(nn.lendings3[cending],2)
                cending = nn.char + cending
                nn = nn.prev
            n.endvalues3x.insert(0,[(mxc,round(mxcval,2))])
    for n in noo.iterate_nodes(nnn):
        if len(n.lendings3)==1:
            n.lendings3.clear()

def calculate_ending_contexts(nnn):
    endcontext = {}
    paircontext = {}
    SUPER_COEF = 5
    SOLE_COEF = 0.2
    for n in noo.iterate_nodes(nnn):
        cont = n.char
        if len(n.lendings3)>0:
            if n.good_stem2 or n.bad_stem==False and n.bad_stem2==False: ok = 1
            else: ok = -1
            ss = n.lendings3.values()
            avg = sum(ss) / len(ss)
            coef = ok * avg ** SUPER_COEF
            for e in n.lendings3:
                if e not in endcontext:
                    endcontext[e] = Counter()
                endcontext[e][cont] += coef * SOLE_COEF
#                if e in ('m','s') and cont=='ī':
#                    rlp.log(f"{n.subword} {e} {coef * SOLE_COEF}",fid="_iimiis")
            for e,f in iterate_pairs(list(n.lendings3.keys())):
                ef = listtostr((e,f))
                if ef not in paircontext:
                    paircontext[ef] = Counter()
                paircontext[ef][cont] += coef
#                if e in ('m','s') and cont=='ī':
#                    rlp.log(f"{n.subword} {e} {coef}",fid="_iimiis")
#                if f in ('m','s') and cont=='ī':
#                    rlp.log(f"{n.subword} {f} {coef}",fid="_iimiis")
    return endcontext,paircontext                

def calculate_local_endings4(nnn,endcontext,paircontext):
    for n in noo.iterate_nodes(nnn):
        n.lendings4 = Counter()
        n.lendings4x = {}
        n.lendings4xsum = 0.0
    for n in noo.iterate_nodes(nnn):
        if n.pos>0:
            cont = n.char
            ends = []
            for e,occ in noo.iterate_words_also_self(n):
                if e in endcontext:
                    ends.append(e)
                    if e in endcontext and endcontext[e][cont]>0:
                        n.lendings4[e] += endcontext[e][cont]
                        n.lendings4[e] = round(n.lendings4[e],2)
            for e,f in iterate_pairs(ends):
                ef = listtostr((e,f))
                if ef in paircontext and paircontext[ef][cont]>0:
                    n.lendings4[e] += paircontext[ef][cont]
                    n.lendings4[f] += paircontext[ef][cont]
                    n.lendings4[e] = round(n.lendings4[e],2)
                    n.lendings4[f] = round(n.lendings4[f],2)

def calculate_local_endings4_extended(nnn,endcontext):
    for n in noo.iterate_nodes(nnn):
        n.endvalues4 = []
        if n.word_occ>0:
            nn = n
            cending = ""
            mval = None
            while nn.pos>=1 and cending in endcontext:
                if cending in nn.lendings4:
                    val = nn.lendings4[cending]
                    n.endvalues4.append((cending,round(val,2)))
                    if mval is None or val>mval:
                        mval = val
                cending = nn.char + cending
                nn = nn.prev
            nn = n
            cending = ""
            while nn.pos>=1 and cending in endcontext:
                if cending in nn.lendings4:
                    val = nn.lendings4[cending]
                    if mval > 0.01:
                        actualval = round(val/mval,2)
                        nn.lendings4x[cending] = actualval
                        nn.lendings4xsum += actualval
#                    else:
#                        print('*',n.subword)
                cending = nn.char + cending
                nn = nn.prev

def calculate_endsuffix_info(nnn):
    endsuffixes = Counter()
    suffixes = Counter()
    for n in noo.iterate_nodes(nnn):
        nn = n.prev
        suff = n.char
        while nn.pos>=1:
            if len(nn.lendings4x)>0:
                for e,ecnt in n.lendings4x.items():
                    endsuffixes[(suff,e)] += ecnt * nn.lendings4xsum
                    suffixes[suff] += ecnt * nn.lendings4xsum
            suff = nn.char + suff
            nn = nn.prev
            
    SUFF_RATE = 0.001
    endsuffixes2 = Counter()
    endsuffixes2x = {}
    suffixes2 = Counter()
    mxs = None
    for esuff,cnt in sorted(endsuffixes.items(),key=lambda x: -x[1]):
        esuffx = "".join(esuff)
        if mxs is None:
            mxs = cnt
        elif cnt<mxs*SUFF_RATE:
            break
        endsuffixes2[esuff] = cnt
        if esuffx not in endsuffixes2x:
            endsuffixes2x[esuffx] = []
        endsuffixes2x[esuffx].append(esuff)
    mxx = None
    for suff,cnt in sorted(suffixes.items(),key=lambda x: -x[1]):
        if mxx is None:
            mxx = cnt
        elif cnt<mxx*SUFF_RATE:
            break
        suffixes2[suff] = cnt
    if rlp.DEBUG!=0:
        for esuff,cnt in sorted(endsuffixes2.items(),key=lambda x: -x[1]):
            rlp.log(f" {esuff} {cnt}",fid="_esuff")
        for suff,cnt in sorted(suffixes2.items(),key=lambda x: -x[1]):
            rlp.log(f" {suff} {cnt}",fid="_suff")
    return endsuffixes2,endsuffixes2x

def print_word_tree(nnn):
    if rlp.DEBUG!=0:
        for n in noo.iterate_nodes(nnn):
            endstatus = '*' if n.good_stem2 else ""
            endstatus += '@@@' if n.bad_stem2 and n.bad_stem else ('@@' if n.bad_stem2 else ('@' if n.bad_stem else '(*)'))
            rlp.log(" "*(n.pos),n.subword,f"wocc={n.word_occ} swocc={n.subword_occ} swf={n.subword_forms}",
                  f"val1={n.val1} val3={n.val3}",
    #              f"(sf={n.subword_forms},socc={n.subword_occ})",
    #              f"{'@@' if n.bad_stem2 else ('@' if n.bad_stem else '(***)')}",
                  f"{endstatus}",
    #              f"({n.val1})end={list(n.lendings1)}!!!{list(n.local_endings_non)}+++{list(n.next_endings)}",
                  f"end1x={list(n.lendings1ext)} end1N={list(n.lendings1neg)}",
                  fid='@tree')
            if len(n.lendings4)>0:
                le4sort = sorted(n.lendings4.items(),key=lambda x: -x[1])
                rlp.log(" "*(n.pos),f"   * {le4sort}",fid='@tree')
            if len(n.lendings4x)>0:
                le4sort = sorted(n.lendings4x.items(),key=lambda x: -x[1])
                rlp.log(" "*(n.pos),f"   + [[{round(n.lendings4xsum,2)}]] {le4sort}",fid='@tree')
            if len(n.endvalues4)>0:
                rlp.log(" "*(n.pos),f"  ** {n.endvalues4}",fid='@tree')
            if len(n.endvalues5)>0:
                rlp.log(" "*(n.pos),f"  ++ {n.endvalues5}",fid='@tree')
            if len(n.lendings3)>0:
                le3sort = sorted(n.lendings3.items(),key=lambda x: -x[1])
                rlp.log(" "*(n.pos),f"   # {le3sort}",fid='@tree')
            if len(n.endvalues3x)>0:
    #            rlp.log(" "*(n.pos),f"  ## {n.endvalues3}",fid='@tree')
                rlp.log(" "*(n.pos),f"  ## {n.endvalues3x}",fid='@tree')
                
def is_capitalized(word):
    return len(word)>=2 and word[:1].isupper() and word[1:].islower()

def split_word(nnn,word,endcontext,paircontext,endsuffixes2,endsuffixes2x,n=None,sepmark='@@',capmark="##"):
#    FULLWORD_COEFF = 1.0               
    stems = []
    stemvals = []
    endvals = []
    mxval = 0.0
    origword = word
    word = word.lower()
    mxcending = None
    for i,nn in enumerate(noo.iterate_subword_nodes(nnn,word)):
        cending = word[i+1:]
        if nn is not None and i>=1:
            if cending in endcontext or cending in endsuffixes2x:
                stems.append(word[:i+1])
                stemvals.append(0.0)
                if nn is not None:
                    stemvals[-1] += nn.lendings4xsum
                endvals.append(0.0)
                cont = word[i]
                if cending in endcontext:
                    endvals[-1] += endcontext[cending][cont]
                    if nn is not None:
                        ends = list(nn.lendings4.keys())
                        for e in ends:
                            ef = listtostr((e,cending))
                            if ef in paircontext:
                                endvals[-1] += paircontext[ef][cont]
                if cending in endsuffixes2x:
                    for esuff in endsuffixes2x[cending]:
#                        endvals[-1] += endsuffixes2[esuff]
                        endvals[-1] = max(endvals[-1],endsuffixes2[esuff])
                val1 = stemvals[-1]
                val2 = endvals[-1]
                if cending=='':
                    val1 += nn.word_occ * rlp.FULLWORD_COEFF
                    val2 += 1
                val = val1 * val2
                if val>mxval:
                    mxval = val
                    mxcending = cending
                if n is not None:
                    n.endvalues5.append((cending,round(val1,2),round(val2,2)))
    if mxcending is not None and mxcending!="" and origword[1:].islower():
        split = [origword[:len(word)-len(mxcending)],sepmark+mxcending]
    else:
        split = [origword]
    if capmark!="" and is_capitalized(split[0]):
        split[0] = split[0][0].lower() + split[0][1:]
        split.insert(0,capmark)
    if n is not None:
        n.endvalues5.insert(0,split)
    return split

def segment_line(nnn,s,endcontext,paircontext,endsuffixes2,endsuffixes2x,sepmark='@@',capmark="##"):
    ret = []
    for word in s.split():
        ret += split_word(nnn,word,endcontext,paircontext,endsuffixes2,endsuffixes2x,None,sepmark,capmark)
    return " ".join(ret)
#    return ret

def split_all_tree_words(nnn,endcontext,paircontext,endsuffixes2,endsuffixes2x):
    if rlp.DEBUG!=0:
        for n in noo.iterate_nodes(nnn):
            n.endvalues5 = []
            if n.word_occ>0:
                split_word(nnn,n.subword,endcontext,paircontext,endsuffixes2,endsuffixes2x,n=n)
                
def serialize_word_tree(nnn):
    nnnlist = []
    for n in noo.iterate_nodes(nnn):
        nnnlist.append([n.subword,n.word_occ,n.lendings4,n.lendings4xsum])
    return nnnlist
                
def deserialize_word_tree(nnnlist):
    nnn = noo()
    for ninfo in nnnlist:
        nnn.add_node_subsub(*ninfo)
    return nnn
                
def subsub_learn(voc=None,mfilename=None,maxforms=None,bestendings=None):
    if voc is not None:
        rlp.vocab1 = voc    
#    for w,occ in sorted(rlp.vocab1.items(),key=lambda x: -x[1]):
#        if w.isalpha():
#            rlp.maxwocc = occ
#            print(w,occ)
#            break
    if mfilename is not None:
        rlp.segseg_model_filename = mfilename         
    if maxforms is not None:
        rlp.MAX_INITIAL_SUBWORD_FORMS = maxforms
    if bestendings is not None:
        rlp.BEST_ENDINGS = bestendings
    nnn = rlp.create_noodle_from_vocab(rlp.vocab1)
    
    endings2,endix=calculate_initial_ending_info(nnn)    
    rlp.statusmsg("Step 1")

    calculate_node_significance(nnn,endings2,endix)
    rlp.statusmsg("Step 2")

    # 3.2. calculate bad nodes v.1. to hold endings using local endings v.1.
    parads33 = calculate_good_bad(nnn)
    
    calculate_val3(nnn,endings2,parads33)
    rlp.statusmsg("Step 3.1")

    endings2ext=extend_local_endings(nnn,endings2)
    endings2plus=set(endings2.keys()).union(endings2ext)

    parads33 = calculate_good_bad(nnn,dolog=True)
    calculate_val3(nnn,endings2plus,parads33)

    rlp.statusmsg("Step 3.2")
    
    calculate_local_endings3(nnn,endings2plus,parads33)
    
    endcontext,paircontext=calculate_ending_contexts(nnn)                
    rlp.statusmsg(f"Step 4.2")

    calculate_local_endings4(nnn,endcontext,paircontext)                    
    rlp.statusmsg("Step 5.1")

    calculate_local_endings4_extended(nnn,endcontext)
    rlp.statusmsg("Step 5.2")
    
    endsuffixes2,endsuffixes2x=calculate_endsuffix_info(nnn)
    rlp.statusmsg("Step 6.1")

    split_all_tree_words(nnn,endcontext,paircontext,endsuffixes2,endsuffixes2x)
    rlp.statusmsg("Step 6.2")
    
#    n = nnn.find_subword_node("pil")
#    if n is not None:
#        print(list(n.__dict__.keys()))
    
    print_word_tree(nnn)
    rlp.statusmsg("Step 7")
    
    nnnlist = serialize_word_tree(nnn)
    
    nnn.clean()

#    nnn.clean_special(('prev', 'val1', 'lendings1neg', 'lendings1ext',
#                       'bad_stem', 'bad_stem2', 'good_stem2', 'val30', 'val3',
#                       'lendings3', 'endvalues3x', 'lendings4x', 'endvalues4', 'endvalues5',
#                       'subword_occ', 'subnodes', 'subword_forms', 'char',
#                       'subword', 'pos'))

#    nnn2 = deserialize_word_tree(nnnlist)
#    nnn2 = noo()
#    for ninfo in nnnlist:
#        nnn2.add_node(*ninfo)

#    n = nnn.find_subword_node("pil")
#    if n is not None:
#        print(list(n.__dict__.keys()))
    
    mf = open(rlp.segseg_model_filename,"wb")
    pickle.dump((nnnlist,endcontext,paircontext,endsuffixes2,endsuffixes2x),mf)
    mf.close()

#    mf = open(rlp.segseg_model_filename,"wb")
#    pickle.dump((nnn,endcontext,paircontext,endsuffixes2,endsuffixes2x),mf)
#    mf.close()
#
#    mf = open(rlp.segseg_model_filename+"list","wb")
#    pickle.dump((nnnlist,endcontext,paircontext,endsuffixes2,endsuffixes2x),mf)
#    mf.close()

#def subsub_load_tree(fname):                
#    mf = open(fname,"rb")
#    nnn,endcontext,paircontext,endsuffixes2,endsuffixes2x=pickle.load(mf)
#    mf.close()
#    return nnn,endcontext,paircontext,endsuffixes2,endsuffixes2x

def subsub_load(fname):                
    mf = open(fname,"rb")
    nnnlist,endcontext,paircontext,endsuffixes2,endsuffixes2x=pickle.load(mf)
    mf.close()
    nnn = deserialize_word_tree(nnnlist)
    return nnn,endcontext,paircontext,endsuffixes2,endsuffixes2x

def subsub_segment_document(fin,fout,nnn,endcontext,paircontext,endsuffixes2,endsuffixes2x,
                            marker1="9474",marker2="9553",fullword=None):
    if marker1.isdigit(): marker1 = chr(int(marker1))
    if marker2.isdigit(): marker2 = chr(int(marker2))
    if fullword is not None:
        rlp.FULLWORD_COEFF = fullword
    lopenin = False
    lopenout = False
    if isinstance(fin,str): 
        fin = open(fin, 'r', encoding='utf-8')
        lopenin = True
    if isinstance(fout,str): 
        fout = open(fout, 'w', encoding='utf-8')
        lopenout = True
    for s in fin:
        fout.write("{}\n".format(segment_line(nnn,s,endcontext,paircontext,endsuffixes2,endsuffixes2x,marker1,marker2)))
    if lopenin:
        fin.close()
    if lopenout:
        fout.close()
        
def unprocess_line(sentence,marker1,marker2):
    output = []
    len1 = len(marker1)
    upper = False
    prev = ""
    for word in sentence.split():
        # uppercase marking
        if word==marker2:
            upper=True
            continue
        elif upper:
            word = word[0].upper() + word[1:]
            upper = False
        if word[:len1]==marker1: # postfix
            output[len(output)-1] += word[len1:]
        else:
            output.append(prev+word)
            prev = ""
    return ' '.join(output)

# code 9474: '│'; code 9553: '║'
def subsub_unprocess_document(fin,fout,marker1="9474",marker2="9553"):
    if marker1.isdigit(): marker1 = chr(int(marker1))
    if marker2.isdigit(): marker2 = chr(int(marker2))
    lopenin = False
    lopenout = False
    if isinstance(fin,str): 
        fin = open(fin, 'r', encoding='utf-8')
        lopenin = True
    if isinstance(fout,str): 
        fout = open(fout, 'w', encoding='utf-8')
        lopenout = True
    for line in fin:
        fout.write(unprocess_line(line,marker1,marker2).strip())
        fout.write(' \n')
    if lopenin:
        fin.close()
    if lopenout:
        fout.close()
        
