import logging
import time

from scrapy.dupefilters import BaseDupeFilter
from scrapy.utils.request import request_fingerprint
from  . import defaults
from .connection import get_redis_from_settings
logger=logging.getLogger(__name__)
#继承父类，重写了scrapy自带的request判重的功能
"""
 单机版本：只需要使用scrapy自带的判重类，在内存或者本地磁盘的request队列进行比较
 分布式：要求各个主机上的scheduer都要连接到一个数据库的同一个request队列来判断这次的请求是否重复

 BaseDupeFilter原理：通过hash来判断两个url是否相等。这里将沿用此种模式。
 该类通过连接redis，使用一个key来向redis的一个set中插入fingerprint(这个key对于同一种spider是相同的，在这里为了区分不同的爬虫。
 使用spider名字+DupeFilter的key来保证不同的主机上的不同爬虫获取同一种spider下的同一个set)

 DupeFilter判重会在scheduler中用到，每一个request在进入调度之前都需要进行判重
"""
class RFPDupeFilter(BaseDupeFilter):
    logger=logger
    def __init__(self,server,key,debug=False):
        """Initialize the duplicates filter.

        Parameters
        ----------
        server : redis.StrictRedis
            The redis server instance.
        key : str
            Redis key Where to store fingerprints.根据签名来判断是否有重复的
        debug : bool, optional
            Whether to log filtered requests.

        """
        self.server=server
        self.key=key
        self.debug=debug
        self.logdupes=True


    @classmethod
    def from_settings(cls, settings):
        server=get_redis_from_settings(settings)

        key=defaults.DUPEFILTER_KEY%{'timestamp':int(time.time())}
        debug=defaults.getbool('DUPEFILTER_DEBUG')
        return cls(server,key=key,debug=debug)
#http://www.admin5.com/article/20080825/100523.shtml
#记录这spider和crawler的区别
    @classmethod
    def from_crawler(cls,crawler):
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        #如果启用过滤且不重复
        fp=self.request_fingerprint(request)
        added=self.server.sadd(self.key,fd)
        return added==0

    def request_fingerprint(self,request):
        return request_fingerprint(request)

    @classmethod
    def from_spider(cls,spider):
        settings=spider.settings
        server=get_redis_from_settings(settings)
        dupefilter_key=settings.get("SCHEDULER_DUPEFILTER_KEY", defaults.SCHEDULER_DUPEFILTER_KEY)
        key=dupefilter_key%{'spider':spider.name}
        debug=settings.getbool('DUPEFILTER_DEBUG')
        return cls(server,key=key,debug=debug)
    #关闭时候清除数据
    def close(self, reason):
        self.clear()

    def clear(self):
        self.server.delete(self.key)

    def log(self, request, spider):
        if self.debug:
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
            self.logdupes = False



