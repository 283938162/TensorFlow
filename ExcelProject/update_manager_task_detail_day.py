# -*- coding:utf-8  -*-

from ExcelProject.PyDBPool import PyDBPool

# 初始化数据库连接池对象
dbpool = PyDBPool()

'''
@manageTask()  按天更新工单信息
@task_detail_id 传入的工单id参数

'''


def manageTask(task_detail_id):
    if task_detail_id is None:
        print("工单号为空")
        return

    # 查询指定工单号的工单记录，如果不存在该记录 跳过
    result = dbpool.select(
        "select * from manager_task_detail where task_detail_id = %d and type1 != '%s'" % (task_detail_id, 'XN'))
    print(result)
    if len(result) == 0: return

    result2 = dbpool.select(
        "SELECT * FROM DATA_DATE AS dd JOIN `manager_task_detail` AS mtd ON dd.ttime = mtd.ttime AND dd.thour = '23'")
    print(result2)
    if len(result2) == 0: return

    # 取出当前工单号中的日期
    list_date = []
    list_hour = []
    for x in result:
        fault_detehour = x[36]
        print(fault_detehour)

        dates = fault_detehour.split(';')
        for y in dates:
            dates = y.split(':')[0]
            hours = y.split(':')[1:]

            print(dates)
            print(hours)

            list_date.append(dates)
            list_hour.append(hours)
    print("list_date:", list_date)  # list_date: ['2017-03-25', '2017-03-26']
    print("list_hour:", list_hour)  # list_hour: [['00,01,03,04,05,06,07,12,15'], ['04,05,06,07']]

    # 从属性数据库PROPERTIES_DB取出相关数据

    # result3 = dbpool.select(
    #     "select pd.DEF_CELLNAME,pd.TYPE1,pd.TYPE3,pd.TTIME,pd.FAULT_DESCRIPTION,pd.LABEL,pd.THOUR,pd.LEVEL_R FROM PROPERTIES_DB as pd join manager_task_detail as mtd on pd.DEF_CELLNAME = mtd.DEF_CELLNAME where pd.TTIME in (%s) limit 2" % (
    #         ', '.join((map(lambda x: '%s', list_date)))))

    result3 = dbpool.select(
        "select pd.DEF_CELLNAME,pd.TYPE1,pd.TYPE3,pd.TTIME,pd.FAULT_DESCRIPTION,pd.LABEL,pd.THOUR,pd.LEVEL_R FROM PROPERTIES_DB as pd join manager_task_detail as mtd on pd.DEF_CELLNAME = mtd.DEF_CELLNAME where pd.TTIME in (%s) limit 2" % (
            (','.join((map(lambda x: repr(x), list_date))))))

    print("result3:", result3)

    # 去除result3中不符合条件的记录

    # todo

    result4 = dbpool.select(
        "select * from import_reason as ir join manager_task_detail as mtd on ir.type1 = mtd.type1 where INSTR(ir.representation,mtd.type3) > 0 limit 2")

    print("result4:", result4)

    #
    result5 = dbpool.select(
        "select pd.TTIME,pd.THOUR,ir.priority,ir.suggest,ir.reason,ir.importantreason from PROPERTIES_DB as pd join import_reason as ir on pd.TYPE3=ir.reason and pd.LEVEL_R = ir.level_r  and ir.importantreason !=0 limit 100")
    print("result5:", result5)

    reason_suggest = []

    # 按priority升序排列 取top5

    result6 = list(set(sorted(result5, key=lambda x: x[2])))[0:5]

    print("result6:", result6)

    # 合并result6

    for i in result6:
        result7 = dict()

        ttime = i[0]

        if i[1].find(":") > 0:
            thour = str(i[1][0:-1])
        else:
            thour = i[1]

        suggest = i[3]
        reason = i[4]


        sr = (suggest, reason)
        if sr not in result7:
            date_list = []
            date_list.append(ttime + ':' + thour)
            result7[sr] = date_list
        else:
            result7[sr].append(';'+ttime + ':' + thour)

        print(result7)


if __name__ == '__main__':
    task_detail_id = 6
    manageTask(task_detail_id)
