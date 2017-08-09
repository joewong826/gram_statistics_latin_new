#-*- coding=utf-8 -*-

import codecs
import os
import subprocess
import time

import re

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf8') 
except:
    pass



def getHtmlCharsetByFile(path, defaultCharset='utf-8'):
    with open(path, 'r') as fp:
        return getHtmlCharset(fp.read(), defaultCharset)
    
def getHtmlCharset(html, defaultCharset='utf-8'):
    cs = re.findall('<meta.+?charset=[^\w]*?([-\w]+)', html, re.IGNORECASE)+[defaultCharset]
    return cs[0]
	
def toUnicode(text):
    try:
        text = text.decode('utf8', 'ignore')
    except:
        try:
            text = text.decode('gbk', 'ignore')
        except:
            pass
    return text
        

def getFiles(rootdir, recursive=False, suffix='*', bIgnoreHiddenFile=True):
    '''
    rootdir: 目录
    recursive: 是否递归查找
    suffix: 筛选文件扩展名
    bIgnoreHiddenFile: 忽略隐藏文件
    '''
    #paths = []
    if recursive:
        for root, dirs, files in os.walk(rootdir):
            if bIgnoreHiddenFile and os.path.basename(root).startswith('.'):
                continue
            for filename in files:
                if bIgnoreHiddenFile and (filename.startswith('.') or filename.endswith('~')):
                    continue
                if '*' == suffix or os.path.splitext(filename)[1][1:] == suffix:
                    path = os.path.join(root, filename)
                    #paths.append(os.path.abspath(path))
                    yield path
    else:
        for filename in os.listdir(rootdir):
            if bIgnoreHiddenFile and (filename.startswith('.') or filename.endswith('~')):
                continue
            if '*' == suffix or os.path.splitext(filename)[1][1:] == suffix:
                path = os.path.join(rootdir, filename)
                #paths.append(os.path.abspath(path))
                yield path
    #return paths
    
def now():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    
def getfilecount(path):
    '''通过shell方式,获取指定路径的文件个数,不包含文件夹.'''
    cmd = 'ls -lR "%s" | grep "^-" | wc -l' % (path)
    count = 0
    try:
        ls = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        count = int(ls.stdout.read().strip())
    except:
        pass
    
    return count

def getfileencode(path, defaultencoding='utf-8'):
    encoding = defaultencoding
    with open(path, 'r') as fp:
        header = fp.read(3)
        if header == codecs.BOM_UTF8:
            encoding='utf_8_sig'     
        elif header[:2] == codecs.BOM_LE:
            encoding='utf-16'
        elif header[:2] == codecs.BOM_BE:
            encoding='utf-16'
        return encoding
    
def domainHashCode(domain):
    ''' 域名hashcode，从larbin工程中提取的代码，
    通过域名的hashcode值保存网站内容
    hashcode最大为20000，larbin生成目录最大为1000.
    目录用d00000标识
    '''
    h = 0   
    for c in domain:
        h = 37*h + ord(c)
        h &= 0xFFFFFFFF
    return h % 20000 % 1000
import encodings
def printMaxSizeFile(dirpath, outputpath, maxcount=100):
    '''输出指定目录下排行前maxcount的最大的文件路径及大小'''
    if not os.path.isdir(dirpath):
        print 'path:',dirpath,'not a directory...'
        return
    
    sizeAndPaths = [None]*maxcount
    for root, dirs, files in os.walk(dirpath):        
        for filename in files:
            path = os.path.join(root, filename)            
            size = os.path.getsize(path)            
            for i in range(maxcount):
                if sizeAndPaths[i] == None or size > sizeAndPaths[i][0]:
                    sizeAndPaths[i] = (size, path)
                    insert = True
                    break
    with codecs.open(outputpath, 'w', 'utf_8_sig') as fp:
        for f in sizeAndPaths:
            path = f[1]	
            try:
                path = path.decode('utf8')
            except:
                pass
            fp.write("%10d\t%s\n"%(f[0],path))
    print 'output:',outputpath
    
def findStatisticsWords(rootpath, words):
    outputpath = 'test.txt'
    #rootpath = '/data/goime/spider/pt_pt_20150420/output/output_statistics'
    #words = [u'\ufeffe']
    words_map = dict(zip(words, len(words)*[[0, 0, '']]))
    with codecs.open(outputpath, 'w', 'utf16') as fpOut:
        for root, dirs, files in os.walk(rootpath):
            for filename in files:
                path = os.path.join(root, filename)
                try:
                    path = path.decode('utf8')
                except:
                    pass
                with codecs.open(path, 'r', 'utf-8') as fp:
                    for line in fp:
                        word, freq = (line.strip().split('\t')+['1'])[:2]
                        freq = int(freq)
                        if word in words:
                            fpOut.write(word+'\t'+str(freq)+'\t'+path+'\n')
                            words_map[word][0] += freq
                            if freq > words_map[word][1]:
                                words_map[word][1] = freq
                                words_map[word][2] = path                   
    for key, value in words_map.items():
        print key, value    
            
import sys
from optparse import OptionParser  
def run(args):
    parser = OptionParser(usage="%prog [-s] [-n] [-f] [-w] -i FILE -o FILE"
                           , version="%prog 1.0")    
     
    #add_option用来加入选项，action是有store，store_true，store_false等，dest是存储的变量，default是缺省值，help是帮助提示     
    parser.set_description(u'');
     
     
    parser.add_option("-s", "--outputfilesize", action="store_true", dest="outputfilesize", default=False
                       , help=u'输出指定目录的文件大小，按大小排列，默认输出最大100个，-i设置目录路径，-o设置输出文件路径，-n设置最大文件数，默认100')      
    parser.add_option("-n", "--number", type="int", dest="number", help=u'一个整数')

    parser.add_option("-f", "--find_words", action="store_true", dest="findWords", default=False
                      , help=u'查找统计的结果里面，某些词出现情况， 需要指定-w和-i（目录或文件）')
    parser.add_option("-w", "--words", metavar="STRING", dest="words", default=''
                      , help=u'需要查找的词语，多个词语用,分隔。和-f搭配使用')
    
    parser.add_option("-i", "--input", dest="inputpath",metavar="FILE", help=u'输入文件路径')
    parser.add_option("-o", "--output", dest="outputpath",metavar="FILE", help=u'输出文件路径')     
     

    if len(args) <= 1:
        parser.print_help()
        return
    (opt, args) = parser.parse_args(args)
    #print opt
    if opt.outputfilesize == True:
        if opt.inputpath == None or opt.outputpath == None:
            print 'error: check args, -i FILE -o FILE'
            return
        num = 100
        if opt.number != None:
            num = opt.number
        printMaxSizeFile(opt.inputpath, opt.outputpath, num)
    elif opt.findWords == True:
        tempstr = opt.words
        try:
            tempstr = tempstr.decode('utf8')
        except:
            pass
        words = tempstr.split(',')
        findStatisticsWords(opt.inputpath, words)
      
if __name__ == '__main__':
    run(sys.argv)
    #run(['-f', 
         #'-w', '你好,猫扑',
         #'-i', 'output/output_statistics'
         #])
    #path = '/home/zhaokun/IME/DicTools/1&2 gram statistics'
    #paths = getFiles(path, True, '*')
    #for path in paths:
        #print path
    #print domainHashCode('transportespublicos.pt')
    #printMaxSizeFile('/data/goime/spider/pt_pt_20150420/save', 'log.txt', 100)
