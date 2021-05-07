# 火币网交易接口的简单封装
提供火币网交易接口的python封装，提供买入、卖出、查询账户余额等接口

### 接口说明
* order_value() 进行买入操作，参数为买入的币和买入的金额
 买入返回的详情数据:{'单号': '272229546125038', '成交数量': 0.000177, '成交金额': '10.000000', '扣手续费': 3.56240360358, '平均价格': 56497.18}
* order_target() 进行卖出操作，参数为卖出的币和卖出的金额
 卖出返回的详情数据:{'单号': '272229722396768', '成交数量': 0.000177, '成交金额': 9.93279219, '扣手续费': 0.01986558438, '平均价格': 56229.7}
* get_amount() 获取币的账户余额

* 最简单的例子
  btc的买入和卖出，以及查询账户余额

```python
#自己的火币账户的access_key, secret_key
access_key = 'XXXXXXXXXXXXXXXXXXXX'
secret_key = 'XXXXXXXXXXXXXXXXXXXXXXX'
trade = hb_trade(access_key, secret_key)
coin_code = 'btc.usdt'
#买入金额(单位:美元)
init_money = 1000.00
#买入btc
buy_json = trade.order_value(coin_code, init_money)
#查询btc的数量
amount = trade.get_amount(coin_code)
print('当前账户%s数量:' % (coin_code) + str(amount))
#卖出btc
sell_json = trade.order_target(coin_code, amount)
```


## 需安装第三方库
* requests
* pandas
 

----------------------------------------------------
### 巴特量化(BestQuant)：数字货币 股市量化工具 行情系统软件提供商
----------------------------------------------------

![加入群聊](https://github.com/mpquant/huobi_intf/blob/main/img/qrcode.png) 

