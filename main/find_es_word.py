#輸入日期  畫出文字雲
#輸入關鍵字找新聞
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from snownlp import sentiment
from matplotlib.font_manager import FontProperties # 設定字體
font_path = matplotlib.font_manager.FontProperties(fname='msj.ttf')
from elasticsearch import Elasticsearch


user = "2019-07-25"
uuse = "2020-01-04"


def userfindtime(use,uuse):
    es = Elasticsearch(['192.168.1.29:9200'])

    dsl = {
        'query': {
            'range': {
                'time':{
                    "gte": user,
                    "lte": uuse,

                }
            }

        }
    }

    result2 = es.search(index='news_doc', doc_type='politics', body=dsl)
    # print(result2)
    hits = result2["hits"]
    hit = hits["hits"]
    for k in hit:
        # print(k['_source'])
        # print(k['_source']['content'])

        sent = sentiment.Sentiment()
        words_list=sentiment.Sentiment.handle(sent,k['_source']['content'])
            # print(words_list)
            #
        wl_space_split = "/".join(words_list)
        # print(wl_space_split)
    #
        wl_space_split += wl_space_split
    # # print(wl_space_split)
    #
    my_wordcloud = WordCloud().generate(wl_space_split)
    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.show()




# userfindtime(user,uuse)




#####################################################################

user = "中國  美金"

def userfindtitle(str_in):
    es = Elasticsearch(['192.168.1.29:9200'])

    dsl = {
        'query':{
            'match':{
                'title':str_in
            }

        }
    }

    result2 = es.search(index='newnew_doc',doc_type='politics',body=dsl)

    hits = result2["hits"]
    hit = hits["hits"]
    news_list = []
    for k in hit:
        news_list.append(k['_source'])
    #     # print(k['_source'])
    #     print(k['_source']["title"])
    #     print(k['_source']["url"])
    #     print(k['_source']["time"])
    #     print(k['_source']["content"])
    return news_list

userfindtitle(user)



# if re.search("^[0-9]*$", user):
#     print(999)
#     userfindtime(user)
# else:
#     userfindtitle(user)
#     print(222)
#