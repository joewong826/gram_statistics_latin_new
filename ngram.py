#-*- coding=utf-8 -*-


import codecs
import os
import re
import tools

class NGram:
    NGRAM_FREQ, NGRAM_CHILD = range(2)
    def __init__(self, n=(1, 2), bCaseSensitive=True, maxWordLen=30):
        self.ngrams = {} # {'a': [1, {'b': [1]}]} a和ab频率各为1
        self.n = n
        self.bCaseSensitive = bCaseSensitive
        self.maxWordLen = maxWordLen
        
    def clear(self):
        self.ngrams.clear()
        
    def __add(self, ngrams, words, freq=1):
        wordCount = len(words)
        if wordCount == 0:
            return False
        node = None
        word = words[0].strip()
        if len(word) == 0 or len(word) > self.maxWordLen:
            return False
        if ngrams.has_key(words[0]):
            node = ngrams[words[0]]               
        else:
            node = ngrams[words[0]] = [0, {}]
            
        if wordCount == 1:
            node[self.NGRAM_FREQ] += freq
            return True        
        else:
            return self.__add(node[self.NGRAM_CHILD], words[1:], freq)
    def add(self, words, freq=1):
        '''返回是否add'''          
        # words: [word1, word2, ...] or (word1, word2, ...)
        if self.n.count(len(words)) == 0:
            return False    
        # 如果不区分大小写， 则把所有词转换为小写再统计
        if not self.bCaseSensitive:
            for i in range(len(words)):
                words[i] = words[i].lower()
        #print ' '.join(words)
        return self.__add(self.ngrams, words, freq)
    
    def addSentence(self, sentence, bStatisticsWord=False):
        '''
        sentence 句子，str，空格分隔。或者词语列表
        bStatisticsWord 是否统计字，Latin统计字母，中文统计汉字
        '''
        if isinstance(sentence, str):
            sentence = tools.toUnicode(sentence)
            sentence = sentence.split()
        elif isinstance(sentence, unicode):
            sentence = sentence.split()      
        else:
            for i, s in enumerate(sentence): 
                sentence[i] = tools.toUnicode(s)
                #如果出现转换失败的。直接过滤掉
                if not isinstance(sentence[i], unicode):
                    sentence[i] = u''
        count = len(sentence)
        # 句首词需要按小写来统计
        if count > 0 and self.bCaseSensitive:
            sentence[0] = sentence[0].lower()        
            
        # 如果是纯数字或者包含+-×/,.:的数字都去掉
        pattern = re.compile(r'^[\'@#!$%\^&\(\)\[\]\{\}:+-\\*\/,.\d]+$')
        max_ngram = sorted(self.n, reverse=True)[0]
        for i in range(count):
            if len(re.findall(pattern, sentence[i])) > 0:
                continue
            if bStatisticsWord and len(sentence[i]) > 1:
                for c in sentence[i]:
                    self.__add(self.ngrams, c, 1)
            for j in range(i+1, min(i+1+max_ngram, count+1)):
                if self.n.count(j-i) == 0:
                    continue
                if j-1 != i and len(re.findall(pattern, sentence[j-1])) > 0:
                    break
                self.add(sentence[i:j])
    
    def __reprNode(self, word, ngram):
        s = u''
        for key, value in ngram.items(): 
            if value[self.NGRAM_FREQ] > 0:
                node = u'%s=%d, ' %(word+' '+key, value[self.NGRAM_FREQ])
                #print node
                s += node
            s += self.__reprNode(word+' '+key, value[self.NGRAM_CHILD])         
        return s
    
    def __str__(self):        
        s = self.__reprNode(u'', self.ngrams)   
        return s.encode('utf8')
    def __repr__(self):
        return self.__str__()    
    def __setitem__(self, words, _):
        self.add(words)
              
    def __getitem__(self, words):
        node = self.ngrams
        freq = 0        
        for word in words:
            if node.has_key(word):
                freq = node[word][self.NGRAM_FREQ]
                node = node[word][self.NGRAM_CHILD]                
            else:
                freq = 0
                break
        
        return freq 
    
    def save(self, outputPath, dimension=(1, 2), sortFreq=True):
        # 目录不存在， 则递归创建目录
        if not os.path.exists(os.path.dirname(os.path.abspath(outputPath))):
            os.makedirs(os.path.dirname(outputPath))
        with codecs.open(outputPath, 'w', 'utf_8_sig') as fp:
            words_freq = self.get(dimension)
            if sortFreq:
                words_freq = sorted(words_freq, key=lambda word_freq: word_freq[1], reverse=True)
            for word, freq in words_freq:   
                try:
                    fp.write('%s\t%d\n' % (word, freq))
                except:
                    fp.write('%s\t%d\n' % (word.decode('utf8'), freq))
        return True
    
    def __getNode(self, prevWord, ngram, depth=0, dimension=(1, 2)):
        words = []
        prefix = '' if len(prevWord) == 0 else prevWord + ' '
        for key, value in ngram.items():
            if depth+1 in dimension and value[self.NGRAM_FREQ] > 0:
                words.append((prefix+key, value[self.NGRAM_FREQ]))
            words += self.__getNode(prefix+key, value[self.NGRAM_CHILD], depth+1, dimension) 
        return words
    
    def get(self, dimension=(1, 2)):
        '''根据ngram返回对应的词
        1维：[(word1, freq), (word2, freq)]
        2维：[(word1 word2, freq), (word2 word3, freq)]
        '''        
        words = self.__getNode('', self.ngrams, 0, dimension)        
        return words

        
    def load(self, filepath):
        encoding = tools.getfileencode(filepath)             
        with codecs.open(filepath, 'r', encoding) as fp:
            for line in fp:
                infos = line.split('\t')+['1']
                words = infos[0].strip().split(' ')
                freq = int(infos[1].strip())
                self.add(words, freq)
                
                
    
if __name__ == '__main__':
    ngram = NGram(n=range(1, 3))
    #ngram.addSentence('a 54.771,2006 b')
    ngram.load('/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output/output_statistics/html.html')
    ngram.load('/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output/output_statistics/html_index.htm')
    print ngram
    #ngram.add(['a', 'b', 'c'])
    #ngram.add(['a', 'b'])
    #ngram.add(['a', 'b', 'c'])
    
    #print ngram 
    
    #print ngram[['a', 'b', 'c']]
    #print ngram[['a', 'b']]
    #print ngram[['a', 'c']]
    #print ngram[['a']]