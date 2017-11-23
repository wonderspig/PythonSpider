# -*- coding:utf-8 -*-
import redis


# For standalone use.
DUPEFILTER_KEY = 'dupefilter:%(timestamp)s'

PIPELINE_KEY = '%(spider)s:items'
#redis实例类型redis-py提供两个类Redis和StrictRedis用于实现Redis的命令，StrictRedis用于实现大部分官方的命令，并使用官方的语法和命令
# （比如，SET命令对应与StrictRedis.set方法）。Redis是StrictRedis的子类，用于向后兼容旧版本的redis-py。
# 简单说，官方推荐使用StrictRedis方法
REDIS_CLS = redis.StrictRedis
REDIS_ENCODING = 'utf-8'
# Sane connection defaults.
REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': REDIS_ENCODING,
}

SCHEDULER_QUEUE_KEY = '%(spider)s:requests'
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER_DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'

#编写爬虫时，其实url从redis的Key中获取
START_URLS_KEY = '%(name)s:start_urls'

#获取其实的url，从集合中获取还是列表中获取，集合false，列表true
START_URLS_AS_SET = False

