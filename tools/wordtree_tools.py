from collections import Counter

class noo:
    cnodes = 0
    cwords = 0
    csubword_chars = 0
    
    def init_reverse(n):
        n.subword_forms = 0
    
    def __init__(self,char='',subword='',pos=-1,prev=None,specialfunini=None):
        self.char = char
        self.subword = subword
        self.pos = pos
        self.prev = prev
        self.next = {}
        self.subword_occ = 0 # how many SUBwords found in the text (ending in this node)
        self.word_occ = 0 # how many words found in the text (ending in this node)
        self.subnodes = 0
        if specialfunini is not None:
            specialfunini(self)
        else:
            self.init_default()
        noo.cnodes += 1
        noo.csubword_chars += len(subword)
        
    def init_default(self):
        self.subword_forms = 0
        
    def init_empty(self):
        pass
        
    def init_plus(self):
        self.wuples = Counter()
        self.tran = Counter()
        self.tcount = 0
        self.ucount = 1
        self.prefixrest = Counter()
        self.postfixrest = Counter()
        
    def clean(self):
        if hasattr(self,"prev"):
            self.prev = None
        for char in self.next:
            self.next[char].clean()
        self.next = None

    def clean_special(self,lst):
        for a in lst:
            if hasattr(self,a):
                delattr(self,a)
        for char in self.next:
            self.next[char].clean_special(lst)
        
    def add_word(self,word,freq=1,
                 specialfunini=None,specialfun=None,specialdata=None):
        assert len(word)>0
        nnext = self.next
        nprev = self
        for pos,char in enumerate(word):
            if char not in nnext:
                nnext[char] = noo(char,word[:pos+1],pos,nprev,specialfunini=specialfunini)
                p = nnext[char].prev
                while p is not None:
                    p.subnodes += 1
                    p = p.prev
            n = nnext[char]
            n.subword_occ += freq
            nprev = n
            nnext = n.next
        if specialfun is not None:
            specialfun(n,specialdata)
        else:
            if n.word_occ == 0: # if no such word registered yet (ending in this node)
                noo.cwords += 1
                p = n
                while p is not None:
                    p.subword_forms += 1
                    p = p.prev
        n.word_occ += freq
        return n
            
    def add_node_subsub(self,word,word_occ,lendings4,lendings4xsum):
        assert len(word)>0
        nnext = self.next
        nprev = self
        for pos,char in enumerate(word):
            if char not in nnext:
                nnext[char] = noo(char,word[:pos+1],pos,nprev,specialfunini=noo.init_empty)
            n = nnext[char]
            nprev = n
            nnext = n.next
        n.word_occ = word_occ
        n.lendings4 = lendings4
        n.lendings4xsum = lendings4xsum
        return n
            
    def find_longest_prefix(self,word,minforms=100):
        nnext = self.next
        ret = ''
        for pos,char in enumerate(word):
            if pos==len(word)-1:
                return ret
            if char not in nnext:
                return ret
            n = nnext[char]
            if n.subword_forms<minforms:
                return ret
            ret += char
            nnext = n.next
            
    def find_subword_node(self,word):
        nnext = self.next
        for pos,char in enumerate(word):
            if char not in nnext:
                return None
            n = nnext[char]
            if pos==len(word)-1:
                return n
            nnext = n.next
            
    def iterate_subword_nodes(self,word):
        nnext = self.next
        nodenotexists = False
        for pos,char in enumerate(word):
            if nodenotexists:
                yield None
            elif char not in nnext:
                nodenotexists = True
                yield None
            else:
                n = nnext[char]
                yield n
                nnext = n.next
            
    def find_or_create_word_node(self,word):
        n = self.find_subword_node(word)
        if n is None:
            n = self.add_word(word)
        return n

    def search_word(self,word):
        n = self.find_subword_node(word)
        return False if n is None else n.word_occ>0
            
    def get_word_occ(self,word):
        n = self.find_subword_node(word)
        return 0 if n is None else n.word_occ
            
    def get_word_subword_forms_list(self,word):
        n = self.find_subword_node(word)
        ret = []
        while n.pos>=0:
            ret.insert(0,(n.char,n.subword_forms))
            n = n.prev
        return ret
            
    def get_word_subword_forms_list_plus(self,word,postnoodle):
        n = self.find_subword_node(word)
        npost = postnoodle
        ret = []
        postforms = npost.subword_forms
        while n.pos>=0:
            ret.insert(0,(n.char,n.subword_forms,postforms,[n.subword_forms*postforms//100]))
            if npost is None or n.char not in npost.next:
                postforms = 0
            else:
                npost = npost.next[n.char]
                postforms = npost.subword_forms
            n = n.prev
        return ret
            
    def get_word_subnodes_list_plus(self,word,postnoodle):
        n = self.find_subword_node(word)
        npost = postnoodle
        ret = []
        postnodes = npost.subnodes
        while n.pos>=0:
            ret.insert(0,(n.char,n.subnodes,postnodes,[n.subnodes*postnodes//100]))
            if npost is None or n.char not in npost.next:
                postnodes = 0
            else:
                npost = npost.next[n.char]
                postnodes = npost.subnodes
            n = n.prev
        return ret
            
    def get_word_forms(self,word):
        n = self.find_subword_node(word)
        return 0 if n is None else 1
            
    def search_subword(self,word):
        n = self.find_subword_node(word)
        return n is not None
            
    def get_subword_occ(self,word):
        n = self.find_subword_node(word)
        return 0 if n is None else n.subword_occ
            
    def get_subword_forms(self,word):
        n = self.find_subword_node(word)
        return 0 if n is None else n.subword_forms
            
    def iterate_words(nstart,word=""):
        for char,n in nstart.next.items():
            wordnext = word + char
            if n.word_occ > 0:
                yield wordnext,n.word_occ
            for w,occ in noo.iterate_words(n,wordnext):
                yield w,occ
                
    def iterate_words_also_self(nstart,word=""):
        if nstart.word_occ > 0:
            yield word,nstart.word_occ
        for char,n in nstart.next.items():
            wordnext = word + char
            if n.word_occ > 0:
                yield wordnext,n.word_occ
            for w,occ in noo.iterate_words(n,wordnext):
                yield w,occ
                
    def iterate_nodes(nstart):
        for n in nstart.next.values():
            yield n
            for nn in noo.iterate_nodes(n):
                yield nn
                
    def iterate_nodes_word(n,word):
        pos = 0
        while pos<len(word) and word[pos] in n.next:
            n = n.next[word[pos]]
            pos+=1
            yield n
                
    def iterate_nodes_also_self(nstart):
        yield nstart
        for n in nstart.next.values():
            yield n
            for nn in noo.iterate_nodes(n):
                yield nn
        