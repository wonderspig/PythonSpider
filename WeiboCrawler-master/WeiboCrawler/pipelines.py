# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#pipelines中得到最终抓到的item，可以在这里将item存储到数据库中
import pymongo
from scrapy.conf import settings

#定义一个mongodb缓存
class MongoDBCache(object):
    def __int__(self):
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbName = settings['MONGODB_DBNAME']
        client = pymongo.MongoClient(host=host, port=port)
        tdb = client[dbName]
        self.WeibocrawlerItem = tdb[settings['MONGODB_DOCNAME']]


#定义一个磁盘缓存
class DiskCace(object):
    def __init__(self):
        self.cache_dir=settings['DISKCACHE']

class WeibocrawlerPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item,WeibocrawlerItem):
            try:
                self.WeibocrawlerItem.insert(dict(item))
            except Exception:
                pass
        return item
