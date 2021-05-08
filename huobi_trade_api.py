#-*- coding:utf-8 -*-
import requests
import datetime
import hmac
import hashlib
import base64
import json
import random
from urllib import parse
import pandas as pd
from tools import *
from requests.adapters import HTTPAdapter


class HuobiData(object):

    huobi_api_domain = 'api.huobi.pro'  #交易接口域名

    def __init__(self, huobi_access_key, huobi_secret_key):
        self.huobi_access_key = huobi_access_key
        self.huobi_secret_key = huobi_secret_key
        self.vpair = self.get_symbols()
        self.huobi_account_id = self.get_api_user_info()[0]['id']    #根据token获取实际交易account_id

    #手动更新精度信息
    def update_vpair(self):
        self.vpair = self.get_symbols()

    def api_signature(self, method, param, url_path):  # 对请求参数进行签名，返回含签名的完整请求URL
        timestamp = parse.quote(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))  # 创建时间戳
        default_param = {
            'AccessKeyId': self.huobi_access_key,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Timestamp': timestamp
        }
        if method == 'GET': default_param.update(param)
        sorted_param = dict(
            sorted(default_param.items(), key=lambda d: d[0], reverse=False))  # 对字典的排序，按key已ascii码排序
        url_param = ''
        a = 0
        for param_key, param_value in sorted_param.items():  # 循环param字典拼接请求参数
            a += 1
            url_param = url_param + '%s=%s' % (param_key, param_value)
            if a < len(sorted_param):
                url_param = url_param + '&'  # 如果循环次数少于字典长度则在后面加连接符&

        need_secret_string = '%s\n%s\n%s\n%s' % (
            method, self.huobi_api_domain, url_path, url_param
        )  # 拼接需要进行签名计算的字符串
        need_secret_string_encode = need_secret_string.encode(encoding='UTF8')  # 生成签名加密字符串  调整字符串编码
        huobi_secret_key_encode = self.huobi_secret_key.encode(encoding='UTF8')
        secret_string = hmac.new(
            huobi_secret_key_encode,
            need_secret_string_encode,
            digestmod=hashlib.sha256).digest()  # 进行加密计算 并 签名
        signature = base64.b64encode(secret_string)
        signature = signature.decode()
        signature = parse.quote(signature)  # 签名
        url_param = url_param + f'&Signature={signature}'  # 把签名字符串拼接到请求url
        url = f'https://{self.huobi_api_domain}{url_path}?{url_param}'  # 拼接出最终完整url
        return url

    def request_api(self,
                    method='GET',
                    url_path='/v1/account/accounts',
                    param={}):  # 以GET或POST请求API（签名验证的形式）返回结果的字典格式
        url = self.api_signature(method, param, url_path)  # 把请求参数进行签名，获得含有签名的完整请求URL
        try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=3))
            s.mount('https://', HTTPAdapter(max_retries=3))
            s.keep_alive = False  # 关闭多余连接
            r = None
            if method == 'GET': 
                r = s.get(url)
            if method == 'POST':
                r = s.post(url,
                           data=json.dumps(param),
                           headers={'Content-Type': 'application/json'})
            request_dict = json.loads(r.text)
            data = request_dict['data']
            if 'status' in request_dict.keys():
                status = request_dict['status']
                if status != 'ok':
                    err_code = request_dict['err-code']
                    err_msg = request_dict['err-msg']
                    print(url_path, err_code, err_msg)
            return data  # 消息成功发送，返回
        except Exception as e:
            print(repr(e))
            return []  #出错返回空，以便len(res)

    def get_symbols(self, TradePair=[]):  #获取交易对精度信息，只获取TradePair内的值
        try:
            ret = requests.get(f"https://{self.huobi_api_domain}/v1/common/symbols")
            #正式网址  国内"https://api.huobi.de.com/v1/common/symbols"
        except:
            return None
        ret = json.loads(ret.text)['data']
        TradePair = [x.replace('.', '') for x in TradePair]
        df = pd.DataFrame(ret,
                          columns=[
                              'symbol', 'quote-currency', 'price-precision',
                              'amount-precision', 'value-precision',
                              'min-order-value', 'sell-market-min-order-amt'
                          ])
        df = df[df['quote-currency'].isin(['btc', 'usdt'])]
        df.set_index('symbol', inplace=True)
        df.index.name = ''
        if TradePair: 
            df = df[df.index.isin(TradePair)]
        return df  #  购买金额精度 df.loc['btcusdt','value-precision']    卖出币数量精度df.loc['btcusdt','amount-precision']

    def get_api_user_info(self):  # 先获取获取账号信息 UID不是账号，账号是 pot：现货账户， margin：逐仓杠杆账户，otc：OTC 账户
        url_path = '/v1/account/accounts'
        return self.request_api('GET', url_path, param={})  # 请求接口

    def get_api_user_balance(self):  # 获取账号余额
        account_id = self.huobi_account_id 
        url_path = f'/v1/account/accounts/{account_id}/balance'
        param = {
            'account-id': self.huobi_account_id,
        }
        return self.request_api('GET', url_path, param)

    def get_algo_order(self):  # 策略委托
        url_path = '/v2/algo-orders/opening'
        return self.request_api('GET', url_path, param={})

    # 现货买单委托    amount订单交易金额（市价买单为订单交易额）  price订单价格（对市价单无效）
    def buy_order(self,
                  accountID='',
                  code='btc.usdt',
                  types="buy-market",
                  amount=1,
                  price='0',
                  source='spot-api'):
        url_path = '/v1/order/orders/place'
        code = code.replace('.', '')
        orderid = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + str(random.randint(100000, 999999))  #'20210221-172007-657483'
        amount = cut_float(amount, self.vpair.loc[code, 'value-precision'])  #根据交易额精度数据修正交易额 买入25.1234元(usdt)的币 保留8位小数
        param = {
            'account-id': self.huobi_account_id,
            'symbol': code,
            'type': types,
            'amount': str(amount),
            'price': price,
            'source': source,
            'client-order-id': orderid
        }
        order_id = self.request_api('POST', url_path, param=param)
        return order_id

    # 现货卖单,市价卖出币的数量,  price订单价格（对市价单无效）
    def sell_order(self,
                   accountID='',
                   code='btc.usdt',
                   types="sell-market",
                   amount=1,
                   price='0',
                   source='spot-api'):
        url_path = '/v1/order/orders/place'
        code = code.replace('.', '')
        orderid = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + str(random.randint(100000, 999999))  #'20210221-172007-657483'
        amount = cut_float(amount, self.vpair.loc[code, 'amount-precision'])  #根据交易量的精度 修正交易数量，卖出12.5721个ada 保留n位小数
        param = {
            'account-id': self.huobi_account_id,
            'symbol': code,
            'type': types,
            'amount': str(amount),
            'price': price,
            'source': source,
            'client-order-id': orderid
        }
        order_id = self.request_api('POST', url_path, param=param)
        return order_id

    # 撤单
    def cancel_order(self, order_id):
        url_path = f'/v1/order/orders/{order_id}/submitcancel'
        param = {'order-id': order_id}
        return self.request_api('POST', url_path, param=param)

    #查询当前未成交订单:   输入交易对，返回一个list，里面是字典结构的订单详情
    def check_open_order(self, code='btc.usdt'):
        url_path = f'/v1/order/openOrders'
        code = code.replace('.', '')
        param = {'account-id': self.huobi_account_id, 'symbol': code}
        return self.request_api('GET', url_path, param=param)

    #查询订单详情 :       输入订单id，返回一个list，里面是字典结构的订单详情
    def find_order(self, order_id):
        url_path = f'/v1/order/orders/{order_id}'
        param = {'order-id': order_id}
        return self.request_api('GET', url_path, param=param)

    # 获取成交明细, 返回一个list，里面是字典结构的成交详情,   市价单可能会被拆成多个订单，所以返回的是一个list
    def get_order_details(self, order_id):
        url_path = f'/v1/order/orders/{order_id}/matchresults'
        param = {'order-id': order_id}
        return self.request_api('GET', url_path, param=param)

    #根据成交明细获取真实扣费情况，算是对get_order_details的功能包装 2021-3-28
    def get_real_fees(self, order_id):  # 买币eos.usdt：如果无点卡，返回扣的eos费数量(0.2%)  有点卡返回0
        ks = self.get_order_details(order_id)
        fee = 0  # 卖币eos.udt: 如果无点卡，返回扣的usdt费数量(0.2%) 有点卡返回0
        if not ks: return 0  # 明细获取出错，直接返回0
        for k in ks:
            fee = fee + float(k['filled-fees'])
        return fee

    # 获取账户估值, 按照BTC或法币计价单位，获取指定账户的总资产估值
    def get_amount_valuation(self, currency='USD'):  # 可选BTC,CNY,USD
        url_path = f'/v2/account/asset-valuation'
        param = {'accountType': 'spot', 'valuationCurrency': currency}
        data = self.request_api('GET', url_path, param=param)
        balance = 0
        if data != None:
            balance = data['balance']
        return balance

    #策略委托市价下单,火币网一个子账号最多下99个策略单，能创建200个子账号
    #orderValue：按金额下单   （orderSize按币数量下单,市价单时无效)
    def set_algo_order(self,
                       accountID='',
                       code='btc.usdt',
                       orderSide='buy',
                       orderValue='0',
                       stopPrice='0'):
        url_path = '/v2/algo-orders'
        code = code.replace('.', '')
        orderid = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + str(random.randint(100000, 999999))  # '20210221-172007-657483'
        param = {
            'accountId': self.huobi_account_id,
            'symbol': code,
            'orderSide': 'buy',
            'orderValue': orderValue,
            'orderType': 'market',
            'stopPrice': stopPrice,
            'clientOrderId': orderid
        }
        return self.request_api('POST', url_path, param=param)

    # 策略委托撤单 (传来的单号 clientOrderIds必须是个列表，不能是字符串)
    def cancel_algo_order(self, clientOrderIds):
        url_path = f'/v2/algo-orders/cancellation'
        param = {
            'clientOrderIds': clientOrderIds
        }  #clientOrderIds必须是列表，最多列表50个，最多撤50个
        return self.request_api('POST', url_path, param=param)

    #查询币的数量
    def get_amount(self, coin_code):
        clear_amount = self.get_balance(split_code(coin_code))
        amount_precision = int(self.vpair.loc[HB(coin_code), 'amount-precision'])  #的到币的数量精度
        amount = cut_float(clear_amount, amount_precision)
        return amount

    #查询某个币的余额
    def get_balance(self, coin):
        count = 0
        df = pd.DataFrame()
        balance = self.get_api_user_balance()  #是现货账户id ，不是uid
        if balance != None:
            ks = json.dumps(balance['list'])
            df = pd.read_json(ks, orient='records')
            df_coin = df[(df.balance > 0.0001) & (df.currency == coin)]
            if (not df_coin.empty) and (len(df_coin) > 0):
                count = df_coin['balance'].values[0] 
        return count
