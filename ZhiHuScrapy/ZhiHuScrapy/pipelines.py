# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import random
import jieba.analyse
import jieba
from itemadapter import ItemAdapter

from USFP.models import *
from .items import ZhiHuScrapyItem

class ZhiHuScrapyPipeline:

    def process_item(self, item, spider):
        myItem = ZhiHuScrapyItem()
        myItem["content"] = item["content"]
        myItem["postTime"] = item["postTime"]
        myItem["modifyTime"] = item["modifyTime"]
        myItem["commonUser"] = CommonUser.objects.get(commonUserID=random.randint(1,50))
        # allTagsList = Tag.objects.values_list("tagName", flat=True)
        # for i in jieba.analyse.extract_tags(item["content"], topK=5, withWeight=True, allowPOS=('n', 'nr', 'ns')):
        #     if i[0] in allTagsList:
        #         tag = Tag.objects.get(tagName=i[0])
        #         myItem['tags'].add(tag)
        #         tag.tagShowNum = tag.tagShowNum + 1
        #         tag.save()
        #     else:
        #         newTag = Tag.objects.create(tagName=i[0], tagShowNum=1)
        #         myItem['tags'].add(newTag)
        #         allTagsList = Tag.objects.values_list("tagName", flat=True)
        myItem.save()
