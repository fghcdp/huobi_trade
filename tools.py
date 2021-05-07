# coding: utf-8 ----------------------------工具库---------------------------------------
import os,sys,time,datetime,json,copy,math;     import pandas as pd; import numpy as np   

def HK(n,k=3):                   #把小数规整到3位，好看   
    return round(n, k)         

def pct(v,k=2):                  #获取百分比,2位小数
    return round(v*100-100, k)   

def cut_float(v, precision):    #根据精度舍弃精度后面的位数，不进行四舍五入，宁可少，不能多 2021-3-10
    ret = int(v*pow(10,precision))/pow(10,precision)
    #精度为0
    if precision == 0:
        ret = int(v)
    return ret   #买了2.058个币(火币买入数量不是按精度来的)， round后成2.06,卖出肯定出

#得到yyyy-mm-dd hh:ss:nn格式的字符串
def fmt_now_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

def float_to_str(float_num, rate=1):  #float_num 为浮点数，输出不带科学计数法的长字符串
    fstr = str(float_num * rate)
    flen = len(str(float_num))  #rate是直接扣掉手续费
    if not 'e' in fstr: return fstr[:flen]
    ws = int(fstr[-3:])
    ks = '0' * (abs(ws) - 1)
    tn = fstr[:-4].replace('.', '')
    return '0.' + ks + tn if ws < 0 else (tn + ws * '0')[:ws + 1]

#---------------------------------------下面是具体功能函数--------------------------------------------------------------

def HB(code):
    return code.replace('.', '')  #转换成hb代码格式

#取btc.usdt的点前边的部分
def split_code(stock):
    return stock.split('.')[0]
