#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import math
import datetime
import BeautifulSoup

from knn import KNN
from forecast import Forecast

def parseHTML(html):
    result = {}
    soup = BeautifulSoup.BeautifulSoup(html.decode('utf-8'))
    table = soup.find('table', {'class': 'data2_s'})
    year, month, day = map(int, re.findall(r'\d+', table.find('caption').text))

    for tr in table.findAll('tr'):
        td = tr.findAll('td')
        if len(td) < 1 or not td[0].text.isdigit() or int(td[0].text) % 6 != 3:
            continue

        hour = int(td[0].text)
        date = datetime.datetime(year, month, day, hour, 0, 0)
        result[date] = {'input': [month, hour]}

        for i in range(1, 8):
            if td[i].text == '--':
                result[date]['input'].append(0)
            else:
                result[date]['input'].append(float(td[i].text))

        directions = ['北', '北北東', '北東', '東北東', '東', '東南東', '南東', '南南東', '南', '南南西', '南西', '西南西', '西', '西北西', '北西', '北北西', '北']
        if td[9].text.encode('utf-8') in directions:
            degree = math.pi * directions.index(td[9].text.encode('utf-8')) / 8
            result[date]['input'].append(math.cos(degree) * float(td[8].text))
            result[date]['input'].append(math.sin(degree) * float(td[8].text))
        else:
            result[date]['input'].append(0)
            result[date]['input'].append(0)

        cloud = int(re.search(r'\d+', td[15].text).group())
        result[date]['input'].append(cloud)
        result[date]['input'].append(float(td[16].text))
        result[date]['result']= re.search(r'[^/]+\.gif', td[14].find('img').get('src')).group().encode('utf-8')

    return result

def load(start = None, end = None):
    if not start:
        start = datetime.datetime(1990, 1, 1)
    if not end:
        end = datetime.datetime(2013, 1, 1)

    data = {}
    while start < end:
        print start
        html = open(os.path.join('data', '%04d' % start.year, '%s.html' % start.strftime('%Y-%m-%d'))).read()
        res = parseHTML(html)
        data = dict(data.items() + res.items())
        start += datetime.timedelta(days = 1)
    return data

if __name__ == '__main__':
    data = eval(open(os.path.join('data', 'data')).read())
    testdata = eval(open(os.path.join('data', 'testdata')).read())

    #forecast = Forecast(data, testdata, scale = [7.0, 10.0, 2.0, 12.0, 5.0, 8.0, 16.0, 5.0, 6.0, 8.0, 1, 11.0, 3.0])
    #forecast = Forecast(data, testdata, scale = [42.0, 30.0, 0.0, 108.0, 60.0, 56.0, 144.0, 70.0, 42.0, 128.0, 20.0, 220.0, 36.0])
    #print forecast.annealing([(0, 20) for i in range(len(testdata.values()[0]['input']))], trial = 30)

    scale = dict([(-1 * i, []) for i in range(5)])
    veclen = len(testdata.values()[0]['input'])

    try:
        for vector in eval(open('../output').read()):
            forecast = Forecast(data, testdata, scale = vector)
            result = forecast.validation(trial = 100)

            if result in scale:
                scale[result].append(vector)
            elif sorted(scale.keys(), reverse = True)[-1] < result:
                del scale[sorted(scale.keys(), reverse = True)[-1]]
                scale[result] = [vector]
            print vector, result
    except:
        pass

    print scale
