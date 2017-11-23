#主要是因为redis数据库不能存储复杂的对象，因此我们需要堆需要存入的数据先进行串行化成文本才行
#对任意一个类型的对象进行序列化
try:
    import cPickle as pickle #py2版本下
except ImportError:
    import pickle
#反序列化
def load(s):
    return pickle.load(s)
#序列化
def dump(obj):
    return pickle.dumps(obj, protocol=-1)