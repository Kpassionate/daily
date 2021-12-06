#!/user/bin/python
# _*_ coding:utf-8 _*_
# 多线程爬取幽默笑话 2020/5/21
__author__ = "super.gyk"

import requests
import threadpool
import time
import os, sys
import re
from lxml import etree


class DataSpider(object):

    def __init__(self, _url, end):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36"
        }
        self.start_url = _url
        self.next_page_url = ""  # 下一页的url
        self.page_num = 1
        self.end_num = end

    def download(self, detail_url):  # 抓取数据并存为TXT文件
        _url = None
        if detail_url:
            _url = "http://xiaohua.zol.com.cn/{}".format(detail_url)
        if not _url:
            return
        request = requests.get(_url, headers=self.headers)
        html = request.text

        content_list = re.findall('<div class="article-text">(.*?)</div>', html, re.S)
        for index in range(len(content_list)):
            # 使用正则表达式过滤掉回车、制表符和p标签
            content_list[index] = re.sub(r'(\r|\t|<p>|</p>)+', '', content_list[index])
        content = "".join(content_list)
        # 存储数据
        basedir = os.path.dirname(__file__)
        file_path = os.path.join(basedir)
        filename = "xiaohua{}.txt".format(self.page_num)
        file = os.path.join(file_path, 'xiaohua', filename)
        with open(file, 'a', encoding='utf-8') as f:
            f.write(content)

    def run(self):
        if self.page_num > self.end_num:
            sys.exit()
        if self.start_url:
            print("开启第{}页抓取".format(self.page_num))
            request = requests.get(self.start_url, headers=self.headers)
            html = request.text
            element = etree.HTML(html)
            all_url_list = element.xpath("//a[@class='all-read']/@href")  # 当前页面所有查看全文
            next_page_relative_url = element.xpath("//a[@class='page-next']/@href")  # 获取下一页的url(相对地址)
            next_page_len = len(next_page_relative_url)
            if next_page_len:
                self.next_page_url = 'http://xiaohua.zol.com.cn/{}'.format(next_page_relative_url[0])
            # 调用线程池
            pool = threadpool.ThreadPool(len(all_url_list))  # 创建线程池(num_workers, 线程数量)
            request_items = threadpool.makeRequests(self.download, all_url_list)  # 创建线程池处理的任务
            for item in request_items:
                pool.putRequest(item)  # put到线程池中
                # time.sleep(0.1)
                pool.wait()
            else:
                # 处理完当前页数据，开启下页
                if self.next_page_url:
                    self.page_num += 1
                    self.start_url = self.next_page_url
                    self.run()
                else:
                    # 无下一页，结束
                    sys.exit()
        else:
            print("起始路由有问题！")


if __name__ == "__main__":
    start_url = "https://xiaohua.zol.com.cn/lengxiaohua/"
    spider = DataSpider(start_url, 3)
    spider.run()
