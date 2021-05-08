# 火币网交易接口的简单封装
提供火币网交易接口的python封装，提供买入、卖出、查询账户余额等接口

### 接口说明
* order_value() 进行买入操作，参数为买入的币和买入的金额  
买入返回的详情数据:  
{'单号': '272229546125038', '成交数量': 0.000177, '成交金额': '10.000000', '扣手续费': 3.56240360358, '平均价格': 56497.18}
* order_target() 进行卖出操作，参数为卖出的币和卖出的金额  
卖出返回的详情数据:  
{'单号': '272229722396768', '成交数量': 0.000177, '成交金额': 9.93279219, '扣手续费': 0.01986558438, '平均价格': 56229.7}
* get_amount() 获取币的账户余额

* 最简单的例子 (trade_app.py)
  btc的买入和卖出，以及查询账户余额

```python

#自己的火币账户的access_key, secret_key (火币每个主账号能创建200个子账号，尽量使用子账号操作,防范风险)
access_key = 'XXXXXXXXXXXXXXXXXXXX'
secret_key = 'XXXXXXXXXXXXXXXXXXXXXXX'

trade = hb_trade(access_key, secret_key)               #初始化交易类
coin_code = 'btc.usdt'                                 #定义交易对  
init_money = 1000.00                                   #买入金额(单位:usdt)
buy_json = trade.order_value(coin_code, init_money)    #用1000USDT 买入btc   

#  buy_json 返回字典类型，买入成交回报：
# {'单号':'2722295','成交数量':0.000177,'成交金额':'10.0000','扣手续费':3.562403,'平均价格':56497.18}


amount = trade.get_amount(coin_code)                   #查询买到btc的数量
print('当前账户%s数量:' % (coin_code) + str(amount))    
sell_json = trade.order_target(coin_code, amount)      #卖出当前持仓所有btc

# sell_json 返回字典类型，卖出成交回报：
# {'单号':'2722297','成交数量': 0.000177,'成交金额': 9.9327,'扣手续费':0.019865,'平均价格': 56229.7}
```



## 需安装第三方库
* requests
* pandas
 

----------------------------------------------------
### 巴特量化
* 数字货币 股市量化工具 行情系统软件开发

* BTC虚拟货币量化交易策略开发 自动化交易策略运行

----------------------------------------------------

![加入群聊](https://github.com/mpquant/huobi_intf/blob/main/img/qrcode.png) 

