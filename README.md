# PythonSpider
功能：python+scrapy实现网络爬虫，爬取微博南京地铁两年数据

环境：win67或者以上(64位)/linux+python2.7.13(64（位置)+scrapy1.1.0

使用方法：cmd->python main.py->输入关键字，输出的结果可以选择保存至磁盘即在main.py同级目录下的result.csv文件中，也可以选择保存之MongoDB数据库

磁盘缓存：无须安装其他模块，并且文件管理中就能查看结果，但是受制于本地文件系统，例如每个卷下和每个目录下的文件数量是有限制的。
        
数据库缓存：以mongodb为例，使用pip install pymongo命令安装pymongo模块，支持缓存。加载数据库缓存的事件几乎是加载磁盘缓存的两倍。

需要改进：

1.目前仅支持单线程，尚未引入多线程

