# -*- coding:utf-8 -*-
from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import Spider, CrawlSpider

from . import connection, defaults
from .utils import bytes_to_str
#主要是从redis queue中获取数据
class RedisMixin(object):
    redis_key = None
    redis_batch_size = None
    redis_encoding = None
    # Redis client placeholder.
    server = None

    def start_request(self):
        return self.next_requests()

    def setup_redis(self,crawler=None):
        #安装redis连接和空闲的信号
        if  self.server is not None:
            return
        if crawler is None:
            crawler=getattr(self,'crawler',None)
        if crawler is None:
            raise ValueError("crawler is required")

        settings = crawler.settings

        if self.redis_key is None:
            self.redis_key=settings.get('REDIS_START_URLS_KEY', defaults.START_URLS_KEY)

        self.redis_key=self.redis_key%{'name':self.name}

        if not self.redis_key.strip():
            raise ValueError("redis_key must not be empty")

        if self.redis_batch_size is None:
            self.redis_batch_size=settings.getint('REDIS_START_URLS_BATCH_SIZE',settings.getint('CONCURRENT_REQUESTS'))

        try:
            self.redis_batch_size=int(self.redis_batch_size)
        except (TypeError,ValueError):
            raise ValueError("redis_batch_size must be an integer")

        if self.redis_encoding is None:
            self.redis_encoding=settings.get('REDIS_ENCODING',defaults.REDIS_ENCODING)

        self.server=connection.from_settings(crawler.settings)

        #当空闲的信号发生时，表明没有爬取的任务，此时我们将会从redis的队列中调度新得请求

        crawler.signals.connect(self.spider_idle,signal=self.spider_idle)

    def next_requests(self):
        #
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        #如果设置了use_set，将随机移除，否则返回和移除列表的最后一个元素
        fetch_one = self.server.spop if use_set else self.server.lpop
        found =0
        while found<self.redis_batch_size:
            data=fetch_one(self.redis_key)
            if not data:
                break
            req=self.make_request_from_data(data)

            if req:
                yield req
                found+=1
            else:
                self.logger.debug("Request not made from data: %r", data)
        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.redis_key)

    def make_request_from_data(self,data):
        #二进制的数据转成字符串
        url=bytes_to_str(data,self.redis_encoding)
        return self.make_request_from_url(url)

    def schedule_next_requests(self):
        for req in self.next_requests():
            self.crawler.engine.crawl(req,spider=self)

    def spider_idle(self):
        #调度一个请求，如果是可用的话，否则就阻塞等待
        self.schedule_next_requests()
        raise DontCloseSpider

class RedisSpider(RedisMixin,Spider):
    #spider用于从redis队列中读取url
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        obj=super(RedisSpider,self).from_crawler(crawler,*args,**kwargs)
        obj.setup_redis(crawler)
        return obj

class RedisCrawlSPider(RedisMixin,CrawlSpider):
    #spider用于从redis队列中读取url
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        obj=super(RedisCrawlSPider, self).from_crawler(crawler,*args,**kwargs)
        obj.setup_redis(crawler)



