# coding:utf-8

import urllib, urllib2, re, smtplib, urlparse, time, threading
from lxml import etree
from StringIO import StringIO
from email.mime.text import MIMEText

link_file = 'bbs_links.txt'
bbs_home_url = "http://bbs.ustc.edu.cn/cgi/"
bbs_board_urls = ["http://bbs.ustc.edu.cn/cgi/bbstdoc?board=WebMaster",
	"http://bbs.ustc.edu.cn/cgi/bbstdoc?board=ParttimeJob",
	"http://bbs.ustc.edu.cn/cgi/bbstdoc?board=Job",
	"http://bbs.ustc.edu.cn/cgi/bbstdoc?board=EEIS",
	"http://bbs.ustc.edu.cn/cgi/bbstdoc?board=CS",
	"http://bbs.ustc.edu.cn/cgi/bbstdoc?board=Notice"
]
interested_urls = []

def abs_url(url):
	if len(url)>=5 and (url[0:5]=='http:' or url[0:6]=='https:'):
		return url
	else:
		return urlparse.urljoin(bbs_home_url, url)
		
def send_email(title, email_str):
	msg = MIMEText(email_str.encode('utf-8'), 'html', 'utf-8')
	msg['Subject'] = title.encode('utf-8')
	msg['From'] = 'zuoyuan@mail.ustc.edu.cn'
	msg['To'] = '563876960@qq.com'

	s = smtplib.SMTP('mail.ustc.edu.cn')
	pw = open('pw.txt').read()
	s.login('zuoyuan@mail.ustc.edu.cn',pw)
	s.sendmail(msg['From'], ['15155977600@139.com', '563876960@qq.com'], msg.as_string())
	s.quit()
	
def get_dom_from_url(url):
	try:
		html = urllib2.urlopen(url).read()
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

def dom_to_html(elem):
	return etree.tostring(elem, pretty_print=True)
	
def get_visited_urls():
	return set(open(link_file,'r').read().split('\n'))
	
def save_visited_url(url):
	f = open(link_file,'a')
	f.write(url + '\n')
	f.close()
	
def interested_in(text):
	words = open('interested','r').read().decode('utf-8').split('\n')
	#words = [w.decode('utf-8') for w in words]
	text = text.lower()
	# print text.encode('gbk','ignore')
	for w in words:
		# print text.find(w)
		if text.find(w)!=-1:
			return True
	return False
	
def visited_bbs():
	visited_urls = get_visited_urls()
	for url in bbs_board_urls:
		T = get_dom_from_url(url)
		title_links = T.findall('//a[@class="o_title"]')
		
		for tl in title_links:
			if abs_url(tl.attrib['href']) in visited_urls:
				continue
			save_visited_url(abs_url(tl.attrib['href']))	
			if interested_in(tl.text) or url in interested_urls:
				email_content = '<a href="%s">%s</a>' % (abs_url(tl.attrib['href']), tl.text)
				
				# get detail content
				T = get_dom_from_url(abs_url(tl.attrib['href']))
				detail = dom_to_html(T.find('//div[@class="post_text"]'))
				email_content = email_content + detail
				# email_content = email_content.decode('utf-8','ignore')
				# print email_content
				send_email('[BBS]', email_content)
				print tl.text.encode('gbk','ignore')
				time.sleep(5)
			
def main():
#	visited_bbs()
	interested_urls = open('interested_urls').read().split('\n')
	
	try:
		visited_bbs()
	except Exception:
		print '[ERROR] Error happed when execute visited_bbs'
		pass
	timer = threading.Timer(3600*4, main)
	timer.start()
	
if __name__ == '__main__':
	main()
	