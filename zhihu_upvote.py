# coding:utf-8

import urllib, urllib2, re, smtplib, urlparse
from lxml import etree
from StringIO import StringIO
from email.mime.text import MIMEText
import threading, time

zhihu_home_url = 'http://www.zhihu.com/'
zhihu_user_url = 'http://www.zhihu.com/people/tracholar'
zhihu_collections_url = 'http://www.zhihu.com/people/notdelicious/collections'

interval = 60   # 间隔时间

def abs_url(url):
	if len(url)>=5 and (url[0:5]=='http:' or url[0:6]=='https:'):
		return url
	else:
		return urlparse.urljoin(zhihu_home_url, url)

def get_dom_from_url(url):
	try:
		html = urllib2.urlopen(url).read()
	except Exception:
		html = '<html></html>'
		print 'error when open url ', url
	tree = etree.parse(StringIO(html), etree.HTMLParser())
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
	msg['From'] = 'zuoyuan@mail.ustc.edu.cn'
	msg['To'] = '563876960@qq.com'

	s = smtplib.SMTP('smtp.163.com')
	s.login('tracholar_devtest@163.com',open('email163pw.txt').read())
	s.sendmail(msg['From'], [msg['To']], msg.as_string())
	s.quit()
	
def dom_to_html(elem):
	return etree.tostring(elem, pretty_print=True)
	
def get_visited_urls():
	return open('links.txt','r').read().split('\n')
	
def save_visited_url(url):
	f = open('links.txt','a')
	f.write(url + '\n')
	f.close()
	
	
def get_collection():
	T = get_dom_from_url(zhihu_collections_url)
	collection_links = T.findall('//a[@class="zm-profile-fav-item-title"]')
	
	visited_urls = get_visited_urls()
	
	for link in collection_links:
		T2 = get_dom_from_url(abs_url(link.attrib['href']))
		zm_items = T2.findall('//div[@class="zm-item"]')
		for zm_item in zm_items:
			# print dom_to_html(zm_item)
			zm_item_link = zm_item.find('./h2[@class="zm-item-title"]/a')
			if zm_item_link is None:
				continue
			title = zm_item_link.text
			answer_link = zm_item_link.attrib['href']+'/answer/' + zm_item.find('.//div[@class="zm-item-answer "]').attrib['data-atoken']
			href = abs_url(answer_link)
			if href in visited_urls:
				print '[visited]',href,title
				continue
			
			content = zm_item.find('.//textarea[@class="content hidden"]').text
			header = '<p><a href="%s">%s</a></p>' % (href, title)
			send_email(title, header + content)
			
			save_visited_url(href)
			print href,title
			time.sleep(5)
		
	
	
def main():
	
	get_collection()

	timer = threading.Timer(interval, main)
	timer.start()

if __name__ == '__main__':
	main()