from Login import login
import time
import json
import math
from multiprocessing import Pool as ThreadPool
import random
from DataPersistence import DataPesistence
import threading
import asyncio

# 一个用来存放已经爬取过的token的集合
old_user_packet = set()
# 待爬取的队列， 用来存放未使用的token
new_user_packge = set()
# login()

requests = login()

# def get_first_person():
person_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}


detail_headers = {
'accept':'application/json, text/plain, */*',
'Accept-Encoding':'gzip, deflate, sdch, br',
'Accept-Language':'zh-CN,zh;q=0.8',
'authorization':'Bearer Mi4wQUFCQ0xaOEFjd3NBUUlJbnJRZnhDeGNBQUFCaEFsVk4tVFJ3V1FEOTYzOG5tb1haZmNWbGtLVDQ3aG1pUjNxTW1n|1497933817|9fb5ef01c2267d608cc658bc5c3419f16cf53b5c',
'Connection':'keep-alive',
'Host':'www.zhihu.com',
'Referer':'https://www.zhihu.com',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
'x-udid':'AECCJ60H8QuPTq2mDffa94B8gO_YSWP0tCg='
}


# 构造关注人列表的url
def get_following_url(user_token, offset):
    following_person = 'https://www.zhihu.com/api/v4/members/' + str(user_token) +'/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset='+ str(offset)+'&limit=20'
    return following_person


def first_request():
    # 或者关注人列表
    r = requests.get(url=get_following_url('sgai', 0), headers=person_headers)
    print(r.text)
    dic = json.loads(r.text)
    # print(dic)
    # 获得总页数
    total = int(dic['paging']['totals'])
    total_page = math.ceil(total/20)
    print(total_page)
    user_token = 'sgai'
    # 拿到关注者列表的每一页token
    for page in range(total_page):
        offset = page * 20
        r = requests.get(get_following_url(user_token, offset), headers=person_headers)
        time.sleep(random.uniform(1, 3))
        d = json.loads(r.text)
        dic = d['data']
        for each_person_token in dic:
            # token用来构造详情页url，获取详情信息
            url_token = each_person_token['url_token']
            new_user_packge.add(url_token)
        detail_info()


# 获得关注人列表
def get_following_token(user_token):
    offset = 0
    # 构造关注人列表的url
    following_url = get_following_url(user_token, offset)
    # 请求并解析following_url
    # Pool = ThreadPool(processes=10)
    # Pool.apply_async(request_following, (following_url, user_token))
    # Pool.close()
    # Pool.join()
    ##########################
    thread1 = threading.Thread(target=request_following, args=(following_url, user_token))
    thread1.start()
    
    # request_following(following_url, user_token)


# 请求此token对应的关注人列表
def request_following(following_url, person_token):
    r = requests.get(url=following_url, headers=person_headers)
    time.sleep(random.uniform(0, 5))
    response = json.loads(r.text)
    parser_following(response, person_token)


# 解析关注人列表，并且将关注人的token放入带爬取的队列
def parser_following(respnse, person_token):
    total = int(respnse['paging']['totals'])
    total_page = math.ceil(total / 20)
    print(total_page)
    # 拿到关注人列表的所有token,翻页
    for page in range(total_page):
        offset = page * 20
        r = requests.get(url=get_following_url(person_token, offset), headers=person_headers)
        d = json.loads(r.text)
        dic = d['data']
        for each_person_token in dic:
            # token用来构造详情页url，获取详情信息
            url_token = each_person_token['url_token']
            # print(url_token)
            # 如果这个url_token 没有被爬取过，并且不再待爬取的列表中， 就放入待爬取列表
            if url_token not in old_user_packet and url_token not in new_user_packge:
                new_user_packge.add(url_token)


# 从待爬取队列中取得user_token, 获得用户详情信息，用于持久化
# @ asyncio.coroutine
def detail_info():
    if len(new_user_packge) == 0:
        try:
            # 获取更多的token放入带爬取集合
            old_user_token = old_user_packet.pop()
            # 获取此token对应的关注人的所有token
            get_following_token(old_user_token)
        except Exception as e:
            print("无法获取更多的token")
            print(e)
    else:
        # 从队列中拿出一个token
        user_token = new_user_packge.pop()
        # 把token放入已爬取过的token包裹中， 避免爬取已经爬过的token
        old_user_packet.add(user_token)

        # 获取此token对应用户的详细信息
        person_info_url = 'https://www.zhihu.com/api/v4/members/'+str(user_token)+'?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
        print('>>>>>>>>>>>>: '+person_info_url)

        try:
            person_detail = requests.get(url=person_info_url, headers=detail_headers)
            time.sleep(random.uniform(1, 2))
            # print(person_detail)
            # print(person_detail.text)
            d = json.loads(person_detail.text)
            # 昵称
            name = d['name']
            # 自我介绍
            headline = d['headline']
            # 关注者
            follow_count = d['follower_count']
            # 文章数
            article_count = d['articles_count']
            # 回答数
            answer_count = d['answer_count']
            # 性别
            gen = d['gender']
            # 职业经历
            employments = d['employments']
            # 可能有多段职业经历
            employment = []
            if len(employments) != 0:
                for i in d['employments']:
                    company = i['company']['name']
                    if 'job' in i:
                        job = i['job']['name']
                        each_employment = company + '->' + job
                        employment.append(each_employment)

            if gen == '-1':
                gender = '男'
            else:
                gender = '女'
            dp = DataPesistence()
            # await dp.save_data(user_token, name, headline, follow_count, article_count, answer_count, gender, employment)
            # loop = asyncio.get_event_loop()
            # loop.run_until_complete(asyncio.wait(detail_info))
            # loop.close()
            pool = ThreadPool(processes=10)
            pool.apply_async(dp.save_data, (user_token, name, headline, follow_count, article_count, answer_count, gender, employment))
            pool.close()
            pool.join()
            # dp.save_data(user_token, name, headline, follow_count, article_count, answer_count, gender, employment)
            # print(name, headline, employment, follow_count, article_count, answer_count, gender)
        except Exception as e:
            print('用户token为:' + user_token + "的详情页获取异常")
            print(e)


if __name__ == '__main__':
    first_request()

    while 1:
        thread2 = threading.Thread(target=detail_info())
        thread2.start()


