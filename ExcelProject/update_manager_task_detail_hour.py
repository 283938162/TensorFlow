# -*- coding:utf-8  -*-

from ExcelProject.PyDBPool import PyDBPool

# 初始化数据库连接池对象
dbpool = PyDBPool('mysql')

'''
@updateMtdByHour()  按小时更新工单信息manager_task_detail
@task_detail_id     传入的工单id参数

'''


def updateMtdByHour(task_detail_id):
    if task_detail_id is None:
        print("工单号为空")
        return

    updateMtdInitSql = "update ROSAS.manager_task_detail set type3 = '%s' where task_detail_id = %d and reply= '0' and type1 = 'XN' and ifnull(type3,'') = ''" % (
        '高掉线小区', task_detail_id)

    if dbpool.update(updateMtdInitSql) > 0:
        print("初始化数据更新成功!")
    else:
        print("初始化数据未更新!")

    mtd = dbpool.select(
        "select * from ROSAS.manager_task_detail where TASK_DETAIL_ID = %d" % (task_detail_id))
    if len(mtd) == 0:
        print("未查询到该指定工单号的记录")
        return
    ttime = mtd[0][2]
    print('ttime :', ttime)
    faultDatehour = mtd[0][36]
    print('faultDatehour :', faultDatehour)
    defCellname = mtd[0][4]
    print("defCellname :", defCellname)
    thour = mtd[0][19]
    print("thour :", thour)

    # 取出当前工单号中的日期和时间
    list_date = []

    dates = faultDatehour.split(';')
    for y in dates:
        dates = y.split(':')[0]
        hours = y.split(':')[1:]
        list_date.append(dates)

    print("list_date:", list_date)

    tablePropertiesDb = dbpool.select(
        "select * from PROPERTIES_DB where DEF_CELLNAME = '%s' and TTIME in (%s) and TYPE1 not in(%s);" % (
            (defCellname),
            (','.join((map(lambda x: repr(x), list_date)))),
            (','.join((map(lambda x: repr(x), ['显性故障', '干扰', '容量']))))))

    print('tablePropertiesDb', tablePropertiesDb)
    print('tablePropertiesDb length = ', len(tablePropertiesDb))

    tablePropertiesDbHour = dbpool.select(
        "select pd.DEF_CELLNAME,pd.TYPE1,pd.TYPE3,pd.TTIME,pd.FAULT_DESCRIPTION,pd.LABEL,pd.THOUR,pd.LEVEL_R,pd.FAULT_OBJECT FROM PROPERTIES_DB_HOUR as pd where pd.DEF_CELLNAME = '%s' and pd.TTIME in (%s) " % (
            (defCellname),
            (','.join((map(lambda x: repr(x), list_date))))))

    print('tablePropertiesDbHour', tablePropertiesDbHour)
    print('tablePropertiesDbHour length = ', len(tablePropertiesDbHour))

    # todo 取出记录
    mtdType1 = mtd[0][13]
    mtdType3 = mtd[0][15]

    print('mtdType1:', mtdType1)

    tableImportReason = dbpool.select(
        "select * from import_reason as ir where ir.type1 = '%s' and INSTR(ir.representation,'%s') > 0" % (
            mtdType1, mtdType3))

    print("tableImportReason:", tableImportReason)
    print("tableImportReason length:", len(tableImportReason))

    reasonSuggest = []

    for x in tablePropertiesDbHour:
        pdType3 = x[2]
        pdLevelR = x[7]

        # print('pdType3 = ', pdType3)
        # print('pdLevelR = ', pdLevelR)
        for y in tableImportReason:
            irReason = y[1]
            irLevelR = y[2]
            irImportantreason = y[4]

            # print('irReason =', irReason)
            # print('irLevelR = ', irLevelR)

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
    print("reasonSuggest length = ", len(reasonSuggest))

    reasonSuggestMatch = []

    # 按priority升序排列 取top5 并去重

    reasonSuggestMatch = list(set(sorted(reasonSuggest, key=lambda x: x[3])))[0:5]

    print("reasonSuggestMatch:", reasonSuggestMatch)
    print("reasonSuggestMatch length = :", len(reasonSuggestMatch))

    #  即把相同的suggest,reason记录里面日期和小时合并到一起

    return
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

        print("rsm:", rsm)

        reasonSuggestMerge.append(rsm)

    print('reasonSuggestMerge', reasonSuggestMerge)

    # mtd保存cellquestion IS NULL AND  cellproject IS NULL为空的工单

    # 更新 mtd的变量里面的内容
    mtd = dbpool.select(
        "select * from manager_task_detail where cellproject is Null and cellquestion is  null  and  ttime = '%s' limit 100;" % (
            ttime))

    newMtd = []

    print('mtd :', mtd)

    # 关联  reasonSuggestMerge 和 mtd  更新原因,建议,Type_pro
    # 将更新后的内容保存到newMtd集合中
    for x in reasonSuggestMerge:
        rsKeys = list(x.keys())

        reason = rsKeys[0][0]
        suggest = rsKeys[0][1]

        print(reason)
        print(suggest)

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

    # 更新后的数据  newMtd 如何落地?

    # 室分性能,室分劣化 cellquestion IS NULL 更新
    # type1 13
    # type3 15

    # cellquestion 27
    # cellproject 28
    # cellsuggest 25

    # picell- pi378 393
    # picell-ttime 12
    # picell- def_cellname 5

    mtdSF = []
    for i in newMtd:
        type1 = i[13]
        cellquestion = i[27]
        print("type1 = '%s', cellquestion = '%s'" % (type1, cellquestion))
        if type1 in ('SFXN', 'SFLH') and cellquestion is None:
            mtdSF.append(i)

    print('mtdSF = ', mtdSF)

    tablePiCell = dbpool.select("select * from PI_CELL  where (PI55 + PI56) = 0 and pi378 >=0 limit 1;")

    newMtdCell = []

    for x in tablePiCell:
        pi378 = float(x[393])
        print('pi378:', float(pi378))
        xttime = x[12]
        xdefCellname = x[5]
        for y in mtdSF:
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

    print('newMtdCell :', newMtdCell)

    # 系统未发现原因的更新
    # type1 13
    # type3 15

    # cellquestion 27
    # cellproject 28
    # cellsuggest 25
    newMtdCellNoReason = []

    for i in newMtdCell:

        type3 = i[15]
        type1 = 1[13]

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

    # 更新白名单
    mtdWhilte = []

    lteLhxqWhite = dbpool.select("select * from lte_lhxq_white;")

    for i in lteLhxqWhite:
        idefCellname = i[2]

        for j in newMtdCellNoReason:
            jdefCellnameChinese = j[6]
            if jdefCellnameChinese == idefCellname:
                # 更新 cellproject = cellproject + '\r本小区属于白名单小区，建议不下派工单。'
                j[28] = j[28] + '\r本小区属于白名单小区，建议不下派工单。'
                mtdWhilte.append(j)

    print('mtdWhilte = ', mtdWhilte)

    # 以下所有语句是更新更具体的建议cellproject

    # 接下来两次更新白名单

    # 第一次
    # 查询 table

    mtdWhilteOnce = []

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
    print("mtdWhilteTwice: ", mtdWhilteTwice)

    # 将上述所有对数据的操作更新到 manager_task_detail

    print("执行更新工单操作...")
    # for x in mtdWhilteTwice:
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


if __name__ == '__main__':
    # task_detail_id = 4379
    task_detail_id = 901
    updateMtdByHour(task_detail_id)
