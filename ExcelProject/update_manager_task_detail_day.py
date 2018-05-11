# -*- coding:utf-8  -*-

import datetime
from ExcelProject.PyDBPool import PyDBPool  # 程序内

# from PyDBPool import PyDBPool  #服务器运行时去掉包名

"""
@updateMtdByDay()  按天更新工单信息

@task_detail_id 传入的工单id参数
@dbtype  数据库类型
         dbtype 默认mysql 
         需要指定sqlserver时,传入'mssql'

"""

"""
根据工单id 查询单条工单记录

ttime 工单时间
data  fault_datehour字段中的所有日期
mtdType1 工单类型   
mtdType3

"""


def getSingleMtdInfo(task_detail_id, dbpool):
    # 查询指定工单号的工单记录，如果不存在该记录 跳过
    mtd = dbpool.select(
        "select * from manager_task_detail where task_detail_id = %d and type1 != '%s'" % (task_detail_id, 'XN'))
    print("mtd = ", mtd)
    if len(mtd) == 0:
        print('请检查输入的工单号是否正确!')
        exit()
    ttime = mtd[0][2]
    print("ttime = ", ttime)
    tabeleDataDate = dbpool.select(
        "SELECT * FROM DATA_DATE where ttime='%s' AND thour = '23'" % (ttime))
    print("tabeleDataDate = ", tabeleDataDate)
    if len(tabeleDataDate) == 0:
        print('请检查输入表DATA_DATE中的ttime字段的日期是否与工单记录中的ttime字段的日期一致!')
        exit()
    # 取出当前工单号中的日期和时间
    list_date = []
    fault_datehour = mtd[0][36]
    dates = fault_datehour.split(';')
    for y in dates:
        dates = y.split(':')[0]
        list_date.append(dates)
    print('list_date = ', list_date)
    defCellname = mtd[0][4]
    # todo 取出记录
    mtdType1 = mtd[0][13]
    mtdType3 = mtd[0][15]

    return mtd, ttime, list_date, defCellname, mtdType1, mtdType3


"""
PROPERTIES_DB	小区属性库
manager_task_detail 与 PROPERTIES_DB 关联 取出 小区名一样且日期在mtd的date_list中的数据
"""


def getTablePropertiesDb(dbpool, dbtype, defCellname, list_date):
    if dbtype == 'mysql':
        tablePropertiesDb = dbpool.select(
            "select pd.DEF_CELLNAME,pd.TYPE1,pd.TYPE3,pd.TTIME,pd.FAULT_DESCRIPTION,pd.LABEL,pd.THOUR,pd.LEVEL_R,pd.FAULT_OBJECT FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME = '%s' and pd.TTIME in (%s) " % (
                (defCellname),
                (','.join((map(lambda x: repr(x), list_date))))))
    else:
        # 由于varchar对中文支持不友好,使用mssql读取sqlserver的中文时出现乱码,需要使用conver进行转换
        tablePropertiesDb = dbpool.select(
            "select pd.DEF_CELLNAME,convert(nvarchar(255),pd.TYPE1),convert(nvarchar(255),pd.TYPE3),pd.TTIME,convert(nvarchar(255),pd.FAULT_DESCRIPTION),convert(nvarchar(255),pd.LABEL),pd.THOUR,convert(nvarchar(255),pd.LEVEL_R),convert(nvarchar(255),pd.FAULT_OBJECT) FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME = '%s' and pd.TTIME in (%s) " % (
                (defCellname),
                (','.join((map(lambda x: repr(x), list_date))))))

    print("tablePropertiesD = :", tablePropertiesDb)
    print("tablePropertiesDb length = ", len(tablePropertiesDb))
    return tablePropertiesDb


"""
import_reason	工单、原因、方案预配置
manager_task_detail 与 import_reason 关联 取出 type1 与 type3 一致的数据
"""


def getTableImportReason(dbpool, dbtype, mtdType1, mtdType3):
    if dbtype == 'mysql':
        tableImportReason = dbpool.select(
            "select * from import_reason as ir where ir.type1 = '%s' and INSTR(ir.representation,'%s') > 0" % (
                mtdType1, mtdType3))
    else:
        tableImportReason = dbpool.select(
            "select * from import_reason as ir where ir.type1 = '%s' and charindex(ir.representation,'%s') > 0" % (
                mtdType1, mtdType3))
    print("tableImportReason = ", tableImportReason)
    print("tableImportReason length = ", len(tableImportReason))
    return tableImportReason


"""
关联条件如下:
@table_properties_db.type3 = @table_import_reason.reason
@table_properties_db.LEVEL_R = @table_import_reason.LEVEL_R 

取出以下字段

@table_properties_db.ttime
@table_properties_db.thour
@table_import_reason.priority
@table_import_reason.suggest
@table_import_reason.reason 
@table_import_reason.importantreason

"""


def getReasonSuggest(tablePropertiesDb, tableImportReason):
    reasonSuggest = []
    for x in tablePropertiesDb:
        pdType3 = x[2]
        pdLevelR = x[7]
        for y in tableImportReason:
            irReason = y[1]
            irLevelR = y[2]
            irImportantreason = y[4]

            if (pdType3 == irReason) and (pdLevelR == irLevelR) and (irImportantreason != 0):
                rs = []
                rs.append(x[3])
                rs.append(x[6])
                rs.append(y[3])
                rs.append(y[5])
                rs.append(y[1])
                rs.append(y[4])
                reasonSuggest.append(tuple(rs))
    print("reasonSuggest", reasonSuggest)
    return reasonSuggest


def getNewMtd(reasonSuggestMergeDate, mtd):
    newMtd = []
    for x in reasonSuggestMergeDate.keys():
        reason = x[0]
        suggest = x[1]

        # 取出元组中的单条工单记录
        singleMtd = list(mtd[0])

        # 依次更新单条工单记录中的 cellquestion cellproject cellsuggest 字段中的内容
        singleMtd[27] = reason
        singleMtd[28] = suggest
        singleMtd[25] = '小区关键问题原因是：' + reason + '\r优化建议方案：' + suggest

        # 将修改后的记录放入一个新的集合
        newMtd.append(singleMtd)

    print('newMtd :', newMtd)
    print('newMtd的长度 = ', len(newMtd))  # 4条测试数据
    return newMtd


def getMtdSF(newMtd):
    mtdSF = []
    for i in newMtd:  # 如何上面的更新不满足更新条件 则 mtdSF =  mtd
        type1 = i[13]
        cellquestion = i[27]
        print('type1 = %s, cellquestion = %s' % (type1, cellquestion))
        if type1 in ('SFXN', 'SFLH') and cellquestion == '':
            mtdSF.append(i)

    print('mtdSF = ', mtdSF)
    print('mtdSF Length= ', len(mtdSF))
    return mtdSF


"""
PI_CELL  小区性能表
取出10条小区性能数据
"""


def getTablePiCell(dbpool, dbtype):
    if dbtype == 'mysql':
        tablePiCell = dbpool.select(
            "select TTIME,DEF_CELLNAME,PI378 from PI_CELL  where (PI55 + PI56) = 0 and pi378 >=0;")
    else:
        tablePiCell = dbpool.select(
            "SELECT TTIME,DEF_CELLNAME,PI378 FROM pi_cell WHERE (CONVERT(FLOAT, pi55) + CONVERT(FLOAT, pi56)) = 0 AND CONVERT(FLOAT, pi378) >= 0")

    print('tablePiCell = ', tablePiCell)
    print('tablePiCell Length = ', len(tablePiCell))
    return tablePiCell


def getNewMtdCell(tablePiCell, mtdSF):
    newMtdCell = []

    for x in tablePiCell:  # 5
        x = list(x)
        xttime = x[0]
        xdefCellname = x[1]
        pi378 = float(x[2])

        for y in mtdSF:  # 3
            y = list(y)
            yttime = y[2]
            ydefCellname = y[4]

            if xttime == yttime and xdefCellname == ydefCellname:
                # todo
                # 更新操作 cellquestion cellproject cellsuggest
                if pi378 > 0:
                    y[27] = '可能设备隐性故障或设备遭破坏'
                    y[28] = '现场测试并对室分设备进行检查。'
                    y[25] = '小区关键问题原因是：可能设备隐性故障或设备遭破坏。\r优化建议方案：现场测试并对室分设备进行检查。'
                else:
                    y[27] = '小区无用户'
                    y[28] = '现场测试并对室分设备进行检查。'
                    y[25] = '小区关键问题原因是：小区无用户。\r优化建议方案：现场测试并对室分设备进行检查。'

                newMtdCell.append(y)

    print('newMtdCell =', newMtdCell)
    print('newMtdCell Length=', len(newMtdCell))
    return newMtdCell


def getNewMtdCellNoReason(newMtdCell):
    newMtdCellNoReason = []

    for i in newMtdCell:
        i = list(i)

        type3 = i[15]
        type1 = i[13]
        # print('type1 = ', type1)
        # print('type3 = ', type3)

        # cellquestion
        if type3 in ('严重弱覆盖小区',
                     '近端弱覆盖小区'):

            i[27] = '疑似小区天线挂高过低，机械下倾角过大或者小区覆盖方向存在阻挡。'
        elif type3 in (
                '远端弱覆盖小区'
                , '过覆盖'
                , '下行严重弱覆盖小区'
                , '下行弱覆盖小区'
        ):
            i[27] = '疑似小区天线挂高过高，机械下倾角过小或者小区站间距过大。'
        elif type3 == '室分弱覆盖小区':
            i[27] = '疑似室分分布系统故障或分布不合理。'

        elif type3 in (
                '重叠覆盖且高质差宏站小区'
                , '重叠覆盖'
        ):
            i[27] = '疑似小区或邻区工参不合理。'

        elif type1 == 'MR':
            i[27] == '系统并未发现影响小区覆盖的原因。'
        else:
            i[27] = '系统未发现影响小区性能的原因。'

        # cellproject
        if type3 in ('严重弱覆盖小区',
                     '近端弱覆盖小区'):
            i[28] = '疑似小区天线挂高过低，机械下倾角过大或者小区覆盖方向存在阻挡。'
        elif type3 in (
                '远端弱覆盖小区'
                , '过覆盖'
                , '下行严重弱覆盖小区'
                , '下行弱覆盖小区'
        ):
            i[28] = '疑似小区天线挂高过高，机械下倾角过小或者小区站间距过大。'
        elif type3 == '室分弱覆盖小区':
            i[28] = '疑似室分分布系统故障或分布不合理。'

        elif type3 in (
                '重叠覆盖且高质差宏站小区'
                , '重叠覆盖'
        ):
            i[28] = '疑似小区或邻区工参不合理。'

        elif type1 == 'MR':
            i[28] == '请到现场排查是否存在阻挡、站高和下倾角是否合理或其他原因导致。'
        else:
            i[28] = '需继续观察指标，或现场测试及对基站硬件进行排查。'

        # cellsuggest
        if type3 in ('严重弱覆盖小区',
                     '近端弱覆盖小区'):
            i[25] = '疑似小区天线挂高过低，机械下倾角过大或者小区覆盖方向存在阻挡。'
        elif type3 in (
                '远端弱覆盖小区'
                , '过覆盖'
                , '下行严重弱覆盖小区'
                , '下行弱覆盖小区'
        ):
            i[25] = '疑似小区天线挂高过高，机械下倾角过小或者小区站间距过大。'
        elif type3 == '室分弱覆盖小区':
            i[25] = '小区关键问题原因是：疑似室分分布系统故障或分布不合理。\r优化建议方案：现场测试基站是否存在故障，室内分布否合理。'

        elif type3 in (
                '重叠覆盖且高质差宏站小区'
                , '重叠覆盖'
        ):
            i[25] = '小区关键问题原因是：疑似小区或邻区工参不合理。\r优化建议方案：现场测试基站工程参数是否合理。'

        elif type1 == 'MR':
            i[25] == '小区关键问题原因是：系统并未发现影响小区覆盖的原因。\r优化建议方案：请到现场排查是否存在阻挡、站高和下倾角是否合理或其他原因导致。'
        else:
            i[25] = '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。'

        newMtdCellNoReason.append(i)
    print('newMtdCellNoReason = ', newMtdCellNoReason)
    print('newMtdCellNoReason Length = ', len(newMtdCellNoReason))
    return newMtdCellNoReason


"""
 lte_lhxq_white  LTE劣化小区白名单
 查询白名单中的小区名
"""


def getTableMtdWhite(dbpool, dbtype):
    if dbtype == 'mysql':
        tableMtdWhite = dbpool.select("select CELL_NAME from lte_lhxq_white limit 3;")
    else:
        tableMtdWhite = dbpool.select("select top 3 convert(nvarchar(255),CELL_NAME) as CELL_NAME from lte_lhxq_white;")
    print("白名单列表 = ", tableMtdWhite)
    print("白名单列表长度 = ", len(tableMtdWhite))
    return tableMtdWhite


def getUpdateupdateMtdWhite(tableMtdWhite, newMtdCellNoReason):
    updateMtdWhite = []
    for i in tableMtdWhite:
        idefCellname = i[0]
        # print('idefCellname = ',idefCellname)
        for j in newMtdCellNoReason:
            jdefCellnameChinese = j[6]
            # print('jdefCellnameChinese = ',jdefCellnameChinese)
            if jdefCellnameChinese == idefCellname:
                # 更新 cellproject = cellproject + '\r本小区属于白名单小区，建议不下派工单。'
                j[28] = j[28] + '\r本小区属于白名单小区，建议不下派工单。'
                updateMtdWhite.append(j)
    print('updateMtdWhite = ', updateMtdWhite)
    print('updateMtdWhite Length = ', len(updateMtdWhite))
    return updateMtdWhite


def getUpdateMtdWhiteOnce(tablePropertiesDb, updateMtdWhite):
    updateMtdWhiteOnce = []

    # print("tablePropertiesDb length = ", len(tablePropertiesDb))
    for y in tablePropertiesDb:  # 14
        y = list(y)
        ydefCellname = y[0]
        yttime = y[3]

        # # 模拟 tablePropertiesDb - type3 = '相关小区故障'
        # y[2] = '相关小区故障'
        ytype3 = y[2]
        yfaultDescription = y[4]
        for x in updateMtdWhite:  # 3
            x = list(x)
            xdefCellname = x[4]
            xttime = x[2]
            xtype3 = x[15]

            # # 模拟 mtd cellquestion = '相关小区故障'
            # x[27] = '相关小区故障'
            xcellquestion = x[27]

            # print('xdefCellname = ',xdefCellname)
            # print('ydefCellname = ',ydefCellname)
            # print('xttime = ',xttime)
            # print('yttime = ',yttime)
            # print('ytype3 =',ytype3)
            # print('xcellquestion =',xcellquestion)

            if xdefCellname == ydefCellname and xttime == yttime and ytype3 == '相关小区故障' and '相关小区故障' in xcellquestion:
                # 更新cellproject
                x[28] = x[28].replace('建议处理相关小区故障', '建议处理' + yfaultDescription)
                updateMtdWhiteOnce.append(x)

    print('updateMtdWhiteOnce = ', updateMtdWhiteOnce)
    print('updateMtdWhiteOnce length = ', len(updateMtdWhiteOnce))
    return updateMtdWhiteOnce


"""
根据type3 筛选 小区属性表 PROPERTIES_DB
"""


def getTablePropertiesDbByType(dbpool, dbtype):
    tablePropertiesDbByType = dbpool.select(
        "select DEF_CELLNAME,TTIME,FAULT_OBJECT from PROPERTIES_DB where TYPE1 = '%s' and TYPE3='%s'" % (
            'MR', '覆盖方向需调整'))  # 大约80行

    print('tablePropertiesDbByType = ', tablePropertiesDbByType)
    print('tablePropertiesDbByType length = ', len(tablePropertiesDbByType))
    return tablePropertiesDbByType


def getUpdateMtdWhiteTwice(tablePropertiesDbByType, updateMtdWhiteOnce):
    updateMtdWhiteTwice = []
    for x in tablePropertiesDbByType:
        xfaultObject = x[2]
        xdefCellname = x[0]
        xttime = x[1]

        # print('xdefcellname = ', xdefCellname)
        # print('xttime = ', xttime)

        for y in updateMtdWhiteOnce:
            yttime = y[2]
            ydefCellname = y[4]
            ycellquestion = y[27]

            # print('ydefCellname = ', ydefCellname)
            # print('yttime = ', yttime)
            # print('ycellquestion = ', ycellquestion)

            if xdefCellname == ydefCellname and xttime == yttime and '覆盖方向需调整' in ycellquestion:
                ycellproject = y[28]
                if ('建议调整方向角' in ycellproject):
                    re = '建议处理相关小区故障'
                else:
                    re = '建议处理' + xfaultObject

                y[28] = y[28].replace('覆盖方向需调整', re)

                updateMtdWhiteTwice.append(y)
    print("updateMtdWhiteTwice = ", updateMtdWhiteTwice)
    print("updateMtdWhiteTwice Length = ", len(updateMtdWhiteTwice))
    return updateMtdWhiteTwice


def updateMtd(dbpool, mtdFinally):
    for x in mtdFinally:
        # print("x = ", x)

        xcellquestion = x[27]
        xcellproject = x[28]
        xcellsuggest = x[25]
        xtypePro = x[37]

        updateMtdSql = "update manager_task_detail set cellquestion = '%s',cellproject = '%s',cellsuggest= '%s',Type_pro='%s' where TASK_DETAIL_ID = %d" % (
            xcellquestion, xcellproject, xcellsuggest, xtypePro, task_detail_id)
        dbpool.update(updateMtdSql)

        # if (dbpool.update(updateMtdSql) > 0):
        #     print("成功更新一条工单记录!")


def getReasonSuggestMergeDate(reasonSuggestMatch):
    rsDict = {}
    for x in reasonSuggestMatch:
        dhList = []
        reason = x[4]
        suggest = x[3]
        date = x[0]
        hour = x[1]
        rs = (reason, suggest)

        if rs not in rsDict:
            dhList.append(date + ':' + hour)
            rsDict[rs] = dhList
        else:
            if date in rsDict[rs][0]:
                if 'AllDay' not in rsDict[rs][0]:
                    rsDict[rs][0] = rsDict[rs][0] + (',' + hour)
            else:
                rsDict[rs][0] = rsDict[rs][0] + (';' + date + ':' + hour)
    return rsDict


def updateMtdByDay(task_detail_id, dbtype):
    # 初始化数据库连接池对象
    dbpool = PyDBPool(dbtype)

    # 查询manager_task_detail表
    mtd, ttime, list_date, defCellname, mtdType1, mtdType3 = getSingleMtdInfo(task_detail_id, dbpool)

    # mtd =  [(1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #        'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #        '小区关键问题原因是：X2接口故障告警\\r阻塞干扰\\r\\r优化建议方案：建议处理X2接口故障告警故障\\r建议检查基站硬件\\现场扫频\\r', '', '系统未发现影响小区性能的原因。',
    #        '需继续观察指标，或现场测试及对基站硬件进行排查。', '9102890920160310165244ms2', '', '', '', '', '', '',
    #        '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
    #        None, None, None)]

    # 模拟满足mtdSF的数据，
    # type1 in ('SFLH','SFLX')  cellquestion = ''
    # def_cellchiese
    # type3 相关小区故障
    mtd = [(1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳衡东县大托HLD3900256532PT-3', '衡阳', '石鼓区', '', '', '', '',
            'SFXN', '自动', '相关小区故障', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
            '小区关键问题原因是：X2接口故障告警\\r阻塞干扰\\r\\r优化建议方案：建议处理X2接口故障告警故障\\r建议检查基站硬件\\现场扫频\\r', '', '',
            '需继续观察指标，或现场测试及对基站硬件进行排查。', '9102890920160310165244ms2', '', '', '', '', '', '',
            '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
            None, None, None)]

    # 从小区属性表PROPERTIES_DB取出关联数据
    tablePropertiesDb = getTablePropertiesDb(dbpool, dbtype, defCellname, list_date)

    # 从工单,原因表import_reason取出关联数据
    tableImportReason = getTableImportReason(dbpool, dbtype, mtdType1, mtdType3)

    # tablePropertiesDb 和 tableImportReason 集合关联,保存满足条件的变量
    # 元素样式 ('2017-03-26', '11', 400, '建议降低小区的发射功率', '室分功率参数不合理', 1)
    reasonSuggest = getReasonSuggest(tablePropertiesDb, tableImportReason)
    if len(reasonSuggest) == 0: return

    # reasonSuggest[('2016-02-01', '19,20,21,22,23', 20, '建议处理【衍生告警】LTE基站BASE STATION FAULTY故障', '外部干扰', 1), (
    # '2016-02-02', '00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22', 20,
    # '建议处理【衍生告警】LTE基站BASE STATION FAULTY故障', '外部干扰', 1), (
    #               '2016-02-02', 'AllDay', 116, '建议处理【衍生告警】华为GSM同一基站同时产生多条射频类告警故障', 'X2接口故障告警', 1), (
    #               '2016-02-02', 'AllDay', 108, '', 'X2接口故障告警', 1), (
    #               '2016-02-02', 'AllDay', 84, '建议处理【衍生告警】诺西LTE同一网元同时产生多条小区类告警故障', 'X2接口故障告警', 1), (
    #               '2016-02-02', 'AllDay', 91, '建议处理【衍生告警】普天TD同一网元同时产生多条RRU告警故障', 'X2接口故障告警', 1)]

    # 按priority升序排列 取top5 并去重
    reasonSuggestMatch = sorted(list(set(reasonSuggest)), key=lambda x: x[2])[0:5]

    # reasonSuggestMatch = [('2016-02-02', '00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22', 20,
    #                        '建议处理【衍生告警】LTE基站BASE STATION FAULTY故障', '外部干扰', 1),
    #                       ('2016-02-01', '19,20,21,22,23', 20, '建议处理【衍生告警】LTE基站BASE STATION FAULTY故障', '外部干扰', 1),
    #                       ('2016-02-02', 'AllDay', 84, '建议处理【衍生告警】诺西LTE同一网元同时产生多条小区类告警故障', 'X2接口故障告警', 1),
    #                       ('2016-02-02', 'AllDay', 108, '', 'X2接口故障告警', 1),
    #                       ('2016-02-02', 'AllDay', 116, '建议处理【衍生告警】华为GSM同一基站同时产生多条射频类告警故障', 'X2接口故障告警', 1)]

    print("reasonSuggestMatch:", reasonSuggestMatch)

    # 把相同的suggest,reason记录里面日期和小时合并到一起

    reasonSuggestMergeDate = getReasonSuggestMergeDate(reasonSuggestMatch)
    print('reasonSuggestMergeDate = ', reasonSuggestMergeDate)

    # reasonSuggestMergeDate = {('外部干扰', '建议处理【衍生告警】LTE基站BASE STATION FAULTY故障'): [
    #     '2016-02-02:00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22;2016-02-01:19,20,21,22,23'],
    #                           ('X2接口故障告警', '建议处理【衍生告警】诺西LTE同一网元同时产生多条小区类告警故障'): ['2016-02-02:AllDay'],
    #                           ('X2接口故障告警', '建议处理【衍生告警】普天TD同一网元同时产生多条RRU告警故障'): ['2016-02-02:AllDay'],
    #                           ('X2接口故障告警', ''): ['2016-02-02:AllDay']}

    # 模拟满足mtdSF条件的数据  cellquestion = ''
    # reasonSuggestMergeDate = {('', '建议处理【衍生告警】LTE基站BASE STATION FAULTY故障'): [
    #     '2016-02-02:00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22;2016-02-01:19,20,21,22,23'],
    #     ('', '建议处理【衍生告警】诺西LTE同一网元同时产生多条小区类告警故障'): ['2016-02-02:AllDay'],
    #     ('', '建议处理【衍生告警】普天TD同一网元同时产生多条RRU告警故障'): ['2016-02-02:AllDay'],
    #     ('X2接口故障告警', ''): ['2016-02-02:AllDay']}

    # mtd保存cellquestion IS NULL AND  cellproject IS NULL为空的工单
    # 更新 mtd的变量里面的内容
    # 关联  reasonSuggestMerge 和 mtd  更新原因,建议,Type_pro 将更新后的内容保存到newMtd集合中
    # 关联两个临时表, 更新原因, 建议, Type_pro
    newMtd = getNewMtd(reasonSuggestMergeDate, mtd)

    # newMtd: [
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：\r优化建议方案：建议处理【衍生告警】LTE基站BASE STATION FAULTY故障', '', '', '建议处理【衍生告警】LTE基站BASE STATION FAULTY故障',
    #      '9102890920160310165244ms2', '', '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None,
    #      None, None, '·ñ', None, None, None, '5.07', None, None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：\r优化建议方案：建议处理【衍生告警】诺西LTE同一网元同时产生多条小区类告警故障', '', '', '建议处理【衍生告警】诺西LTE同一网元同时产生多条小区类告警故障',
    #      '9102890920160310165244ms2', '', '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None,
    #      None, None, '·ñ', None, None, None, '5.07', None, None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：\r优化建议方案：建议处理【衍生告警】普天TD同一网元同时产生多条RRU告警故障', '', '', '建议处理【衍生告警】普天TD同一网元同时产生多条RRU告警故障',
    #      '9102890920160310165244ms2', '', '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None,
    #      None, None, '·ñ', None, None, None, '5.07', None, None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：X2接口故障告警\r优化建议方案：', '', 'X2接口故障告警', '', '9102890920160310165244ms2', '', '', '', '', '', '',
    #      '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
    #      None, None, None]]

    # 室分性能,室分劣化 cellquestion IS NULL 更新
    # type1 13
    # type3 15

    # cellquestion 27
    # cellproject 28
    # cellsuggest 25

    # picell- pi378 393
    # picell-ttime 12
    # picell- def_cellname 5

    # 过滤newMtd中的数据 取出type1 in ('SFXN','SFLH') and cellquestion is null 的记录 放入新集合mtdSF
    mtdSF = getMtdSF(newMtd)

    # type1 in ('SFXN','SFLH')  cellquesion = ''
    # mtdSF = [
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：\r优化建议方案：建议处理【衍生告警】LTE基站BASE STATION FAULTY故障', '', '', '建议处理【衍生告警】LTE基站BASE STATION FAULTY故障',
    #      '9102890920160310165244ms2', '', '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None,
    #      None, None, '·ñ', None, None, None, '5.07', None, None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：\r优化建议方案：建议处理【衍生告警】诺西LTE同一网元同时产生多条小区类告警故障', '', '', '建议处理【衍生告警】诺西LTE同一网元同时产生多条小区类告警故障',
    #      '9102890920160310165244ms2', '', '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None,
    #      None, None, '·ñ', None, None, None, '5.07', None, None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：\r优化建议方案：建议处理【衍生告警】普天TD同一网元同时产生多条RRU告警故障', '', '', '建议处理【衍生告警】普天TD同一网元同时产生多条RRU告警故障',
    #      '9102890920160310165244ms2', '', '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None,
    #      None, None, '·ñ', None, None, None, '5.07', None, None, None, None]]

    # 查询PI_CELL小区性能表 取出全部数据(这里仅取10条做测试)
    tablePiCell = getTablePiCell(dbpool, dbtype)

    # 工单记录中的def_cellname与PI_CELL中的def_cellname的样式不一样? 关联不到数据!
    #                 ttime          def_cellname                                       pi378
    # tablePiCell = [('2015-12-05', 'oss1-YUYXYjunyuejiudianEL-R6601467726PT-1-4677261', '0.0'),
    #                ('2015-12-04', 'oss1-YUYPJsandunxiaodongcunEL-R6601258755PT-1-2587551', '0.0'),
    #                ('2015-12-04', 'oss1-YUYMLgaotiechezhanEL-R6601258476PT-1-2584762', '0.0'),
    #                ('2015-12-05', 'oss1-YUYPJxianchonghuanghuacunEL-R6601774667PT-1-7746671', '0.0'),
    #                ('2015-12-05', 'oss1-YUYjinghuwanEL-R6601467499PT-1-4674992', '0.0')]

    # 模拟合适的tablePiCell数据  日期改为'2016-02-02' 小区名改为'1-20799-1-133'

    newTableCell = []
    for t in tablePiCell:
        t = list(t)
        t[0] = '2016-02-02'
        t[1] = '1-20799-1-133'
        newTableCell.append(t)

    tablePiCell = newTableCell
    print('NewtablePiCell = ', tablePiCell)

    # NewtablePiCell = [['2016-02-02', '1-20799-1-133', '0.0']]

    # 室分性能,室分劣化
    newMtdCell = []
    if len(mtdSF) == 0:
        mtdSF = newMtd
    newMtdCell = getNewMtdCell(tablePiCell, mtdSF)  # cellquestion cellproject cellsuggest 更新后 数据都一致！

    # newMtdCell = [
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：小区无用户。\r优化建议方案：现场测试并对室分设备进行检查。', '', '小区无用户', '现场测试并对室分设备进行检查。', '9102890920160310165244ms2', '',
    #      '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None,
    #      None, '5.07', None, None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：小区无用户。\r优化建议方案：现场测试并对室分设备进行检查。', '', '小区无用户', '现场测试并对室分设备进行检查。', '9102890920160310165244ms2', '',
    #      '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None,
    #      None, '5.07', None, None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：小区无用户。\r优化建议方案：现场测试并对室分设备进行检查。', '', '小区无用户', '现场测试并对室分设备进行检查。', '9102890920160310165244ms2', '',
    #      '', '', '', '', '', '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None,
    #      None, '5.07', None, None, None, None]]

    # 系统未发现原因的更新 todo
    newMtdCellNoReason = []
    if len(newMtdCell) == 0:
        newMtdCell = mtdSF
    newMtdCellNoReason = getNewMtdCellNoReason(newMtdCell)

    # newMtdCellNoReason = [
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。', '', '系统未发现影响小区性能的原因。',
    #      '需继续观察指标，或现场测试及对基站硬件进行排查。', '9102890920160310165244ms2', '', '', '', '', '', '',
    #      '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
    #      None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。', '', '系统未发现影响小区性能的原因。',
    #      '需继续观察指标，或现场测试及对基站硬件进行排查。', '9102890920160310165244ms2', '', '', '', '', '', '',
    #      '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
    #      None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳市区雁北监狱HLD3900256417PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。', '', '系统未发现影响小区性能的原因。',
    #      '需继续观察指标，或现场测试及对基站硬件进行排查。', '9102890920160310165244ms2', '', '', '', '', '', '',
    #      '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
    #      None, None, None]]

    # 查询白名单
    tableMtdWhite = getTableMtdWhite(dbpool, dbtype)
    #
    # 白名单列表 = [('衡阳衡东县京珠高速雁城服务区HLD3900776297PT-23',), ('长沙浏关口杨溪湖(共电信)HL-D3900983086PT-132',),
    #          ('衡阳衡东县大托HLD3900256532PT-3',)]

    # 更新白名单(关联mtd 更新工单记录中的cellproject字段内容)
    updateMtdWhite = []
    if len(newMtdCellNoReason) == 0:
        newMtdCellNoReason = newMtdCell
    updateMtdWhite = getUpdateupdateMtdWhite(tableMtdWhite, newMtdCellNoReason)

    # updateMtdWhite = [
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳衡东县大托HLD3900256532PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。', '', '系统未发现影响小区性能的原因。',
    #      '需继续观察指标，或现场测试及对基站硬件进行排查。\r本小区属于白名单小区，建议不下派工单。', '9102890920160310165244ms2', '', '', '', '', '', '',
    #      '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
    #      None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳衡东县大托HLD3900256532PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。', '', '系统未发现影响小区性能的原因。',
    #      '需继续观察指标，或现场测试及对基站硬件进行排查。\r本小区属于白名单小区，建议不下派工单。', '9102890920160310165244ms2', '', '', '', '', '', '',
    #      '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
    #      None, None, None],
    #     [1, None, '2016-02-02', '', '1-20799-1-133', '171', '衡阳衡东县大托HLD3900256532PT-3', '衡阳', '石鼓区', '', '', '', '',
    #      'SFXN', '自动', 'CSFB指标', '问题符合低接入最差小区筛选规则', '0', 'admin', '22', '', 3, 16, '', '',
    #      '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。', '', '系统未发现影响小区性能的原因。',
    #      '需继续观察指标，或现场测试及对基站硬件进行排查。\r本小区属于白名单小区，建议不下派工单。', '9102890920160310165244ms2', '', '', '', '', '', '',
    #      '2016-02-01:13,23;2016-02-02:22', None, None, None, None, None, None, '·ñ', None, None, None, '5.07', None,
    #      None, None, None]]

    # 以下所有语句是更新更具体的建议cellproject, 接下来两次更新白名单   两次更新应该是或的关系！
    # 第一次  关联条件  xdefCellname == ydefCellname and xttime == yttime and ytype3 == '相关小区故障' and '相关小区故障' in xcellquestion:
    updateMtdWhiteOnce = []
    if len(updateMtdWhite) == 0:
        updateMtdWhite = newMtdCellNoReason
    updateMtdWhiteOnce = getUpdateMtdWhiteOnce(tablePropertiesDb, updateMtdWhite)

    # 查询PROPERTIES_DB  根据type3 筛选 小区属性表 PROPERTIES_DB
    tablePropertiesDbByType = getTablePropertiesDbByType(dbpool, dbtype)

    # 第二次更新
    # 第二次 关联条件 xdefCellname == ydefCellname and xttime == yttime and '覆盖方向需调整' in ycellquestion:
    updateMtdWhiteTwice = []
    if len(updateMtdWhiteOnce) == 0:
        updateMtdWhiteOnce = updateMtdWhite
    updateMtdWhiteTwice = getUpdateMtdWhiteTwice(tablePropertiesDbByType, updateMtdWhiteOnce)

    # updateMtdWhiteTwice = [(6, None, '2017-03-26', None, '1-19905-1-130', '29', '北部新区海州国际公寓灯杆F-HLHB', '重庆', '其它', 'null',
    #                   'null', None, None, 'SFXN', '自动', '高掉线小区', '问题符合高掉线小区筛选规则', '3', 'admin', '07', '', 3, 13, None,
    #                   '',
    #                   '小区关键问题原因是：互调干扰,发生时间：2017-03-26:03,04,05,06,07,08,09,10,关联系数：0.4\\r\\r优化建议方案：GSM900：2f1、f1+f2，DCS1800:2f1-f140且自身互调性能较差\\r',
    #                   None, '', '建议排查周边存在电信联通FDD使用2024MHz频段，自身接收机性能较差；设备故障；周边存在干扰器开启等\\r', None, None, None, None, None,
    #                   None, None, '2017-03-25:00,01,03,04,05,06,07,12,15;2017-03-26:04,05,06,07', None, None, None,
    #                   None, None, None, None, None, None, None, None, None, None, None)]

    # 将上述所有对数据的操作更新到 manager_task_detail ,更新的是detail表中的四个字段  cellquestion cellproject cellsuggest type_pro

    if len(updateMtdWhiteTwice) == 0:
        updateMtdWhiteTwice = updateMtdWhiteOnce

    print("mtdFinally = ", updateMtdWhiteTwice)
    print("mtdFinally Length = ", len(updateMtdWhiteTwice))
    print("执行更新工单操作...")
    updateMtd(dbpool, updateMtdWhiteTwice)


if __name__ == '__main__':
    # task_detail_id = 4379 # mysql
    task_detail_id = 1  # mssql

    starttime = datetime.datetime.now()
    print('starttime = ', starttime)

    updateMtdByDay(task_detail_id, 'mssql')
    endtime = datetime.datetime.now()

    print('endtime = ', endtime)
    print('endtime - starttime = ', (endtime - starttime).seconds)
