#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixreaddata.py

'''
Created on Aug 21, 2020

@author: anduin
'''

import os
import numpy as np
import json
import datetime
import pandas as pd
import xarray
import time

from publictype.fixparamtypes import FixParamTypes

class FixReadData(object):
    def __init__(self, logger):
        self.logger = logger
        
    #处理grib的过滤条件,filters的格式为：产品分类 产品编号 层次类型 层次值，其中不需要的条件设置为-1
    #grib2文件中对应的变量名：parameterCategory parameterNumber typeOfFirstFixedSurface level
    def __filter_grib_msg(self, grb, filters):
        if filters is None:
            return True

        splitrsts = filters.split(',')
        if len(splitrsts) != 4:
            raise Exception('filters format error %s' % str(filters))

        rst = int(splitrsts[0])
        if rst >= 0 and grb.parameterCategory != rst:
            return False
        
        rst = int(splitrsts[1])
        if rst >= 0 and grb.parameterNumber != rst:
            return False

        #rst = int(splitrsts[2])
        #if rst >= 0 and grb.typeOfFirstFixedSurface != rst:
        #    return False
        if grb.typeOfFirstFixedSurface != splitrsts[2]:
            return False

        rst = int(splitrsts[3])
        if rst >= 0 and grb.level != rst:
            return False

        return True

    #读单个grib2文件，返回以seqnum为key，文件中grib为value的字典
    def read_gribdata_from_grib2_with_pygrib_single_file_seqnum(self, params):
        from publictype.gribtypes import GribTypes
        
        from_file = params[FixParamTypes.SFullPath]
        seq_key_is_num = params[FixParamTypes.SeqKeyIsNum] if FixParamTypes.SeqKeyIsNum in params else False
        seq_and_p_num = None
        if FixParamTypes.SeqAndPNum in params:
            seq_and_p_num = params[FixParamTypes.SeqAndPNum]
        elif FixParamTypes.SeqObj in params:
            if seq_key_is_num:
                seq_and_p_num = params[FixParamTypes.SeqObj]
            else:
                seq_and_p_num = list(map(str, params[FixParamTypes.SeqObj]))

        #seqfield = params[FixParamTypes.SeqField] if FixParamTypes.SeqField in params else GribTypes.endStep
        pnumfield = params[FixParamTypes.PNumField] if FixParamTypes.PNumField in params else None   #GribTypes.perturbationNumber
        
        logger = params[FixParamTypes.CurLogger] if FixParamTypes.CurLogger in params else None
        if logger is None:
            logger = self.logger

        filters = params[FixParamTypes.Filters] if FixParamTypes.Filters in params else None

        try:
            import pygrib
            logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum start %s' % (str(params)))
            
            rst = {}
            grbs = pygrib.open(from_file)
            for grb in grbs:
                if not self.__filter_grib_msg(grb, filters):
                    continue

                seqnum = 0
                if grb.productDefinitionTemplateNumber == 0:
                    seqnum = grb.stepRange
                elif grb.productDefinitionTemplateNumber == 8:
                    seqnum = grb.endStep
                else:
                    raise Exception('error seq field')
                '''
                if seqfield == GribTypes.endStep:
                    seqnum = grb.endStep
                elif seqfield == GribTypes.stepRange:
                    seqnum = grb.stepRange
                else:
                    raise Exception('error seq field')
                '''

                if seq_key_is_num:
                    seqnum = int(seqnum)

                pnum = 0
                if pnumfield == None:
                    pass
                elif pnumfield == GribTypes.perturbationNumber:
                    pnum = grb.perturbationNumber
                else:
                    raise Exception('error pnum field')

                curkey = None
                if seq_key_is_num:
                    curkey = seqnum
                else:
                    curkey = str(seqnum) if pnum == 0 else str(pnum) + '_' + str(seqnum)

                if seq_and_p_num is None:
                    rst[curkey] = grb
                else:
                    if curkey in seq_and_p_num:
                        rst[curkey] = grb

            logger.info('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum over %s' % (str(params)))
            return rst
        except Exception as data:
            logger.error('FixReadData read_gribdata_from_grib2_with_pygrib_single_file_seqnum except %s %s' % (str(params), str(data)))

            return None
        
    def read_griddata_from_micaps4(self, params):
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        grid = params[FixParamTypes.GridR] if FixParamTypes.GridR in params else None
        
        logger = params[FixParamTypes.CurLogger] if FixParamTypes.CurLogger in params else None
        if logger is None:
            logger = self.logger

        try:
            logger.info('FixReadData read_griddata_from_micaps4 start %s' % (str(params)))

            grd = None
            if grid is None:
                grd = meb.read_griddata_from_micaps4(filename=from_file)
            else:
                grd = meb.read_griddata_from_micaps4(filename=from_file, grid=grid)

            if grd is None:
                logger.error('FixReadData read_griddata_from_micaps4 read error %s' % (str(params)))
            else:
                logger.info('FixReadData read_griddata_from_micaps4 over')

            return grd
        except Exception as data:
            logger.error('FixReadData read_griddata_from_micaps4 except %s %s' % (str(params), str(data)))

            raise data
            
    def read_griddata_from_bin(self, params):
        import math
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        curdtype = params[FixParamTypes.DType] if FixParamTypes.DType in params else np.float64
        slon = params[FixParamTypes.SLon] if FixParamTypes.SLon in params else None
        elon = params[FixParamTypes.ELon] if FixParamTypes.ELon in params else None
        dlon = params[FixParamTypes.DLon] if FixParamTypes.DLon in params else None
        nlon = params[FixParamTypes.NLon] if FixParamTypes.NLon in params else None
        slat = params[FixParamTypes.SLat] if FixParamTypes.SLat in params else None
        elat = params[FixParamTypes.ELat] if FixParamTypes.ELat in params else None
        dlat = params[FixParamTypes.DLat] if FixParamTypes.DLat in params else None
        nlat = params[FixParamTypes.NLat] if FixParamTypes.NLat in params else None
        multi = params[FixParamTypes.Multi] if FixParamTypes.Multi in params else None
        grid = params[FixParamTypes.GridR] if FixParamTypes.GridR in params else None
        offset = params[FixParamTypes.Offset] if FixParamTypes.Offset in params else 0
        seq = params[FixParamTypes.SeqObj] if FixParamTypes.SeqObj in params else 0
        if seq is None or type(seq) is not int:
            raise Exception('seq error')
        
        logger = params[FixParamTypes.CurLogger] if FixParamTypes.CurLogger in params else None
        if logger is None:
            logger = self.logger

        try:
            logger.info('FixReadData read_griddata_from_bin start %s' % (str(params)))
            
            if (slon is None or elon is None or dlon is None or nlon is None or slat is None or elat is None or dlat is None or nlat is None) and grid is None:
                raise Exception('grid error')

            if nlon is None:
                nlon = 1 + ( grid.glon[1] - grid.glon[0]) / grid.glon[2]
                error = abs(round(nlon) - nlon)/nlon
                if (error > 0.01):
                    nlon = int(math.ceil(nlon))
                else:
                    nlon = int(round(nlon))

            if nlat is None:
                nlat = 1 + (grid.glat[1] - grid.glat[0]) / grid.glat[2]
                error = abs(round(nlat) - nlat)/nlat
                if (error > 0.01):
                    nlat = int(math.ceil(nlat))
                else:
                    nlat = int(round(nlat))

            grd = None

            datalen = -1  #nlon * nlat
            curdata = np.fromfile(from_file, dtype=curdtype, count=datalen, offset=offset)
            if datalen != -1 and len(curdata) != datalen:
                logger.error('FixReadData read_griddata_from_bin data len error %s' % (str(params)))
                return grd

            curdata.resize(nlat, nlon)

            if multi is not None:
                curdata = curdata * multi
                
            if grid is None:
                grid = meb.grid([slon, elon, dlon], [slat, elat, dlat])

            grd = meb.grid_data(grid, data=curdata)
            meb.reset(grd)
            
            return grd
        except Exception as data:
            logger.error('FixReadData read_griddata_from_bin except %s %s' % (str(params), str(data)))

            raise data
        
    def read_griddata_from_bin_wind(self, params):
        import math
        import meteva.base as meb

        from_file = params[FixParamTypes.SFullPath]
        curdtype = params[FixParamTypes.DType] if FixParamTypes.DType in params else np.float64
        slon = params[FixParamTypes.SLon] if FixParamTypes.SLon in params else None
        elon = params[FixParamTypes.ELon] if FixParamTypes.ELon in params else None
        dlon = params[FixParamTypes.DLon] if FixParamTypes.DLon in params else None
        nlon = params[FixParamTypes.NLon] if FixParamTypes.NLon in params else None
        slat = params[FixParamTypes.SLat] if FixParamTypes.SLat in params else None
        elat = params[FixParamTypes.ELat] if FixParamTypes.ELat in params else None
        dlat = params[FixParamTypes.DLat] if FixParamTypes.DLat in params else None
        nlat = params[FixParamTypes.NLat] if FixParamTypes.NLat in params else None
        multi = params[FixParamTypes.Multi] if FixParamTypes.Multi in params else None
        grid = params[FixParamTypes.GridR] if FixParamTypes.GridR in params else None
        offset = params[FixParamTypes.Offset] if FixParamTypes.Offset in params else 0
        seq = params[FixParamTypes.SeqObj] if FixParamTypes.SeqObj in params else 0
        if seq is None or type(seq) is not int:
            raise Exception('seq error')
        
        logger = params[FixParamTypes.CurLogger] if FixParamTypes.CurLogger in params else None
        if logger is None:
            logger = self.logger

        try:
            logger.info('FixReadData read_griddata_from_bin start %s' % (str(params)))

            if (slon is None or elon is None or dlon is None or nlon is None or slat is None or elat is None or dlat is None or nlat is None) and grid is None:
                raise Exception('grid error')
            
            if nlon is None:
                nlon = 1 + ( grid.glon[1] - grid.glon[0]) / grid.glon[2]
                error = abs(round(nlon) - nlon)/nlon
                if (error > 0.01):
                    nlon = int(math.ceil(nlon))
                else:
                    nlon = int(round(nlon))

            if nlat is None:
                nlat = 1 + (grid.glat[1] - grid.glat[0]) / grid.glat[2]
                error = abs(round(nlat) - nlat)/nlat
                if (error > 0.01):
                    nlat = int(math.ceil(nlat))
                else:
                    nlat = int(round(nlat))

            grd = None

            datalen = -1  #nlon * nlat
            curdata = np.fromfile(from_file, dtype=curdtype, count=datalen, offset=offset)
            if datalen != -1 and len(curdata) != datalen:
                logger.error('FixReadData read_griddata_from_bin data len error %s' % (str(params)))
                return grd

            curdata.resize(2*nlat, nlon)

            if multi is not None:
                curdata = curdata * multi
                
            if grid is None:
                grid = meb.grid([slon, elon, dlon], [slat, elat, dlat])

            grd_u = meb.grid_data(grid, data=curdata[:nlat])
            meb.reset(grd_u)
            
            grd_v = meb.grid_data(grid, data=curdata[nlat:2*nlat])
            meb.reset(grd_v)
            
            return (grd_u, grd_v)
        except Exception as data:
            logger.error('FixReadData read_griddata_from_bin except %s %s' % (str(params), str(data)))

            raise data
        
if __name__ == '__main__':
    print('done')
