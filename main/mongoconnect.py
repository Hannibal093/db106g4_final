from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
Timestamp = pd.Timestamp
idx = pd.IndexSlice


class MongoConnection(object):

    def __init__(self):
        self.client = MongoClient('mongodb://hannibal:`1q@192.168.1.109/news')

    def get_database(self, dbname):
        self.db = self.client[dbname]

    def get_collection(self, name):
        self.collection = self.db[name]


class NewsCollection(MongoConnection):

    def __init__(self):
        super(NewsCollection, self).__init__()
        self.get_database('news')
        self.get_collection('news.doc')

    def find_twenty(self, page):
        news_list = []

        if page >= 1:
            page -= 1
        else:
            page = 0
        if self.collection.find({}).count():
            for i in self.collection.find().skip(page*20)\
                    .limit(20).sort('time', -1):
                news_list.append(i)
        return news_list

    def find_all(self):
        return self.collection.find({})

    def find_all_list(self):
        news_list = []
        news_data = self.collection.find({})
        for n in news_data:
            news_list.append(n)
        return news_list

    def find_single(self):
        return self.collection.find_one({})

    def find_single_for_stock(self, news_id):
        return self.collection.find_one({"_id": news_id}, {"_id": 0, "title": 1, "time": 1, "url": 1})

    def find_by_id(self, news_id):
        return self.collection.find_one({"_id": news_id})

    def find_by_source(self, source):
        news_list = []
        for i in self.collection.find({"source": source}):
            news_list.append(i)
        return news_list

    def find_by_type(self, news_type):
        self.get_database('test')
        self.get_collection('ltn')
        news_list = []
        for i in self.collection.find({"news_type":news_type},
                                      {"_id": 0, "title": 1, "date": 1, "href": 1}).limit(10):
            news_list.append(i)
        self.get_collection('cnyes')
        for j in self.collection.find({"news_type":news_type},
                                      {"_id": 0, "title": 1, "date": 1, "href": 1}).limit(10):
            news_list.append(j)
        return news_list

    def get_recommand_news(self, news_type):
        first_day = datetime.today() - timedelta(days=104)
        last_day = datetime.today() - timedelta(days=21)
        news_g = []
        news_b = []
        news_t = []
        for g_news in self.collection.find({
            "news_type": news_type,
            "good_news": '1',
            "time": {"$gt": first_day, "$lt": last_day},
            "title_score": {"$gt": float(0.5)}
        },
                {"_id": 0,
                 "title": 1,
                 "url": 1,
                 "time": 1,
                 "title_score": 1,
                 "good_news": 1}).sort("time", -1).limit(5):
            news_g.append(g_news)

        for b_news in self.collection.find({
            "news_type": news_type,
            "good_news": '0',
            "time": {"$gt": first_day, "$lt": last_day},
            "title_score": {"$lt": float(0.3)}
        },
                {"_id": 0,
                 "title": 1,
                 "url": 1,
                 "time": 1,
                 "title_score": 1,
                 "good_news": 1}).sort("time", -1).limit(5):
            news_b.append(b_news)

        return news_g, news_b

    def find_collections(self):
        return self.db.list_collection_names()

    def count_doc(self):
        return self.collection.count_doc()

    def category_update(self, title, new_list):
        self.collection.find_one({"title": title}, {"$set": {"category": new_list}})


class StockCollection(MongoConnection):

    def __init__(self):
        super(StockCollection, self).__init__()
        self.get_database('stock')
        self.get_collection('stock.doc')

    def get_stock_list(self):
        stock_list = []
        stock_data = self.collection.find({}, {"_id": 0,
                                               "stock_id": 1,
                                               "stock_name": 1,
                                               'industry': 1}).sort("stock_id", 1)
        for i in stock_data:
            stock_list.append(i)
        return stock_list

    def get_stock_list_ftn(self, page):
        stock_list = []

        if page >= 1:
            page -= 1
        else:
            page = 0

        stock_data = self.collection.find({"industry": {"$exists": True},
                                           "price": {"$exists": True},
                                           "month": {"$exists": True},
                                           "bargin": {"$exists": True},
                                           "stock_name": {"$exists": True}},
                                          {"_id": 0,
                                           "stock_id": 1,
                                           "stock_name": 1,
                                           "industry": 1}).sort("stock_id", 1).skip(page*15).limit(15)
        for i in stock_data:
            stock_list.append(i)
        return stock_list

    def get_single_by_id(self, stock_id='2330'):
        stock_data = self.collection.find_one({"stock_id": stock_id})
        return stock_data

    def get_by_name(self, stock_name='台積電'):
        stock_data = self.collection.find_one({"stock_name": stock_name})

        return stock_data

    def get_single_price(self, stock_id):
        stock_data = self.collection.find_one({"stock_id": stock_id}, {"_id": 0, "price": 1})
        df = pd.DataFrame(stock_data['price']).set_index('date')
        return df

    def get_latest_price(self, stock_id):
        stock_data = self.collection.find_one({"stock_id": stock_id}, {"_id": 0, "price": 1, "stock_name": 1})
        df = pd.DataFrame(stock_data['price']).sort_values(by=['date'], ascending=True).tail(100).set_index('date')
        return df, stock_data['stock_name']

    def get_by_industry(self, industry, page=0):
        stock_list = []
        total_count = self.collection.count_documents({"industry": industry})
        lim = max(15, total_count)
        if page * 15 <= total_count:
            pass
        else:
            if total_count % 15 == 0:
                page = (total_count // 15) - 1
            else:
                page = (total_count // 15)
        stock_data = self.collection.find({"industry": industry}, {"_id": 0,
                                                                   "stock_id": 1,
                                                                   "stock_name": 1,
                                                                   "industry": 1})\
                                    .sort('stock_id', 1).limit(lim).skip(page * 15)
        for s in stock_data:
            stock_list.append(s)
        return stock_list

    def get_recommand_stock(self, stock_type):
        stock_list_best = []
        stock_list_sec = []
        stock_list_trd = []
        stock_list_normal = []
        stock_best = self.collection.find(
            {"pred_from_report": '1',
             "best_twenty": 1,
             "stock_name": {"$exists": True},
             "stock_type": stock_type},
            {"_id": 0, "price": 0, "bargin": 0, "month": 0, "season": 0})

        stock_sec = self.collection.find(
            {"pred_from_report": '0',
             "best_twenty": 1,
             "stock_name": {"$exists": True},
             "stock_type": stock_type},
            {"_id": 0, "price": 0, "bargin": 0, "month": 0, "season": 0})

        stock_trd = self.collection.find(
            {"pred_from_report": '1',
             "best_twenty": 0,
             "stock_name": {"$exists": True},
             "stock_type": stock_type},
            {"_id": 0, "price": 0, "bargin": 0, "month": 0, "season": 0})

        for sb in stock_best:
            try:
                ab = sb['abnor_rep']
                if ab == '0':
                    stock_list_best.append(sb)
                else:
                    stock_list_sec.append(sb)
            except:
                stock_list_best.append(sb)

        for ss in stock_sec:
            try:
                ab = ss['abnor_rep']
                if ab == '0':
                    stock_list_sec.append(ss)
                else:
                    stock_list_trd.append(ss)
            except:
                stock_list_sec.append(ss)

        for st in stock_trd:
            try:
                ab = st['abnor_rep']
                if ab == '0':
                    stock_list_trd.append(st)
                else:
                    stock_list_normal.append(st)
            except:
                stock_list_trd.append(st)

        return stock_list_best, stock_list_sec, stock_list_trd, stock_list_normal

    def get_relate_news(self, stock_id):
        try:
            stock_data = self.collection.find_one({"stock_id": stock_id}, {"relate_news": 1})
            news_list = stock_data['relate_news']
        except:
            news_list = []
        return news_list

    def get_by_stock_type(self, stock_type):
        stock_list = []
        stock_data = self.collection.find({"industry": {"$exists": True}, "stock_type": {"$exists": True}},
                                          {"_id": 0, "stock_id": 1, "stock_name": 1, "industry": 1}).sort("stock_id", 1)
        for s in stock_data:
            stock_list.append(s)
        return stock_list

    def get_industry_exist(self):
        stock_data = self.collection.find({"industry": {"$exists": True}},
                                          {"_id": 0, "stock_id": 1, "stock_name": 1, "industry": 1}).sort("stock_id", 1)
        return stock_data

    def get_industry_exist2(self):
        stock_data = self.collection.find({"industry": {"$exists": True}}).sort("stock_id", 1)
        return stock_data

    def update_column(self, stock_id, dict_to_update):
        self.collection.update_one({"stock_id": stock_id}, {"$set": dict_to_update})

    def update_stock(self, stock_id, dict_to_update):
        self.collection.update_one({"stock_id": stock_id}, {"$set": dict_to_update}, upsert=True)

    def get_basic_info_by_id(self, stock_id):
        stock_list = []
        stock_data = self.collection.find({"stock_id": stock_id},
                                          {"_id": 0, "price": 0, "month": 0, "bargin": 0, "season": 0})
        for s in stock_data:
            stock_list.append(s)
        return stock_list

    def get_info_complete(self):
        stock_list = []
        stock_data = self.collection.find({"industry": {"$exists": True},
                                           "category": {"$exists": True},
                                           "stock_type": {"$exists": True}},
                                          {"_id": 0, "price": 0, "month": 0, "bargin": 0, "season": 0})
        for s in stock_data:
            stock_list.append(s)
        return stock_list

    def get_abnor_rep(self):
        stock_list = []
        for s in self.collection.find({"abnor_rep": {"$exists": True}},
                                      {"_id": 0, "price": 0, "month": 0, "bargin": 0, "season": 0}):
            stock_list.append(s)
        return stock_list


class UserCollection(MongoConnection):

    def __init__(self):
        super(UserCollection, self).__init__()
        self.get_database('user')
        self.get_collection('user.doc')

    def add_user(self, dict_to_update):
        self.collection.insert_one(dict_to_update)

    def get_user(self, user_id, name):
        try:
            user = self.collection.find_one({'id': user_id, 'name': name})
        except:
            user = ''
        return user

    def get_subscribe(self, user_id):
        user_data = self.collection.find_one({"id": user_id})
        try:
            sub_stock = user_data['stock']
        except:
            sub_stock = []
        return sub_stock

    def subscribe_stock(self, user_id, stock_id):
        user_data = self.collection.find_one({"id": user_id})
        sub_stock = user_data['stock']
        sub_stock.append(stock_id)
        dict_to_update = {'stock': sub_stock}
        self.collection.update_one({'id': user_id}, {"$set": dict_to_update}, upsert=True)

    def unsubscribe_stock(self, user_id, stock_id):
        user_data = self.collection.find_one({"id": user_id})
        sub_stock = user_data['stock']
        sub_stock.remove(stock_id)
        dict_to_update = {'stock': sub_stock}
        self.collection.update_one({'id': user_id}, {"$set": dict_to_update}, upsert=True)