#!/usr/bin/python
#-*- coding=utf-8 -*-


import os
import re
import codecs

'''
配置文件格式：[]为语言locale，多个语言可以用|分割，如[en|fr], [common]为公共locale，不指定locale或无该locale时读取
[common] # 公共的
#Latin
#Base Latin
0x0041-0x005a
0x0061-0x007a
[en]
#Latin
#Base Latin
0x0041-0x005a
0x0061-0x007a

[fr]

[tr]

[ar]
0x0600-0x06FF
0x0750-0x077F
0x08A0-0x08FF
'''

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf8') 
except:
    pass

class ValidChars:
    TAB_COMMON = 'common'
    def __init__(self):
        self.path = 'validchars'
        self.validcharsLineMap = {ValidChars.TAB_COMMON:[]}
        #self.validChars = {ValidChars.TAB_COMMON:[]}
        #if os.path.exists(self.path):
            #self.read(self.path)
        
    def read(self, path):
        self.path = path
        self.validcharsLineMap = {ValidChars.TAB_COMMON:[]}
        with codecs.open(path, 'r') as fp:            
            locales = [ValidChars.TAB_COMMON]
            vcs = []
            for line in fp:
                line = re.sub('#.+', '', line).strip()
                if len(line) == 0:
                    continue
                if line[0] == '[':
                    for locale in locales:
                        self.validcharsLineMap[locale] = [vcs, None]
                    
                    locale = (re.findall('\[(.+)\]', line)+[''])[0]
                    locales = [l.strip() for l in locale.split('|')]
                    vcs = []
                    continue
                vcs.append(line)
            for locale in locales:
                self.validcharsLineMap[locale] = [vcs, None]
        
        for locale in self.validcharsLineMap.iterkeys():
            pattern = self.__getPatternInvalidChars(locale)
            self.validcharsLineMap[locale][1] = pattern
        
    def __str__(self):
        strs = []
        for k, v in self.validcharsLineMap.iteritems():
            strs.append(k)
            for code in v[0]:
                strs.append('\t'+code)
            if v[1] != None:
                strs.append('\t'+v[1])
        return '\n'.join(strs)
        
    def getValidChars(self, locale):
        vcs = self.validcharsLineMap.get(locale, [])
        return vcs
    
    def getPatternInvalidChars(self, locale):
        pattern = ''
        if self.validcharsLineMap.has_key(locale):
            pattern = self.validcharsLineMap[locale][1]
        else:
            print "Warning: Don't specify the locale, Use the default common.."
            pattern = self.validcharsLineMap[ValidChars.TAB_COMMON][1]
        return pattern
    
    def __getPatternInvalidChars(self, locale):
        pattern = ' '
        if self.validcharsLineMap.has_key(locale):
            vcs = self.validcharsLineMap.get(locale, [[]])[0]
        else:
            vcs = self.validcharsLineMap.get(ValidChars.TAB_COMMON, [[]])[0]
        #if not self.validChars.has_key(locale):
            #self.validChars[locale] = []
        #validChars = self.validChars.get(locale)
        for line in vcs:
            line = re.sub("#.+", "", line).strip()
            if len(line) == 0:
                continue
            start = ''
            end = ''                    
            if line.find('-') >= 0:
                start, end = [c.strip() for c in line.split('-')]
            else:
                start = end = line.strip()
            try:     
                start = int(start, 16)
                end = int(end, 16)                           
            except:
                print 'locale [%d] valid chars error: [%s] to int faild' % (locale, line)
                continue
            if start > end:                
                print 'locale [%d] valid chars error: [%s] first < second' % (locale, line)
                continue
            start = unichr(start)
            end = unichr(end)
            start = ur'\-' if start == u'-' else start
            end = ur'\-' if end == u'-' else end

            pattern += '%s-%s' % (start, end)
            #for i in range(start, end+1):                
                #validChars.append(unichr(i))
        #pattern = pattern.rstrip('|')
        #pattern = pattern.replace('\\', r'\\')

        return None if len(pattern) == 0 else u'[^%s]+'%pattern
    
    
if __name__ == '__main__':
    vc = ValidChars()
    vc.read('/home/zhaokun/IME/DicTools/gram_statistics_latin/output/validchars_alllanguage.txt')
    pattern = vc.getPatternInvalidChars('zh')
    print vc
    print pattern
    print re.findall(pattern, u'abc你\'ad-.b好吗,*@def')    
    
    pass