#-*- coding:utf-8 -*-
from huobi_trade_api import *
from tools import *

class hb_trade(object):

    def __init__(self, access_key, secret_key):
        self.trade = HuobiData(huobi_access_key=access_key, huobi_secret_key=secret_key)

    #买入币
    def order_value(self, code, money):  #按金额市价买入币,有最小量的限制
        result_json = {}
        amount_precision = int(self.trade.vpair.loc[HB(code), 'amount-precision'])  #的到币的数量精度
        price_precision = int(self.trade.vpair.loc[HB(code), 'price-precision'])  #获取价格精度 0.004351个usdt买一个TRX
        order_id = self.trade.buy_order(code=code, amount=money)  #用现金市价买入币
        usdt = self.trade.get_amount_valuation('USD')
        btc = self.trade.get_amount_valuation('BTC')  #获取账号市值，纯粹延时等待成交
        print('btc=' + str(usdt), 'btc=' + btc)
        if order_id:  #成功获取到成交单号, None是订单不成功
            ord_info = self.trade.find_order(order_id)
            print('ord=', ord_info)
            real_fees = self.trade.get_real_fees(order_id)  #得到真实的扣费，有点卡的时候扣点卡了，不扣本币的费
            cj_amount = float(ord_info['field-amount'])  #得到成交量，就是成交回报的成交量
            amount = ord_info['amount']
            field_amount = cut_float(cj_amount - real_fees, amount_precision)  #买到的真实数量(扣手续费) cut_float取小数，能少不多取
            avg_price = round(float(amount) / field_amount, price_precision)  #此单的平均价格,手续费也算进去了
            print('单号:' + order_id + ' 成交数量:' + str(field_amount) + ' 平均价格:' + str(avg_price))
            result_json['单号'] = order_id
            result_json['成交数量'] = field_amount
            result_json['成交金额'] = amount
            result_json['扣手续费'] = real_fees
            result_json['平均价格'] = avg_price
            return result_json
        else:
            print('买入订单产生失败')
            return result_json

    #卖出币
    def order_target(self, code, clear_amount=0, fee=0.002):  #市价卖单：  把股票清空卖出 (火币留0.002做手续费,如果不开点卡抵扣，交易费是从这个交易币中扣的)
        result_json = {}
        price_precision = int(self.trade.vpair.loc[HB(code), 'price-precision'])  #获取价格精度 0.004351个usdt买一个TRX
        order_id = self.trade.sell_order(code=code, amount=clear_amount)  #市价全部卖出，减一点，防止误差，否则订单会失败
        usdt = self.trade.get_amount_valuation('USD')
        btc = self.trade.get_amount_valuation('BTC')  #获取账号市值，纯粹延时等待成交
        print(usdt, btc)
        print(f'{code} 市价卖单委托单号:{order_id}')
        if order_id:  #成功获取到成交单号, None是订单不成功
            ord = self.trade.find_order(order_id)
            real_fees = self.trade.get_real_fees(order_id)  #得到真实的扣费，无点卡扣usdt, 有点卡的时候扣点卡了，
            cash_amount = float(ord['field-cash-amount'])  #委托下单卖出的金额
            field_amount = float(ord['field-amount'])
            avg_price = round((cash_amount + real_fees) / field_amount, price_precision)  #(卖出的金额+费)/实际成交的币数量=平均成交价格
            print(f'成交回报：卖出成交数量{field_amount}  成交金额{cash_amount}  扣手续费{real_fees}   加扣费后均价{avg_price} ')
            result_json['单号'] = order_id
            result_json['成交数量'] = field_amount
            result_json['成交金额'] = cash_amount
            result_json['扣手续费'] = real_fees
            result_json['平均价格'] = avg_price
            return result_json
        else:
            print('卖出订单产生失败')
            return result_json

if __name__ == '__main__':
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

    amount = huobi_trade.get_amount(coin_code)                  #查询btc的数量
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