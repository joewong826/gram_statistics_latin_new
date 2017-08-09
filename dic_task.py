#!/usr/bin/python
#-*- coding=utf-8 -*-


import dic_statistics
import os
import Queue
import time
import tools
import threading
import codecs
from ngram import NGram
from merger import Merger

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf8') 
except:
    pass

'''
主要分为主线程、输入线程、检查目录线程、网页提取任务线程、分词统计任务线程和网页提取任务队列、分词统计任务队列
主线程：主要用来打印log信息，运行状态
输入线程：用来接收用户输入，来指定运行或停止操作
检查目录线程：用来检查larbin下载的网页输出路径，把文件传给网页提取任务队列
网页提取任务线程：从网页提取任务队列里获取任务， 成功的任务传给分词统计任务队列
分词统计任务线程：从分词统计任务队列里获取任务
'''

class DicManage:
    DEFAULT_OUTPUT = 'output'
    DIR_WEBCONTENT = 'output_webContent'
    DIR_STATISTICS = 'output_statistics'
    FILE_UNIGRAM = 'unigram.txt'
    FILE_BIGRAM = 'bigram.txt'
     


    LOG_FILE_PATH = 'log.txt'

    def __init__(self, locale='', webRootDir=None, outputDir=None, cover=False):
        self.locale = locale
        self.cover = cover# 是否覆盖,True,覆盖原文件, False,如果文件存在则跳过
        self.webRootDir = webRootDir
        self.outputDir = outputDir if outputDir != None else self.DEFAULT_OUTPUT
        self.webContentOutputDir = os.path.join(self.outputDir, self.DIR_WEBCONTENT)
        self.statisticsOutputDir = os.path.join(self.outputDir, self.DIR_STATISTICS)
         
        self.dicStatistics = dic_statistics.DicStatistics()     
        self.dicStatistics.loadTranslateTable('translate_table.txt')
        self.dicStatistics.loadValidChars('validchars', self.locale)
         
        self.queueStatistics = Queue.Queue()
        self.queueWebContent = Queue.Queue()
        self.mutexQueueStatistics = threading.Lock()
        self.mutexQueueWebContent = threading.Lock()
         
        self.checkCount = 0
        self.webFilesCount = 0
        self.webContentWaitingFilesCount = 0
        self.webContentSuccessFilesCount = 0          
        self.webContentErrorFilesCount = 0  
        self.statisticsWaitingFilesCount = 0
        self.statisticsSuccessFilesCount = 0
        self.statisticsErrorFilesCount = 0
        
        self.bExit = False
        self.bStopWebContent = False
        self.bStopStatistics = False
        self.bStartMergerStatisticsState = 0# 0为没有merger, 1为正在merger, 2为merger完毕         
         

        self.logFp = codecs.open(self.LOG_FILE_PATH, 'w', 'utf8')
        self.logMutex = threading.Lock()
          
    def __exit__(self):
        if self.logFp != None:
            self.logMutex.acquire()
            self.logFp.close()
            self.logFp = None
            self.logMutex.release()
        
    def log(self, text): 
        if self.logFp != None:
            self.logMutex.acquire()
            self.logFp.write(text)
            self.logFp.write(os.linesep)
            self.logMutex.release()
             
     
    def loadFilterThesaurus(self, path, filter_rate=0.2):
        self.dicStatistics.loadFilterThesaurus(path, filter_rate)
     
    def mergerStatistics(self, rootDir, outputDir=DEFAULT_OUTPUT):
        unigram = {}
        bigram = {}
          
        #for root, dirs, files in os.walk(rootDir):
            #for filename in files:               
                #path = os.path.join(root, filename)              
                #with codecs.open(path,'r', 'utf-8') as fp:
                    #for line in fp:
                        #infos = line.split('\t')+['1']
                        #ngram = unigram
                        #if infos[0].count(' ') > 0:
                            #ngram = bigram
                        #if ngram.has_key(infos[0]):
                            #ngram[infos[0]] += int(infos[1].strip())
                        #else:
                            #ngram[infos[0]] = int(infos[1].strip())
        
        #for ngram in [unigram, bigram]:
            #path = os.path.join(outputDir, self.FILE_UNIGRAM if ngram == unigram else self.FILE_BIGRAM)
            #ngram = sorted(ngram.iteritems(), key=lambda b: b[1], reverse=True)          
            #with codecs.open(path, 'w','utf-8') as fp:
                #for word, freq in ngram:
                    #fp.write(word+'\t'+str(freq)+'\n')
                         
                         
        #ngram = NGram(n=range(1, 3))  # [1, 2]  1维和2维         
        #for root, dirs, files in os.walk(rootDir):
            #for filename in files:               
                #path = os.path.join(root, filename)        
                #ngram.load(path)
        #path = os.path.join(outputDir, self.FILE_UNIGRAM)
        #ngram.save(path, dimension=(1,))
        #path = os.path.join(outputDir, self.FILE_BIGRAM)
        #ngram.save(path, dimension=(2,))          
        merger = Merger()
        merger.clear()          
        if os.path.isfile(rootDir):
            merger.load(rootDir)
        else:
            filecount = tools.getfilecount(rootDir)
            i = 0
            for path in tools.getFiles(rootDir, recursive=True):
            # for root, dirs, files in os.walk(rootDir):
            #     for filename in files:
            #         path = os.path.join(root, filename)
                    merger.load(path)
                    i += 1
                    print 'merger: %d(%d)%.2f%%\r' % (filecount, i, float(i*1.0/filecount*100)),
        merger.save(outputDir)
        print '\n','output:',outputDir
          

    def __task_statistics(self, path, outputPath):
        ret = False    
        try:
            ret = self.dicStatistics.statisticsFile(path, outputPath)   
        except Exception,e:
            print 'error:', e
            self.log('error:'+e.message+' path:'+path)
        return ret

    def __task_saveWebContent(self, path, outputPath):
        ret = False    
        try:        
            ret = self.dicStatistics.saveWebContent(path, outputPath)
        except Exception,e:
            print 'error:', e 
            self.log('error:'+e.message+' path:'+path)
        return ret

    def __task_saveWebContentFilter(self, path, outputPath):
        ret = False
        try:
            ret = self.dicStatistics.saveWebContentFilter(path, outputPath)
        except Exception,e:
            print 'error:', e
            self.log('error:'+e.message+' path:'+path)
        return ret

    def __task_save(self, path, outputPath, func):
        #print 'task statistics: ', path, 'output:', outputPath
        if os.path.isfile(path):
            if os.path.isdir(outputPath):
                outputPath = os.path.join(outputPath, os.path.basename(path)) 
            if self.cover or not os.path.exists(outputPath):
                func(path, outputPath)
            elif os.path.exists(outputPath) and os.path.isdir(outputPath):
                print 'error: 存在相同名字的目录。'
                self.log('error: 存在相同名字的目录。'+' outputPath:' + outputPath)
                sys.exit(0)  
            elif os.path.exists(outputPath):
                print 'warning: 未输出，输出文件已经存在，添加-c参数可以覆盖。'
                self.log('warning: 未输出，输出文件已经存在，添加-c参数可以覆盖。')
        elif os.path.isdir(path):
            path = path if path[-1] != os.path.sep else path[:-1]
            if os.path.isfile(outputPath):
                print "输入路径是目录，输出路径不能是文件。。"
                self.log("输入路径是目录，输出路径不能是文件。。")
                sys.exit(0)
            i = 0
            path_str_len = len(path.rstrip(os.path.sep))
            for ip in tools.getFiles(path, recursive=True):
            # for root, dirs, files in os.walk(path):
            #     for filename in files:
                    i += 1
                    print i,'\r',
                    # ip = os.path.join(root, filename)
                    op = os.path.join(outputPath, ip[path_str_len+1:])
                    if self.cover or not os.path.exists(op):
                        #print "input:",ip
                        func(ip, op)
            print '\n'
        else:
            print "输入路径不是文件也不是目录。。"
            self.log("输入路径不是文件也不是目录。。")
            sys.exit(0)  
        return outputPath

    def saveWebContent(self, path, outputPath):
        #if os.path.isdir(path):
        outputPath = os.path.join(outputPath, self.DIR_WEBCONTENT)
        try:
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
        except Exception, e:
            print 'error:'+e.message+' path:'+path
            self.log('error:'+e.message+' path:'+path)
            pass
        return self.__task_save(path, outputPath, self.__task_saveWebContent)

    def saveWebContentFilter(self, path, outputPath):
        outputPath = os.path.join(outputPath, self.DIR_WEBCONTENT)
        try:
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
        except Exception, e:
            print 'error:' + e.message + ' path:' + path
            self.log('error:' + e.message + ' path:' + path)
            pass
        return self.__task_save(path, outputPath, self.__task_saveWebContentFilter)

    def saveStatistics(self, path, outputPath):
        #if os.path.isdir(path):
        outputPath = os.path.join(outputPath, self.DIR_STATISTICS)
        try:
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
        except Exception, e:
            print 'error:'+e.message+' path:'+path
            self.log('error:'+e.message+' path:'+path)
            pass
        func = self.__task_statistics
        return self.__task_save(path, outputPath, func) 
                   
    def __putQueueStatistics(self, path, outputPath):
        #self.mutexQueueStatistics.acquire()
        self.queueStatistics.put((path, outputPath))
        #self.mutexQueueStatistics.release()
         
    def __putQueueWebContent(self, path, outputPath):
        #self.mutexQueueWebContent.acquire()
        self.queueWebContent.put((path, outputPath))
        #self.mutexQueueWebContent.release()
    
    def __getQueueStatistics(self):
        #self.mutexQueueStatistics.acquire()
        path, outputPath = self.queueStatistics.get()
        #self.mutexQueueStatistics.release()
        return (path, outputPath)
         
    def __getQueueWebContent(self):
        #self.mutexQueueWebContent.acquire()
        path, outputPath = self.queueWebContent.get()     
        #self.mutexQueueWebContent.release()
        return (path, outputPath)

    def task_saveWebContent(self):    
        path = ''
        outputDirLen = len(self.webContentOutputDir.rstrip(os.path.sep))
        while(True):
            try:
                path, outputPath = self.__getQueueWebContent()
                #print 'web contnet: ',path,outputPath
                if (not self.cover and os.path.exists(outputPath) 
                    or True == self.__task_saveWebContent(path, outputPath)):
                    self.webContentSuccessFilesCount += 1
                    self.statisticsWaitingFilesCount += 1
                    path = outputPath
                    outputPath = os.path.join(self.statisticsOutputDir, path[outputDirLen+1:])
                    self.__putQueueStatistics(path, outputPath)
                else:
                    self.log('webContent error path:'+path)
                    self.webContentErrorFilesCount += 1
            except Exception,e:
                print 'error:', e
                self.log('error:'+e.message+' path:'+path)
                #assert(False)
                        
    def task_statistics(self):
        func = self.__task_statistics
        path = ''
        while(not self.bStopStatistics):
            try:
                path, outputPath = self.__getQueueStatistics()
                if path == None or len(path) == 0:
                    print 'error: path is null'
                    continue
                #print 'statistics: ',path, outputPath
                if (os.path.exists(outputPath) 
                    or True == func(path, outputPath)):
                    self.statisticsSuccessFilesCount += 1
                else:
                    self.log('statistics error path:'+path)
                    self.statisticsErrorFilesCount += 1
            except Exception,e:
                print 'error:', e
                self.log('error:'+e.message+' path:'+path)
                #assert(False)
    
    def __hasQueue(self):
        return not self.queueWebContent.empty() or not self.queueStatistics.empty()
                   
    def checkWebDir(self):          
        self.checkCount = 0
        self.checkCountdown = 0
        while True:
            if self.__hasQueue():
                self.checkCountdown = 1*60
                time.sleep(self.checkCountdown)
                continue;
            
            self.checkCount += 1
            self.webFilesCount = 0
            self.webContentWaitingFilesCount = 0               
            self.webContentSuccessFilesCount = 0
            self.webContentErrorFilesCount = 0
            self.statisticsWaitingFilesCount = 0
            self.statisticsSuccessFilesCount = 0
            self.statisticsErrorFilesCount = 0
            webRootDirLen = len(self.webRootDir.rstrip(os.path.sep))
            for path in tools.getFiles(self.webRootDir, recursive=True):
            # for root, dirs, files in os.walk(self.webRootDir):
            #     for filename in files:
                    if self.bStopWebContent:
                        return
                    # path = os.path.join(root, filename)
                    outputPath = os.path.join(self.webContentOutputDir, path[webRootDirLen+1:])
                    path = os.path.abspath(path)
                                        
                    self.webFilesCount += 1                         
                    try:
                        self.webContentWaitingFilesCount += 1                              
                        self.__putQueueWebContent(path, outputPath)
                    except Exception,e:
                        print 'error:', e
                        self.log('error:'+e.message+' path:'+path)
                        assert(False)
                           
            time.sleep(5*60)
        
         
    def __startMerger(self):
        # 0为没有merger, 1为正在merger, 2为merger完毕
        self.bStartMergerStatisticsState = 1          
        self.mergerStatistics(self.statisticsOutputDir)
        self.bStartMergerStatisticsState = 0

    def __task_input(self):
        '''input: (e) exit
                  (1) stop web content
                  (2) stop statistics
                  (3) merger statistics
        '''
        while True:
            input = raw_input("").lower()
            if input == 'e':
                self.bExit = True
            elif input == '1':
                self.bStopWebContent = True
            elif input == '2':
                self.bStopStatistics = True
            elif input == '3':
                threading.Thread(target=self.__startMerger).start()
    
    def __startTask(self):
        self.threadInput = threading.Thread(target=self.__task_input)
        self.threadInput.setDaemon(True)
        self.threadInput.start()          
        self.threadCheckWebDir = threading.Thread(target=self.checkWebDir)
        self.threadCheckWebDir.setDaemon(True)
        self.threadCheckWebDir.start()
        self.threadWebContent = threading.Thread(target=self.task_saveWebContent)
        self.threadWebContent.setDaemon(True)
        self.threadWebContent.start()   
        self.threadStatistics = threading.Thread(target=self.task_statistics)
        self.threadStatistics.setDaemon(True)
        self.threadStatistics.start()
         
    def start(self):
        self.checkCount = 0
        self.webFilesCount = 0
        self.webContentWaitingFilesCount = 0
        self.webContentSuccessFilesCount = 0          
        self.webContentErrorFilesCount = 0  
        self.statisticsWaitingFilesCount = 0
        self.statisticsSuccessFilesCount = 0
        self.statisticsErrorFilesCount = 0
        
        self.__startTask()
        t = 0
        while not self.bExit:
            os.system("clear")
            now_time = tools.now()               
            log_state = 'check count: %5d\n' \
                  'web files count : %10d\n' \
                  '------- web content -------\n' \
                  'queue count: %10d, success count: %10d, error count: %10d\n' \
                  '-------  statistics -------\n' \
                  'queue count: %10d, success count: %10d, error count: %10d\n' \
                  '-------   merger    --------\n' \
                  '%s' \
                  '---------------------------\n' \
                  '\n' \
                  'input: (e) exit \n' \
                  '       (1) stop web content \n' \
                  '       (2) stop statistics \n' \
                  '       (3) merger statistics \n' \
                  % (self.checkCount,
                     self.webFilesCount,
                     self.webContentWaitingFilesCount,
                     self.webContentSuccessFilesCount,      
                     self.webContentErrorFilesCount,
                     self.statisticsWaitingFilesCount,
                     self.statisticsSuccessFilesCount,
                     self.statisticsErrorFilesCount,                        
                     'start merger statistics .... \n' if self.bStartMergerStatisticsState==1 else '',
                     )
            
            if t == 60:
                t = 0
                with codecs.open('task_state.txt', 'w', 'utf8') as fp:
                    fp.write(now_time+'\n')                       
                    fp.write(log_state+'\n')
                    fp.write('threadWebContent is alive:'+str(self.threadWebContent.isAlive())+'\n')
                    fp.write('threadStatistics is alive:'+str(self.threadStatistics.isAlive())+'\n')
            print now_time
            print log_state
            t += 1
            time.sleep(1)
             
        input = raw_input('merger statistics files ? (y/n)')
        if input.lower() == 'y':
            self.__startMerger()
            path = os.path.join(outputDir, self.FILE_UNIGRAM if ngram == unigram else self.FILE_BIGRAM)
            print 'merger end, check unigram.txt and bigram.txt.....'
            self.log('merger end, check unigram.txt and bigram.txt.....')

               
import sys
from optparse import OptionParser  
def run(args):
    parser = OptionParser(usage="%prog [-e] [-s] [-m] or [-r] [-c]  [-f FILE] [-n] [-l]  -i FILE -o FILE"
                          , version="%prog 1.0")    
    
    #add_option用来加入选项，action是有store，store_true，store_false等，dest是存储的变量，default是缺省值，help是帮助提示     
    parser.set_description(u'1.从网页中提取正文内容 2.分词统计  3.合并 4.检测目录,提取、分词统计同步进行');
    parser.add_option("-e", "--extract", action="store_true", dest="extract", default=False
                      , help=u'提取网页内容')
    parser.add_option("-E", "--Extract", action="store_true", dest="extract_filter", default=False
                      , help=u'提取网页内容，并根据语言字符和基本词表过滤')
    parser.add_option("-s", "--statistics", action="store_true", dest="statistics", default=False
                      , help=u'分词统计, 可以单独使用也可以和-e搭配使用')
    parser.add_option("-m", "--merger", action="store_true", dest="merger", default=False
                      , help=u'合并所有的统计文件，在当前目录生成unigram.txt和bigram.txt。')  
    
    parser.add_option("-i", "--input", dest="inputpath",metavar="FILE", help=u'输入文件路径，可以是文件或目录')  
    parser.add_option("-o", "--output", dest="outputpath",metavar="FILE"
                      , help=u'输出文件路径，-o必须是目录，网页正文会在该目录下的output_webContent， 分词统计为output_statistics， 合并为unigram.txt和bigram.txt')     
    
    parser.add_option("-r", "--run", action="store_true", dest="checkrun", default=False
                      , help=u'检测目录,提取、分词统计同步进行, [-r -i 检测目录]')
    
    parser.add_option("-c", "--cover", action="store_true", dest="cover", default=False
                      , help=u'覆盖以存在文件,默认不覆盖,输出文件存在,则跳过')
    
    parser.add_option("-f", "--filter", dest="filter_filepath",metavar="FILE", default=None
                      , help=u'词表，用来过滤一行，有多少个词不在范围内则过滤')
    parser.add_option("-n", "--numrate", dest="filter_rate", type='float', default=0.2
                      , help=u'过滤的比例，取指0<=rate<1, 和-f搭配使用，默认不在此表里的词超过20%，则丢弃')
    
    parser.add_option("-l", "--locale", dest="locale", metavar="string"
                      , help=u'语言locale, 通过locale来决定有效字符', default='')
     
     
     
     
     #parser.add_option("-l", "--log", action="store_false", dest="log", default=False, help=u'打印log信息')
    if len(args) <= 1:
        parser.print_help()
        return
    
    (opt, args) = parser.parse_args(args)
    
    if opt.inputpath and opt.inputpath[-1] == os.path.sep:
        opt.inputpath = opt.inputpath[:-1]
    if opt.outputpath and opt.outputpath[-1] == os.path.sep:
        opt.outputpath = opt.outputpath[:-1]     

    if opt.checkrun == True and (opt.extract == True or opt.statistics == True or opt.extract_filter == True):
        print 'error: -r不可和-e-s搭配使用。'
        sys.exit(0)
    if opt.merger == True and opt.statistics == False and (opt.extract == True or opt.extract_filter == True):
        print 'error: -m不可单独和-e搭配使用， 要么单独使用，要么和-s搭配使用。'
        print '忽略-m.'
        opt.merger = False
    if opt.extract_filter == True and not opt.filter_filepath:
        print 'error: 使用-E时必须搭配-f使用。'
        sys.exit(0)
    if opt.locale == '':
        print 'error: 没有通过-l指定locale。'
        sys.exit(0)
    #opt.log
     
    if opt.checkrun: 
        print tools.now()
        if opt.inputpath == None:
            print 'error:', 'Do not specify a check path..'
            return               
        if not os.path.exists(opt.inputpath):
            print 'error:',opt.inputpath, ' not find..'
            return
        dicManage = DicManage(opt.locale, opt.inputpath, opt.outputpath, opt.cover)
        if opt.filter_filepath != None:
            dicManage.loadFilterThesaurus(opt.filter_filepath, opt.filter_rate)
        dicManage.start()
        print tools.now()
        return          
     
    #统一把输出指定为目录
    if os.path.isfile(opt.outputpath):
        print 'error: -o dir, no file..'
        sys.exit()
    if not os.path.exists(opt.outputpath):
        try:
            os.makedirs(opt.outputpath)
        except Exception, e:
            print 'error: makedirs ', opt.outputpath, ' error:',e
            sys.exit()
     
    dicManage = DicManage(locale=opt.locale, cover=opt.cover)
    if opt.extract:
        print tools.now()          
        path = dicManage.saveWebContent(opt.inputpath, opt.outputpath)
        print tools.now()
        print "output web content:", path
    if opt.extract_filter:
        print tools.now()
        dicManage.loadFilterThesaurus(opt.filter_filepath, opt.filter_rate)
        path = dicManage.saveWebContentFilter(opt.inputpath, opt.outputpath)
        print tools.now()
        print "output web content:", path
    if opt.statistics:
        print tools.now()
        inputpath = opt.inputpath
        if opt.extract:
            inputpath = os.path.join(opt.outputpath, DicManage.DIR_WEBCONTENT)
        if opt.filter_filepath != None:
            dicManage.loadFilterThesaurus(opt.filter_filepath, opt.filter_rate)   
        
        path = dicManage.saveStatistics(inputpath, opt.outputpath)
        print tools.now()
        print "output statistics:", path
    if opt.merger:
        print tools.now()
        inputDir = opt.inputpath
        if opt.statistics:
            inputDir = os.path.join(opt.outputpath, DicManage.DIR_STATISTICS)
        
        dicManage.mergerStatistics(inputDir, opt.outputpath)
        print tools.now()
        print 'output unigram.txt(%s), bigram.txt(%s)' \
              % (os.path.exists(os.path.join(opt.outputpath, DicManage.FILE_UNIGRAM))
                 , os.path.exists(os.path.join(opt.outputpath, DicManage.FILE_BIGRAM)))
if __name__ == '__main__':   
    run(sys.argv)
    #run(['-s', '-i', 'output/output_webContent',
    #    '-o', 'output', '-c'#, '-l' ,'en'
    #    ])
     #run(['-e', 
          #'-i', '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/2015', 
          #'-o', '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output'])
          
     #run(['-s', '-i', '123.txt', 
              # '-o', 'output',
               #'-m'])     
     
     #run(['-s', 
          #'-f', '/home/zhaokun/IME/DicTools/1&2 gram statistics/data/words.txt',
          ##'-n', '0.2',
          #'-i', '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output/output_webContent', 
          #'-o', '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output'])     

     #run(['-m', 
          #'-i', '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output/output_statistics', 
          #'-o', '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output'])
     
     #webDir = '/home/zhaokun/IME/DicTools/save'
     #webContentOutputDir = 'output/output_webContent'
     #statisticsOutputDir = 'output/output_statistics'
     
     #dicManage = DicManage(webDir, webContentOutputDir, statisticsOutputDir)
     #dicManage.start()
     