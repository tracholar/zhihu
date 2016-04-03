# coding:utf-8

import urllib, urllib2, re, smtplib, urlparse
from lxml import etree
from StringIO import StringIO
from email.mime.text import MIMEText
import threading, time, md5, os, gzip

zhihu_home_url = 'http://www.zhihu.com/'
zhihu_user_url = 'http://www.zhihu.com/people/tracholar'
zhihu_user_collection_url = 'http://www.zhihu.com/people/tracholar/collections'
zhihu_collections_base_urls = ['http://www.zhihu.com/collection/20025828',
                                'http://www.zhihu.com/collection/20615676',
                                'http://www.zhihu.com/collection/28112560',
                                'http://www.zhihu.com/collection/30557268',
                                'http://www.zhihu.com/collection/19553038',
                                'http://www.zhihu.com/collection/36271480',
                                'http://www.zhihu.com/collection/20387017',
                                'http://www.zhihu.com/collection/19764022',
                                'http://www.zhihu.com/collection/27109279',
                                'http://www.zhihu.com/collection/20208448',
                                'http://www.zhihu.com/collection/19915395',
                                'http://www.zhihu.com/collection/25973370',
                                'http://www.zhihu.com/collection/29548625',
                                'http://www.zhihu.com/collection/29674111']

interval = 10  # 间隔时间

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

def send_email(title, email_str):
    msg = MIMEText(email_str.encode('utf-8'), 'html', 'utf-8')
    msg['Subject'] = title.encode('utf-8') + '-左元的知乎动态'
    msg['From'] = 'zuoyuanlxz@gmail.com'
    msg['To'] = 'zuoyuanlxz@gmail.com'

    s = smtplib.SMTP('smtp.163.com')
    s.login('tracholar_devtest@163.com',open('email163pw.txt').read())
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()

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
    
def get_visited_urls():
    return open('links.txt','r').read().split('\n')
    
def save_visited_url(url):
    f = open('links.txt','a')
    f.write(url + '\n')
    f.close()
    
def get_collections_urls_from_base_url(url):
    T = get_dom_from_url(url)
    page = T.find('//div[@class="zm-invite-pager"]/span[last()-1]/a')
    if page is None:
        pages_num = 1
    else:
        pages_num = int(page.text)
    for i in range(1,pages_num+1):
        yield(url + '?page=' + str(i))
        
def get_collection(base_url):
    
    visited_urls = get_visited_urls()
    sleep_time = 5
    
    for zhihu_collections_url in get_collections_urls_from_base_url(base_url):
        print '[visited]' , zhihu_collections_url
        if zhihu_collections_url in visited_urls and '?page=' not in zhihu_collections_url:
            continue
        T = get_dom_from_url(zhihu_collections_url)
        
        zm_items = T.findall('//div[@class="zm-item"]')
        
        zm_item_link_old = None
        for zm_item in zm_items:
            
            zm_item_link = zm_item.find('.//h2[@class="zm-item-title"]/a')
            # print dom_to_html(zm_item_link)
            if zm_item_link is None:
                print '[warning] zm_item_link is none'
                zm_item_link = zm_item_link_old
            else:
                zm_item_link_old = zm_item_link
                
            title = zm_item_link.text
            
            # author
            author = zm_item.find('.//a[@class="author-link"]')
            
            if author is None:
                author = '匿名用户'.decode('utf-8')
            else:
                author = author.text
            
            zm_item_answer = zm_item.find('.//div[@class="zm-item-answer "]')
            
            
            answer_link = zm_item_link.attrib['href']+'/answer/' + zm_item_answer.attrib['data-atoken']
            href = abs_url(answer_link)
            header = '<p><a href="%s">%s</a></p>' % (href, title)
            
            content_dom = zm_item_answer.find('.//textarea[@class="content hidden"]')
            if content_dom is None:
                pass
            else:
                content = content_dom.text
                
                save_answer(title, author, header + content)
            print '[saved]',href,title.encode('gbk','ignore')
            #if href in visited_urls:
            #   print '[visited]',href,title
            #   continue
            #   
            #try:
            #   send_email(title, header +  content)
            #   save_visited_url(href)
            #   print href,title
            #except Exception:
            #
            #   print '[error]', href, title
            #   pass
            #
            #
            #
            #time.sleep(sleep_time)
        save_visited_url(zhihu_collections_url)
        
def get_user_collections(user_collection_url):
    T = get_dom_from_url(user_collection_url)
    collection_links = T.findall('//a[@class="zm-profile-fav-item-title"]')
    for link in collection_links:
        get_collection(abs_url(link.attrib['href']))
    
def main():
    try:
        for zhihu_collections_base_url in zhihu_collections_base_urls:
            print '[BASE URL]', zhihu_collections_base_url
            get_collection(zhihu_collections_base_url)
        # get_user_collections(zhihu_user_collection_url)
    except Exception:
        raise
        timer = threading.Timer(interval, main)
        timer.start()

if __name__ == '__main__':
    main()