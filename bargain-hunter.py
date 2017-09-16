#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import sys
import urllib2
import time

fee = 0.002

ma1_size = 5 # 第一根均线，快线
ma2_size = 30 # 第二根均线，慢线

market = sys.argv[1]
step = (int)(eval(sys.argv[2]) * 60)
start_time = long(sys.argv[3])
end_time = long(sys.argv[4])

opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
f = opener.open('https://k.sosobtc.com/data/period?symbol=' + market + '&step=' + str(step))
k = f.readline()

sticks = json.loads(k)

times = []
opens = dict()
highs = dict()
lows = dict()
closes = dict()

for stick in sticks:
    times.append(stick[0])
    opens[stick[0]] = stick[1]
    highs[stick[0]] = stick[2]
    lows[stick[0]] = stick[3]
    closes[stick[0]] = stick[4]

ma1_line = dict()
ma2_line = dict()
for i in range(len(times)):
    ma1_len = ma1_size
    if i + 1 < ma1_size:
        ma1_len = i + 1

    ma1 = 0
    for j in range(ma1_len):
        t = times[i - j]
        ma1 += closes[t]

    ma1 = ma1 / ma1_len
    ma1_line[times[i]] = ma1

    ma2_len = ma2_size
    if i + 1 < ma2_size:
        ma2_len = i + 1

    ma2 = 0
    for j in range(ma2_len):
        t = times[i - j]
        ma2 += closes[t]

    ma2 = ma2 / ma2_len
    ma2_line[times[i]] = ma2

init_asset = 10000 # 初始资金10000
asset = init_asset

cny = init_asset
coins = 0

asset_quotas = 7 # 资金分成10份进行抄底，可修改
asset_unit = init_asset / asset_quotas # 每次抄底使用资金

for i in range(len(times)):
    if i == 0:
        continue

    pt = times[i - 1]
#    pt = times[i]
    ct = times[i]
    if ct < start_time:
        continue

    if ct > end_time:
        break

    if ct not in ma1_line.keys():
        continue

    latest_price = closes[pt]

    lt = time.localtime(ct)
    str_time = time.strftime('%Y-%m-%d', lt)

#    buy_price = (highs[ct] + closes[ct]) / 2
#    sp = (lows[ct] + closes[ct]) / 2
    buy_price = opens[ct]

    if ma1_line[pt] < ma2_line[pt] and ma1_line[ct] > ma2_line[ct] and cny > 0: # ma1 上穿 ma2
        if cny > 0:
            coins += asset_unit / buy_price
            cny -= asset_unit

            print(str_time + ": 开仓买入，买入价格:" + str(buy_price) + ", 使用资金: " + str(asset_unit))

ct = times[len(times) - 1]
latest_price = closes[ct]
asset = cny + coins * latest_price

print('\n最新价格: ' + str(latest_price) + ', 初始资产: ' + str(init_asset) + ', 最终资产: ' + str(asset))
