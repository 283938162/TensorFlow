# -*- coding:utf-8  -*-

from ExcelProject.PyDBPool import PyDBPool


"""
@updateMtdByDay()  按天更新工单信息

@task_detail_id 传入的工单id参数
@dbtype 数据库类型 mysql 或者 mssql

"""

def updateMtdByDay(task_detail_id, dbtype):

    # 初始化数据库连接池对象
    dbpool = PyDBPool(dbtype)

    if task_detail_id is None:
        print("工单号为空")
        return

    # 查询指定工单号的工单记录，如果不存在该记录 跳过
    mtd = dbpool.select(
        "select * from manager_task_detail where task_detail_id = %d and type1 != '%s'" % (task_detail_id, 'XN'))
    print("mtd:", mtd)
    if len(mtd) == 0: return
    ttime = mtd[0][2]
    print("ttime:", ttime)

    result2 = dbpool.select(
        "SELECT * FROM DATA_DATE where ttime='%s' AND thour = '23'" % (ttime))
    print("result2", result2)
    if len(result2) == 0: return

    # 取出当前工单号中的日期和时间
    list_date = []
    list_hour = []
    fault_datehour = mtd[0][36]
    dates = fault_datehour.split(';')
    for y in dates:
        dates = y.split(':')[0]
        hours = y.split(':')[1:]

        print(dates)
        # print(hours)

        list_date.append(dates)
        # list_hour.append(hours)

    print('fault_datehour:', fault_datehour)

    print("list_date:", list_date)  # list_date: ['2017-03-25', '2017-03-26']
    # print("list_hour:", list_hour)  # list_hour: [['00,01,03,04,05,06,07,12,15'], ['04,05,06,07']]

    # 从属性数据库PROPERTIES_DB取出相关数据

    defCellname = mtd[0][4]
    print("defCellname:", defCellname)

    tablePropertiesDb = dbpool.select(
        "select pd.DEF_CELLNAME,pd.TYPE1,pd.TYPE3,pd.TTIME,pd.FAULT_DESCRIPTION,pd.LABEL,pd.THOUR,pd.LEVEL_R,pd.FAULT_OBJECT FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME = '%s' and pd.TTIME in (%s) " % (
            (defCellname),
            (','.join((map(lambda x: repr(x), list_date))))))

    print("tablePropertiesDb:", tablePropertiesDb)

    # 去除result3中不符合条件的记录

    # todo 取出记录
    mtdType1 = mtd[0][13]
    mtdType3 = mtd[0][15]

    print('mtdType1:', mtdType1)

    if dbtype == 'mysql':
        tableImportReason = dbpool.select(
            "select * from import_reason as ir where ir.type1 = '%s' and INSTR(ir.representation,'%s') > 0" % (
                mtdType1, mtdType3))
    else:
        tableImportReason = dbpool.select(
            "select * from import_reason as ir where ir.type1 = '%s' and charindex(ir.representation,'%s') > 0" % (
                mtdType1, mtdType3))

    print("tableImportReason:", tableImportReason)

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

                # print('x = ', x)
                # print('y = ', y)

                reasonSuggest.append(tuple(rs))

    print("reasonSuggest", reasonSuggest)

    reasonSuggestMatch = []

    # 按priority升序排列 取top5 并去重

    reasonSuggestMatch = list(set(sorted(reasonSuggest, key=lambda x: x[2])))[0:5]

    print("reasonSuggestMatch:", reasonSuggestMatch)

    #  即把相同的suggest,reason记录里面日期和小时合并到一起

    # reasonSuggestMatch = [('2017-03-26', '21', 376, '低空大气波导效应、天线挂高过高、发射功率过大等原因导致', '疑似邻区存在隐性故障', 1),
    #                       ('2017-03-26', '05,17,22', 376, '低空大气波导效应、天线挂高过高、发射功率过大等原因导致', '疑似邻区存在隐性故障', 1),
    #                       ('2017-03-26', '09,14,15', 376, '低空大气波导效应、天线挂高过高、发射功率过大等原因导致', '疑似邻区存在隐性故障', 1),
    #                       ('2017-03-26', '08', 458, '建议进行负载均衡参数调整', '邻区干扰影响切换', 1),
    #                       ('2017-03-26', '10', 376, '低空大气波导效应、天线挂高过高、发射功率过大等原因导致', '疑似邻区存在隐性故障', 1)]

    reasonSuggestMerge = []

    for i in reasonSuggestMatch:
        rsm = dict()

        ttime = i[0]

        if i[1].find(":") > 0:
            thour = str(i[1][0:-1])
        else:
            thour = i[1]

        suggest = i[3]
        reason = i[4]

        rs = (reason, suggest)
        if rs not in rsm:
            date_list = []
            date_list.append(ttime + ':' + thour)
            rsm[rs] = date_list
        else:
            rsm[rs].append(';' + ttime + ':' + thour)
        reasonSuggestMerge.append(rsm)

    reasonSuggestMergeDate = getMergeDate(reasonSuggestMerge)
    print('reasonSuggestMergeDate', reasonSuggestMergeDate)

    # mtd保存cellquestion IS NULL AND  cellproject IS NULL为空的工单

    # 更新 mtd的变量里面的内容

    # 关联  reasonSuggestMerge 和 mtd  更新原因,建议,Type_pro
    # 将更新后的内容保存到newMtd集合中

    # reasonSuggestMergeDate = {('互调干扰', '建议处理同频单向邻区'): ['2017-03-26:03,04,05,06,07,08,09,10'],
    #                           ('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-26:05,17,22,11,21'],
    #                           ('邻区干扰影响切换', '建议进行负载均衡参数调整'): ['2017-03-26:08']}

    newMtd = []
    # 关联两个临时表, 更新原因, 建议, Type_pro

    # 如果 reasonSuggestMergeDate 是空

    if len(reasonSuggestMergeDate) == 0:
        for x in reasonSuggestMergeDate.keys():
            reason = x[0]
            suggest = x[1]

            # print("reason = ", reason)
            # print("suggest = ", suggest)

            for i in mtd:
                # cellQuestion = reason  #i[26]
                # cellProject =  suggest  #i[27]
                # cellSuggest = '小区关键问题原因是：' + reason + '\r优化建议方案：' + suggest

                singleMtd = list(i)
                # print("singleMtd = ",list(i))

                singleMtd[26] = reason  # i[26]
                singleMtd[27] = suggest  # i[27]
                singleMtd[24] = '小区关键问题原因是：' + reason + '\r优化建议方案：' + suggest

                newMtd.append(singleMtd)

        print('newMtd :', newMtd)
        print('newMtd的长度 = ', len(newMtd))

    # 室分性能,室分劣化 cellquestion IS NULL 更新
    # type1 13
    # type3 15

    # cellquestion 27
    # cellproject 28
    # cellsuggest 25

    # picell- pi378 393
    # picell-ttime 12
    # picell- def_cellname 5

    # todo 上面newMtd中的cellquestion没有空数据！！！ 上面对其中的cellquestion已经进行了赋值
    # 但是  如果不满足赋值条件，则直接进入下面的程序！！！

    mtdSF = []
    for i in mtd:  # 如何上面的更新不满足更新条件 则 mtdSF =  mtd
        type1 = i[13]
        cellquestion = i[27]
        # print('type1 = %s, cellquestion = %s' % (type1, cellquestion))
        # print("taskid = '%s', type1 = '%s'"%( i[0],i[13]))
        print('type1 = ', type1)
        print('cellquestion = ', cellquestion)
        if type1 in ('SFXN', 'SFLH') and cellquestion == '':
            mtdSF.append(i)

    print('mtdSF = ', mtdSF)

    if dbtype == 'mysql':
        tablePiCell = dbpool.select("select * from PI_CELL  where (PI55 + PI56) = 0 and pi378 >=0 limit 10;")
    else:
        tablePiCell = dbpool.select(
            "SELECT top 10 * FROM pi_cell WHERE (CONVERT(FLOAT, pi55) + CONVERT(FLOAT, pi56)) = 0 AND CONVERT(FLOAT, pi378) >= 0")

    print('tablePiCell', tablePiCell)
    print('tablePiCell length = ', len(tablePiCell))

    # 室分性能, 室分劣化
    # cellquestion
    # IS
    # NULL
    # 更新  更新后的变量存入 newmtdCell
    newMtdCell = []
    for x in tablePiCell:
        x = list(x)
        pi378 = float(x[393])
        # print('pi378:', float(pi378))
        xttime = x[12]
        xdefCellname = x[5]

        # print('tablePiCell-xttime = ',xttime)
        # print('tablePiCell-xdefCellname = ',xdefCellname)
        for y in mtdSF:
            y = list(y)
            yttime = y[2]
            ydefCellname = y[4]
            # print('mtdSF-yttime = ', yttime)
            # print('mtdSF-ydefCellname = ', ydefCellname)

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

    print('newMtdCell :', newMtdCell)

    #
    # newMtdCell = [(6, None, '2017-03-26', None, '1-19905-1-130', '29', '北部新区海州国际公寓灯杆F-HLHB', '重庆', '其它', 'null', 'null',
    #               None, None, 'SFXN', '自动', '高掉线小区', '问题符合高掉线小区筛选规则', '3', 'admin', '07', '', 3, 13, None, '',
    #               '小区关键问题原因是：互调干扰,发生时间：2017-03-26:03,04,05,06,07,08,09,10,关联系数：0.4\\r\\r优化建议方案：GSM900：2f1、f1+f2，DCS1800:2f1-f140且自身互调性能较差\\r',
    #               None, '', '建议排查周边存在电信联通FDD使用2024MHz频段，自身接收机性能较差；设备故障；周边存在干扰器开启等\\r', None, None, None, None, None,
    #               None, None, '2017-03-25:00,01,03,04,05,06,07,12,15;2017-03-26:04,05,06,07', None, None, None, None,
    #               None, None, None, None, None, None, None, None, None, None)]

    # 系统未发现原因的更新 todo
    # type1 13
    # type3 15

    # cellquestion 27
    # cellproject 28
    # cellsuggest 25
    newMtdCellNoReason = []

    for i in newMtdCell:

        print('newMtdCell= ', i)
        i = list(i)

        type3 = i[15]
        type1 = i[13]
        print('type3 = ', type3)
        print('type1 = ', type1)

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
    print('newMtdCellNoReason :', newMtdCellNoReason)

    # 更新白名单  默认为空吗 ?
    mtdWhilte = []

    lteLhxqWhite = dbpool.select("select * from lte_lhxq_white;")
    print("白名单列表: ", lteLhxqWhite)
    if len(lteLhxqWhite) != 0:
        for i in lteLhxqWhite:
            idefCellname = i[2]

            for j in newMtdCellNoReason:
                jdefCellnameChinese = j[6]
                if jdefCellnameChinese == idefCellname:
                    # 更新 cellproject = cellproject + '\r本小区属于白名单小区，建议不下派工单。'
                    j[28] = j[28] + '\r本小区属于白名单小区，建议不下派工单。'
                    mtdWhilte.append(j)
    else:
        mtdWhilte = newMtdCellNoReason

    print('mtdWhilte = ', mtdWhilte)

    # 以下所有语句是更新更具体的建议cellproject

    # 接下来两次更新白名单

    # 第一次
    # 查询 table

    mtdWhilteOnce = []

    print("tablePropertiesDb length = ", len(tablePropertiesDb))
    for y in tablePropertiesDb:
        ydefCellname = y[0]
        yttime = y[3]
        ytype3 = y[2]
        yfaultDescription = y[4]
        for x in mtdWhilte:
            xdefCellname = x[4]
            xttime = x[2]
            xtype3 = x[15]
            xcellquestion = x[27]

            if xdefCellname == ydefCellname and xttime == yttime and ytype3 == '相关小区故障' and '相关小区故障' in xcellquestion:
                # 更新cellproject
                x[28] = x[28].replace('建议处理相关小区故障', '建议处理' + yfaultDescription)
                mtdWhilteOnce.append(x)

    if len(mtdWhilteOnce) == 0:
        mtdWhilteOnce = mtdWhilte

    print('mtdWhilteOnce: ', mtdWhilteOnce)

    # 第二次更新

    mtdWhilteTwice = []

    tablePropertiesDbByType = dbpool.select(
        "select DEF_CELLNAME,TTIME,FAULT_OBJECT from PROPERTIES_DB where TYPE1 = '%s' and TYPE3='%s'" % (
            'MR', '覆盖方向需调整'))  # 大约80行

    for x in tablePropertiesDbByType:
        xfaultObject = x[2]
        xdefCellname = x[0]
        xttime = x[1]

        for y in mtdWhilteOnce:
            yttime = y[2]
            ydefCellname = y[4]
            ycellquestion = y[27]

            if xdefCellname == ydefCellname and xttime == yttime and '覆盖方向需调整' in ycellquestion:
                ycellproject = y[28]
                if ('建议调整方向角' in ycellproject):
                    re = '建议处理相关小区故障'
                else:
                    re = '建议处理' + xfaultObject

                y[28] = y[28].replace('覆盖方向需调整', re)

                mtdWhilteTwice.append(y)

    if len(mtdWhilteTwice) == 0:
        mtdWhilteTwice = mtdWhilteOnce

    print("mtdWhilteTwice: ", mtdWhilteTwice)

    # mtdWhilteTwice = [(6, None, '2017-03-26', None, '1-19905-1-130', '29', '北部新区海州国际公寓灯杆F-HLHB', '重庆', '其它', 'null',
    #                   'null', None, None, 'SFXN', '自动', '高掉线小区', '问题符合高掉线小区筛选规则', '3', 'admin', '07', '', 3, 13, None,
    #                   '',
    #                   '小区关键问题原因是：互调干扰,发生时间：2017-03-26:03,04,05,06,07,08,09,10,关联系数：0.4\\r\\r优化建议方案：GSM900：2f1、f1+f2，DCS1800:2f1-f140且自身互调性能较差\\r',
    #                   None, '', '建议排查周边存在电信联通FDD使用2024MHz频段，自身接收机性能较差；设备故障；周边存在干扰器开启等\\r', None, None, None, None, None,
    #                   None, None, '2017-03-25:00,01,03,04,05,06,07,12,15;2017-03-26:04,05,06,07', None, None, None,
    #                   None, None, None, None, None, None, None, None, None, None, None)]

    # 将上述所有对数据的操作更新到 manager_task_detail

    # 租后更新的是detail表中的四个字段  cellquestion cellproject cellsuggest type_pro
    print("执行更新工单操作...")
    # for x in mtdWhilteTwice:
    #     print("x = ",x)
    #
    #     xcellquestion = x[27]
    #     xcellproject = x[28]
    #     xcellsuggest = x[25]
    #     xtypePro = x[37]
    #
    #     updateMtdSql = "update manager_task_detail set cellquestion = '%s',cellproject = '%s',cellsuggest= '%s',Type_pro='%s' where TASK_DETAIL_ID = %d" % (
    #         xcellquestion, xcellproject, xcellsuggest, xtypePro, task_detail_id)
    #
    #     if (dbpool.update(updateMtdSql) > 0):
    #         print("成功更新一条工单！")


def getMergeDate(reasonSuggestMerge):
    d = dict()
    # d = {}  两种声明字典的结果一样
    for i in reasonSuggestMerge:
        dateList = []
        key = list(i.keys())[0]
        value = i[key]
        datehour = i[key][0].split(':')

        if key not in d:
            d[key] = i[key]
            dateList += datehour
        else:  # 相同的key  value合并  [data1:hour1;date2:hour2...]
            for i in range(len(d[key])):
                if datehour[0] in d[key][i]:
                    d[key] += datehour[1:]

            datetime = ','.join(d[key])
            a = []
            a.append(datetime)  # append 没有返回值~~~
            d[key] = a

    return d


if __name__ == '__main__':
    # task_detail_id = 4379
    task_detail_id = 6
    updateMtdByDay(task_detail_id, 'mysql')
