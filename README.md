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
huobi_trade = hb_trade(access_key, secret_key)              #初始化交易类

usdt_balance = huobi_trade.trade.get_balance('usdt')        #查询稳定币usdt的余额

coin_code = 'btc.usdt'                                      #定义交易对 
init_money = 10.00                                          #买入金额(单位:usdt)
buy_json = huobi_trade.order_value(coin_code, init_money)   #用1000USDT 买入btc
#  buy_json 返回字典类型，买入成交回报：
# {'单号':'2722295','成交数量':0.000177,'成交金额':'10.0000','扣手续费':3.562403,'平均价格':56497.18}

amount = huobi_trade.trade.get_amount(coin_code)            #查询btc.usdt交易对的数量,有精度控制
print('当前账户%s数量:' % (coin_code) + str(amount))

sell_json = huobi_trade.order_target(coin_code, amount)     #卖出当前持仓所有btc
# sell_json 返回字典类型，卖出成交回报：
# {'单号':'2722297','成交数量': 0.000177,'成交金额': 9.9327,'扣手续费':0.019865,'平均价格': 56229.7}

#查询当前未成交订单 入参是定义的交易对
#详细返回参数请参考 https://huobiapi.github.io/docs/spot/v1/cn/#95f2078356
open_order = huobi_trade.trade.check_open_order(coin_code)

#查询订单详情 入参是单号
#详细返回参数请参考 https://huobiapi.github.io/docs/spot/v1/cn/#92d59b6aad
find_order = huobi_trade.trade.find_order('272249503181077')

#获取成交明细 入参是单号
#详细返回参数请参考 https://huobiapi.github.io/docs/spot/v1/cn/#56c6c47284
order_details = huobi_trade.trade.get_order_details('272249503181077')

#根据成交单号获取真实扣费情况 入参是单号
real_fees = huobi_trade.trade.get_real_fees('272249503181077')
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

