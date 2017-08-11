
# encoding=utf-8
import requests
import urllib2
from lxml import etree

"""
输入你的微博账号和密码，可去淘宝买，一元七个。
建议买几十个，微博限制的严，太频繁了会出现302转移。
或者你也可以把时间间隔调大点。
"""
# myWeiBo = [
#     #{'no': '18655629450', 'psw': 'hetao199368'},
#     {'no': '13037159758', 'psw': '159758xxf'},
# ]


myWeiBo = [
    {'no': '13037159758', 'psw': '159758xxf'},
    #{'no': '1607251617@qq.com', 'psw': '1qaz2wsx'},

]

referer = 'http://login.weibo.cn/login/?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt='

headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 1.5; en-us; sdk Build/CUPCAKE) AppleWebkit/528.5 (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1',
        'Referer': referer
    }


def getCookies(weibo):
    cookies = []
    for elem in weibo:
        user=elem['no']
        password=elem['psw']

        s = requests.Session()
        res = s.get('http://weibo.cn/login/', headers=headers)
        selector = etree.HTML(res.content)
        rand_ = selector.xpath("//*[@class='c'][2]/form/@action")[0]
        vk = selector.xpath("//*[@class='c'][2]/form/div/input[@name='vk']/@value")[0]
        capId = selector.xpath("//*[@class='c'][2]/form/div/input[@name='capId']/@value")[0]
        _password = selector.xpath("//*[@class='c'][2]/form/div/input[2]/@name")[0]

        img = 'http://weibo.cn/interface/f/ttt/captcha/show.php?cpt=' + capId
        logUrl = 'https://weibo.cn/login/' + rand_ + '&revalid=2&ns=1'
        pic = urllib2.urlopen(img).read()
        with open('123.jpg', 'wb') as f:
            f.write(pic)
        checkcode = raw_input("请输入验证码：")
        playload = {
            'mobile': user,
            _password: password,
            'code': checkcode,
            'remember': 'on',
            'backURL': 'http%3A%2F%2Fweibo.cn%2Flogin',
            'backTitle': '微博',
            'tryCount': '',
            'vk': vk,
            'capId': capId,
            'submit': '登录'
        }

        res1 = s.post(logUrl, data=playload, headers=headers)
        #print res1.content
        if "验证码错误" in res1.content:
            print "账号: %s,验证码错误"%user
        elif "登录名或密码错误" in res1.content:
            print "账号: %s,登录名或密码错误"%user
        elif "自动跳转" in res1.content:
            print "账号: %s,登录成功"%user
            url_logined = 'http://weibo.cn/'
            res3 = s.get(url_logined)
            cookie = s.cookies.get_dict()
            cookies.append(cookie)
            #print cookie
        else:
            print "账号: %s,登录失败"%user
    return cookies

cookies = getCookies(myWeiBo)
print "Get Cookies Finish!( Num:%d)" % len(cookies)