# -*- coding:utf-8 -*-
from scrapy.utils.reqser import request_from_dict,request_to_dict

from . import picklecompat

class Base(object):
    def __init__(self,server,spider,key,serializer=None):
        #serializer 对象是loads和dumps方法产生的
        if serializer is None:
            serializer=picklecompat
        if not hasattr(serializer, 'loads'):
            raise TypeError("serializer does not implement 'loads' function: %r"
                            % serializer)
        if not hasattr(serializer, 'dumps'):
            raise TypeError("serializer '%s' does not implement 'dumps' function: %r"
                            % serializer)
        self.server=server
        self.spider=spider
        self.key=key%{'spider':spider.name}
        self.serializer=serializer


    def _encode_request(self,request):
        #编码请求对象
        obj=request_to_dict(request,self.spider)
        return self.serializer.dumps(obj)

    def _decode_request(self,encoded_request):
        #解码一个请求对象
        obj=self.serializer.loads(encoded_request)
        return request_from_dict(obj,self.spider)

    def __len__(self):
        raise NotImplementedError

    def push(self,request):
        raise NotImplementedError

    def pop(self,timeout=0):
        raise NotImplementedError

    def clear(self):
        self.server.delete(self.key)


class PriorityQueue(Base):
    #使用有序数据集实现每个爬虫优先队列
    def __len__(self):
        #获取集合的长度
        return self.server.zcard(self.key)

    def push(self,request):
        data=self._encode_request(request)
        score=-request.priority
        self.server.execute_command('ZADD',self.key,score,data)

#管道（pipeline）是redis在提供单个请求中缓冲多条服务器命令的基类子类。通过减少服务器-客户端
# 之间反复的TCP数据库包，从而大大提高了执行批量命令的功能。
    def pop(self,timeout=0):
        pipe=self.server.pipeline()
        #MUTIL：开启事务，此后所有的操作将会添加到当前链接的事务“操作队列”中。
        pipe.multi()
        pipe.zrange(self.key,0,0).zremrangebyrank(self.key,0,0)
        #提交事务
        results,count=pipe.execute()
        if results:
            return self._decode_request(results[0])

class LifoQueue(Base):
    def __len__(self):
        return self.server.llen(self.key)

    def push(self,request):
        self.server.lpush(self.key,self._encode_request(request))

    def pop(self,timeout=0):
        if timeout > 0:
            data = self.server.blpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.lpop(self.key)

        if data:
            return self._decode_request(data)

class FifoQueue(Base):
    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            return self._decode_request(data)

SpiderQueue = FifoQueue
SpiderStack = LifoQueue
SpiderPriorityQueue = PriorityQueue
