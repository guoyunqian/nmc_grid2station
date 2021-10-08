#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: nmc_grid2station.py

"""
Created on Aug 25, 2021

@author: anduin
"""

import os
import sys
import datetime
import meteva.base as meb
import copy
import numpy as np
import pandas as pd

from logmodule.loglibmul import *
from publictype.fixparamtypes import FixParamTypes
from publictype.columnnames import ColumnNames
from publictype.readfuncnames import ReadFuncNames
import public
import public.convert_wind as convert_wind
from cfg_main import CfgMain
from cfg_srcdata import CfgSrcData

from framework.fixfileinfos import FixFileInfos
from framework.fixreaddata import FixReadData
from framework.fixwritedata import FixWriteData

import procfunc
from publictype.interptypes import InterpTypes

from zczc.zczcwriter import ZCZCWriter


#时间设定应该是和s_is_bjt保持一致，s_is_bjt是true，这两个时间就应该是北京时间，否则是utc时间
#结束时间和小时数（t_num）不会同时使用到，分别对应不同的获取时间列表的函数
#用于回算
#fix_stime = datetime.datetime(2021,3,29,8,0,0)
#fix_etime = datetime.datetime(2021,4,1,8,0,0)
#用于实时，类似于使用t_num
'''
def get_etime():
    curutcdt = datetime.datetime.utcnow().replace(second=0,microsecond=0)
    if curutcdt.minute >= 10 and curutcdt.minute < 30:
        return curutcdt.replace(minute=0) - datetime.timedelta(hours=1)
    else:
        return curutcdt.replace(minute=0)
    '''
#fix_etime = get_etime()
fix_etime = datetime.datetime.now()  #.replace(minute=0,second=0,microsecond=0)
#fix_stime = fix_etime - datetime.timedelta(hours=12)

#获取时间列表时，每个时间的最小间隔
delta_t = 60

#日志对象
loglib = LogLibMul()
#日志文件存储目录
log_file_dir = 'logfiles'
#日志文件的文件名
log_file_name = 'nmc_grid2station.log'

#配置文件存储目录
cfg_file_dir = 'config'
#日志文件的文件名
cfg_file_name = 'cfg_main.ini'

#初始化日志
def init_log(logfiles, loglib):
    loglib.init(logfiles.keys())
    loglib.addTimedRotatingFileHandler(logfiles)

    levels = {}
    for k,v in logfiles.items():
        levels[k] = logging.DEBUG

    loglib.setLevel(levels)
    
#读二进制格点数据，插值到站点
def read_grid_bin(dt, srccfg, seqobj, ffinfos, frdata, src_datas, stainfos, logger):
    logger.info('read_grid_bin start')
    
    bobj = srccfg[FixParamTypes.CfgObj]
    cfgobj = bobj.srcinfos
    
    grdlist = {}
    for curseq in seqobj:
        fixfullpath = os.path.join(public.get_path_with_replace(cfgobj[FixParamTypes.SDict], dt, curseq), \
                                    public.get_path_with_replace(cfgobj[FixParamTypes.SFnFmt], dt, curseq))
        if not os.path.exists(fixfullpath):
            logger.warning('read_grid_bin read file not exist %s' % (fixfullpath))
            continue

        try:
            params = {}
            
            params[FixParamTypes.SFullPath] = fixfullpath
            params[FixParamTypes.SLon] = cfgobj[FixParamTypes.SLon]
            params[FixParamTypes.ELon] = cfgobj[FixParamTypes.ELon]
            params[FixParamTypes.DLon] = cfgobj[FixParamTypes.DLon]
            params[FixParamTypes.NLon] = cfgobj[FixParamTypes.NLon]
            params[FixParamTypes.SLat] = cfgobj[FixParamTypes.SLat]
            params[FixParamTypes.ELat] = cfgobj[FixParamTypes.ELat]
            params[FixParamTypes.DLat] = cfgobj[FixParamTypes.DLat]
            params[FixParamTypes.NLat] = cfgobj[FixParamTypes.NLat]
            params[FixParamTypes.DType] = np.float32

            grd = frdata.read_griddata_from_bin(params)
            grd['dtime'] = [curseq]
            if FixParamTypes.Miss in cfgobj and cfgobj[FixParamTypes.Miss] is not None:
                if not np.isnan(cfgobj[FixParamTypes.Miss]):
                    grd.values[grd.values == cfgobj[FixParamTypes.Miss]] = np.nan

            if srccfg[FixParamTypes.InterpType] == InterpTypes.interp_gs_linear:
                sta = meb.interp_gs_linear(grd, stainfos)
            elif srccfg[FixParamTypes.InterpType] == InterpTypes.interp_gs_nearest:
                sta = meb.interp_gs_nearest(grd, stainfos)
            else:
                raise Exception('error interptype')
            
            sta.drop(['level', 'time', 'lon', 'lat', 'dtime'], axis=1, inplace=True)
            sta.rename(columns={ ColumnNames.MebStaDefault.value:srccfg[FixParamTypes.DName] }, inplace = True)
            sta = sta.reindex(columns=[ColumnNames.StaID.value, srccfg[FixParamTypes.DName]])

            grdlist[curseq] = sta
        except Exception as data:
            logger.error('read_grid_bin read file except %s %s' % (fixfullpath, str(data)))
            grdlist = None

    if grdlist is None:
        logger.error('read_grid_bin read file error %s' % (str(dt)))
        return False
        

    src_datas[srccfg[FixParamTypes.DName]] = grdlist

    logger.info('read_grid_bin over')

    return True

#读二进制uv风格点数据，转成风速风向，插值到站点
def read_grid_bin_wind_from_uv_to_ds(dt, srccfg, seqobj, ffinfos, frdata, src_datas, stainfos, logger):
    logger.info('read_grid_bin_wind_from_uv_to_ds start')
    
    bobj = srccfg[FixParamTypes.CfgObj]
    cfgobj = bobj.srcinfos
    
    grdlist_d = {}
    grdlist_s = {}
    for curseq in seqobj:
        fixfullpath = os.path.join(public.get_path_with_replace(cfgobj[FixParamTypes.SDict], dt, curseq), \
                                    public.get_path_with_replace(cfgobj[FixParamTypes.SFnFmt], dt, curseq))
        if not os.path.exists(fixfullpath):
            logger.warning('read_grid_bin_wind_from_uv_to_ds read file not exist %s' % (fixfullpath))
            continue

        try:
            params = {}
            
            params[FixParamTypes.SFullPath] = fixfullpath
            params[FixParamTypes.SLon] = cfgobj[FixParamTypes.SLon]
            params[FixParamTypes.ELon] = cfgobj[FixParamTypes.ELon]
            params[FixParamTypes.DLon] = cfgobj[FixParamTypes.DLon]
            params[FixParamTypes.NLon] = cfgobj[FixParamTypes.NLon]
            params[FixParamTypes.SLat] = cfgobj[FixParamTypes.SLat]
            params[FixParamTypes.ELat] = cfgobj[FixParamTypes.ELat]
            params[FixParamTypes.DLat] = cfgobj[FixParamTypes.DLat]
            params[FixParamTypes.NLat] = cfgobj[FixParamTypes.NLat]
            params[FixParamTypes.DType] = np.float32

            grd_u, grd_v = frdata.read_griddata_from_bin_wind(params)
            grd_u['dtime'] = [curseq]
            grd_v['dtime'] = [curseq]
            if FixParamTypes.Miss in cfgobj and cfgobj[FixParamTypes.Miss] is not None:
                if not np.isnan(cfgobj[FixParamTypes.Miss]):
                    grd_u.values[grd_u.values == cfgobj[FixParamTypes.Miss]] = np.nan
                    grd_v.values[grd_v.values == cfgobj[FixParamTypes.Miss]] = np.nan

            if srccfg[FixParamTypes.InterpType] == InterpTypes.interp_gs_linear:
                sta_u = meb.interp_gs_linear(grd_u, stainfos)
                sta_v = meb.interp_gs_linear(grd_v, stainfos)
            elif srccfg[FixParamTypes.InterpType] == InterpTypes.interp_gs_nearest:
                sta_u = meb.interp_gs_nearest(grd_u, stainfos)
                sta_v = meb.interp_gs_nearest(grd_v, stainfos)
            else:
                raise Exception('error interptype')
            
            sta_d = copy.deepcopy(sta_u)
            sta_s = copy.deepcopy(sta_v)

            d,s = convert_wind.convert_uv_to_ds(sta_d[ColumnNames.MebStaDefault.value], sta_s[ColumnNames.MebStaDefault.value], needcopy=True)

            sta_d[ColumnNames.MebStaDefault.value] = d
            sta_d.drop(['level', 'time', 'lon', 'lat', 'dtime'], axis=1, inplace=True)
            sta_d.rename(columns={ ColumnNames.MebStaDefault.value:srccfg[FixParamTypes.DName][0] }, inplace = True)
            sta_d = sta_d.reindex(columns=[ColumnNames.StaID.value, srccfg[FixParamTypes.DName][0]])

            sta_s[ColumnNames.MebStaDefault.value] = s
            sta_s.drop(['level', 'time', 'lon', 'lat', 'dtime'], axis=1, inplace=True)
            sta_s.rename(columns={ ColumnNames.MebStaDefault.value:srccfg[FixParamTypes.DName][1] }, inplace = True)
            sta_s = sta_s.reindex(columns=[ColumnNames.StaID.value, srccfg[FixParamTypes.DName][1]])

            grdlist_d[curseq] = sta_d
            grdlist_s[curseq] = sta_s
        except Exception as data:
            logger.error('read_grid_bin read file except %s %s' % (fixfullpath, str(data)))
            grdlist_d = None
            grdlist_s = None

    if grdlist_d is None or grdlist_s is None:
        logger.error('read_grid_bin_wind_from_uv_to_ds read file error %s' % (str(dt)))
        return False
        

    src_datas[srccfg[FixParamTypes.DName][0]] = grdlist_d
    src_datas[srccfg[FixParamTypes.DName][1]] = grdlist_s

    logger.info('read_grid_bin_wind_from_uv_to_ds over')

    return True

#def get_save_paths(ffinfos, dpath, dst_fullpaths, savecfginfos, savedt, logger):
#    logger.info('get_save_paths start')

#    params = { FixParamTypes.DT:savedt, FixParamTypes.DDict:dpath,
#              FixParamTypes.DFnFmt:savecfginfos[FixParamTypes.DFnFmt], FixParamTypes.DSeq:savecfginfos[FixParamTypes.DSeq]
#              }

#    saveinfos = ffinfos.get_save_path(params)

#    if saveinfos is None:
#        logger.info('get_save_paths error')

#        return False

#    dst_fullpaths.update(saveinfos)

#    logger.info('get_save_paths over')

#    return True

def write_data_m4(cfgobj, fwrite, dst_fullpaths, savedt, dst_datas, logger):
    logger.info('write_data_m4 start')

    #保存
    wparams = {}
    wparams[FixParamTypes.DT] = savedt

    wparams[FixParamTypes.NLon] = cfgobj.savecfginfos[FixParamTypes.NLon]
    wparams[FixParamTypes.NLat] = cfgobj.savecfginfos[FixParamTypes.NLat]
    wparams[FixParamTypes.SLon] = cfgobj.savecfginfos[FixParamTypes.SLon]
    wparams[FixParamTypes.SLat] = cfgobj.savecfginfos[FixParamTypes.SLat]
    wparams[FixParamTypes.ELon] = cfgobj.savecfginfos[FixParamTypes.ELon]
    wparams[FixParamTypes.ELat] = cfgobj.savecfginfos[FixParamTypes.ELat]
    wparams[FixParamTypes.DLon] = cfgobj.savecfginfos[FixParamTypes.DLon]
    wparams[FixParamTypes.DLat] = cfgobj.savecfginfos[FixParamTypes.DLat]

    wparams[FixParamTypes.Decimals] = cfgobj.savecfginfos[FixParamTypes.Decimals]
    wparams[FixParamTypes.ScaleDecimals] = cfgobj.savecfginfos[FixParamTypes.ScaleDecimals]

    for seqnum,griddata in dst_datas.items():
        wparams[FixParamTypes.GridData] = griddata.values.reshape(wparams[FixParamTypes.NLat], wparams[FixParamTypes.NLon])
        wparams[FixParamTypes.DFullPath] = dst_fullpaths[seqnum]
        wparams[FixParamTypes.SeqNum] = seqnum

        if fwrite.save_griddata_to_m4_no_meb(wparams):
            logger.info('write_data_m4 over %s' % (dst_fullpaths[seqnum]))
        else:
            logger.error('write_data_m4 error %s' % (dst_fullpaths[seqnum]))

    logger.info('write_data_m4 over')
    
def write_data_m11(cfgobj, fwrite, dst_fullpath, savedt, dst_datas, logger):
    logger.info('write_data_m11 start')

    #保存
    wparams = {}
    wparams[FixParamTypes.DT] = savedt

    wparams[FixParamTypes.NLon] = cfgobj.savecfginfos[FixParamTypes.NLon]
    wparams[FixParamTypes.NLat] = cfgobj.savecfginfos[FixParamTypes.NLat]
    wparams[FixParamTypes.SLon] = cfgobj.savecfginfos[FixParamTypes.SLon]
    wparams[FixParamTypes.SLat] = cfgobj.savecfginfos[FixParamTypes.SLat]
    wparams[FixParamTypes.ELon] = cfgobj.savecfginfos[FixParamTypes.ELon]
    wparams[FixParamTypes.ELat] = cfgobj.savecfginfos[FixParamTypes.ELat]
    wparams[FixParamTypes.DLon] = cfgobj.savecfginfos[FixParamTypes.DLon]
    wparams[FixParamTypes.DLat] = cfgobj.savecfginfos[FixParamTypes.DLat]

    wparams[FixParamTypes.Decimals] = cfgobj.savecfginfos[FixParamTypes.Decimals]
    wparams[FixParamTypes.ScaleDecimals] = cfgobj.savecfginfos[FixParamTypes.ScaleDecimals]

    for seqnum,griddata in dst_datas.items():
        wparams[FixParamTypes.GridData] = griddata.values.reshape(2*wparams[FixParamTypes.NLat], wparams[FixParamTypes.NLon])
        wparams[FixParamTypes.DFullPath] = dst_fullpaths[seqnum]
        wparams[FixParamTypes.SeqNum] = seqnum

        if fwrite.save_griddata_to_m11_no_meb(wparams):
            logger.info('write_data_m11 over %s' % (dst_fullpaths[seqnum]))
        else:
            logger.error('write_data_m11 error %s' % (dst_fullpaths[seqnum]))

    logger.info('write_data_m11 over')
    
def write_data_zczc(cfgobj, dst_fullpath, savedt, dst_datas, logger):
    logger.info('write_data_zczc start')
    
    savedt_ut = savedt - datetime.timedelta(hours=8)

    p = ZCZCWriter()
    p.set_params(dst_fullpath, cfgobj.savecfginfos[FixParamTypes.CCCC], savedt.strftime('%d%H%M'), None, \
        cfgobj.savecfginfos[FixParamTypes.ProductDesc], cfgobj.savecfginfos[FixParamTypes.ProductCode], \
        savedt_ut, len(cfgobj.stainfos[FixParamTypes.StaInfos]), dst_datas, \
        decimals=cfgobj.savecfginfos[FixParamTypes.Decimals], scale_decimals=cfgobj.savecfginfos[FixParamTypes.ScaleDecimals])

    #print('write start:', datetime.datetime.now())
    #p.write()
    #print('write end:', datetime.datetime.now())
    #print('write with line start:', datetime.datetime.now())
    p.write_with_line()
    #print('write with line end:', datetime.datetime.now())

    logger.info('write_data_zczc over')

def proc(cfgobj, etime, delta_t, logger, loglib):
    ffinfos = FixFileInfos(logger)
    frdata = FixReadData(logger)
    fwrite = FixWriteData(logger)
    
    save_e_time = etime+datetime.timedelta(minutes=cfgobj.savecfginfos[FixParamTypes.DFhsDelta])
    #数据的起报时时间
    save_dt = public.get_dt_with_fhs(save_e_time, cfgobj.savecfginfos[FixParamTypes.DFHS], delta_t)

    #从数据源中获取的数据，以多层字典形式存在，第一层key为配置文件中的section名字
    #value为以时效为key，xarray的格点数据为value的字典
    src_datas = {}

    #从数据源获得数据
    for srccfg in cfgobj.srccfglist:
        srclogger = loglib.getlogger(srccfg[FixParamTypes.DatasName])
        if srclogger is None:
            srclogger = logger

        if srccfg[FixParamTypes.FuncName] == ReadFuncNames.read_grid_bin:
            read_grid_bin(save_dt, srccfg, srccfg[FixParamTypes.DSeq], ffinfos, frdata, src_datas, cfgobj.stainfos[FixParamTypes.StaInfos], srclogger)
        elif srccfg[FixParamTypes.FuncName] == ReadFuncNames.read_grid_bin_wind_from_uv_to_ds:
            read_grid_bin_wind_from_uv_to_ds(save_dt, srccfg, srccfg[FixParamTypes.DSeq], ffinfos, frdata, src_datas, cfgobj.stainfos[FixParamTypes.StaInfos], srclogger)
        else:
            print('unknown read func')
            return

    #经过处理后的需要保存的数据，以时效为key，xarray的格点数据为value的字典
    dst_datas = {}
    
    #处理数据
    logger.info('proc start')

    for proccfg in cfgobj.proccfglist:
        pparams = procfunc.procfuncs.set_func_params(proccfg[FixParamTypes.FuncName], save_dt, proccfg, src_datas, \
            cfgobj.savecfginfos, dst_datas, logger, stainfos=cfgobj.stainfos[FixParamTypes.StaInfos])
        procfunc.procfuncs.run_func(proccfg[FixParamTypes.FuncName], pparams, logger)
        
    logger.info('proc over')

    #数据保存路径
    dst_dir = public.get_path_with_replace(cfgobj.savecfginfos[FixParamTypes.DDict], save_dt)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    dst_fullpath = os.path.join(dst_dir, public.get_path_with_replace(cfgobj.savecfginfos[FixParamTypes.DFnFmt], save_dt))

    #保存
    write_data_zczc(cfgobj, dst_fullpath, save_dt, dst_datas[FixParamTypes.GridData], logger)

    if cfgobj.savecfginfos[FixParamTypes.SaveHDF] == 1:
        logger.info('to_hdf start')

        dst_dir_hdf = public.get_path_with_replace(cfgobj.savecfginfos[FixParamTypes.DDictHDF], save_dt)
        if not os.path.exists(dst_dir_hdf):
            os.makedirs(dst_dir_hdf)

        dst_fullpath_hdf = os.path.join(dst_dir_hdf, public.get_path_with_replace(cfgobj.savecfginfos[FixParamTypes.DFnFmtHDF], save_dt))
        dst_datas[FixParamTypes.GridData].to_hdf(dst_fullpath_hdf, 'zczc', 'w', complevel=9)

        logger.info('to_hdf over')



if __name__ == '__main__':
    workdir = os.path.dirname(os.path.abspath(__file__))
    
    mainlogger = None

    logdir, logfile = public.get_path_infos(None, workdir=workdir, defaultdir=log_file_dir, defaultfn=log_file_name)

    init_log({ log_file_name:logfile }, loglib)
    mainlogger = loglib.getlogger(log_file_name)
    
    progparams = public.parse_prog_params()
    if progparams is None:
        print('program params error')
        mainlogger.error('program params error')
        sys.exit(1)

    if FixParamTypes.LogFilePath in progparams:
        loglib.uninit()

        logdir, logfile = public.get_path_infos(progparams[FixParamTypes.LogFilePath], workdir=workdir, defaultdir=log_file_dir, defaultfn=log_file_name)

        init_log({ log_file_name:logfile }, loglib)
        mainlogger = loglib.getlogger(log_file_name)

    cfgfiledir = None
    cfgfilepath = None
    if FixParamTypes.CfgFilePath in progparams:
        cfgfiledir, cfgfilepath = public.get_path_infos(progparams[FixParamTypes.CfgFilePath], workdir=workdir, defaultdir=cfg_file_dir, defaultfn=cfg_file_name)
    else:
        cfgfiledir, cfgfilepath = public.get_path_infos(None, workdir=workdir, defaultdir=cfg_file_dir, defaultfn=cfg_file_name)

    cfgobj = CfgMain(mainlogger)
    if cfgobj.parse(cfgfilepath) is None:
        #print('config ini params error')
        mainlogger.error('config ini params error')
        sys.exit(1)

    stapath = ''
    if os.path.isabs(cfgobj.stainfos[FixParamTypes.StaPath]):
        stapath = cfgobj.stainfos[FixParamTypes.StaPath]
    else:
        stapath = os.path.join(cfgfiledir, cfgobj.stainfos[FixParamTypes.StaPath])

    cfgobj.stainfos[FixParamTypes.StaInfos] = meb.read_station(stapath, keep_alt=True)

    #for srccfg in cfgobj.srccfglist:
    #    srclogdir, srclogfile = public.get_path_infos(srccfg[FixParamTypes.LogFilePath], workdir=logdir)
    #    init_log({ srccfg[FixParamTypes.DatasName]:srclogfile }, loglib)

    #如果没有参数，使用默认的fix_etime，否则使用参数运行程序
    #如果参数是一个时间段，默认往前找对应的起报时执行，否则按指定时间执行。
    if FixParamTypes.STime in progparams and FixParamTypes.ETime in progparams:
        if progparams[FixParamTypes.STime] is None:
            proc(cfgobj, fix_etime, delta_t, mainlogger, loglib)
        elif progparams[FixParamTypes.ETime] is None:
            fix_etime = progparams[FixParamTypes.STime]
            proc(cfgobj, fix_etime, delta_t, mainlogger, loglib)
        else:
            stime = progparams[FixParamTypes.STime]
            etime = progparams[FixParamTypes.ETime]
            etime = public.get_dt_with_fhs(etime, cfgobj.savecfginfos[FixParamTypes.DFHS], delta_t)
            while(stime <= etime):
                fix_etime = etime
                proc(cfgobj, fix_etime, delta_t, mainlogger, loglib)

                etime -= datetime.timedelta(minutes=delta_t)
                etime = public.get_dt_with_fhs(etime, cfgobj.savecfginfos[FixParamTypes.DFHS], delta_t)
    else:
        #fix_etime = datetime.datetime(2021,8,31,8)
        proc(cfgobj, fix_etime, delta_t, mainlogger, loglib)

    print('done')
