import requests
from lxml import html
from http import cookiejar
from http.cookiejar import LoadError
import time

'''
    关于cookiejar的使用（cookies的存储和读取）。http://docs.python-requests.org/en/master/api/#cookies
    三种用法：
    requests.utils.dict_from_cookiejar(cj)
    requests.utils.add_dict_to_cookiejar(cj, cookie_dict)
    requests.cookies.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
    
'''

# 创建一个session会话
session = requests.session()
# 实例化一个LWPCookieJar对象
session.cookies = cookiejar.LWPCookieJar(filename='cookies.txt')

try:
    session.cookies = requests.utils.cookiejar_from_dict(session.cookies.load(ignore_discard=True, ignore_expires=True))
    # session.cookies.load(ignore_discard=True, ignore_expires=True)  加载文件中的cookies
    # requests.util.cookiejar_from_dict 把文件中的cookies转换为cookiejar类型， 并且赋值为session。cookies
except LoadError as e:
    print(e)


def get_headers():
    login_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.36 ',
    }
    return login_headers


def get_xsrf():
    login_page = session.get("https://www.zhihu.com/", headers=get_headers(), timeout=5)
    # print(session.headers)
    response = html.fromstring(login_page.content)
    xrsf = response.xpath('/html/body/div[1]/div/div[2]/div[2]/form/input/@value')
    _xsrf = "".join(xrsf)
    return _xsrf


def get_captcha():
    t = str((time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=1497449177140' + t + '&type=login'
    r = session.get(captcha_url, headers=get_headers(), timeout=5)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
    captcha = input('验证码')
    return captcha


def get_data():
    data = {
        '_xsrf': get_xsrf(),
        'password': '.',
        'captcha': get_captcha(),
        'email': ''
    }
    return data


def login():
    get_data()
    response = session.post("https://www.zhihu.com/login/email", headers=get_headers(), data=get_data())
    # print(response.text)
    login_code = response.json()
    print(login_code['msg'])
    for i in session.cookies: print(i)
    try:
        # 把session.cookies 中的cookies 添加在cookies.txt文件中
        requests.utils.add_dict_to_cookiejar('cookies.txt', session.cookies)
    except AttributeError as e:
        print(e)
    return session

# if __name__ == '__main__':
#     login()
