#!/usr/bin/python
#-*- coding=utf-8 -*-


import os, sys, string
import bsddb, time
import codecs
import tools
import re




class Merger:
    # 过滤所有的标点+数字         
    pattern = re.compile(r'^[ \'@#!$%\^&\(\)\[\]\{\}:+-\\*\/,.\d]+$')
    '''合并统计数据，数据量过大，使用map会出现内存占用过大导致被系统杀死进程，
    这里使用bsddb数据库处理
    '''    
    def __init__(self):
        self.home = "db_home"
        self.unigram_filename = "unigram.db"
        self.bigram_filename = "bigram.db"        
        try:
            # 创建home目录
            os.mkdir(self.home)
        except Exception,e:
            print 'make dir:',self.home, 'error:', e
        # 创建数据库环境
        self.dbenv = bsddb.db.DBEnv()
        # 打开数据库环境
        self.dbenv.open(self.home, bsddb.db.DB_CREATE | bsddb.db.DB_INIT_MPOOL)
        self.init()
        
    def init(self):
        # 创建数据库对象
        self.unigram_db = bsddb.db.DB(self.dbenv)        
        self.bigram_db = bsddb.db.DB(self.dbenv)
        # 打开数据库, 这里的第二个参数就是指定使用什么数据访问方法
        # btree是 bsddb.db.DB_BTREE， hash是bsddb.db.DB_HASH
        # queu 是 bsddb.db.DB_QUEUE,  recno 是bsddb.db.DB_RECNO
        self.unigram_db.open(self.unigram_filename, bsddb.db.DB_BTREE, bsddb.db.DB_CREATE, 0666)        
        self.bigram_db.open(self.bigram_filename, bsddb.db.DB_BTREE, bsddb.db.DB_CREATE, 0666)          
    
    def __exit__(self):
        # 关闭，这时会把数据写回文件
        self.unigram_db.close()
        self.bigram_db.close()
        self.dbenv.close()
        
    def filter(self, words):
        #if isinstance(words, unicode) or isinstance(words, str):
        if hasattr(words, 'split'):
            words = words.split(" ")        
        # 过滤所有的标点+数字                
        for word in words:            
            if self.pattern.findall(word) != []:
                return True
        return False

    def put(self, word, freq_str):
        if self.filter(word):
            return False
        db = self.unigram_db
        if word.count(' ') == 1:
            db = self.bigram_db
        
        if db.has_key(word):
            db[word] = str(int(db[word])+int(freq_str))
        else:
            db.put(word, freq_str)
        return True
        
    def load(self, filepath):
        encoding = tools.getfileencode(filepath)
        with codecs.open(filepath, 'r', encoding) as fp:
            for line in fp:                
                infos = line.strip().split('\t')+['1']
                try:
                    infos[0] = infos[0].encode('utf8')
                except:
                    pass
                self.put(infos[0], infos[1])
    
    def clear(self):
        #close会出现堵塞的问题
        #self.unigram_db.close()
        #self.bigram_db.close()        
        #self.unigram_db = bsddb.db.DB(self.dbenv)        
        #self.bigram_db = bsddb.db.DB(self.dbenv)        
        #self.unigram_db.remove(self.unigram_filename)
        #self.bigram_db.remove(self.bigram_filename)        
        try:
            unigrampath = os.path.join(self.home, self.unigram_filename)
            bigrampath = os.path.join(self.home, self.bigram_filename)
            os.remove(unigrampath)
            os.remove(bigrampath)
        except:
            pass
        
        self.init()
 

    def __save(self, path, db):
        FILTER_COUNT = 1
        print 'start save:', path
        with codecs.open(path, 'w', 'utf_8_sig') as fp:
            count = len(db)      
            print 'db count:',count
            cursor = db.cursor()
            words_freq = []
            i = 0
            while count != 0 and True:
                word_freq = cursor.next()
                i += 1
                
                print '%.2f%%\r' % (100.0*i / count),
                if word_freq == None:
                    break;
                if int(word_freq[1]) <= FILTER_COUNT:
                    continue                
                words_freq.append(word_freq)            
            ## 出现次数<=FILTER_COUNT的不输出            
            #words_freq = [word_freq for word_freq in db.items() if int(word_freq[1]) > FILTER_COUNT]        
                    
            words_freq = sorted(words_freq, key=lambda word_freq: int(word_freq[1]), reverse=True)
            print 'start write:', path
            i = 0
            count = len(words_freq)
            for word, freq in words_freq:
                try:                    
                    word = word.decode('utf8')
                except:
                    pass
                
                fp.write(word+'\t'+freq+'\n')
                i += 1
                print '%.2f%%\r' % (100.0*i / count),
                
    
        
    def save(self, outputDir):
        if not os.path.exists(outputDir):
            try:
                os.makedirs(outputDir)        
            except:
                pass
        
        unigram_filename = 'unigram.txt'
        bigram_filename = 'bigram.txt'
        self.__save(os.path.join(outputDir, unigram_filename), self.unigram_db)
        self.__save(os.path.join(outputDir, bigram_filename), self.bigram_db)
            
def test():    
    merger = Merger()
    #merger.clear()
    #merger.load('/home/zhaokun/IME/DicTools/gram_statistics/data/unigram.txt')
    #print merger.put('123 456 abc', 1)
    #print merger.put('1,23 abc', 1)
    #print merger.put('1,23abc', 1)
    #print merger.put('123abc', 1)
    #print merger.put('12.3 abc', 1)
    #print merger.put('(12.3)', 1)
    #print merger.put('@#$%^&*()12.3)', 1)    
    merger.save("db_home")
        
if __name__ == '__main__': 
    oldtime = time.time()
    #print tools.now()
    #import profile
    #profile.run('test()', 'runstats.txt')
    #import pstats
    #p = pstats.Stats("runstats.txt")
    #p.sort_stats("time").print_stats()    
    #print tools.now()
    test()
    print 'runtime:',time.time()-oldtime
