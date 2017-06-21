from pymongo import MongoClient


class DataPesistence():
    connect = MongoClient('localhost', 27017)
    db = connect.zhihu
    collecton = db.zhihu

# 插入数据
    def save_data(self, user_token, name, headline, follow_count, article_count, answer_count, gender, employment):
        dic = {
            'user_token': user_token,
            'name': name,
            'headline': headline,
            'follow_count': follow_count,
            'article_count': article_count,
            'answer_count': answer_count,
            'gender': gender,
            'employments': employment
        }
        self.collecton.save(dic)
        # print(dic + "插入成功")
        self.connect.close()




