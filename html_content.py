#!/usr/bin/python
#-*- coding=utf-8 -*-
__author__ = 'Zhaokun'

'''提取网页正文，采用了基于文本密度的提取算法
参考https://github.com/stanzhai/Html2Article的python实现
'''
import urllib2
import re
import os
import HTMLParser
import tools
import dic_statistics

class HtmlContent:
    #按行分析的深度，默认为6
    _depth = 6
    #字符限定数，当分析的文本数量达到限定数则认为进入正文内容
    #默认180个字符数
    _limitCount = 180
    #确定文章正文头部时，向上查找，连续的空行到达_headEmptyLines，则停止查找
    _headEmptyLines = 2
    #用于确定文章结束的字符数
    _endLimitCharCount = 20  
    #是否使用追加模式，默认为True
    #使用追加模式后，会将符合过滤条件的所有文本提取出来    
    _appendMode = True

    #正则添加(?is)代表所在位置的右侧的表达式开启忽略大小写(i)和开启单行模式(s)
    COMPILE_TITLE = re.compile('(?is)<title.*?>([\s\S]*?)</title>')
    COMPILE_H1 = re.compile('(?is)<h1.*?>(.*?)</h1>')
    COMPILE_BODY = re.compile('(?is)<body.*?</body>')
    COMPILE_NEWLINE = re.compile('(?is)</p>|<\s*br.*?/>|<\s*br\s*>')
    COMPILE_TAG = re.compile('(?is)<.*?>')
    #需要过滤掉的样式、脚本等不相干的标签
    FILTERS = [
        (re.compile('(?is)<script[^>]*?>.*?</script>'), ''),
        (re.compile('(?is)<noscript[^>]*?>.*?</noscript>'), ''),
        (re.compile('(?is)<style[^>]*?>.*?</style>'), ''),
        #过滤注释
        (re.compile('(?is)<!--.*?-->'), ''),
        #针对链接密集型网站，主要针对门户类网站，降低链接干扰
        (re.compile('(?is)</a>'), '</a>\n'),
        
        ##过滤页脚和版权信息
        (re.compile('(?is)<div[^>]*?copyright[^>]*?>.*?</div>'), ''),
        (re.compile('(?is)<div[^>]*?footer[^>]*?>.*?</div>'), ''),        
        (re.compile('(?is)<footer[^>]*?>.*?</footer>'), ''),
        
        (re.compile('(?is)<ul[^>]*?>.*?</ul>'), ''),#<ul> 标签定义无序列表。  
        #(re.compile('(?is)<article[^>]*?>.*?</article>'), ''),# <article> 标签定义外部的内容。 
        (re.compile('(?is)<select[^>]*?>.*?</select>'), ''),# <select> 单选或多选菜单
    ]
    def __init__(self):
        self.htmlParser = HTMLParser.HTMLParser()
        pass
    
    def formatEscapeCharacter(self, html):
        '''格式化转义字符， 把html里的转义字符转换成实际字符
        如&quot;对应"， &lt;对应< 等
        '''
        #escapeCharactes = [
            #(u'&quot;',  u'\"'),
            #(u'&amp;',   u'&'),
            #(u'&lt;',    u'<'),
            #(u'&gt;',    u'>'),
            #(u'&nbsp;',  u' '),
            #(u'&ldquo;',  u'“'),
            #(u'&rdquo;',  u'”'),
        #]
        #for org, dst in escapeCharactes:
            #html = html.replace(org, dst)
       
        ##其他转义字符
        #try:
            ##html = html.decode('utf8')
            #html = re.sub('&#([0-9]{1,5});', lambda m: unichr(int(m.group(1))), html)
        #except:
            #pass

        html = self.htmlParser.unescape(html)        
        return html
    
    def __format_html(self, html):                
        #标签规整化处理，将标签属性格式化处理到同一行
        #处理形如以下的标签：
        #<a 
        #  href='http://www.baidu.com'
        #  class='test'>
        # 处理后为
        #  <a href='http://www.baidu.com' class='test'>      
        html = re.sub('(?is)(<[^<>]+)', lambda m: re.sub('\s+', ' ', m.group(0)), html) 

        #提取正文的时候会对br标签进行转换的
        ## 所有<br>标签先换成换行
        #html = re.sub('<br>', os.linesep, html)        
        
        for _compile, dst in HtmlContent.FILTERS:
            html = _compile.sub(dst, html)        
        
        #如果换行符的数量小于10，则认为html为压缩过的
        #由于处理算法是按照行进行处理，需要先添加换行，便于处理        
        if html.count('\n') < 10:
            html = html.replace('>', '>\n')            
        return html
    
    def getTitle(self, html):
        title = (HtmlContent.COMPILE_TITLE.findall(html)+[''])[0]
        h1 = (HtmlContent.COMPILE_H1.findall(html)+[''])[0]
        if title.startswith(h1):
            title = h1
        if not isinstance(title, unicode):    
            title = tools.toUnicode(title)
           
        return title
    
    def getContent(self, html):
        title = ''#self.getTitle(html)        
        #获取html的body标签内容
        body = (HtmlContent.COMPILE_BODY.findall(html)+[''])[0]
        if len(body.strip()) == 0:
            return (title, '', '')
        #格式化body，去除无用标签等
        body = self.__format_html(body)
        #把要处理的内容转成unicode，下面处理是按字符个数判断正文的
        if not isinstance(body, unicode):
            body = tools.toUnicode(body)
             
        
        originalLines = body.split(os.linesep)
        linecount = len(originalLines)
        lines = ['']*linecount
        #去除每行的空白字符和标签
        for i, line in enumerate(originalLines):
            #处理换行，使用[CRLF]做为回车标记符，最后统一处理
            line = HtmlContent.COMPILE_NEWLINE.sub('[CRLF]', line)
            line = HtmlContent.COMPILE_TAG.sub(' ', line)
            lines[i] = line
        linecount = len(lines)
        
        prevTextLen = 0 #记录上次统计的字符数量
        startPos = -1   #记录文章正文的起始位置
        content = '' #文本正文内容，不包含标签
        contentList = ['']*linecount
        contentWithTags = '' #文本正文内容，包含标签        

        for i in range(linecount-HtmlContent._depth):
            textlen = 0
            for j in range(HtmlContent._depth):
                #这里要取清除左右的空白字符和上面添加的换行标签后的长度
                textlen += len(lines[i+j].strip().replace('[CRLF]', ''))
            if startPos == -1:#还没有找到文章起始位置，需要判断起始位置
                if prevTextLen > HtmlContent._limitCount and textlen > 0:
                    #查找文章起始位置, 如果向上查找，发现2行连续的空行则认为是头部
                    emptyCount = 0
                    for j in range(i-1, 0, -1):
                        if lines[j] == None or lines[j] == '':
                            emptyCount += 1
                        else:
                            emptyCount = 0
                        if emptyCount == HtmlContent._headEmptyLines:
                            startPos = j + HtmlContent._headEmptyLines
                            break
                    #如果没有定位到文章头，则以当前查找位置作为文章头
                    if startPos == -1:
                        startPos = i;
                    #填充发现的文章起始部分
                    for j in range(startPos, i+1):
                        #content += lines[j]+os.linesep
                        contentList[j] = lines[j]
                        #contentWithTags += originalLines[j]
            else:
                #当前长度为0，且上一个长度也为0，则认为已经结束
                if (textlen <= HtmlContent._endLimitCharCount 
                    and prevTextLen < HtmlContent._endLimitCharCount):
                    if not HtmlContent._appendMode:
                        break;                        
                    startPos = -1;
                #content += lines[i]+os.linesep
                contentList[i] = lines[i]
                #contentWithTags += originalLines[i]
            prevTextLen = textlen

        content = os.linesep.join(
            [line.strip() for line in contentList if line.strip() != '']
        )
        #处理换行符
        content = content.replace('[CRLF]', os.linesep)
        content = re.sub('[\r\n]+[\s]*', os.linesep, content)
        content = self.formatEscapeCharacter(content)
        content = HtmlContent.COMPILE_TAG.sub(' ', content)
        return (title, content, contentWithTags)

    def getContentFilter(self, html, dicStatistics):
        title = ''  # self.getTitle(html)
        # 获取html的body标签内容
        body = (HtmlContent.COMPILE_BODY.findall(html) + [''])[0]
        if len(body.strip()) == 0:
            return (title, '', '')
        # 格式化body，去除无用标签等
        body = self.__format_html(body)
        # 把要处理的内容转成unicode，下面处理是按字符个数判断正文的
        if not isinstance(body, unicode):
            body = tools.toUnicode(body)

        # originalLines = body.split(os.linesep)
        originalLines = body.split('\n')
        linecount = len(originalLines)
        lines = [''] * linecount
        # 去除每行的空白字符和标签
        for i, line in enumerate(originalLines):
            # 处理换行，使用[CRLF]做为回车标记符，最后统一处理
            line = HtmlContent.COMPILE_NEWLINE.sub('[CRLF]', line)
            line = HtmlContent.COMPILE_TAG.sub(' ', line)
            lines[i] = line
        linecount = len(lines)

        prevTextLen = 0  # 记录上次统计的字符数量
        startPos = -1  # 记录文章正文的起始位置
        content = ''  # 文本正文内容，不包含标签
        contentList = [''] * linecount
        contentWithTags = ''  # 文本正文内容，包含标签

        for i in range(linecount - HtmlContent._depth):
            textlen = 0
            for j in range(HtmlContent._depth):
                # 这里要取清除左右的空白字符和上面添加的换行标签后的长度
                textlen += len(lines[i + j].strip().replace('[CRLF]', ''))
            if startPos == -1:  # 还没有找到文章起始位置，需要判断起始位置
                if prevTextLen > HtmlContent._limitCount and textlen > 0:
                    # 查找文章起始位置, 如果向上查找，发现2行连续的空行则认为是头部
                    emptyCount = 0
                    for j in range(i - 1, 0, -1):
                        if lines[j] == None or lines[j] == '':
                            emptyCount += 1
                        else:
                            emptyCount = 0
                        if emptyCount == HtmlContent._headEmptyLines:
                            startPos = j + HtmlContent._headEmptyLines
                            break
                    # 如果没有定位到文章头，则以当前查找位置作为文章头
                    if startPos == -1:
                        startPos = i;
                    # 填充发现的文章起始部分
                    for j in range(startPos, i + 1):
                        # content += lines[j]+os.linesep
                        contentList[j] = lines[j]
                        # contentWithTags += originalLines[j]
            else:
                # 当前长度为0，且上一个长度也为0，则认为已经结束
                if (textlen <= HtmlContent._endLimitCharCount
                    and prevTextLen < HtmlContent._endLimitCharCount):
                    if not HtmlContent._appendMode:
                        break;
                    startPos = -1;
                # content += lines[i]+os.linesep
                contentList[i] = lines[i]
                # contentWithTags += originalLines[i]
            prevTextLen = textlen

        # dicStatistics = dic_statistics.DicStatistics()
        finalContentList = []
        for line in contentList:
            line = line.strip()
            if len(line) == 0:
                continue
            line = line.replace('[CRLF]', os.linesep)
            line = re.sub('[\r\n]+[\s]*', os.linesep, line)
            line = self.formatEscapeCharacter(line)
            line = HtmlContent.COMPILE_TAG.sub(' ', line)
            # import pdb;pdb.set_trace()
            sentences = dicStatistics.participle(line)
            if len(sentences) == 0 or sentences == [[]]:
                continue
            if dicStatistics.wordsIsFilter(sentences, dicStatistics.filter_rate):
                continue
            finalContentList.append(line)

        # content = os.linesep.join(
        #     [line.strip() for line in contentList if line.strip() != '']
        # )
        # todo: filter
        content = os.linesep.join(
            [line.strip() for line in finalContentList if line.strip() != '']
        )
        # content = content.replace('[CRLF]', os.linesep)
        # content = re.sub('[\r\n]+[\s]*', os.linesep, content)
        # content = self.formatEscapeCharacter(content)
        # content = HtmlContent.COMPILE_TAG.sub(' ', content)
        return (title, content, contentWithTags)
        
    def getContentByUrl(self, url):
        response = urllib2.urlopen(url)
        buf = response.read()
        return self.getContent(buf)
    
def sub_func(match):
    print match.group(1)
    return unichr(int(match.group(1)))

if __name__ == '__main__':
    htmlContent = HtmlContent()
    #url = 'https://github.com/stanzhai/Html2Article'
    #url = "http://huhehaote.mop.com/thread-61743-1-1.html"
    #url = 'http://www.lefigaro.fr/'
    #url = 'https://github.com/stanzhai/Html2Article'
    url = 'http://www.tgcom24.mediaset.it/economia/tsipras-all-europarlamento-pronti-alle-riforme-ma-l-ue-tagli-il-debito-_2121384-201502a.shtml'
    (title, content, contentWithTags) = htmlContent.getContentByUrl(url)
    print 'title:', title
    #print 'title:', title.decode('utf8').encode('utf8')
    print 'content:', content.encode('utf8')
    import codecs
    with codecs.open('test.txt', 'w', 'utf16') as fp:
        fp.write(content)
