# -*- coding:utf-8  -*-

from ExcelProject.PyDBPool import PyDBPool

# 初始化数据库连接池对象
dbpool = PyDBPool('mysql')

'''
@manageTask()  按天更新工单信息
@task_detail_id 传入的工单id参数

'''


def manageTaskByDay(task_detail_id):
    if task_detail_id is None:
        print("工单号为空")
        return

    # 查询指定工单号的工单记录，如果不存在该记录 跳过
    result = dbpool.select(
        "select * from manager_task_detail where task_detail_id = %d and type1 != '%s'" % (task_detail_id, 'XN'))
    print("result:", result)
    ttime = result[0][2]
    print("ttime:", ttime)

    if len(result) == 0: return

    result2 = dbpool.select(
        "SELECT * FROM DATA_DATE where ttime='%s' AND thour = '23'" % (ttime))
    print("result2", result2)
    if len(result2) == 0: return

    # 取出当前工单号中的日期和时间
    list_date = []
    list_hour = []
    fault_datehour = result[0][36]
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

    defCellname = result[0][4]
    print("defCellname:", defCellname)

    tablePropertiesDb = dbpool.select(
        "select pd.DEF_CELLNAME,pd.TYPE1,pd.TYPE3,pd.TTIME,pd.FAULT_DESCRIPTION,pd.LABEL,pd.THOUR,pd.LEVEL_R FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME = '%s' and pd.TTIME in (%s) " % (
            (defCellname),
            (','.join((map(lambda x: repr(x), list_date))))))

    print("tablePropertiesDb:", tablePropertiesDb)

    # 去除result3中不符合条件的记录

    # todo 取出记录
    mtdType1 = result[0][13]
    mtdType3 = result[0][15]

    print('mtdType1:', mtdType1)

    tableImportReason = dbpool.select(
        "select * from import_reason as ir where ir.type1 = '%s' and INSTR(ir.representation,'%s') > 0" % (
            mtdType1, mtdType3))

    # print("tableImportReason:", tableImportReason)

    # result5 = dbpool.select(
    #     "select pd.TTIME,pd.THOUR,ir.priority,ir.suggest,ir.reason,ir.importantreason from PROPERTIES_DB as pd join import_reason as ir on pd.TYPE3=ir.reason and pd.LEVEL_R = ir.level_r  and ir.importantreason !=0 limit 100")
    # print("result5:", result5)
    #

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

    reasonSuggestMatch = []

    # 按priority升序排列 取top5

    reasonSuggestMatch = list(set(sorted(reasonSuggest, key=lambda x: x[2])))[0:5]

    print("reasonSuggestMatch:", reasonSuggestMatch)

    #  即把相同的suggest,reason记录里面日期和小时合并到一起

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


    print('reasonSuggestMerge',reasonSuggestMerge)

    # mtd保存cellquestion IS NULL AND  cellproject IS NULL为空的工单

    # 更新 mtd的变量里面的内容
    mtd = dbpool.select(
        "select * from manager_task_detail where cellproject is Null and cellquestion is  null  and  ttime = '%s' limit 100;" % (
            ttime))


    print('mtd update ago:',mtd)


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

            print(i[24])

            # i[26] = reason  #i[26]
            # i[27] =  suggest  #i[27]
            # i[24] = '小区关键问题原因是：' + reason + '\r优化建议方案：' + suggest

    print('mtd update after:',mtd)







    # 关联  reasonSuggestMerge 和 mtd   更新原因,建议,Type_pro






if __name__ == '__main__':
    task_detail_id = 4379
    manageTaskByDay(task_detail_id)
