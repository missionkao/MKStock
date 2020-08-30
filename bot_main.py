import re
from utility import Utility
import csv
import pandas as pd
from fugle_realtime import intraday
import time
import os
from send_message import TelegramSender


def parse_csv(csv_file):
    with open(csv_file, newline='') as csvfile:
        rows = csv.reader(csvfile)

        stocks = []
        for index, row in enumerate(rows):
            if index == 0:
                continue
            sid = re.search(r'[0-9]\w+', row[0]).group()
            if sid[0] == "0":
                continue

            name = row[1]
            last_day_high = Utility.str_to_float(row[4])
            last_day_low = Utility.str_to_float(row[5])
            last_day_closing = Utility.str_to_float(row[3])
            last_day_5ma = Utility.str_to_float(row[7])
            last_day_10ma = Utility.str_to_float(row[8])
            last_day_20ma = Utility.str_to_float(row[9])
            last_day_volume = Utility.volume_to_float(row[6])

            all_ma = [last_day_5ma, last_day_10ma, last_day_20ma]

            # 漲停價也不會高於均價 continue
            today_limit = last_day_closing * 1.1
            if today_limit < max(all_ma):
                continue

            # 要漲超過 8% 才能高於均價 (當沖不追高)
            if last_day_closing * 1.08 < max(all_ma):
                continue

            # 最低價還沒掉破均線
            if last_day_low > min(all_ma):
                continue
            # 昨日已升破均線
            if last_day_high > max(all_ma):
                continue
            # 成交量太小
            if last_day_volume < 1000:
                continue
            # 距離 max(all_ma) 還需要漲幾%
            distance = ((max(all_ma) / last_day_closing) - 1) * 100.0
            distance_str = "{:.2f}".format(distance)
            stock = [sid, name, last_day_closing,
                     last_day_5ma, last_day_10ma, last_day_20ma, distance_str]
            stocks.append(stock)

        return stocks


twse_list = parse_csv("twse.csv")
tpex_list = parse_csv("tpex.csv")

stocks = twse_list + tpex_list

print("Total twse stock: {}".format(len(twse_list)))
print("Total tpex stock: {}".format(len(tpex_list)))

columns_name = ["sid", "name", "close",
                "5ma", "10ma", "20ma", "distance"]
pd.set_option('display.max_rows', None)
df = pd.DataFrame(stocks, columns=columns_name)

print(df)

FUGLE_API_TOKEN = os.environ.get('FUGLE_API_TOKEN')
sender = TelegramSender()

buy_list = []

while True:
    for index, row in df.iterrows():
        time.sleep(1.2)
        sid = df.at[index, 'sid']
        name = df.at[index, 'name']
        ma_5 = df.at[index, '5ma']
        ma_10 = df.at[index, '10ma']
        ma_20 = df.at[index, '20ma']

        try:
            print("Checking {} {}".format(sid, name))
            stock_df = intraday.chart(symbolId=sid, apiToken=FUGLE_API_TOKEN)
            price = stock_df['close'].values[-1]
            if price > max([ma_5, ma_10, ma_20]):
                if sid not in buy_list:
                    buy_list.append(sid)
                    text = "突破均線糾結: {} {} price now: {}".format(sid, name, price)
                    sender.send_message(text)

        except KeyError:
            print("An error occur: {} {}".format(sid, name))
            continue
