# coding:utf-8
import os
from os.path import join, exists

root = './data'
fo_name = 'zhihu.html'
fs = [f for f in os.listdir(root) if len(f)>5 and f[-4:]=='html' and f!=fo_name]
fs.sort()



header = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
        <title>知乎2014年以前</title>
    </head>
    <body>
'''
article = '\n<h1>%s</h1>\n<div class="article">\n%s\n</div>\n'
footer = '''
    </body>
</html>
'''

fo = open(join(root, fo_name), 'w')
fo.write(header)
for f in fs:
    title = f[:-4].decode('gbk','ignore')
    try:
        body = open(join(root,f)).read().decode('utf-8','ignore')
    except Exception:
        continue
    
    
    ctx = article % (title, body)
    fo.write(ctx.encode('utf-8','ignore'))
    
    print title.encode('gbk','ignore')
    
fo.close()
    


