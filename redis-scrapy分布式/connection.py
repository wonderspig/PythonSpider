# -*- coding:utf-8 -*-
import six
from  scrapy.utils.misc  import load_object

#这个暂时还没写呢
from . import defaults

#一个参数映射表
SETTINGS_PARAMS_MAP={
    "REDIS_URL":'url',
    'REDIS_HOST': 'host',#主机地址
    'REDIS_PORT': 'port',#主机端口号
    'REDIS_ENCODING': 'encoding',#redis的编码方式
}
#通过配置文件返回一个redis客户端实例
#功能就是根据get_client接口,使用默认的‘defaults.REDIS_PARAS’,这个是全局的，你可以自己进行覆盖
"""
    Parameters
    ----------
    settings : Settings
        A scrapy settings object. See the supported settings below.
    这个需要查看redis支持哪一些接口
    Returns
    -------
    server
        Redis client instance.

    Other Parameters
    ----------------
    REDIS_URL : str, optional
        Server connection URL//服务端连接的url.
    REDIS_HOST : str, optional
        Server host.
    REDIS_PORT : str, optional
        Server port.
    REDIS_ENCODING : str, optional
        Data encoding.
    REDIS_PARAMS : dict, optional
        Additional client parameters.
"""
#外部获取的
def get_redis_from_settings(settings):
    #params是一个字典
    params=defaults.REDIS_PARAMS.copy()
    params.update(settings.getdict('REDIS_PARAMS'))
    for source,dest in SETTINGS_PARAMS_MAP.items():
        val=settings.get(source)
        if val:
            params[dest]=val

    if isinstance(params.get('redis_cls'),six.string_types):
        params['redis_cls']=load_object(params['redis_cls'])
    return get_redis(**params)
from_settings=get_redis_from_settings

def get_redis(**kwargs):
    redis_cls=kwargs.pop('redis_cls',defaults.REDIS_CLS)
    #判断是否包含一个url可使用pop方法 dict.pop(key[,default])，
    # 通过key值删除dict内元素，并返回被删除key对应的value。若key不存在，且default值未设置，则返回KeyError异常
    url=kwargs.pop('url',None)
    if url:
        return redis_cls.from_url(url,**kwargs)
    else:
        return redis_cls(**kwargs)

