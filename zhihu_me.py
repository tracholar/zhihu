# coding:utf-8

import urllib, urllib2, re, smtplib, urlparse
from lxml import etree
from StringIO import StringIO
from email.mime.text import MIMEText
import threading, time, md5, os, gzip
from urlparse import urlparse

links_file = 'zhihu_me_links.txt'
def get_visited_urls():
    if not os.path.exists(links_file):
        return []
    return open(links_file,'r').read().split('\n')
    
def save_visited_url(url):
    f = open(links_file,'a')
    f.write(url + '\n')
    f.close()
    
    
visited_urls = get_visited_urls()
sleep_time = 5
    
class ZhihuHomeHandler:
    def __init__(self):
        pass
        
    def getLinks(self, url):
        host = hostname(url)
        
        T = get_dom_from_url(url)
        links = T.findall('//div[@data-type-detail="member_voteup_answer"]/div/a[@class="question_link"]')
        if links is not None:
            for link in links:
                href = host + link.attrib['href']
                
                yield (href, link.text)
        
    def getBody(self, href):
        
        data =  get_answer_text(href)
        
        return data
        

class ZhihuCollectionHandler:
    def __init__(self):
        pass
        
    def getLinks(self, url):
        host = hostname(url)
        
        for u in get_collections_urls_from_base_url(url):
            T = get_dom_from_url(u)
            divs = T.findall('//div[@class="zm-item"]')
            if divs is not None:
                
                for div in divs:
                    link = div.find('.//h2/a')
                    node = div.find('.//div[@class="zm-item-rich-text js-collapse-body"]')
                    if link is None or node is None:
                        continue
                    href = host + node.attrib['data-entry-url']
                    if href in visited_urls:
                        continue
                    
                    yield (href, link.text)
        
    def getBody(self, href):
        data =  get_answer_text(href)
        save_visited_url(href)
        return data
        
zhihu_urls = [
    ('http://www.zhihu.com/people/tracholar', ZhihuHomeHandler()),
    ('http://www.zhihu.com/collection/34131770', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/20025828', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/20615676', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/28112560', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/30557268', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/19553038', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/36271480', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/20387017', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/19764022', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/27109279', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/20208448', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/19915395', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/25973370', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/29548625', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/29674111', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/27536209', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/37406996', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/38407655', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/36267601', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/29741115', ZhihuCollectionHandler()),
    ('http://www.zhihu.com/collection/33804316', ZhihuCollectionHandler()),
]

interval = 10  # 间隔时间

def hostname(url):
    o = urlparse(url)
    return o.scheme + '://' + o.netloc
    
def http_get(url):
    res = urllib2.urlopen(url)
    html = res.read()
    
    info = res.info()
    if info.getheader('Content-Encoding')=='gzip':
        data = StringIO(html)
        html = gzip.GzipFile(fileobj=data).read()
    return html

def abs_url(url):
    if len(url)>=5 and (url[0:5]=='http:' or url[0:6]=='https:'):
        return url
    else:
        return urlparse.urljoin(zhihu_home_url, url)

def get_dom_from_url(url):
    isOK = False
    

    try:
        html = http_get(url)
        tree = etree.parse(StringIO(html), etree.HTMLParser())
    except Exception:
        html = '<html></html>'
        tree = etree.parse(StringIO(html), etree.HTMLParser())
        print 'error when open url ', url
    
    return tree
def get_dom_from_string(html):
    try:
        tree = etree.parse(StringIO(html), etree.HTMLParser())
    except Exception:
        tree = etree.parse(StringIO(''), etree.HTMLParser())
    return tree
def get_answer_text(answer_url):
    T = get_dom_from_url(answer_url)
    txt = T.find('//div[@id="zh-question-answer-wrap"]')
    
    if txt is None:
        return ''
    txt = txt.find('.//div[@class="zm-editable-content clearfix"]')
    if txt is None:
        return ''
    txt = etree.tostring(txt, encoding='unicode', method="text")
    #print txt
    return txt #re.sub(r'\<.+\>', '', txt)
    
def get_question_answer(answer_url):
    T = get_dom_from_url(abs_url(answer_url))
    txt = etree.tostring(T.find('//div[@id="zh-question-answer-wrap"]'), pretty_print=True)
    # 知乎图片处理
    txt = re.sub(r'<img([^>]+)src="([^"]+)"([^>]+)data-actualsrc="([^"]+)"/>',r'<img\1src="\4"\3data-actualsrc="\2"/>', txt)
    
    # print txt
    return txt
def get_zhihu_update_divs(update_url):
    
    tree = get_dom_from_url(abs_url(update_url))

    divs = tree.findall('//div[@class="zm-profile-section-item zm-item clearfix"]')
    
    return divs


def save_file_from_url(url, path):
    f = open(path, 'wb')
    try:
        
        data = http_get(url)
        f.write(data)
        f.close()
    except Exception:
        print '[error]', url, 'open faild!'
    
def save_answer(title, author, content):
    fname = re.sub(r'[\?\:\\\/\*\<\>\|\s]',' ',title+'-'+author)
    fname = fname.strip()
    
    fname = './data/'+fname+'.html'
    if os.path.exists(fname):
        return
    # process image
    T = get_dom_from_string(content)
    imgs = T.findall('//img')
    for img in imgs:
        root, ext_name = os.path.splitext(img.attrib['src'])
        if ext_name is '':
            ext_name = '.png'
        
        img_name = md5.new(abs_url(img.attrib['src'])).hexdigest() + ext_name 
        local_path = 'data/images/'+img_name
        save_file_from_url(abs_url(img.attrib['src']), local_path)
        content = content.replace(img.attrib['src'], 'images/'+img_name)
    
    try:
        f = open(fname.encode('gbk','ignore'), 'wb')
        f.write(content.encode('utf-8'))
        f.close()
    except Exception:
        print '[error] Create', fname.encode('gbk','ignore'), 'faild!'
        pass
    
def dom_to_html(elem):
    return etree.tostring(elem, pretty_print=True)
    
def get_collections_urls_from_base_url(url):
    T = get_dom_from_url(url)
    page = T.find('//div[@class="zm-invite-pager"]/span[last()-1]/a')
    if page is None:
        pages_num = 1
    else:
        pages_num = int(page.text)
    for i in range(1,pages_num+1):
        yield(url + '?page=' + str(i))
   

def craw(link, title, handler):
        
 
    
    data = handler.getBody(link)
    fn =  title + '-' + str(time.time()) + '.txt'
    fn = re.sub(r'[\?\:\\\/\*\<\>\|\s|\"]',' ',fn)
    fn = 'data2/' + fn
    f = open(fn.encode('gbk','ignore'), 'wb')
    f.write(data.encode('gbk', 'ignore'))
    f.close()
    
    
        
urls = []
preparing = []

def craw_thread(i):
    print '[thread] begin %d' % i
    
    while len(preparing)>0:
        if len(urls)>0:
            url, title, handler = urls.pop(0)
            craw(url, title, handler)
            save_visited_url(url)
            print '[%d] %s' % (i, title.encode('gbk', 'ignore'))
        else:
            time.sleep(10)
            
    print '[thread] end %d' % i   
    
def prepare_urls(url, handler):
    print '[prepare] %s' % url
    
    for link, title in handler.getLinks(url):
        #print 'push',link
        if link in visited_urls:
            continue
        
        urls.append((link, title, handler))
    
    preparing.pop()  
    
    print '[prepare done] %s' % url
        
def main_loop():

    t = []
    for i in range(len(zhihu_urls)):
        preparing.append(1)
        th = threading.Thread(target=prepare_urls, args=zhihu_urls[i])
        th.start()
        t.append(th)
        
        
        
        time.sleep(1)
      
      
    time.sleep(5)
    
    for i in range(20):
        th = threading.Thread(target=craw_thread, args=(i, ))
        th.start()
        t.append(th)
    for th in t:
        th.join()
            
        
            
            #time.sleep(sleep_time)
    
        
def get_user_collections(user_collection_url):
    T = get_dom_from_url(user_collection_url)
    collection_links = T.findall('//a[@class="zm-profile-fav-item-title"]')
    for link in collection_links:
        get_collection(abs_url(link.attrib['href']))
    
def main():
    try:
        main_loop()
    except Exception:
        raise
        timer = threading.Timer(interval, main)
        timer.start()

if __name__ == '__main__':
    main()