import jieba
import jieba.analyse
import scrapy

from USFP.models import *
from ..items import ZhiHuScrapyItem
import time


class ZhiHuScrapySpider(scrapy.Spider):
    name="ZhiHuScrapy"
    allowed_domains=["www.zhihu.com"]
    start_urls=[]
    origin_url = "https://www.zhihu.com/api/v4/topics/19686463/feeds/essence?"
    for i in range(0, 27):
        params = {
            'include': 'data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.content,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.is_normal,comment_count,voteup_count,content,relevant_info,excerpt.author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=article)].target.content,voteup_count,comment_count,voting,author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=people)].target.answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics;data[?(target.type=answer)].target.annotation_detail,content,hermes_label,is_labeled,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,answer_type;data[?(target.type=answer)].target.author.badge[?(type=best_answerer)].topics;data[?(target.type=answer)].target.paid_info;data[?(target.type=article)].target.annotation_detail,content,hermes_label,is_labeled,author.badge[?(type=best_answerer)].topics;data[?(target.type=question)].target.annotation_detail,comment_count;',
            'offset': str(i*5),
            'limit': "5",
         }
        url = origin_url
        for key,value in params.items():
            url=url+key+"="+value+"&"
        start_urls.append(url)


    def parse(self,response):
        json_information = response.json()
        data = json_information["data"]
        for j in data:
            item=ZhiHuScrapyItem()
            try:
                item['content'] = j['target']['question']['title']
            except KeyError:
                item['content'] = j['target']['title']
            try:
                da1 = j['target']['question']['created_time']
            except KeyError:
                da1 = j['target']['created']
            # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(da1)))
            item['postTime']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(da1))
            try:
                da2 = j['target']['updated_time']
            except KeyError:
                da2 = j['target']['updated']
            item['modifyTime']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(da2))
            # allTagsList = Tag.objects.values_list("tagName", flat=True)
            # for i in jieba.analyse.extract_tags(item["content"], topK=5, withWeight=True, allowPOS=('n', 'nr', 'ns')):
            #     if i[0] in allTagsList:
            #         tag = Tag.objects.get(tagName=i[0])
            #         item['tags'].add(tag)
            #         tag.tagShowNum = tag.tagShowNum + 1
            #         tag.save()
            #     else:
            #         newTag = Tag.objects.create(tagName=i[0], tagShowNum=1)
            #         item['tags'].add(newTag)
            #         allTagsList = Tag.objects.values_list("tagName", flat=True)
            # item.save()
            yield item