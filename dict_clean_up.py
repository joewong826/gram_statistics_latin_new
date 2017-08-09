#coding = utf-8



import codecs
import os
import re


filein = 'bigram.txt'
fileout = 'bigram_new.txt'
pattern = re.compile('[^a-z A-Z&\-\']')
with codecs.open(fileout, 'w', 'utf-8') as fpOut:
    filesize = os.path.getsize(filein)
    with codecs.open(filein, 'r', 'utf-8') as fp:
        for line in fp:
            print "",round(1.0*fp.tell()/filesize*100, 2),'%\r',
            word,freq = line.split('\t')
            if (len(word) == 0 
                or len(word) == 1 and not word.isalpha()
                or int(freq.strip()) < 10):
                continue            
            #if word.encode('utf8').isalpha():
            if len(re.findall(pattern, word))==0:
                fpOut.write(line)
                
print 'end.....'