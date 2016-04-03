# coding:utf-8

import urllib, urllib2, re, smtplib, urlparse
from lxml import etree
from StringIO import StringIO
from email.mime.text import MIMEText
import threading, time

zhihu_home_url = 'http://www.zhihu.com/'
zhihu_user_url = 'http://www.zhihu.com/people/tracholar'

interval = 60   # 间隔时间

def abs_url(url):
	if len(url)>=5 and (url[0:5]=='http:' or url[0:6]=='https:'):
		return url
	else:
		return urlparse.urljoin(zhihu_home_url, url)

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
		data = urllib2.urlopen(url).read()
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
	
def get_visited_urls():
	return open('links.txt','r').read().split('\n')
	
def save_visited_url(url):
	f = open('links.txt','a')
	f.write(url + '\n')
	f.close()
	
def update_email():
	
	divs = get_zhihu_update_divs(zhihu_user_url)
	
	if divs is None:
		return
	
	email_str = ''
	
	links_list = get_visited_urls()
	
	
	for div in divs:
		link = div.find('.//a[@class="question_link"]')
		if link is not None:
			save_visited_url(abs_url(link.attrib['href'])+'\n')
			interval = 60*5 # 5 mins
			if abs_url(link.attrib['href']) in links_list:
				pass
			else:
				print '%s - %s' % (abs_url(link.attrib['href']), link.text.encode('gbk'))
				
				interval = 60  # 1 min
				
				txt = get_question_answer(abs_url(link.attrib['href']))
				header = '<p><a href="%s">%s</a></p>' % (abs_url(link.attrib['href']), link.text)
				
				
				# author
				author = zm_item.find('.//h3[@class="zm-item-answer-author-wrap"]').text
				if author.strip() is '':
					author = zm_item.find('.//h3[@class="zm-item-answer-author-wrap"]/a[2]')
					if author is None:
						author = '匿名用户'.decode('utf-8')
					else:
						author = author.text
				save_answer(title, author, header + content)
				print '[saved]',href,title.encode('gbk','ignore')
				
				try:
					print time.strftime('%H:%M:%S') + " send email"
					send_email(link.text, header + txt)
					time.sleep(10)
				except Exception:
					print 'error!'
					pass
				
			
	
def send_email(title, email_str):
	msg = MIMEText(email_str.encode('utf-8'), 'html', 'utf-8')
	msg['Subject'] = title.encode('utf-8') + '-左元的知乎动态'
	msg['From'] = 'tracholar_devtest@163.com'
	msg['To'] = '563876960@qq.com'

	s = smtplib.SMTP('smtp.163.com')
	s.login('tracholar_devtest@163.com','123$%^')
	s.sendmail(msg['From'], [msg['To']], msg.as_string())
	s.quit()

def main():
	
	update_email()

	timer = threading.Timer(interval, main)
	timer.start()

if __name__ == '__main__':
	main()