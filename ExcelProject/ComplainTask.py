import time
from ExcelProject.PyDBPool import PyDBPool  # 程序内

"""
ComplainTask  投诉工单 数据流处理
   
"""


def getTablePropertiesDB(dbPool, cell, mtdTTime, list_date):
    tablePropertiesDb = dbPool.select(
        "select convert(nvarchar(255),pd.DEF_CELLNAME_CHINESE),convert(nvarchar(255),pd.TYPE3),pd.TTIME,convert(nvarchar(255),pd.LEVEL_R) FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME_CHINESE = '%s' and pd.TTIME = '%s'" % (
            (cell, mtdTTime)))

    print("tablePropertiesDb = :", tablePropertiesDb)
    print("tablePropertiesDb length = ", len(tablePropertiesDb))
    return tablePropertiesDb


def getTableImportReason(dbPool, mtdType1, mtdType3):
    tableImportReason = dbPool.select(
        "select ir.reason,ir.level_r,ir.suggest from import_reason as ir where ir.type1 = '%s' and ir.representation = '%s'" % (
            mtdType1, mtdType3))
    print("tableImportReason = ", tableImportReason)
    print("tableImportReason length = ", len(tableImportReason))
    return tableImportReason


def updateMtdQuestionAndProject(dbPool, newMtdCellQuestion, newMtdCellProject, taskId):
    dbPool.update(
        "update manager_task_detail set dbo.manager_task_detail.cellquestion=dbo.manager_task_detail.cellquestion+'%s',dbo.manager_task_detail.cellproject=dbo.manager_task_detail.cellproject+'%s' where dbo.manager_task_detail.TASK_DETAIL_ID =%d" % (
            newMtdCellQuestion, newMtdCellProject, taskId))


def updateCell(dbPool, taskId, cellList, mtdTTime, list_date, mtdType1, mtdType3):
    index = 1
    for cell in cellList:
        print('cell = ', cell)
        tablePropertiesDB = getTablePropertiesDB(dbPool, cell, mtdTTime, list_date)
        tableImportReason = getTableImportReason(dbPool, mtdType1, mtdType3)
        for pd in tablePropertiesDB:
            pdType3 = pd[1]
            pdLevelR = pd[3]

            # print('pdType3 = ', pdType3)
            # print('pdLevelR = ', pdLevelR)
            for ir in tableImportReason:
                irReason = ir[0]
                irLevelR = ir[1]

                irSuggest = ir[2]
                # print('irReason = ', irReason)
                # print('irLevelR = ', irLevelR)

                if (pdType3 == irReason) and (pdLevelR == irLevelR):
                    newMtdCellQuestion = cell + ':' + pdType3 + '\r'
                    newMtdCellProject = cell + ':' + irSuggest + '\r'
                    print('newMtdCellQuestion = ', newMtdCellQuestion)
                    print('newMtdCellProject = ', newMtdCellProject)

                    updateMtdQuestionAndProject(dbPool, newMtdCellQuestion, newMtdCellProject, taskId)

        print('更新cell' + str(index) + ' 完成')
        index += 1

        print("小区级原因更新完成!")


def getTablePropertiesDBArea(dbPool, cell, mtdDefCellName):
    tablePropertiesDbArea = dbPool.select(
        "select pda.TYPE3,pda.LEVEL_R FROM PROPERTIES_DB as pda where pda.DEF_CELLNAME_CHINESE = '%s' and pda.ID = '%s'" % (
            (cell, mtdDefCellName)))

    print("tablePropertiesDb = :", tablePropertiesDbArea)
    print("tablePropertiesDb length = ", len(tablePropertiesDbArea))
    return tablePropertiesDbArea


def updateOTT(dbPool, taskId, mtdDefCellName, cellList, mtdType1, mtdType3):
    index = 1
    for cell in cellList:
        tablePropertiesDBArea = getTablePropertiesDBArea(dbPool, cell, mtdDefCellName)
        tableImportReason = getTableImportReason(dbPool, mtdType1, mtdType3)

        for pda in tablePropertiesDBArea:
            pdaType3 = pda[0]
            pdaLevelR = pda[1]

            print('pdaType3 = ', pdaType3)
            print('pdaLevelR = ', pdaLevelR)

            for ir in tableImportReason:
                irReason = ir[0]
                irLevelR = ir[1]

                irSuggest = ir[2]
                print('irReason = ', irReason)
                print('irLevelR = ', irLevelR)

                if (pdaType3 == irReason) and (pdaLevelR == irLevelR):
                    newMtdCellQuestion = cell + ':' + pdaType3 + '\r'
                    newMtdCellProject = cell + ':' + irSuggest + '\r'
                    print('newMtdOTTQuestion = ', newMtdCellQuestion)
                    print('newMtdOTTProject = ', newMtdCellProject)

                    updateMtdQuestionAndProject(dbPool, newMtdCellQuestion, newMtdCellProject, taskId)
        print('更新cell' + str(index) + ' 完成')
        index += 1

        print("区域级原因更新完成!")


def updateComplainTask(taskId, dbPool):
    # 初始化 cellquestion字段和cellproject字段
    dbPool.update(
        "update manager_task_detail set dbo.manager_task_detail.cellquestion = '%s',dbo.manager_task_detail.cellproject='%s' where dbo.manager_task_detail.TASK_DETAIL_ID = %d;" % (
            '小区级原因:', '小区级建议:', taskId))
    mtd = dbPool.select(
        "select TASK_DETAIL_ID,TTIME,ALLTTIME,DEF_CELLNAME,DEF_CELLNAME_CHINESE,type1,type3,THOUR,relation_cell,cellsuggest,cellquestion,cellproject,fault_datehour from dbo.manager_task_detail where TASK_DETAIL_ID = %d" % (
            taskId))
    relation_cell = mtd[0][8]
    cellList = relation_cell.strip().split(';')
    print('mtd = ', mtd)
    mtdTTime = mtd[0][1]
    mtdDefCellName = mtd[0][3]
    mtdType1 = mtd[0][5]
    mtdType3 = mtd[0][6]
    mtdFaultDatehour = mtd[0][12]

    # 取出 fault_datehour 中 date
    list_date = []
    for y in mtdFaultDatehour.split(';'):
        dates = y.split(':')[0]
        list_date.append(dates)
    print('list_date = ', list_date)
    print('mtdDefCellName = ', mtdDefCellName)  # mtd cellname 放的是投诉工单号

    # updateCell(dbPool, taskId, cellList, mtdTTime, list_date, mtdType1, mtdType3)  # 更新小区级原因

    # todo pda
    updateOTT(dbPool, taskId, mtdDefCellName, cellList, mtdType1, mtdType3)  # 更新区域级原因

    # for cell in cellList:
    #     updateUser()  # 更新用户级原因：


def getComplainTaskID(dbPool):
    # date = time.strftime('%Y-%m-%d')
    date = '2016-02-04'
    print(date)
    return dbPool.select(
        "select TASK_DETAIL_ID from manager_task_detail where type1 = '%s' and ttime = '%s';" % ('TS', date))


# 确定ott    待确定?
def updatePropertiesDbArea(dbPool):
    tableComplainOTT01 = dbPool.select("select * from Complain_OTT where date = ")

    for ott in tableComplainOTT01:
        pdaList = []

        avgRsrp = ott[]

        if avgRsrp < -110:
            pda = []

            areaId = ott[0]  # WO_ID
            areaType = '弱覆盖区域'
            ttime = ''
            label = '原因'
            def_dellname = ''
            defCellnameChinese = ott[]  # ottcellname
            type1 = 'TS'
            type2 = '覆盖'
            type3 = '投诉区域弱覆盖'
            thour = ''
            fault_description = "‘用户占用小区’& Def_Cellname_chinese&’栅格存在区域弱覆盖’"
            fault_total = ''
            reason_ratio = ''
            CUR_VALUE = ''

            pda.applend[
                areaId, areaType, ttime, label, def_dellname, defCellnameChinese, type1, type2, type3, thour, fault_description, fault_total, reason_ratio, CUR_VALUE]
            pdaList.append(pda)

        if avgRsrp < -3:
            pda = []

            areaId = ott[0]  # WO_ID
            areaType = '弱覆盖区域'
            ttime = ''
            label = '原因'
            def_dellname = ''
            defCellnameChinese = ott[]  # ottcellname
            type1 = 'TS'
            type2 = '覆盖'
            type3 = '投诉区域弱覆盖'
            thour = ''
            fault_description = "‘用户占用小区’& Def_Cellname_chinese&’栅格存在区域弱覆盖’"
            fault_total = ''
            reason_ratio = ''
            CUR_VALUE = ''

            pda.applend[
                areaId, areaType, ttime, label, def_dellname, defCellnameChinese, type1, type2, type3, thour, fault_description, fault_total, reason_ratio, CUR_VALUE]
            pdaList.append(pda)

    # 更新list到 pda
    for pda in pdaList:
        dbPool.update("update properties_db_area set ")


def updatePropertiesDbCs(dbPool):
    tableComplainUser = dbPool.select("select * from Complain_User where date = ")

    for user in tableComplainUser:
        pdcList = []
        Rsrp = user[]

        if Rsrp < -110:
            pdc = []

            areaId = user[0]  # WO_ID
            areaType = '弱覆盖区域'
            ttime = ''
            label = '原因'
            def_dellname = ''
            defCellnameChinese = user[]  # ottcellname
            type1 = 'TS'
            type2 = '覆盖'
            type3 = '投诉区域弱覆盖'
            thour = ''
            fault_description = "‘用户占用小区’& Def_Cellname_chinese&’栅格存在区域弱覆盖’"
            fault_total = ''
            reason_ratio = ''
            CUR_VALUE = ''

            pdc.applend[
                areaId, areaType, ttime, label, def_dellname, defCellnameChinese, type1, type2, type3, thour, fault_description, fault_total, reason_ratio, CUR_VALUE]
            pdcList.append(pdc)

    # 用户cause定界 更新 pdc


def main(dbtype):
    dbPool = PyDBPool(dbtype)

    # 通过 Complain_OTT 更新 properties_db_area
    updatePropertiesDbArea(dbPool)

    # 通过 Complain_User 更新 properties_db_cs
    updatePropertiesDbCs(dbPool)

    complainTaskIDList = getComplainTaskID(dbPool)
    print(complainTaskIDList)

    for taskId in complainTaskIDList:
        taskId = taskId[0]
        print('taskId = ', taskId)
        updateComplainTask(taskId, dbPool)


if __name__ == '__main__':
    dbtype = 'mssql'
    main(dbtype)
