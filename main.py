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
                dfsingle = ts.get_report_data(year=year, quarter=quarter - 1)
                dfsingle["period"] = "%d_%d" % (year, quarter - 1)
            dfsingle.to_csv(report)
        dflist.append(dfsingle)
        year += 1

    dfall = pd.concat(dflist)
    dfposprofit = pd.DataFrame(dfall[(dfall["net_profits"] > 0)
                                     & (dfall["profits_yoy"] > 0)])
    result = dfposprofit.groupby(["code", "name"]).size().reset_index()
    print(result.columns)
    result.columns = ["code", "name", "poscontinue"]
    print(result)
    result = pd.DataFrame(result[(result["poscontinue"] >= 3)],
                          columns=["code", "name"]).drop_duplicates()
    print(result)
    result.to_csv(outreport, index=False)


def getlowpricestocks():
    wholestockfile = "./output/all_%s.csv" % (time.strftime('%Y-%m-%d', time.localtime(time.time())))
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
    # print(dfall)
    # df2buy = pd.DataFrame(dfall[(dfall["trade"] < 7) & (dfall["trade"] > 0) & (dfall["pb"] < 1.5)])
    print("Get data which 0< PB <= 1.5 and 0 < PE < 30")
    df2buy = pd.DataFrame(dfall[(dfall["pb"] <= 1.5)
                                & (dfall["pb"] > 0)
                                & (dfall["per"] > 0)
                                & (dfall["per"] < 30)])
    # print(dfindustry)
    dfmerge = pd.merge(df2buy, dfindustry, on=['code', 'name'], how='left')
    # print(dfmerge)
    print("Output to csv")
    dfmerge.to_csv(lowpricestockfile, index=False)
    print(dfmerge)

    dfgroup = dfmerge.groupby("c_name").size()
    print(dfgroup)
    dfgroup.plot(kind="bar")
    chinese = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simhei.ttf')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    # plt.xlabel("c_name",fontproperties=chinese)
    plt.show()


def date_to_num(dates):
    num_time = []
    for date in dates:
        date_time = datetime.datetime.strptime(date, '%Y-%m-%d')
        num_date = date2num(date_time)
        num_time.append(num_date)
    return num_time


def getcandlechart(code):
    # date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    # realmarket = ts.get_k_data(code=code, start="2018-05-02")
    # print(realmarket)
    shyh = ts.get_k_data(code)
    print(shyh)
    mat_shyh = shyh.as_matrix()
    num_time = date_to_num(mat_shyh[:, 0])
    mat_shyh[:, 0] = num_time
    # print(mat_shyh[:3])
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(bottom=0.5)
    mpf.candlestick_ochl(ax, mat_shyh, width=0.6, colorup="r", colordown="g", alpha=1.0)
    chinese = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simhei.ttf')
    plt.grid(True)
    plt.xticks(rotation=30)
    # plt.title(getstockinfo(code))
    plt.title(getstockinfo(code), fontproperties=chinese)
    plt.xlabel("Date")
    plt.ylabel("Price")
    ax.xaxis_date()
    plt.show()


def statisticsfordayofweek(code):
    marketdata = ts.get_k_data(code)
    for index, row in marketdata.iterrows():
        marketdata.loc[index, 'dayofweek'] = time.strftime('%A', time.strptime(row.date, "%Y-%m-%d"))

    downdata = marketdata[((marketdata.close - marketdata.open) / marketdata.open) > 0.005]
    print(downdata.head())
    dayweekgroup = downdata['dayofweek'].groupby(
        downdata['dayofweek'].map(lambda x: x[0:4])) \
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
        return "%s, %s" % ('{:0>6}'.format(stockinfo[0]), stockinfo[1])


def getstockbasicinfo(needreloadbasic=False, needgettoday=False):
    filebasic = './output/stockbasic.csv'
    filetoday = './output/stocktoday.csv'
    if os.path.exists(filebasic) and not needreloadbasic:
        print("Get basic data from csv")
        dfstockbasic = pd.read_csv(filebasic, encoding="ANSI")
    else:
        print("Get basic data from internet")
        try:
            dfstockbasic = ts.get_stock_basics()
            dfstockbasic.to_csv(filebasic, encoding='ANSI')
            dfstockbasic = pd.read_csv(filebasic, encoding="ANSI")
        except Exception as e:
            print(e)
    if os.path.exists(filetoday) and not needgettoday:
        print("Get today data from csv")
        dfstocktoday = pd.read_csv(filetoday, encoding="ANSI")
    else:
        print("Get today data from internet")
        try:
            dfstocktoday = ts.get_today_all()
            dfstocktoday.to_csv(filetoday, encoding='ANSI')
        except Exception as e:
            print(e)

    # dfstockbasic['tomarket'] = pd.to_numeric(dfstockbasic.timeToMarket)
    # dfstockbasic = dfstockbasic[(dfstockbasic.tomarket <= 20180201)]
    dfstockbasic['code'] = dfstockbasic['code'].apply(str)
    for index, row in dfstockbasic.iterrows():
        dfstockbasic.loc[index, 'code'] = '{:0>6}'.format(dfstockbasic.loc[index, 'code'])
        # print(index, ' ', dfstockbasic.loc[index, 'code'])
    dfstockbasic.rename(
        columns={'code': '代码',
                 'name': '名称',
                 'industry': '所属行业',
                 'area': '地区',
                 'pe': '市盈率',
                 'outstanding': '流通股本(亿)',
                 'totals': '总股本(亿)',
                 'totalAssets': '总资产(万)',
                 'liquidAssets': '流动资产',
                 'fixedAssets': '固定资产',
                 'reserved': '公积金',
                 'reservedPerShare': '每股公积金',
                 'esp': '每股收益',
                 'bvps': '每股净资',
                 'pb': '市净率',
                 'timeToMarket': '上市日期',
                 'undp': '未分利润',
                 'perundp': '每股未分配',
                 'rev': '收入同比(%)',
                 'profit': '利润同比(%)',
                 'gpr': '毛利率(%)',
                 'npr': '净利润率(%)',
                 'holders': '股东人数'
                 }, inplace=True)
    dfstockbasic.to_excel('./output/allstockbasicinformation.xlsx', encoding='ANSI')
    return
    dfmerge['totalnessets'] = (dfmerge.totals * dfmerge.trade)

    dfbigstock = dfmerge[dfmerge.totalnessets > 400]
    print(dfbigstock)
    codes = {}
    for index, row in dfbigstock.iterrows():
        codes['{:0>6}'.format(row['code'])] = row['totalnessets']
    getcandlecharts(codes)


def getcandlecharts(codes):
    chinese = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simhei.ttf')
    plt.figure(figsize=(10, 8), facecolor='w')
    index = 1
    for code in codes:
        print(code)
        shyh = ts.get_k_data(code)
        mat_shyh = shyh.as_matrix()
        num_time = date_to_num(mat_shyh[:, 0])
        mat_shyh[:, 0] = num_time
        ax = plt.subplot(4, 4, index)
        mpf.candlestick_ochl(ax, mat_shyh, width=0.6, colorup="r", colordown="g", alpha=1.0)
        plt.grid(True)
        plt.xticks(rotation=30)
        plt.title('%s: %.2f' % (getstockinfo(code), codes[code]), fontproperties=chinese)
        plt.xlabel("Date")
        plt.ylabel("Price")
        ax.xaxis_date()
        index = index + 1
        if index == 16:
            break
    plt.suptitle('2015-10-01之后上市总市值超过400亿人民币的股票', fontproperties=chinese)
    plt.tight_layout(1.5)
    plt.subplots_adjust(top=0.92)
    plt.show()


def testdict():
    doc = {}
    doc[1] = ['234']
    doc[2] = ['22']
    doc[3] = ['78776']
    print(', '.join([str(key) for key in doc.keys()]))


if __name__ == "__main__":
    # getcandlechart("601857")
    # getlowpricestocks()
    if len(sys.argv) > 1 and sys.argv[1] != None and getstockinfo(sys.argv[1]) != None:
        getcandlechart(sys.argv[1])
    else:
    #     # getlowpricestocks()
    #     # getprofitreport()
    #     # statisticsfordayofweek('sh')
    #     # getlowpricestocks()
    #     getstockbasicinfo(needreloadbasic=True)
        testdict()