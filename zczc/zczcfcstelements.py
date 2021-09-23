#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: zczcfcstelements.py

'''
Created on Apr 6, 2021

@author: anduin
'''
import datetime

from logmodule.loglib import *

class ZczcFcstElements:
    def __init__(self,forecast_time):
        """
        初始化预报物理量
        """
        self.forecast_time = forecast_time
        self.tem = '999.9'
        self.relative_humidity = '999.9'
        self.win_d = '999.9'
        self.win_s = '999.9'
        self.air_pressure = '999.9'
        self.precipitation = '999.9'
        self.total_cloud = '999.9'
        self.low_cloud = '999.9'
        self.weather_phenomena = '999.9'
        self.visibility = '999.9'
        self.tem_max = '999.9'
        self.tem_min = '999.9'
        self.relative_humidity_max = '999.9'
        self.relative_humidity_min = '999.9'
        self.total_precipitation_24h = '999.9'
        self.total_precipitation_12h = '999.9'
        self.total_cloud_12h = '999.9'
        self.low_cloud_12h = '999.9'
        self.weather_phenomena_12h = '999.9'
        self.win_d_12h = '999.9'
        self.win_s_12h = '999.9'


if __name__ == '__main__':

    print('test done')


