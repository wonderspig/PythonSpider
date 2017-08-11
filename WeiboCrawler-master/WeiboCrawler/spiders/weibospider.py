# -*- coding: gb2312 -*-

'''
Created on 2017-03-02

@author: Sawatari
'''

import sys
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.selector import Selector
from WeiboCrawler.items import WeibocrawlerItem

class WeiboCrawler(Spider):
    name = "WeiboCrawler"
    download_delay = 4
    allowed_domains = ["weibo.cn"]
    start_urls = [
        "http://weibo.cn/"
    ]

    def parse(self, response):
        # ����ȷ���Ƿ������ɹ�
        starttime="20160101"
        endtime="20161230"
        if response.url == "http://weibo.cn/":
            # ��ȡ��ʱ�ļ�
            temp = open('tempkey.temp', 'r')
            keyword = temp.read()
            temp.close()
            # �����ؼ��ʵ�һҳ
            url = "http://weibo.cn/search/mblog?hideSearchFrame=&keyword=" +keyword\
                  + "&advancedfilter=1&starttime="+starttime+"&endtime="+endtime+"&sort=time&page=1"
            #url = "http://weibo.cn/search/mblog?hideSearchFrame=&keyword=" + keyword + "&page=1"
            # ������ת��Ϊuft-8
            url = url.decode("GBK").encode("utf-8")
            # �ݹ�
            yield Request(url, callback=self.parse)

        else:
            # �����ɹ�

            item=WeibocrawlerItem()
            sel = Selector(response)
            results = sel.xpath('//*[@class="c"]')

            #temp=sel.xpath('//*[@class="pa"]/form/div/input[@name="mp"]/@value').extract()
            temp=sel.xpath('//*[@id="pagelist"]/form/div/input[1]/@value').extract()
            print "temp=%s" %temp
            if temp:
                num=temp[0].encode('utf-8')


            strnum=int(num)
            print "strnum=%d" %strnum
            for result in results:

                name = result.xpath('div/span[@class="ctt"]/text()').extract()
                date = result.xpath('div/span[@class="ct"]/text()').extract()

                # sys.getfilesystemencoding()��ñ��ر��루mbcs���룩
                item['name'] = [na.encode(sys.getfilesystemencoding()) for na in name]
                item['date']=[na.encode(sys.getfilesystemencoding()) for na in date]
                yield item

            # ��ȡ�ؼ���
            keyword = response.url[(response.url.index("keyword=") + 8):response.url.index("&advancedfilter")]
            # �ݹ�
            next_page_urls = []
            url = "http://weibo.cn/search/mblog?hideSearchFrame=&keyword=" +keyword +\
                  "&advancedfilter=1&starttime="+starttime+"&endtime="+endtime+"&sort=time"

            if num:
                for i in range(2, strnum, 1):
                    page = str(i)
                    next_page_urls.append( url  + "&page=" + page)
            # �ݹ��ȡ��ҳ
                for next_page_url in next_page_urls:
                    yield Request(next_page_url, callback=self.parse)
            # 100ҳ�б�
