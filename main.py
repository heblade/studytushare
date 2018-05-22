import tushare as ts
import time
import pandas as pd
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import datetime
from matplotlib.pylab import date2num
import sys
import numpy as np

def getprofitreport():
    profitreport = "./output/profit_%d_%d.csv"
    outreport = "./output/profitcontinuous.csv"
    year = 2015
    quarter = 4

    dflist = []
    for i in range(3):
        report = profitreport % (year, quarter)
        if os.path.exists(report):
            print("Get data from csv")
            dfsingle = pd.read_csv(report, encoding="ANSI")
        else:
            print("Get data from internet")
            try:
                dfsingle = ts.get_report_data(year=year, quarter=quarter)
                dfsingle["period"] = "%d_%d" % (year, quarter)
            except Exception as e:
                dfsingle = ts.get_report_data(year=year, quarter=quarter-1)
                dfsingle["period"] = "%d_%d" % (year, quarter-1)
            dfsingle.to_csv(report)
        dflist.append(dfsingle)
        year += 1

    dfall = pd.concat(dflist)
    dfposprofit = pd.DataFrame(dfall[(dfall["net_profits"] > 0)
                                & (dfall["profits_yoy"] > 0)])
    result = dfposprofit.groupby(["code","name"]).size().reset_index()
    print(result.columns)
    result.columns = ["code", "name", "poscontinue"]
    print(result)
    result = pd.DataFrame(result[(result["poscontinue"] >= 3)],
                          columns=["code", "name"]).drop_duplicates()
    print(result)
    result.to_csv(outreport, index=False)


def getlowpricestocks():
    wholestockfile = "./output/all_%s.csv" % (time.strftime('%Y-%m-%d',time.localtime(time.time())))
    lowpricestockfile = "./output/lowprice_%s.csv" % (time.strftime('%Y-%m-%d', time.localtime(time.time())))
    industryfile = "./output/industry_%s.csv" % (time.strftime('%Y-%m-%d', time.localtime(time.time())))
    if os.path.exists(wholestockfile):
        print("Get data from csv")
        dfall = pd.read_csv(wholestockfile, encoding="ANSI")
        dfindustry = pd.read_csv(industryfile, encoding="ANSI")
    else:
        print("Get data from internet")
        dfall = ts.get_today_all()
        dfall.to_csv(wholestockfile, index=False)
        dfindustry = ts.get_industry_classified()
        dfindustry.to_csv(industryfile, index=False)
    #print(dfall)
    #df2buy = pd.DataFrame(dfall[(dfall["trade"] < 7) & (dfall["trade"] > 0) & (dfall["pb"] < 1.5)])
    print("Get data which 0< PB <= 1.5 and 0 < PE < 30")
    df2buy = pd.DataFrame(dfall[(dfall["pb"] <= 1.5)
                                & (dfall["pb"] > 0)
                                & (dfall["per"] > 0)
                                & (dfall["per"] < 30)])
    #print(dfindustry)
    dfmerge = pd.merge(df2buy, dfindustry, on=['code','name'], how='left')
    #print(dfmerge)
    print("Output to csv")
    dfmerge.to_csv(lowpricestockfile, index=False)
    print(dfmerge)

    dfgroup = dfmerge.groupby("c_name").size()
    print(dfgroup)
    dfgroup.plot(kind="bar")
    chinese = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simhei.ttf')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    #plt.xlabel("c_name",fontproperties=chinese)
    plt.show()

def date_to_num(dates):
    num_time = []
    for date in dates:
        date_time = datetime.datetime.strptime(date,'%Y-%m-%d')
        num_date = date2num(date_time)
        num_time.append(num_date)
    return num_time

def getcandlechart(code):
    # date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    # realmarket = ts.get_k_data(code=code, start="2018-05-02")
    # print(realmarket)
    shyh = ts.get_k_data(code)
    mat_shyh = shyh.as_matrix()
    num_time = date_to_num(mat_shyh[:,0])
    mat_shyh[:,0]=num_time
    #print(mat_shyh[:3])
    fig, ax = plt.subplots(figsize=(10,5))
    fig.subplots_adjust(bottom=0.5)
    mpf.candlestick_ochl(ax, mat_shyh,width=0.6, colorup="r", colordown="g", alpha=1.0)
    chinese = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simhei.ttf')
    plt.grid(True)
    plt.xticks(rotation=30)
    #plt.title(getstockinfo(code))
    plt.title(getstockinfo(code), fontproperties=chinese)
    plt.xlabel("Date")
    plt.ylabel("Price")
    ax.xaxis_date()
    plt.show()

def statisticsfordayofweek(code):
    marketdata = ts.get_k_data(code)
    for index, row in marketdata.iterrows():
        marketdata.loc[index, 'dayofweek'] = time.strftime('%A', time.strptime(row.date, "%Y-%m-%d"))

    downdata = marketdata[((marketdata.close - marketdata.open)/marketdata.open) > 0.005]
    print(downdata.head())
    dayweekgroup = downdata['dayofweek'].groupby(
        downdata['dayofweek'].map(lambda  x: x[0:4]))\
        .count()
    print(dayweekgroup)
    dayweekgroup.plot(kind="bar")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.title(u'Rise over 0.5%', fontsize=17)
    plt.show()


def getstockinfo(code):
    industryfile = "./output/all_2018-03-30.csv"
    dfindustry = pd.read_csv(industryfile, encoding="ANSI")
    for stockinfo in dfindustry[dfindustry["code"] == int(code)].values:
        return "%s, %s" % (stockinfo[0], stockinfo[1])



if __name__ == "__main__":
    # getcandlechart("600036")
    #getlowpricestocks()
    if len(sys.argv) > 1 and sys.argv[1] != None and getstockinfo(sys.argv[1]) != None:
        getcandlechart(sys.argv[1])
    else:
        # getlowpricestocks()
        # getprofitreport()
        # statisticsfordayofweek('sh')
        getlowpricestocks()