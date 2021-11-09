#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: zczcwriter.py

'''
Created on Aug 26, 2021

@author: anduin
'''
import pandas as pd
import numpy as np

#from logmodule.loglib import *
from zczc.zczcpublictype import ZczcPublicType

class ZCZCWriter():
    """description of class 
    城镇报格式解码和生成
    """

    def __init__(self):
        self.filename = None

        self.CCCC = ''
        self.YYGGgg = ''
        self.BBB = ''

        self.product_desc = ''

        self.product_code = ''
        self.fcst_time = None
        self.fcst_time_str = None

        self.sta_count = None

        self.fcst_data = None

        self.seqcount = None
        self.colcount = None

        self.decimals = 1
        self.scale_decimals = 3  

        self.stas = None
        self.contentstr = None
        self.procnum = 4

        self.decimals_fmt = None
        self.scale_decimals_fmt = None

    def set_params(self, filename, CCCC, YYGGgg, BBB, product_desc, product_code, fcst_time, sta_count, \
                    fcst_data, decimals=1, scale_decimals=3, procnum=4):
        self.filename = filename
        self.CCCC = CCCC
        self.YYGGgg = YYGGgg
        self.BBB = BBB
        self.product_desc = product_desc
        self.product_code = product_code
        self.fcst_time = fcst_time
        self.fcst_time_str = fcst_time.strftime(ZczcPublicType.fcst_time_fmt)

        self.sta_count = sta_count
        self.fcst_data = fcst_data

        self.seqcount = int(len(self.fcst_data.values) / self.sta_count)
        self.colcount = len(self.fcst_data.columns) - 5
        
        self.decimals = decimals
        self.scale_decimals = scale_decimals
        
        self.contentstr = None
        self.procnum = procnum
        
    #dataframe:id lon lat alt seq d1 d2 d2 ……
    #一个起报时的数据，按站点，时效排序，每个站点的时效和列数都相同
    def write(self, filename=None):
        if filename is None:
            filename = self.filename

        if self.BBB is None:
            self.contentstr = '%s\n%s  %s  %s\n%s\n%s  %s\n%d\n' % (ZczcPublicType.fileid, ZczcPublicType.TTAAii, \
                    self.CCCC, self.YYGGgg, self.product_desc, self.product_code, self.fcst_time_str, self.sta_count)
        else:
            self.contentstr = '%s\n%s  %s  %s  %s\n%s\n%s  %s\n%d\n' % (ZczcPublicType.fileid, ZczcPublicType.TTAAii, \
                    self.CCCC, self.YYGGgg, self.BBB, self.product_desc, self.product_code, self.fcst_time_str, self.sta_count)

        self.stas = self.fcst_data.iloc[range(0, len(self.fcst_data), self.seqcount), range(4)]
        self.stas['row'] = self.seqcount
        self.stas['row'] = self.stas['row'].astype(np.int32)
        self.stas['col'] = self.colcount
        self.stas['col'] = self.stas['col'].astype(np.int32)
        self.stas.reset_index(drop=True, inplace=True)
        #stasstr = self.stas.to_csv(float_format='%6.3f',sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')
        
        #'%7.1f'
        self.decimals_fmt = '%{}.{}f'.format(self.decimals + 4, self.decimals)
        #'%7.3f'
        self.scale_decimals_fmt = '%{}.{}f'.format(self.scale_decimals + 4, self.scale_decimals)

        curline = 0
        for i in range(self.sta_count):
            self.contentstr += self.stas.loc[[i]].to_csv(float_format=self.scale_decimals_fmt,sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')
            #self.contentstr += self.fcst_data.loc[range(curline, curline+self.seqcount), self.fcst_data.columns[4:]].to_csv(float_format=self.decimals_fmt,sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')
            self.contentstr += self.fcst_data.iloc[curline:curline+self.seqcount, 4:].to_csv(float_format=self.decimals_fmt,sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')

            curline += self.seqcount

        self.contentstr += ZczcPublicType.endstr

        with open(filename, 'w') as f:
            f.write(self.contentstr)
            
        self.contentstr = None
        self.stas = None

    def format_line(self, line_items, fmt):
        return ''.join('%s\n' % ' '.join(
            '%03d' % ele if i == 0 else fmt % ele for i, ele
            in enumerate(eleline))
        for j,eleline in enumerate(line_items))

    def write_with_line(self, filename=None):
        if filename is None:
            filename = self.filename

        self.contentstr = []
        if self.BBB is None:
            self.contentstr.append('%s\n%s  %s  %s\n%s\n%s  %s\n%d\n' % (ZczcPublicType.fileid, ZczcPublicType.TTAAii, \
                    self.CCCC, self.YYGGgg, self.product_desc, self.product_code, self.fcst_time_str, self.sta_count))
        else:
            self.contentstr.append('%s\n%s  %s  %s  %s\n%s\n%s  %s\n%d\n' % (ZczcPublicType.fileid, ZczcPublicType.TTAAii, \
                    self.CCCC, self.YYGGgg, self.BBB, self.product_desc, self.product_code, self.fcst_time_str, self.sta_count))

        self.stas = self.fcst_data.iloc[range(0, len(self.fcst_data), self.seqcount), range(4)]
        self.stas['row'] = self.seqcount
        self.stas['row'] = self.stas['row'].astype(np.int32)
        self.stas['col'] = self.colcount
        self.stas['col'] = self.stas['col'].astype(np.int32)
        self.stas.reset_index(drop=True, inplace=True)
        #stasstr = self.stas.to_csv(float_format='%6.3f',sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')
        
        #'%7.1f'
        self.decimals_fmt = '%{}.{}f'.format(self.decimals + 4, self.decimals)
        #'%7.3f'
        self.scale_decimals_fmt = '%{}.{}f'.format(self.scale_decimals + 4, self.scale_decimals)

        curline = 0
        for i in range(self.sta_count):
            self.contentstr.append(self.stas.loc[[i]].to_csv(float_format=self.scale_decimals_fmt,sep=' ',header=False,index=False,line_terminator='\n',quotechar=' '))
            #self.contentstr += self.fcst_data.loc[range(curline, curline+self.seqcount), self.fcst_data.columns[4:]].to_csv(float_format=self.decimals_fmt,sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')
            #self.contentstr += self.fcst_data.iloc[curline:curline+self.seqcount, 4:].to_csv(float_format=self.decimals_fmt,sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')
            
            #for j in range(curline, curline+self.seqcount):
            #    self.contentstr.append(self.format_line(self.fcst_data.iloc[[j], 4:].values[0], self.decimals_fmt))
            self.contentstr.append(self.format_line(self.fcst_data.iloc[curline:curline+self.seqcount, 4:].values, self.decimals_fmt))
                
            curline += self.seqcount

        self.contentstr.append(ZczcPublicType.endstr)

        with open(filename, 'w') as f:
            f.writelines(self.contentstr)
            
        self.contentstr = None

    def proc_write_with_line(self, stasite):
        curline = self.seqcount * stasite

        headerstr = self.stas.loc[[stasite]].to_csv(float_format=self.scale_decimals_fmt,sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')
        contentstr = self.format_line(self.fcst_data.iloc[curline:curline+self.seqcount, 4:].values, self.decimals_fmt)

        return (headerstr, contentstr)

    def write_with_line_mul(self, filename=None):
        from multiprocessing import Pool

        if filename is None:
            filename = self.filename

        self.contentstr = []
        if self.BBB is None:
            self.contentstr.append('%s\n%s  %s  %s\n%s\n%s  %s\n%d\n' % (ZczcPublicType.fileid, ZczcPublicType.TTAAii, \
                    self.CCCC, self.YYGGgg, self.product_desc, self.product_code, self.fcst_time_str, self.sta_count))
        else:
            self.contentstr.append('%s\n%s  %s  %s  %s\n%s\n%s  %s\n%d\n' % (ZczcPublicType.fileid, ZczcPublicType.TTAAii, \
                    self.CCCC, self.YYGGgg, self.BBB, self.product_desc, self.product_code, self.fcst_time_str, self.sta_count))

        self.stas = self.fcst_data.iloc[range(0, len(self.fcst_data), self.seqcount), range(4)]
        self.stas['row'] = self.seqcount
        self.stas['row'] = self.stas['row'].astype(np.int32)
        self.stas['col'] = self.colcount
        self.stas['col'] = self.stas['col'].astype(np.int32)
        self.stas.reset_index(drop=True, inplace=True)
        #stasstr = self.stas.to_csv(float_format='%6.3f',sep=' ',header=False,index=False,line_terminator='\n',quotechar=' ')
        
        #'%7.1f'
        self.decimals_fmt = '%{}.{}f'.format(self.decimals + 4, self.decimals)
        #'%7.3f'
        self.scale_decimals_fmt = '%{}.{}f'.format(self.scale_decimals + 4, self.scale_decimals)
        
        procrsts = None
        with Pool(self.procnum) as p:
            procrsts = p.map(self.proc_write_with_line, list(range(self.sta_count)))
            p.close()
            p.join()

        for procrst in procrsts:
            self.contentstr.append(procrst[0])
            self.contentstr.append(procrst[1])

        self.contentstr.append(ZczcPublicType.endstr)

        with open(filename, 'w') as f:
            f.writelines(self.contentstr)
        
        self.contentstr = None

if __name__ == '__main__':
    import datetime

    stas = pd.DataFrame(stas.values.repeat(3, axis=0), columns=stas.columns)
    stas['id'] = stas['id'].astype(np.int32)

    d = pd.DataFrame([[1]+list(range(21)), [2]+list(range(21)), [3]+list(range(21))], columns=ZczcPublicType.columns)
    d = pd.DataFrame(np.tile(d.values, (2,1)), columns=d.columns)

    fcstdata = pd.concat([stas, d], axis=1, ignore_index=True)


    print(datetime.datetime.now())
    p = ZCZCWriter()
    p.stas = stas
    p.set_params(r'd:\testdata\aaa.txt', 'BABJ', '210904', None, 'aaaaa', 'SCMOC', datetime.datetime(2021, 9, 4, 12), 2, fcstdata)
    p.write()

    print(datetime.datetime.now())

    print('test done')


