#coding=utf8

import time
import tools
import subprocess
import threading
import dic_statistics
import codecs
import Queue
from bs4 import BeautifulSoup
import string

#class DictCreateProcess:
     #def __init__(self, larbinArgs):
          #self.larbin = None
          #self.larbinArgs = larbinArgs
          #self.downloadFileCount = 0
          #self.queue = Queue.Queue()
          
     #def __exit__(self):
          #if self.larbin:
               #self.larbin.terminate()
               #self.larbin = None
          
     #def __runLarbin(self):
          #self.larbin = subprocess.Popen(self.larbinArgs
                                              #, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
     #def start(self):
          #self.__runLarbin()
     
#line  = 'receive,157,648,642,640,638,637,635,633,629,623,617,609,600,591,581,572,564,555,545,535,525,514,505,497,488,479,452,444,437,431,426,421,417,414,410,407,405,403,404,405,409,417,432,451,489,508,523,537,552,566,596,625,638,648,655,660,664,667,670,672,674,674,672,668,659,645,628,610,557,508,495,482,458,436,427,420,414,409,405,403,401,401,401,405,418,436,455,478,504,550,574,595,616,641,662,685,711,734,759,784,809,834,858,880,901,924,946,966,988,1007,1023,1040,1057,1120,1166,1191,1201,1208,1213,1215,1216,1217,1216,1213,1205,1196,1185,1171,1155,1138,1121,1025,939,903,883,864,829,811,792,774,754,734,712,669,624,599,575,551,502,479,438,422,409,399,393,390,394,394,69,69,69,67,68,68,68,68,68,68,68,66,64,62,60,57,54,50,47,44,42,40,39,37,35,36,36,36,37,39,40,42,44,48,51,56,61,67,72,78,84,96,110,143,157,169,181,196,209,232,252,260,266,269,272,274,275,277,278,278,277,275,270,262,249,232,215,170,126,114,102,79,61,54,47,41,36,32,29,27,26,24,21,17,13,10,6,1,-6,-10,-15,-20,-24,-27,-30,-32,-33,-33,-33,-31,-30,-30,-28,-26,-25,-23,-19,-16,-12,-8,-3,0,17,23,23,23,23,23,23,23,23,25,30,38,50,65,77,92,107,124,188,221,229,233,235,239,241,241,240,237,234,227,207,184,171,157,140,111,95,60,45,32,21,14,10,11,11,0,64,81,98,115,132,148,165,182,199,216,232,249,266,283,300,317,333,350,367,384,401,418,434,451,501,518,535,552,569,586,603,619,636,653,670,687,704,720,737,754,771,788,821,838,855,872,889,905,939,973,990,1006,1023,1040,1057,1074,1090,1107,1124,1191,1208,1225,1242,1259,1275,1292,1342,1393,1410,1427,1460,1494,1511,1528,1545,1561,1578,1595,1612,1629,1646,1662,1679,1696,1713,1730,1747,1780,1797,1814,1831,1847,1864,1881,1898,1915,1932,1948,1965,1982,1999,2016,2033,2049,2066,2083,2100,2117,2133,2150,2167,2234,2285,2319,2335,2352,2369,2386,2403,2419,2436,2453,2470,2487,2504,2520,2537,2554,2571,2654,2738,2773,2790,2806,2840,2857,2874,2891,2907,2924,2941,2974,3008,3025,3042,3059,3092,3109,3143,3160,3176,3193,3210,3227,3244,3252,116,116,116,114,114,114,114,114,114,114,114,114,114,114,114,114,114,114,114,114,114,114,114,114,101,101,101,101,101,101,101,101,101,101,101,101,101,101,101,101,101,101,100,100,100,100,100,100,102,99,99,99,99,99,99,99,99,99,99,99,99,99,99,99,99,99,102,100,100,100,114,101,101,101,101,101,101,101,101,101,101,101,101,101,101,101,101,114,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,117,105,105,105,105,105,105,105,105,105,105,105,105,105,105,105,105,105,106,104,98,98,98,118,118,118,118,118,118,118,99,102,102,102,102,100,100,101,101,101,101,101,101,101,101,101,1'
#cols = line.split(',')
#print 'word:', cols[0]
#print 'num:', cols[1]
#print len(cols[2:-1])/4.0
#print 'x:',cols[2:-1][0*int(cols[1]):1*int(cols[1])+1]
#print 'y:',cols[2:-1][1*int(cols[1]):2*int(cols[1])+1]
#print 't:',cols[2:-1][2*int(cols[1]):3*int(cols[1])+1]
#print 'c:',cols[2:-1][3*int(cols[1]):4*int(cols[1])+1]
#print 'index:', cols[-1]

    
#print returncode

#if __name__ == '__main__':
     #DictCreateProcess(larbinArgs=['/home/zhaokun/IME/DicTools/larbin-2.6.3/larbin'
                                    #, '-c', '/home/zhaokun/IME/DicTools/larbin-2.6.3/larbin.conf'
                                    #, '-u', '/home/zhaokun/IME/DicTools/larbin-2.6.3/urls___.txt'
                                    #, '-pipe'
                                    #]).start()
     #html = codecs.open('/home/zhaokun/IME/DicTools/test.html', 'r').read()
     #soup = BeautifulSoup(html)
       
    
     #index = html.find('footer')
     #print html[index: index+20]
     #print html.count('footer')
     
     #[div_footer.extract() 
                     #for div_footer in soup.findAll('div') 
                     #if len([div for div in ['footer', 'copyright'] 
                                    #if div_footer.get('id') != None 
                                    #and div in div_footer.get('id').lower()]) > 0]  
     #newhtml = soup.prettify()
     #index = newhtml.find('footer')
     #print newhtml[index: index+20]
     #print newhtml.count('footer')
     
     #url = 'http://en.bab.la/dictionary/indonesian-english/%s/%d'                          
     #for c in string.ascii_lowercase:
          #for i in range(1, 175):
               #print url % (c, i)
          

#import urllib2
 
##proxy_support = urllib2.ProxyHandler({'http':'http://zhaokun:Zk1501@hkvpn.3g.net.cn:37853'})  
##opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)  
##urllib2.install_opener(opener)  
#content = urllib2.urlopen('http://www.nytimes.com/').read() 
#with open('g.html', 'w') as fp:
     #fp.write(content)
     
     
     
#import codecs
#import re
#pattern = re.compile('[ăâáắấàằầảẳẩãẵẫạặậđêéếèềẻểẽễẹệíìỉĩịôơóốớòồờỏổởõỗỡọộợưúứùừủửũữụựýỳỷỹỵ]')
#with codecs.open('/home/zhaokun/skype files/vi_corpus_gram_new.txt', 'w', 'utf16') as fpOut:
     #with codecs.open('/home/zhaokun/skype files/vi_corpus_gram.txt', 'r', 'utf16') as fp:
          #for line in fp:
               #if len(re.findall(pattern, line)) > 0:
                  #fpOut.write(line)
              
import os
import codecs
import urllib2
urls = []
#with open('/home/zhaokun/IME/DicTools/larbin-2.6.3/urls.txt', 'r') as fp:
     #for line in fp:
          #if line.strip() == 'priority:0 depth:0 test:1':
               #continue
          #urls.append(line.strip())
#try:
     #os.makedirs('indonesian-english')
#except:
     #pass
#proxy_support = urllib2.ProxyHandler({'http':'http://zhaokun:Zk1501@hkvpn.3g.net.cn:37853'})  
#opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)  
#urllib2.install_opener(opener)  
#for url in urls:
     #print url
     #name = '_'.join(url.split('/')[-2:])
     #path = os.path.join('indonesian-english', name)
     #if os.path.exists(path):
          #continue
     #try:
          #content = urllib2.urlopen(url).read()     
     #except:
          #continue
     #with codecs.open(path, 'w') as fp:
          #fp.write(content)
     
#import re

#print re.compile('[^|\s][+-.\d]+[|$\s]').sub(' ', '123 345 234 456')

#print re.compile('\<[+-.\d]+\>').sub(' ', '123 345 234 456')

#print re.findall(r'^[+-\\*\/.\d]+$', '+12.3/2')

#from bs4 import BeautifulSoup
#import codecs
#import re
#path = '/home/zhaokun/IME/DicTools/1&2 gram statistics/test.html'

#def specialProcessing(content):
          #'''添加这个后, prettify会自动把content内的html转义符转换成实际字符
          #如&lt;&gt转换成<>
          #'''
          #return content;
     
#old = time.time()     
#with codecs.open(path, 'r', 'utf8') as fp:
     #html = fp.read()
     #soup = BeautifulSoup(html)
     
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
     
     #newhtml = soup.prettify(formatter=specialProcessing)
     #regex = re.compile("<[^<>]*>")
     #newhtml = regex.sub('', newhtml)     
     
     ##print newhtml
#print time.time()-old

#import lxml
#import HTMLParser 
#from StringIO import StringIO
#from lxml.html import clean
#old = time.time()  
#html_parser = HTMLParser.HTMLParser()  
#with codecs.open(path, 'r', 'utf8') as fp:
     #html = fp.read()
     #html = '<?xml version="1.0" encoding="gbk"?><DOCUMENT><da><![CDATA[中文，就是任性]]></da></DOCUMENT>'
     #html = html.replace('encoding="gbk"', 'encoding="utf-8"') \
               #.replace('encoding="GBK"', 'encoding="utf-8"') \
               #.replace('charset=gbk', 'charset=utf-8') \
               #.replace('charset=GBK', 'charset=utf-8')
     
     #try:          
          #html = html.encode('utf-8', 'ignore')
     #except:
          #pass
     ##html = lxml.etree.HTML(html)    
     
     ##获取所有文本
     #htmlInfo = lxml.html.fromstring(html)
     #for tag in htmlInfo.findall('*div'):        
          #for footer in tag.find_class('footer'):               
               ##print footer.text_content()
               #footer.clear()
          
     #html = htmlInfo.text_content()
     
     ##cleaner = clean.Cleaner(style=True, 
                             ##scripts=True,
                             ##meta=True,
                             ##javascript=True,
                             ##page_structure=True, #页面的结构部分：``<HEAD>``，``<HTML>``，``<标题>``
                             ##processing_instructions=True,#删除任何处理指令
                             ##kill_tags=["//div[@class=='footer']"],
                             ##safe_attrs_only=False)
     ##html = cleaner.clean_html(html)   
     
     ##regex = re.compile("<[^<>]*>")
     ##html = regex.sub('', html)
     ##html = html_parser.unescape(html)     
     
     ##print html
#print time.time()-old


#path='/home/zhaokun/IME/DicTools/1&2 gram statistics/test.html'
#fp = codecs.open(path, 'r')
#buffer = fp.read()
#fp.close()

#root= lxml.html.fromstring(buffer)
#delNodes = []
#for node in root.getiterator():
          #print node.attrib
          #if node.tag in ['header', 'head', 'footer']:
                    #delNodes.append(node)
                    #continue
          #if node.tag == 'div':                    
                    #for name in ['footer', 'copyright', 'header']:
                              #c = node.get('class')
                              #c = str(c)
                              #func = lambda name, value: value!=None and name in value.lower()
                              #if (lambda name, value: value!=None and name in value.lower()) \
                                 #(name, value = node.get('class')):
                                        #pass
                              #if (node.get('class') and name in  node.get('class').lower()
                                  #or node.get('id') and name in node.get('id').lower()
                                  #):
                                        #delNodes.append(node)
                              
          ##print node.tag,node.get('class')
#for node in delNodes:
          #node.clear()
#print lxml.html.tostring(root)
#print root.text_content()

##b = 'b'
##if (lambda a, b: a == b)(b, a = 'a'):
          ##print a

          #pass
#proxy_support = urllib2.ProxyHandler({'http':'http://zhaokun:Zk1501@hkvpn.3g.net.cn:37853'})  
#opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)  
#urllib2.install_opener(opener)  
#content = urllib2.urlopen('http://www.lemonde.fr').read()   
#print content

#rootpath = '/home/zhaokun/IME/DicTools/1&2 gram statistics/123/output/output_statistics'
#filecount = tools.getfilecount(rootpath)
#i = 0
#for root, dirs, files in os.walk(rootpath):
     #for filename in files:
          #path = os.path.join(root, filename)
          #i += 1
          #with codecs.open(path,'r','utf-8') as fp:
               #for line in fp:
                    #word,freq = (line.strip().split('\t')+['1'])[:2]
                    #if word == u'\xc3\x81ngulo' or word == u'\xc3\x89clat':
                         #print word+'\t'+freq+'\t'+path
          ##print '%0.2f%%' % float(i*1.0/filecount*100)


import lxml
from lxml.html import clean

html = u'''services et d'offres adaptés à vos centres d'intérêts.'''
root= lxml.html.fromstring(html)
print root.text_content()