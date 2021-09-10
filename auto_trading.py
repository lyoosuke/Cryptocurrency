from coincheck import Coincheck
import time
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import schedule
from collections import deque

access_key = "＊＊＊＊＊＊＊＊"
secret_key = "＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊"

coincheck = Coincheck(access_key, secret_key)

btc_rate = deque([])
flag = [-1]
URL_rate_ = 'https://coincheck.com/api/rate/'
path_orders = '/api/exchange/orders'
def job():
	#キューに1分毎の終値を格納していく
	rate = requests.get(URL_rate_+"btc_jpy").json()
	rate = rate['rate']
	btc_rate.append(rate)
	#print(btc_rate)
	if len(btc_rate)>=27:
		btc_rate.popleft()
	#print(btc_rate[0])

	macd = pd.DataFrame({'close':btc_rate})
	#格納した終値からmacdを計算する
	macd['ema_12'] = macd['close'].ewm(span=12).mean()
	macd['ema_26'] = macd['close'].ewm(span=26).mean()
	macd['macd'] = macd['ema_12'] - macd['ema_26']
	macd['signal'] = macd['macd'].ewm(span=9).mean()
	#print(macd)
	if len(macd)==25:
		A = macd['macd'][24]
		B = macd['signal'][24]
		if A>=B:
			flag[0] = 1
		else:
			flag[0] = 0
	if len(macd)==26:
		A = macd['macd'][25]
		B = macd['signal'][25]
		if flag[0] == 1 and A<=B:
			#MACDが売りシグナルで売り注文
			flag[0] = 0
			params = {
				"pair": "btc_jpy",
    			"order_type": "market_sell",
    			"amount": 0.04,
			}
			orders = coincheck.post(path_orders, params)
			print(orders)
			print()
		elif flag[0] == 0 and A>=B:
			#MACDが買いシグナルで買い注文
			flag[0] = 1
			
			params = {
				"pair": "btc_jpy",
    			"order_type": "market_buy",
    			"market_buy_amount": 152000,
			}
			orders = coincheck.post(path_orders, params)
			print(orders)
			print()

schedule.every(2).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

