#!/usr/bin/python
#-*- coding=utf-8 -*-

#import nltk
#try:
#     from bs4 import BeautifulSoup
#except:
#     import BeautifulSoup
import urllib
import re
#from nltk.corpus import PlaintextCorpusReader 
import ConfigParser
import os
#from log import Log
import codecs
import string
import sys
from ngram import NGram
#import chardet
import time
import tools
import html_content
import validchars

#https://pip.pypa.io/en/stable/installing.html
#download get-pip.py  https://bootstrap.pypa.io/get-pip.py
#yum install python-devel or apt-get install python-dev
#yum install libxslt-devel libxml2-devel
#sudo pip install lxml
#import lxml
#import HTMLParser 
#from lxml.html import clean


class DicStatistics:     
        
    def __init__(self, dimension=(1, 2)):
        self.__log = codecs.open('log.txt', 'w', 'utf8')
        self.dimension = dimension # 要生成的几维数据， 如要生成一维和二维， dimension=【1， 2】
        self.translateTable = {}
        self.validChars = []
        self.ngrams = NGram(dimension)
        self.filterThesaurus = {}
        self.filter_rate = 0.0
        self.patternValidChars = None
        #self.html_parser = HTMLParser.HTMLParser()  
        self.html_content = html_content.HtmlContent()
         
    def __del__(self):
        if self.__log != None:
            self.__log.close()
              
    def clear(self):
        self.ngrams.clear()
         
    def loadValidChars(self, path, locale):
        '''加载一份有效字符列表,文件#为注释行, 字符用16进制表示,可以用-来表示区间
        如:a-z用0x0061-0x007a表示
        '''
        #self.validChars=[]
        #if not os.path.exists(path):
             #print 'error: not find valid Chars file.'
             #return          
        #pattern = ' '
        #with codecs.open(path, 'r', 'utf-8') as fp:
             #for line in fp:
                  #sharp = line.find('#')
                  #if sharp >= 0:
                       #line = line[:sharp]
                  #line = line.strip()
                  #if len(line) == 0:
                       #continue
                  #start = ''
                  #end = ''                    
                  #if line.find('-') >= 0:
                       #start, end = [c.strip() for c in line.split('-')]
                  #else:
                       #start = end = line.strip()
                  #try:     
                       #start = int(start, 16)
                       #end = int(end, 16)                           
                  #except:
                       #print 'valid chars line error:', line, 'to int faild.'
                       #continue
                  #if start > end:
                       #print 'valid chars line error:', line, 'first < second'
                       #continue
                  #pattern += '%s-%s' % (unichr(start), unichr(end))
                  #for i in range(start, end+1):
                       #self.validChars.append(hex(i))
        #pattern = pattern.rstrip()
        #pattern = pattern.replace('\\', r'\\')         
        #self.patternValidChars = None if len(pattern) == 0 else re.compile(u'[^%s]+'%pattern)
        
        if not os.path.exists(path):
            print 'error: not find valid Chars file.'
            return                   
        vc = validchars.ValidChars()
        vc.read(path)
        pattern = vc.getPatternInvalidChars(locale)
        #print locale, pattern
        self.patternValidChars = None if len(pattern) == 0 else re.compile(pattern)
        
    
    def hasInvalidChars(self, words):
        '''words可以是一个单词,也可以是空格分割的多个单词, 也可以是[]()的列表'''
        if self.patternValidChars == None:
            return False 
        if isinstance(words, unicode) or isinstance(words, str):
            words = [words]
        has = False
        for word in words:
            if isinstance(word, str):
                try:
                    word = word.decode('utf-8')
                except:
                    try:
                        word = word.decode('gb18030')
                    except:
                        pass
            
            if len(self.patternValidChars.findall(word)) > 0:
                return True
        return False
              
         
                   
         
    def loadFilterThesaurus(self, path, filter_rate=0.2):
        '''加载一份过滤词库， 不在该份词库内的词都过滤掉
        filter_rate：过滤的比例，默认0.2， 如果一行文本有超过这个值的词，则过滤改行
        '''
        self.filter_rate = filter_rate
        encoding = tools.getfileencode(path)
        with codecs.open(path, 'r', encoding) as fp:
            for line in fp:
                word = line.strip().split('\t')[0].lower()
                self.filterThesaurus[word] = 0
    def wordIsFilter(self, word):  
        '''判断该词是否丢弃'''
        word = word.lower()
        return len(self.filterThesaurus)!=0 and not self.filterThesaurus.has_key(word)

    def __getInvalidWordCount(self, words):
        '''返回words里面无效单词的个数'''
        if type(words) == str or type(words) == unicode:
            words = words.split()
            if len(words) == 1:
                return (1 if self.wordIsFilter(words[0]) else 0, 1)
        invalidWordCount = 0
        wordCount = 0
        if hasattr(words, '__iter__'):
            for word in words:  
                iwc, wc = self.__getInvalidWordCount(word)
                invalidWordCount+=iwc
                wordCount+=wc 
        return (invalidWordCount, wordCount)
    
    def wordsIsFilter(self, words, filter_rate=0.2):
        '''判断该段内容是否丢弃，通过判断该段内容有百分之多少的词在FilterThesaurus范围内
        过滤的词超过filter_rate，过滤这些词返回true，否则返回false
        filter_rate为0时，比如全部词都需要才会返回false，否则过滤所有词
        当词的个数<=10时,提高rate为0.5,有一半的词不在FilterThesaurus范围内,则返回true,丢弃这些词
        
        words可以是'a b c d'， 也可以是['a', 'b','c', 'd']， 也可以是[['a', 'b'], 'c', 'd']
        '''
        if len(self.filterThesaurus) == 0:
            return False
        #self.filterThesaurus = {'a':0,'b':0,'c':0, 'd':0}
        if 0 > filter_rate or filter_rate >= 1:
            raise Exception('0 <= filter_rate < 1','in dic_statistics.py')
        invalidWordCount, wordCount = self.__getInvalidWordCount(words)
        #print 'invalidWordCount:', invalidWordCount, 'wordCount:',wordCount
        
        if wordCount <= 10:
            filter_rate = 0.5                 
        return True if wordCount > 0 and invalidWordCount*1.0/wordCount > filter_rate else False
         
    
    def setTranslateTable(self, table):
        self.translateTable = table
         
    #def loadTranslateTable(self, path):
         #self.translateTable.clear()
         #with codecs.open(path, 'r', 'utf-8') as fp:
              #for line in fp:
                   #line = line.lstrip(' ').strip('\r\n')
                   #if line.find('#') == 0:
                        #continue
                   #cols = line.split('\t')
                   #if len(cols) == 2:
                        #if cols[0][:2] == '0x':
                             #self.translateTable[int(cols[0], 16)] = cols[1]
                        #else:
                             #self.translateTable[ord(cols[0])] = cols[1]
                   #else:
                        #print 'error: ' , line
                        
    def loadTranslateTable(self, path):
        self.translateTable.clear()
        with codecs.open(path, 'r', 'utf-8') as fp:
            for line in fp:
                sharp = line.find('#')
                if sharp >= 0:
                    line = line[:sharp]
                line = line.strip()
                if len(line) == 0:
                    continue                    
                cols = line.split()
                if len(cols) != 2:
                    print 'translate table error:', line, ' not 2 cols.'
                    continue
                start = ''
                end = ''
                dst = cols[1]
                if cols[0].find('-') >= 0:
                    start, end = [c.strip() for c in cols[0].split('-')]
                else:
                    start = end = cols[0].strip()
                try:     
                    start = int(start, 16)
                    end = int(end, 16)  
                    dst = int(dst, 16)
                except:
                    print 'translate table error:', line, 'to int faild.'
                    continue
                
                for i in range(start, end+1):
                    self.translateTable[i] = dst
                  
        #items = self.translateTable.items()
        #items.sort()
        #for key, value in items:
             #print hex(key)+'\t'+unichr(key)+'\t'+hex(value)

    def loadUrl(self, url):
        '''加载一个网页，'''
        html = urllib.urlopen(url).read()
        self.loadWebSource(html)
         
    def loadWebSource(self, html):
        '''加载一个网页原数据， 会先清除标签， 然后再分词'''
        content = self.getWebContent(html)
        print content
        for line in content.split('\n'):
            sentences = self.__participle(line.strip())
            for sentence in sentences:
                self.ngrams.addSentence(sentence)
    
    @staticmethod
    def specialProcessing(content):
        '''添加这个后, prettify会自动把content内的html转义符转换成实际字符
        如&lt;&gt转换成<>
        '''
        return content;
         
    #def getWebContent(self, html):
         #'''去除网页源数据的标签'''
         #soup = BeautifulSoup(html)
         ## 去除script、style、header、head、footer标签
         #[script.extract() for script in soup.findAll('script')]
         #[style.extract() for style in soup.findAll('style')]    
         #[header.extract() for header in soup.findAll('header')]    
         #[head.extract() for head in soup.findAll('head')]    
         #[footer.extract() for footer in soup.findAll('footer')]    

         ## 去除网页div的一些头和footer（页脚）部分
         #[div_footer.extract() 
          #for div_footer in soup.findAll('div') 
          #if len([div for div in ['footer', 'copyright', 'header'] 
                         #if div_footer.get('id') != None 
                         #and div in div_footer.get('id').lower()]) > 0]
         
         #newhtml = soup.prettify(formatter=DicStatistics.specialProcessing)
         #regex = re.compile("<[^<>]*>")
         #return regex.sub('', newhtml)
    '''
    def getWebContent(self, html):
         newhtml = html
         try:
              #解决部分网页charset为gbk,然后里面有中文字符,lxml.html.fromstring解析会出错的问题
              #newhtml = html.replace('encoding="gbk"', 'encoding="utf-8"') \
                   #.replace('encoding="GBK"', 'encoding="utf-8"') \
                   #.replace('charset=gbk', 'charset=utf-8') \
                   #.replace('charset=GBK', 'charset=utf-8')         
              #newhtml = newhtml.encode('utf-8', 'ignore')     
              newhtml = newhtml.decode('utf-8', 'ignore')
         except Exception,e:
              pass
         
         # 先把网页中换行的标签替换掉，否则很多正文内容会只用空格分开
         newhtml = re.sub('<br>', os.linesep, newhtml)
         
         try:
              # 使用cleaner也可以清除部分标签,但是发现清理速度不佳,修改为直接使用下面的遍历节点来清除
              #cleaner = clean.Cleaner(style=True,             
                                      #scripts=True,
                                      #meta=True,
                                      #javascript=True,
                                      #page_structure=True, #页面的结构部分：``<HEAD>``，``<HTML>``，``<标题>``
                                      #processing_instructions=True,#删除任何处理指令
                                      ##kill_tags=["//div[@class=='footer']"],
                                      #safe_attrs_only=False)
              #html = cleaner.clean_html(html)             
              root= lxml.html.fromstring(newhtml)
              delNodes = []
              for node in root.getiterator():              
                   if node.tag in ['header'
                                   , 'head'
                                   , 'footer'
                                   , 'style'
                                   , 'script'
                                   , 'noscript'
                                   , 'javascript'
                                   , 'select'
                                   #, 'article' # <article> 标签定义外部的内容。
                                   , 'ul'#<ul> 标签定义无序列表。
                                   ]:
                        delNodes.append(node)
                        continue
                   if node.tag == 'div':                    
                        for name in ['footer', 'copyright', 'header']:
                             if (node.attrib.has_key('class') and name in node.attrib['class']
                                 or node.attrib.has_key('id') and name in node.attrib['id']):
                                  delNodes.append(node) 
                             #if (lambda name, value: value!=None and name in value.lower()) \
                                #(name, value = node.get('class')):
                                  #delNodes.append(node)  
                             #if (lambda name, value: value!=None and name in value.lower()) \
                                #(name, value = node.get('id')):
                                  #delNodes.append(node)          
                                  
              for node in delNodes:
                   #某个节点删除后，可能还有一些子节点也在delNodes里。
                   try:
                        node.clear()          
                   except:
                        pass
              content = root.text_content()
         except Exception,e:
              # 如果lxml解析失败,则直接用正则去除<>的内容
              regex = re.compile("<[^<>]*>")
              content = regex.sub(os.linesep, newhtml)  
         
         #去除多余的空行，并且行周边的空字符也去掉
         content = re.sub('[\r\n]+[\s]*', os.linesep, content)          
         return content     
    '''     
    
    def __vaildWord(self, word):
        '''把词转为有效， 去除头尾可能的标点符号
        word 不能为None
        '''     
        word = word.strip()
        count = len(word)
        if count == 0:
            return word
        start = 0
        end = count
        curWordNewLine = False
        nextWordNewLine = False
        
        #if word[0] in '"[]{}()':
             #start += 1     
        #while end > 0 and word[end-1] in ',".[]{}()':
                  #end -= 1
        
        ## 把后面的标点符号去掉
        #while end > 0 and word[end-1] in ',."?![](){}':
             #end -= 1    
             
        # 去除前面非有效字符
        while start < count and word[start] in u',:;"[](){}<>':
            start += 1
            curWordNewLine = True if curWordNewLine == False else True
        
        # 去除后面非有效字符         
        while end > 0:
            if (word[end-1] in u',.?!:;"[](){}<>'
                or (word[end-1] == '\'' and word[end-2] in u',.?!:;"[](){}<>\'- ')
                or (word[end-1] == '-' and word[end-2] in u',.?!:"[](){}<>\'- ')
                ):
                end -= 1  
                nextWordNewLine = True if nextWordNewLine == False else True
            else:
                break                                               
             
        word = word[start:end]
        
        return (word.strip(), curWordNewLine, nextWordNewLine)

    def participle(self, line):
        return self.__participle(line)

    def __participle(self, line):
        '''对一行文本进行分词,把一行拆分成句子
        如：'good morning, where are you  going?'
        返回结果[['good', 'morning'], ['where', 'are', 'you', 'going']]
        '''
        #print '*'*20
        #print line
        sentences = [[]]
        if len(line) == 0:
            return sentences
        # 提前替换掉一部分字符
        line = line.translate(self.translateTable)     
        # 解决出现'good,morning’的问题
        line = re.sub('[,;?!~]', ', ', line)
        # 解决出现'aaa....bbb'的问题
        line = re.sub('[\.]+', '.', line)
        words = line.strip().split()   
        
        for word in words:          
            newword, curWordNewLine, nextWordNewLine = self.__vaildWord(word)  
            if len(newword) == 0:
                 # 当前单词为无效的,添加一个新行
                sentences.append([])
                continue
            #if word != newword:
                 #print '>>>>>>>>>>>>>%s\t%s' % (word.rjust(15, ' '), newword.ljust(15, ' '))   
            if self.hasInvalidChars(newword):
                 #print 'invalid:',newword
                continue
                 
            if curWordNewLine:
                if sentences[-1] != []:
                    sentences.append([])
            sentences[-1].append(newword)
            if nextWordNewLine:
                if sentences[-1] != []:
                    sentences.append([])
        if sentences[-1] == []:
            sentences = sentences[:-1]
        #for s in sentences:
             #print s
        return sentences
         
    def loadFile(self, path):
        '''加载一个文件,可以加载多个文件,作为一个统计'''
        filesize = os.path.getsize(path)
        encoding = tools.getfileencode(path)             
        with codecs.open(path,'r', encoding) as fp:
            for line in fp:
                print path,":",round(1.0*fp.tell()/filesize*100, 2),'%'
                sentences = self.__participle(line.strip())
                for sentence in sentences:
                    self.ngrams.addSentence(sentence)
                                 
        #print self.ngrams[[u'goods']]
        #print self.ngrams.get(dimension=(2,))
        #self.ngrams.save('ngrams.txt')
    def statisticsFile(self, path, outputPath, bWebContent=False, dimension=(1, 2)):
        '''统计一个文件,一个文件一个统计结果
        bWebContent : 是否需要提取Content， path为网页文件时使用
        '''
        filesize = os.path.getsize(path)          
        ngrams = NGram(dimension)
        encoding = tools.getfileencode(path)    
        with codecs.open(path,'r', encoding) as fp:
            if bWebContent:
                html = fp.read()
                lines = self.getWebContent(html)        
            else:
                lines = fp
            for line in lines:
                #print path,":",round(1.0*fp.tell()/filesize*100, 2),'%'  
                line = line.strip()
                if len(line) == 0:
                    continue
                sentences = self.__participle(line)
                #print line
                if self.wordsIsFilter(sentences, self.filter_rate):
                    #print '-------------del:', line
                    continue
                for sentence in sentences:
                    ngrams.addSentence(sentence)
        return ngrams.save(outputPath,dimension)
    
    def saveWebContent(self, path, outputPath):
        try:
            with open(path,'r') as fp:
                html = fp.read()
                try:
                    charset = tools.getHtmlCharset(html, defaultCharset='utf-8')
                    if (charset.lower() == 'windows-874'
                        or charset.lower() == 'windows874'):
                        charset = 'cp874'
                    html = html.decode(charset, 'ignore')
                except:
                    pass
                #content = self.getWebContent(html)
                (_, content, _) = self.html_content.getContent(html)
                if not os.path.exists(os.path.dirname(os.path.abspath(outputPath))):
                    os.makedirs(os.path.dirname(outputPath))                      
                with codecs.open(outputPath,'w', 'utf8') as fp:
                    fp.write(content)
            return True
        except Exception, e:
            print 'error:'+e.message+' path:'+path
            return False
        except KeyboardInterrupt, e:
            sys.exit(0)

    def saveWebContentFilter(self, path, outputPath):
        try:
            with open(path, 'r') as fp:
                html = fp.read()
                try:
                    charset = tools.getHtmlCharset(html, defaultCharset='utf-8')
                    if (charset.lower() == 'windows-874'
                        or charset.lower() == 'windows874'):
                        charset = 'cp874'
                    html = html.decode(charset, 'ignore')
                except:
                    pass
                # content = self.getWebContent(html)
                (_, content, _) = self.html_content.getContentFilter(html, self)
                if not os.path.exists(os.path.dirname(os.path.abspath(outputPath))):
                    os.makedirs(os.path.dirname(outputPath))
                with codecs.open(outputPath, 'w', 'utf8') as fp:
                    fp.write(content)
            return True
        except Exception, e:
            print 'error:' + e.message + ' path:' + path
            return False
        except KeyboardInterrupt, e:
            sys.exit(0)
         
    # def loadDir(self, rootdir, recursive=False, suffix='txt'):
    #     paths = []
    #     if recursive:
    #         for root, dirs, files in os.walk(rootdir):
    #             for filename in files:
    #                 if os.path.splitext(filename)[1][1:] == suffix:
    #                     path = os.path.join(root, filename)
    #                     paths.append(os.path.abspath(path))
    #     else:
    #         for filename in os.listdir(rootdir):
    #             if os.path.splitext(filename)[1][1:] == suffix:
    #                 path = os.path.join(root, filename)
    #                 paths.append(os.path.abspath(path))
    #
    #     for path in paths:
    #         self.loadFile(path)
              
    def export(self, path, dimension=(1, 2)):
        self.ngrams.save(path,dimension)
        return True
          
               



if __name__ == '__main__':
    dicStatistics = DicStatistics()     
    dicStatistics.loadTranslateTable('translate_table.txt')     
    path = '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output/output_webContent/JaaxJR_10-4-06.htm'
    outputPath = '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output/123.txt'
    filter_path = '/home/zhaokun/IME/DicTools/1&2 gram statistics/data/words.txt'
    #dicStatistics.loadFilterThesaurus(filter_path)
    #dicStatistics.statisticsFile(path, outputPath)
    #print dicStatistics.wordsIsFilter('cabin volumes was from 17 to 31 minutes')
    
    #dicStatistics.loadValidChars('validchars')
    #print dicStatistics.hasInvalidChars(u'abc\\a')
    
    #print dicStatistics.wordsIsFilter([['a', 'b'],'c', 'd', ['d', 'e', 'f'], 'g'])
    #print dicStatistics.wordsIsFilter(['a', 'b','c', 'd', 'd', 'e', 'f', 'g'])
    #print dicStatistics.wordsIsFilter('a b c d d e f g')
    #print dicStatistics.wordsIsFilter('a')
    
    #print dicStatistics._DicStatistics__vaildWord("adfb faskdf.''")
    print dicStatistics._DicStatistics__participle(u"Bistrots - Brasseries - Auberges")
    #pass
    #run()
    #while True:
         #print '+++start time:', tools.now()
         #path_webContent = 'output_webContent'
         #path_statistics = 'output_statistics'
         #path_web = '/home/zhaokun/IME/DicTools/larbin-2.6.3/output/save'
         
         #print ' +++get web content start:', tools.now()
         #task(task_saveWebContent, path_web, path_webContent)
         #print ' ---get web content   end:', tools.now()
         
         #print ' +++dict statistics start:', tools.now()
         #task(task_statistics, path_webContent, path_statistics)
         #print ' ---dict statistics   end:', tools.now()
         
         #print ' +++merger statistics start:', tools.now()
         #mergerStatistics(path_statistics)
         #print ' ---merger statistics   end:', tools.now()
         #print '--- end time:', tools.now()
         
         #prevTime = time.time()
         #while time.time() - prevTime < 5*60:#5分钟检测一次
              #print 'time:', tools.now(), '\r',
              #time.sleep(1)
               
    
    #dicStatistics = DicStatistics()     
    #dicStatistics.saveConfig('options.txt')
    #dicStatistics.loadConfig('options.txt')
    #dicStatistics.loadDir('.', '.*txt')     
    #dicStatistics.loadTranslateTable('translate_table.txt')
    
    #sourcepath = 'data/news.txt'
    ##dicStatistics.loadFile(sourcepath)
    
    #dicStatistics.loadDir('.', True, 'txt')
    #dicStatistics.export('ngram.txt')
      
    #dicStatistics.loadUrl('http://en.wikipedia.org/wiki/Quotation_mark')
    #dicStatistics.export('wiki.txt')
    
    #dicStatistics.loadFile('/home/zhaokun/IME/DicTools/news.txt')
    #dicStatistics.export('/home/zhaokun/IME/DicTools/news_dic.txt', dimension=(1,))
    
    #path = '/home/zhaokun/IME/DicTools/news_dic.txt'
    #words = []
    #with open(path, 'r') as fp:
         #for line in fp:
              #if line.strip().count(' ') > 0:
                   #continue
              #words.append(line.strip().split())
    #print words
    #words = sorted(words, cmp=lambda x, y:cmp(int(x[1]), int(y[1])), reverse=True)
    #wordCount = len(words)
    #print wordCount
    #for word in words:
         #freq = int(int(word[1])*1.0/wordCount*256)
         #print word[0]+'\t'+word[1]+'\t'+str(freq)
          
