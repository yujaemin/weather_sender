# -*- coding: utf-8 -*-
import scrapy
import json
import os
import urllib
from urlparse import urljoin
from scrapy.http import Request, FormRequest #로그인
from datetime import datetime
import pytz
import time
from time import sleep
from urllib import quote,unquote
from dateutil.parser import parse
import re
import logging
import commands

def trace(func):
    def callf(*args, **kwargs):
        logging.info('[scrapy] calling function %s: %s' \
                      % (func.__name__, kwargs))
        r = func(*args, **kwargs)
        logging.info('[scrapy] %s returned %s' % (func.__name__, r))
        return r
    return callf

class WeatherSpider(scrapy.Spider):
    name = "weather"
    allowed_domains = ["daum.net"]
    start_urls = [
        "http://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q=%EB%82%A0%EC%94%A8&tltm=1",
    ]

    handle_httpstatus_list = [404]
    jobid=None;
    clubId = None;
    boardCode = None;
    recentUid = None;
    recentTime = None;
    fromTime = None;
    toTime = None;
    numOfAtc = 10;
    rescrapUids = None;
    excludeUids = None;
    count = None;
    page = None
    scrapAll = None
    uidList = {}

    def __init__(self, boardCode=None, afterUid=None, recentTime=None, fromTime=None, toTime=None, numOfAtc=10, rescrapUids=None, excludeUids=None, scrapAll=None, *args, **kwargs):
        super(WeatherSpider, self).__init__(*args, **kwargs)
        download_delay=5

    def parse(self, response):
        #print response.body
        #print response.xpath('//div[@id="weatherColl"]').extract()
        w = response.xpath('//div[@id="weatherColl"]')
        temperature_3hours = w.xpath('.//td[@headers="today td3am"]/div/span/text()').re('\d+')
        rain_3hours = w.xpath('.//td[@headers="today rain"]').re('\d+')
        for i in range(0, 3):
            r = '{r:#>2}'.format(r=rain_3hours[i])
            r = re.sub('#', '  ', r)
            rain_3hours[i] = r

        print rain_3hours
        yesterday = w.xpath('.//tr[@class="import"]/td[@headers="yesterday"]/div//text()').extract()

        text =  '{d}\n오늘의 날씨\n'.format(d=str(datetime.today().strftime("%Y-%m-%d") ))
        text += '┌────┬────┬──────┐\n'
        text += '│  시간  │  온도  │ 강수확률  │\n'
        text += '├────┼────┼──────┤\n'

        for t in range(0, 8):
            hour = (t + 1) * 3
            text += '│  {h:0>2}시 │  {temperature:0>2}도 │   {r}%       │\n'.format(h=hour, temperature=temperature_3hours[t], r=rain_3hours[t])

        text += '└────┴────┴──────┘\n'
        print text

        d = str(datetime.today())
        cur_path = os.path.dirname(os.path.abspath(__file__))
        filename = 'weather_' +d + '.txt'
        filepath = cur_path + filename
        with open(filepath, 'w') as f:
            f.write(text)

        userlist = []
        userlist.append('s박원형')
        userlist.append('jaemin_yu')

        for user in userlist:
            a, b = commands.getstatusoutput(cur_path + '/tg/bin/telegram-cli -W -e "send_text {id} {path}" /dev/null'.format(id=user, path=filepath))
            print a
            print b

