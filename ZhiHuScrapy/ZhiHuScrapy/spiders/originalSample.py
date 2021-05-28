
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

#
# def paa(ur):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                       'Chrome/72.0.3626.121 Safari/537.36'}
#
#     r1 = requests.get(ur, headers=headers)
#     html_contents = r1.text
#     html_soup = BeautifulSoup(html_contents, "html.parser")
#     print(html_soup)
#     words = []
#     date = []
#     # div = html_soup.find('div', class_='m-wrap')
#     count = 0
#     for div1 in html_soup.find_all('div', class_="card-feed"):
#         if count > 20:
#             break
#         wo = div1.find('p', class_='txt').text.strip().split('展开全文')[0]
#         da = div1.find('p', class_='from').text.strip().split("\n")[0]
#         words.append(wo)
#         date.append(da)
#         count += 1
#     final = pd.DataFrame({"Words": words, "Time": date})
#     return final
#
# def paaz(urr):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                       'Chrome/72.0.3626.121 Safari/537.36'}
#
#     r1 = requests.get(urr, headers=headers)
#     html_contents = r1.text
#     html_soup = BeautifulSoup(html_contents, "html.parser")
#     question = []
#     for div in html_soup.find_all('div', class_="List-item TopicFeedItem"):
#         ques = div.find('a', target='_blank').text.strip()
#         question.append(ques)
#     final = pd.DataFrame({"Questions": question})
#
#     return final
# print(paaz('https://www.zhihu.com/topic/19686463/top-answers'))

# def paaz(urr):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                       'Chrome/72.0.3626.121 Safari/537.36'}
#
#     r1 = requests.get(urr, headers=headers)
#     time.sleep(3)
#     html_contents = r1.text
#     html_soup = BeautifulSoup(html_contents, "html.parser")
#     print(html_soup)
#     question = []
#     date = []
#     for div in html_soup.find_all('span', class_="List-item"):
#         print(div)
#         ques = div.find('span', class_='Highlight').text.strip()
#         print(ques)
#         da = div.find('span', class_='ContentItem-action SearchItem-time').text.strip()
#         question.append(ques)
#         date.append(da)
#     final = pd.DataFrame({"Questions": question, "Time": date})

    # return final

url = "https://www.zhihu.com/api/v4/topics/19686463/feeds/essence"
question = []
date1 = []
date2 = []
for i in range(0, 27):
    params = {
        'include': 'data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.content,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.is_normal,comment_count,voteup_count,content,relevant_info,excerpt.author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=article)].target.content,voteup_count,comment_count,voting,author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=people)].target.answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics;data[?(target.type=answer)].target.annotation_detail,content,hermes_label,is_labeled,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,answer_type;data[?(target.type=answer)].target.author.badge[?(type=best_answerer)].topics;data[?(target.type=answer)].target.paid_info;data[?(target.type=article)].target.annotation_detail,content,hermes_label,is_labeled,author.badge[?(type=best_answerer)].topics;data[?(target.type=question)].target.annotation_detail,comment_count;',
        'offset': str(i*5),
        'limit': 5,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/72.0.3626.121 Safari/537.36'}

    r1 = requests.get(url, headers=headers, params=params)
    json_information = r1.json()
    for j in json_information["data"]:
        # print(j['target'])
        try:
            ques = j['target']['question']['title']
        except KeyError:
            ques = j['target']['title']
        question.append(ques)
        try:
            da1 = j['target']['question']['created_time']
        except KeyError:
            da1 = j['target']['created']
        # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(da1)))
        date1.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(da1)))
        try:
            da2 = j['target']['updated_time']
        except KeyError:
            da2 = j['target']['updated']
        date2.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(da2)))
print(pd.DataFrame({"Questions": question, "CreateTime": date1, "UpdatedTime": date2}))

# for i in range(2, 10):
#     url = "https://s.weibo.com/weibo/UIC?topnav=1&wvr=6&page="+str(i)
#     print(url)
#     time.sleep(0.5)
#     print(paa(url))



