# -*- coding:utf-8 -*-
from scrapy.utils.misc import load_object
from scrapy.utils.serialize import ScrapyJSONDecoder

from twisted.internet.threads import deferToThread

from . import connection,defaults

default_serialize=ScrapyJSONEncoder.encode
#------------------功能-----------------#
#cleansing HTML data
#validating scraped data (checking that the items contain certain fields)
#checking for duplicates (and dropping them)
#storing the scraped item in a database
class RedisPipeline(object):
    def __init__(self,server,key=defaults.PIPELINE_KEY,serialize_func=default_serialize):
        self.server=server
        self.key=key
        self.serialize=serialize_func

    @classmethod
    def from_settings(cls,settings):
        params={
            connection.from_settings(settings),
        }
        if settings.get('REDIS_ITEMS_KEY'):
            params['key'] = settings['REDIS_ITEMS_KEY']
        if settings.get('REDIS_ITEMS_SERIALIZER'):
            params['serialize_func'] = load_object(
                settings['REDIS_ITEMS_SERIALIZER']
            )

        return cls(**params)

    @classmethod
    def from_crawler(cls,crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self):
        #***把同步函数变为异步(返回一个Deferred)***
#twisted的deferToThread(from twisted.internet.threads import deferToThread)也返回一个deferred对象,
        # 不过回调函数在另一个线程处理,主要用于数据库/文件读取操作
        return deferToThread(self._process_item,item,spider)

    def _process_item(self,item,spider):
        key=self.item_key(item,spider)
        data=self.serialize(item)
        self.server.rpush(key,data)
        return item

    def item_key(self,item,spider):
        return self.key % {'spider': spider.name}