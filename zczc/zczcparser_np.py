#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: zczcparser_np.py

'''
Created on Aug 21, 2021

@author: anduin
'''
import datetime
import pandas as pd
import numpy as np
from io import StringIO
import copy

from logmodule.loglib import *
from zczc.zczcpublictype import ZczcPublicType
from publictype.columnnames import ColumnNames
from publictype.conditiontypes import ConditionTypes as ct
import public

class ZCZCParser_np():
    """description of class 
    城镇报格式解码和生成
    """

    def __init__(self):
        #站点id中有的存在字符，如果保持结果中是字符，self.staid_is_str为True，否则安装一定规则转换成数值。
        self.staid_is_str = False

        self.CCCC = ''
        self.YYGGgg = ''
        self.BBB = ''

        self.product_desc = ''

        self.product_code = ''
        self.fcst_time = None
        self.fcst_time_str = None

        self.sta_count = 0

        self.fcst_data = 0

    '''
    def __readlines(self, fdata, pos, count=1, splitstr='\n', isendline=False):
        try:
            nextpos = pos
            if isendline:
                nextpos = fdata.find(splitstr, nextpos)
                if nextpos < 0:
                    return (len(fdata), fdata[pos:])
                else:
                    return (nextpos + len(splitstr), fdata[pos:nextpos])
            else:
                curpos = pos
                for i in range(count):
                    nextpos = fdata.find(splitstr, nextpos)
                    if nextpos < 0:
                        return (-1, None)

                    curpos = nextpos
                    nextpos += len(splitstr)

                return (nextpos, fdata[pos:curpos])
        except Exception as data:
            LogLib.logger.error('ZCZCParser __readlines except %s %s' % (str(data), fdata))

            return (-1, None)
        '''
    def __parse_fileid(self, dl):
        try:
            if dl == ZczcPublicType.fileid:
                return True
            else:
                return False
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_fileid except %s %s' % (str(data), dl))

            return False

    def __parse_first_line(self, fdata):
        try:
            dl = fdata.readline().strip()
            if dl is None or dl == '':
                LogLib.logger.error('ZCZCParser __parse_first_line readlines error %s' % (fdata))
                return False

            if not self.__parse_fileid(dl):
                LogLib.logger.error('ZCZCParser __parse_first_line fileid error %s' % (fdata))
                return False
            
            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_first_line except %s %s' % (str(data), fdata))

            return False

    def __parse_TTAAii(self, dl):
        try:
            if dl == ZczcPublicType.TTAAii:
                return True
            else:
                return False
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_TTAAii except %s %s' % (str(data), dl))

            return False
        
    def __parse_CCCC(self, dl):
        try:
            if len(dl) > 0:
                self.CCCC = dl
                return True
            else:
                return False
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_CCCC except %s %s' % (str(data), dl))

            return False
        
    def __parse_YYGGgg(self, dl):
        try:
            if len(dl) == 6:
                self.YYGGgg = dl
                return True
            else:
                return False
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_YYGGgg except %s %s' % (str(data), dl))

            return False
        
    def __parse_BBB(self, dl):
        try:
            dl = dl.strip('()')
            if len(dl) == 3:
                self.BBB = dl
                return True
            else:
                return False
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_BBB except %s %s' % (str(data), dl))

            return False
        
    def __parse_second_line(self, fdata):
        try:
            dl = fdata.readline().strip()
            if dl is None or dl == '':
                LogLib.logger.error('ZCZCParser __parse_second_line readlines error %s' % (fdata))
                return False

            splitrst = dl.split()
            if len(splitrst) != 3 and len(splitrst) != 4:
                LogLib.logger.error('ZCZCParser __parse_second_line format error %s' % (fdata))
                return False

            if not self.__parse_TTAAii(splitrst[0]):
                LogLib.logger.error('ZCZCParser __parse_second_line TTAAii error %s' % (fdata))
                return False
            
            if not self.__parse_CCCC(splitrst[1]):
                LogLib.logger.error('ZCZCParser __parse_second_line CCCC error %s' % (fdata))
                return False
            
            if not self.__parse_YYGGgg(splitrst[2]):
                LogLib.logger.error('ZCZCParser __parse_second_line YYGGgg error %s' % (fdata))
                return False
            
            if len(splitrst) == 4:
                if not self.__parse_BBB(splitrst[3]):
                    LogLib.logger.error('ZCZCParser __parse_second_line BBB error %s' % (fdata))
                    return False

            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_second_line except %s %s' % (str(data), fdata))

            return False

    def __parse_product_desc(self, dl):
        try:
            self.product_desc = dl.strip()
            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_product_desc except %s %s' % (str(data), dl))

            return False
        
    def __parse_third_line(self, fdata):
        try:
            dl = fdata.readline().strip()
            if dl is None or dl == '':
                LogLib.logger.error('ZCZCParser __parse_third_line readlines error %s' % (fdata))
                return False

            if not self.__parse_product_desc(dl):
                LogLib.logger.error('ZCZCParser __parse_third_line product_desc error %s' % (fdata))
                return False
            
            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_third_line except %s %s' % (str(data), fdata))

            return False
    
    def __parse_product_code(self, dl):
        try:
            self.product_code = dl.strip()
            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_product_code except %s %s' % (str(data), dl))

            return False
        
    def __parse_fcst_time(self, dl):
        try:
            self.fcst_time_str = dl.strip()
            self.fcst_time = datetime.datetime.strptime(self.fcst_time_str, ZczcPublicType.fcst_time_fmt)

            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_fcst_time except %s %s' % (str(data), dl))

            return False
        
    def __parse_fourth_line(self, fdata):
        try:
            dl = fdata.readline().strip()
            if dl is None or dl == '':
                LogLib.logger.error('ZCZCParser __parse_fourth_line readlines error %s' % (fdata))
                return False
            
            splitrst = dl.split()
            if len(splitrst) != 2:
                LogLib.logger.error('ZCZCParser __parse_fourth_line format error %s' % (fdata))
                return False

            if not self.__parse_product_code(splitrst[0]):
                LogLib.logger.error('ZCZCParser __parse_fourth_line product_code error %s' % (fdata))
                return False

            if not self.__parse_fcst_time(splitrst[1]):
                LogLib.logger.error('ZCZCParser __parse_fourth_line fcst_time error %s' % (fdata))
                return False

            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_fourth_line except %s %s' % (str(data), fdata))

            return False
    
    def __parse_sta_count(self, dl):
        try:
            self.sta_count = int(dl.strip())

            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_sta_count except %s %s' % (str(data), dl))

            return False
        
    def __parse_fifth_line(self, fdata):
        try:
            dl = fdata.readline().strip()
            if dl is None or dl == '':
                LogLib.logger.error('ZCZCParser __parse_fifth_line readlines error %s' % (fdata))
                return False

            if not self.__parse_sta_count(dl):
                LogLib.logger.error('ZCZCParser __parse_fifth_line sta_count error %s' % (fdata))
                return False

            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_fifth_line except %s %s' % (str(data), fdata))

            return False

    def __parse_sta_infos(self, fdata):
        try:
            dl = fdata.readline().strip()
            if dl is None or dl == '':
                LogLib.logger.error('ZCZCParser __parse_sta_infos readlines error %s' % (fdata))
                return (None, None, None, None, None, None)
                
            splitrst = dl.split()
            if len(splitrst) != 6:
                LogLib.logger.error('ZCZCParser __parse_sta_infos format error %s' % (fdata))
                return (None, None, None, None, None, None)

            staid = splitrst[0] if self.staid_is_str else public.convert_sta_id_to_int(splitrst[0]) 
            return (staid, float(splitrst[1]), float(splitrst[2]), float(splitrst[3]), int(splitrst[4]), int(splitrst[5]))
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_sta_infos except %s %s' % (str(data), dl))

            return (None, None, None, None, None, None)
        
    def __parse_data(self, fdata, staids=None, columns=None, filters=None):
        try:
            self.fcst_data = None
            pdata = None

            tmpcols = copy.deepcopy(ZczcPublicType.columns) if columns is None else copy.deepcopy(columns)

            tmpdata = pd.read_csv(fdata, sep='\n', delimiter='\s+', header='infer', names=tmpcols) #, low_memory=False)
            tmpcolname = 'xxxxxxxxxxxxxxxxx'
            tmpdata[tmpcolname] = 0
            
            print(datetime.datetime.now())
            sta_info = None
            curpos = 0
            for s in range(11621):
                a = tmpdata.iloc[curpos, :6]
                '''
                if self.staid_is_str:
                    a.values[0] = str(a.values[0])
                else:
                    if type(a.values[0]) is str:
                        a.values[0] = public.convert_sta_id_to_int(a.values[0])
                        '''
                rowcount = int(a.values[4])
                adf = pd.DataFrame(np.tile(a.values[:4], rowcount).reshape((rowcount,4)), columns=[ColumnNames.StaID.value, ColumnNames.Lon.value, ColumnNames.Lat.value, ColumnNames.Alt.value])
                if sta_info is None:
                    sta_info = adf
                else:
                    sta_info = sta_info.append(adf)

                #sta_info.append(tmpdata.iloc[s * 85 + 1:s * 85 + 85, :])

            print(datetime.datetime.now())

            stainfos = []
            curpos = 0
            allline = len(tmpdata)
            while(curpos < allline):
                staid, lon, lat, alt, rowcount, columncount = tmpdata.loc[curpos][:6]
                if (type(staid) is not str and np.isnan(staid)) or np.isnan(lon) or np.isnan(lat) or np.isnan(alt) or np.isnan(rowcount) or np.isnan(columncount):
                    return False

                tmpdata.values[curpos][-1] = 1

                if self.staid_is_str:
                    staid = str(staid)
                else:
                    if type(staid) is str:
                        staid = public.convert_sta_id_to_int(staid)

                if staids is not None and staid not in staids:
                    #tmpdata.drop(index=range(curpos, curpos+rowcount+1), inplace=True)
                    continue
                #else:
                    #tmpdata.drop(index=curpos, inplace=True)
                    
                rowcount = int(rowcount)
                columncount = int(columncount)

                stainfos.append([staid, lon, lat, alt] * (rowcount+1))

                curpos += rowcount + 1
            
            stadf = pd.DataFrame(stainfos, columns=[ColumnNames.StaID.value, ColumnNames.Lon.value, ColumnNames.Lat.value, ColumnNames.Alt.value])
            pdata = pd.concat([pdata, stadf], axis=1)
            #print('6  ,',datetime.datetime.now())

            if filters is not None:
                for k,c,v in filters:
                    if c == ct.Greater:
                        pdata = pdata.loc[pdata[k] > v]
                    elif c == ct.Less:
                        pdata = pdata.loc[pdata[k] < v]
                    elif c == ct.Equal:
                        pdata = pdata.loc[pdata[k] == v]
                    elif c == ct.Not_Greater:
                        pdata = pdata.loc[pdata[k] <= v]
                    elif c == ct.Not_Less:
                        pdata = pdata.loc[pdata[k] >= v]
                    elif c == ct.Not_Equal:
                        pdata = pdata.loc[pdata[k] != v]
                    elif c == ct.Nan:
                        pdata = pdata.loc[np.isnan(pdata[k])]
                    elif c == ct.Not_Nan:
                        pdata = pdata.loc[~np.isnan(pdata[k])]
                    elif c == ct.In:
                        pdata = pdata.loc[pdata[k].isin(v)]
                    elif c == ct.Not_In:
                        pdata = pdata.loc[~pdata[k].isin(v)]
                    else:
                        raise Exception('unknown condition')

            if pdata is not None:
                pdata.reset_index(drop=True)

            #print('7  ,',datetime.datetime.now())

            self.fcst_data = pdata

            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_data except %s %s' % (str(data), fdata))

            return False
    
    def __parse_endstr(self, dl):
        try:
            if dl.strip() == ZczcPublicType.endstr:
                return True
            else:
                return False
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_endstr except %s %s' % (str(data), dl))

            return False

    def __parse_endline(self, fdata):
        try:
            dl = fdata.readline().strip()
            if dl is None or dl == '':
                LogLib.logger.error('ZCZCParser __parse_endline readlines error %s' % (fdata))
                return False

            if not self.__parse_endstr(dl):
                LogLib.logger.error('ZCZCParser __parse_endline endline error %s' % (fdata))
                return False

            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser __parse_endline except %s %s' % (str(data), fdata))

            return False

    #解析数据，fdata是StringIO类型
    def parse(self, fdata, staids=None, columns=None, filters=None):
        try:
            LogLib.logger.info('ZCZCParser parse start %s' % (fdata))

            self.nextpos = 0

            if not self.__parse_first_line(fdata):
                return False
            
            if not self.__parse_second_line(fdata):
                return False
            
            if not self.__parse_third_line(fdata):
                return False
            
            if not self.__parse_fourth_line(fdata):
                return False

            if not self.__parse_fifth_line(fdata):
                return False
            
            if not self.__parse_data(fdata, staids=staids, columns=columns, filters=filters):
                return False
            
            if not self.__parse_endline(fdata):
                return False
            
            return True
        except Exception as data:
            LogLib.logger.error('ZCZCParser parse except %s %s' % (str(data), fdata))

            return False

    #解析数据
    def parsefile(self, fullpath, staids=None, columns=None, filters=None):
        try:
            LogLib.logger.info('ZCZCParser parsefile start %s' % (fullpath))

            fd = None
            with open(fullpath, 'r') as f:
                fd = f.read()

            with StringIO(fd) as fdata:
                print(datetime.datetime.now())
                rst = self.parse(fdata,  staids=staids, columns=columns, filters=filters)
                print(datetime.datetime.now())
                if rst:
                    LogLib.logger.info('ZCZCParser parsefile over %s' % (fullpath))
                else:
                    LogLib.logger.error('ZCZCParser parsefile error %s' % (fullpath))

                return rst
        except Exception as data:
            LogLib.logger.error('ZCZCParser parsefile except %s %s' % (fullpath, str(data)))

            return False
        

if __name__ == '__main__':
    import os

    workdir = os.path.dirname(__file__)

    logdir = os.path.join(workdir, 'logfiles')
    if not os.path.exists(logdir):
        os.mkdir(logdir)

    LogLib.init()
    LogLib.addTimedRotatingFileHandler(os.path.join(logdir, 'zczcparser.log'))
    LogLib.setLevel(logging.DEBUG)

    print(datetime.datetime.now())
    p = ZCZCParser_np()
    #print(p.parsefile(r'C:\workdoc\城镇报\a.txt'))
    #for i in range(4):

    #print(p.parsefile(r'C:\testdata\check_tmx\SEVP_NMC_RFFC_SNWFD_EME_ACHN_L88_P9_20210329080016812.TXT'))
    print(p.parsefile(r'D:\testdata\SEVP_NMC_RFFC_SCMOC_EME_ACHN_L88_P9_20210622120016812.txt'))

    print(datetime.datetime.now())

    LogLib.uninit()
    
    print('test done')


