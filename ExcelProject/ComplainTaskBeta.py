import time
from ExcelProject.PyDBPool import PyDBPool  # 程序内

"""
ComplainTask  投诉工单 数据流处理

   
"""


def getTablePropertiesDB(dbPool, cell, mtdTTime, list_hours):
    """根据detail表中信息查询出满足条件的小区信息"""
    tablePropertiesDb = dbPool.select(
        "select convert(nvarchar(255),pd.DEF_CELLNAME_CHINESE) as DEF_CELLNAME_CHINESE,convert(nvarchar(255),pd.TYPE3) as TYPE3,pd.TTIME,convert(nvarchar(255),pd.LEVEL_R) as LEVEL_R,pd.THOUR FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME_CHINESE = '%s' and pd.TTIME = '%s'" % (
            (cell, mtdTTime)))

    print('tablePropertiesDb sql = ',
          "select convert(nvarchar(255),pd.DEF_CELLNAME_CHINESE) as DEF_CELLNAME_CHINESE,convert(nvarchar(255),pd.TYPE3) as TYPE3,pd.TTIME,convert(nvarchar(255),pd.LEVEL_R) as LEVEL_R,pd.THOUR FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME_CHINESE = '%s' and pd.TTIME = '%s'" % (
              (cell, mtdTTime)))

    # print("tablePropertiesDb = :", tablePropertiesDb)
    # print("tablePropertiesDb length = ", len(tablePropertiesDb))

    # list_hours =  [8, 9, 12, 17, 14, 15]
    # Manager_task_detail.fault_datehour包含PROPERTIES_DB.thour   hour有交集就ok
    tablePropertiesDbNew = []
    for t in tablePropertiesDb:
        # print('t = ', t)
        thour = t[4]
        if thour is not None:
            if thour == 'AllDay':
                tablePropertiesDbNew.append(t)
            else:
                thour = [int(i) for i in thour.split(",")]
                if len(list(set(thour).intersection(set(list_hours)))) > 0:
                    tablePropertiesDbNew.append(t)

    print("tablePropertiesDbNew = :", tablePropertiesDbNew)
    print("tablePropertiesDbNew length = ", len(tablePropertiesDbNew))
    return tablePropertiesDb


def getTableImportReason(dbPool, mtdType1, mtdType3):
    tableImportReason = dbPool.select(
        "select ir.reason,ir.level_r,ir.suggest,ir.priority from import_reason as ir where ir.type1 = '%s' and ir.representation = '%s'" % (
            mtdType1, mtdType3))

    print('sql = ',
          "select ir.reason,ir.level_r,ir.suggest,ir.priority from import_reason as ir where ir.type1 = '%s' and ir.representation = '%s'" % (
              mtdType1, mtdType3))
    print("tableImportReason = ", tableImportReason)
    print("tableImportReason length = ", len(tableImportReason))
    return tableImportReason


def updateMtdQuestionAndProject(dbPool, newMtdCellQuestion, newMtdCellProject, taskId):
    dbPool.update(
        "update manager_task_detail set dbo.manager_task_detail.cellquestion=dbo.manager_task_detail.cellquestion+'%s',dbo.manager_task_detail.cellproject=dbo.manager_task_detail.cellproject+'%s' where dbo.manager_task_detail.TASK_DETAIL_ID =%d" % (
            newMtdCellQuestion, newMtdCellProject, taskId))


def updateCell(dbPool, taskId, cellList, mtdTTime, list_date, mtdType1, mtdType3):
    """呈现小区级原因"""
    index = 1
    # tableImportReason = getTableImportReason(dbPool, mtdType1, mtdType3)  # 3
    tableImportReason = dbPool.select(
        "select ir.reason,ir.level_r,ir.suggest,ir.priority from import_reason as ir where ir.type1 = '%s' and ir.representation = '%s'" % (
            mtdType1, mtdType3))

    if len(tableImportReason) == 0: return

    cellDict = {}
    for cell in cellList:  # 3
        print('cell = ', cell)
        tablePropertiesDB = getTablePropertiesDB(dbPool, cell, mtdTTime, list_date)

        # 一个小区名可能多个type3, 过滤掉重复的
        cellDict[cell] = []
        type3List = []

        for ir in tableImportReason:  # 3
            print('ir = ', ir)
            irReason = ir[0]
            irLevelR = ir[1]

            irSuggest = ir[2]

            # print('pdType3 = ', pdType3)
            # print('pdLevelR = ', pdLevelR)
            for pd in tablePropertiesDB:  # 3
                print('pd = ', pd)
                pdType3 = pd[1]
                pdLevelR = pd[3]

                # print('irReason = ', irReason)
                # print('irLevelR = ', irLevelR)

                print('----------pdType3 = ', pdType3)
                print('----------irReason = ', irReason)

                if (pdType3 == irReason) and (pdLevelR == irLevelR):
                    # print('type3 === ', pdType3)
                    # print('type3 === ', pdType3)

                    print("*****************cell = '%s',type3 = '%s'" % (cell, pdType3))

                    if pdType3 not in type3List:
                        type3List.append(pdType3)
                        cellDict[cell].append(ir)

    # 列出关联出的type3
    print('更新cell' + str(index) + ' 完成')
    index += 1

    print('cellDict = ', cellDict)
    print("小区级原因更新完成!")

    # 根绝priority排序 取前三reason

    if len(cellDict) > 0:
        resultOn(cellDict, dbPool, taskId, 'cell')

    # for cell in cellDict.keys():
    #     pdType3List = ''
    #     irSuggestList = ''
    #     for i in sorted(cellDict[cell], key=lambda x: x[3])[:3]:
    #         pdType3List += i[0] + ','
    #         irSuggestList += i[2] + ','
    #     # print('pdType3List = ', pdType3List[0:-1])
    #     # print('irSuggestList = ', irSuggestList[0:-1])
    #     newMtdCellQuestion = cell + ':' + pdType3List[0:-1] + '\r'
    #     newMtdCellProject = cell + ':' + irSuggestList[0:-1] + '\r'
    #     print('newMtdCellQuestion = ', newMtdCellQuestion)
    #     print('newMtdCellProject = ', newMtdCellProject)
    #
    #     updateMtdQuestionAndProject(dbPool, newMtdCellQuestion, newMtdCellProject, taskId)


def getTablePropertiesDBOTT(dbPool, cell, mtdDefCellName):
    print('mtdDefCellName = ', mtdDefCellName)

    tablePropertiesDbAOTT = dbPool.select(
        "select id,convert(nvarchar(255),def_cellname_chinese) as def_cellname_chinese,convert(nvarchar(255),type3) as type3,convert(nvarchar(255),level_r) as level_r FROM properties_db_ott where DEF_CELLNAME_CHINESE = '%s' and ID = '%s'" % (
            cell, mtdDefCellName))

    print('tablePropertiesDbAOTT - sql = ',
          "select id,convert(nvarchar(255),def_cellname_chinese) as def_cellname_chinese,convert(nvarchar(255),type3) as type3,convert(nvarchar(255),level_r) as level_r FROM properties_db_ott where DEF_CELLNAME_CHINESE = '%s' and ID = '%s'" % (
              cell, mtdDefCellName))
    print("tablePropertiesDbOTT = :", tablePropertiesDbAOTT)
    print("tablePropertiesDbOTT length = ", len(tablePropertiesDbAOTT))
    return tablePropertiesDbAOTT


def updateOTT(dbPool, taskId, mtdDefCellName, cellList, mtdType1, mtdType3):
    # 初始化 cellquestion字段和cellproject字段
    # dbPool.update(
    #     "update manager_task_detail set dbo.manager_task_detail.cellquestion = manager_task_detail.cellquestion+'%s',dbo.manager_task_detail.cellproject=manager_task_detail.cellproject + '%s' where dbo.manager_task_detail.TASK_DETAIL_ID = %d;" % (
    #         '栅格级原因:', '栅格级建议:', taskId))

    index = 1
    ottDict = {}

    tableImportReason = getTableImportReason(dbPool, mtdType1, mtdType3)

    # tableImportReason = dbPool.select(
    #     "select ir.reason,ir.level_r,ir.suggest,ir.priority from import_reason as ir where ir.type1 = '%s' and ir.representation = '%s'" % (
    #         mtdType1, mtdType3))

    if len(tableImportReason) == 0: return

    for cell in cellList:

        ottDict[cell] = []
        type3List = []
        tablePropertiesDBOTT = getTablePropertiesDBOTT(dbPool, cell, mtdDefCellName)

        for ir in tableImportReason:
            irReason = ir[0]
            irLevelR = ir[1]
            irSuggest = ir[2]
            print('irReason = ', irReason)
            print('irLevelR = ', irLevelR)
            for pdo in tablePropertiesDBOTT:
                pdoType3 = pdo[2]
                pdoLevelR = pdo[3]

                print('pdoType3 = ', pdoType3)
                print('pdoLevelR = ', pdoLevelR)

                if (pdoType3 == irReason) and (pdoLevelR == irLevelR):
                    print("*****************cell = '%s',type3 = '%s'" % (cell, pdoType3))

                    # PROPERTIES_DB.type3(type3有多个用逗号隔开)?
                    # 怎么判断有多个type3? 哪个维度一对多

                    if pdoType3 not in type3List:
                        type3List.append(pdoType3)
                        ottDict[cell].append(ir)

    print("区域级原因更新完成!")

    # 列出关联出的type3
    print('更新ott' + str(index) + ' 完成')
    index += 1

    print('#########################ottDict = ', ottDict)

    # 根绝priority排序 取前三reason
    if len(ottDict) > 0:
        resultOn(ottDict, dbPool, taskId, 'ott')

    # for cell in ottDict.keys():
    #     pdoType3List = ''
    #     irSuggestList = ''
    #     for i in sorted(ottDict[cell], key=lambda x: x[3])[:3]:
    #         pdoType3List += i[0] + ','
    #         irSuggestList += i[2] + ','
    #     # print('pdType3List = ', pdType3List[0:-1])
    #     # print('irSuggestList = ', irSuggestList[0:-1])
    #     newMtdOTTQuestion = cell + ':' + pdoType3List[0:-1] + '\r'
    #     newMtdOTTProject = cell + ':' + irSuggestList[0:-1] + '\r'
    #     print('newMtdCellQuestion = ', newMtdOTTQuestion)
    #     print('newMtdCellProject = ', newMtdOTTProject)
    #
    #     updateMtdQuestionAndProject(dbPool, newMtdOTTQuestion, newMtdOTTProject, taskId)


def updateOTTJoin(dbPool, taskId, mtdDefCellName, cellList, mtdType1, mtdType3):
    # 初始化 cellquestion字段和cellproject字段
    # dbPool.update(
    #     "update manager_task_detail set dbo.manager_task_detail.cellquestion = manager_task_detail.cellquestion+'%s',dbo.manager_task_detail.cellproject=manager_task_detail.cellproject + '%s' where dbo.manager_task_detail.TASK_DETAIL_ID = %d;" % (
    #         '栅格级原因:', '栅格级建议:', taskId))

    index = 1
    ottDict = {}

    # tableImportReason = getTableImportReason(dbPool, mtdType1, mtdType3)

    tableImportReason = dbPool.select(
        "select ir.reason,ir.level_r,ir.suggest,ir.priority from import_reason as ir where ir.type1 = '%s' and ir.representation = '%s'" % (
            mtdType1, mtdType3))

    if len(tableImportReason) == 0: return

    for cell in cellList:

        ottDict[cell] = []
        type3List = []
        # tablePropertiesDBOTT = getTablePropertiesDBOTT(dbPool, cell, mtdDefCellName)

        tablePropertiesDBOTT = dbPool.select(
            "select id,convert(nvarchar(255),def_cellname_chinese) as def_cellname_chinese,convert(nvarchar(255),type3) as type3,convert(nvarchar(255),level_r) as level_r FROM properties_db_ott where DEF_CELLNAME_CHINESE = '%s' and ID = '%s'" % (
                cell, mtdDefCellName))

        for ir in tableImportReason:
            irReason = ir[0]
            irLevelR = ir[1]
            irSuggest = ir[2]
            print('irReason = ', irReason)
            print('irLevelR = ', irLevelR)
            for pdo in tablePropertiesDBOTT:
                pdoType3 = pdo[2]
                pdoLevelR = pdo[3]

                print('pdoType3 = ', pdoType3)
                print('pdoLevelR = ', pdoLevelR)

                if (pdoType3 == irReason) and (pdoLevelR == irLevelR):
                    print("*****************cell = '%s',type3 = '%s'" % (cell, pdoType3))

                    # PROPERTIES_DB.type3(type3有多个用逗号隔开)?
                    # 怎么判断有多个type3? 哪个维度一对多

                    if pdoType3 not in type3List:
                        type3List.append(pdoType3)
                        ottDict[cell].append(ir)

    print("区域级原因更新完成!")

    # 列出关联出的type3
    print('更新ott' + str(index) + ' 完成')
    index += 1

    print('#########################ottDict = ', ottDict)

    # 根绝priority排序 取前三reason
    if len(ottDict) > 0:
        resultOn(ottDict, dbPool, taskId, 'ott')

    # for cell in ottDict.keys():
    #     pdoType3List = ''
    #     irSuggestList = ''
    #     for i in sorted(ottDict[cell], key=lambda x: x[3])[:3]:
    #         pdoType3List += i[0] + ','
    #         irSuggestList += i[2] + ','
    #     # print('pdType3List = ', pdType3List[0:-1])
    #     # print('irSuggestList = ', irSuggestList[0:-1])
    #     newMtdOTTQuestion = cell + ':' + pdoType3List[0:-1] + '\r'
    #     newMtdOTTProject = cell + ':' + irSuggestList[0:-1] + '\r'
    #     print('newMtdCellQuestion = ', newMtdOTTQuestion)
    #     print('newMtdCellProject = ', newMtdOTTProject)
    #
    #     updateMtdQuestionAndProject(dbPool, newMtdOTTQuestion, newMtdOTTProject, taskId)


def getMtdHours(fault_datehour):
    """提取detail表中fault_datehour字段的小时内容"""
    list_hours = []
    date_hours = fault_datehour.split(';')
    for y in date_hours:
        hours = y.split(':')[1]
        for h in hours.split(","):
            list_hours.append(int(h))
    print('list_hours = ', list_hours)
    return list_hours


def getTablePropertiesDBCs(dbPool, cell, mtdDefCellName, mtdTTime, list_hours):
    # 是否有过滤条件 label = '原因定界' ?
    tablePropertiesDBCs = dbPool.select(
        "select convert(nvarchar(255),type1) as type1,convert(nvarchar(255),type3) as type3,convert(nvarchar(255),Level_R) as Level_R,convert(nvarchar(255),LABEL) as LABEL,THOUR from PROPERTIES_DB_CS where DEF_CELLNAME_CHINESE = '%s' and CS_ID = '%s' and TTIME = '%s'" % (
            cell, mtdDefCellName, mtdTTime))

    print('tablePropertiesDBCs - sql = ',
          "select convert(nvarchar(255),type1) as type1,convert(nvarchar(255),type3) as type3,convert(nvarchar(255),Level_R) as Level_R,convert(nvarchar(255),LABEL) as LABEL,THOUR from PROPERTIES_DB_CS where DEF_CELLNAME_CHINESE = '%s' and CS_ID = '%s' and TTIME = '%s'" % (
              cell, mtdDefCellName, mtdTTime))
    print("tablePropertiesDBCs = :", tablePropertiesDBCs)
    print("tablePropertiesDBCs length = ", len(tablePropertiesDBCs))

    tablePropertiesDbCsNew = []
    for t in tablePropertiesDBCs:
        thour = t[4]
        if thour is not None:
            if thour == 'AllDay':
                tablePropertiesDbCsNew.append(t)
            else:
                thour = [int(i) for i in thour.split(",")]
                if len(list(set(thour).intersection(set(list_hours)))) > 0:
                    tablePropertiesDbCsNew.append(t)

    print("tablePropertiesDbCsNew = :", tablePropertiesDbCsNew)
    print("tablePropertiesDbCsNew length = ", len(tablePropertiesDbCsNew))
    return tablePropertiesDBCs


def getTableImportComplainEvent(dbPool):
    tableImportComplainEvent = dbPool.select("select * from IMPORT_COMPLAIN_EVENT;")
    if len(tableImportComplainEvent) > 0:
        return tableImportComplainEvent
    else:
        print("this is No data in table IMPORT_COMPLAIN_EVENT")
        return None


# 根绝priority排序 取前三reason
def resultOn(resultDict, dbPool, taskId, resultOnType):
    print('resultDict = ', resultDict)

    # 初始化 cellquestion字段和cellproject字段
    if resultOnType == 'cell':
        initSql = "update manager_task_detail set dbo.manager_task_detail.cellquestion = '%s',dbo.manager_task_detail.cellproject='%s' where dbo.manager_task_detail.TASK_DETAIL_ID = %d;" % (
            '小区级原因:', '小区级建议:', taskId)
    elif (resultOnType == 'ott'):
        initSql = "update manager_task_detail set dbo.manager_task_detail.cellquestion = manager_task_detail.cellquestion+'%s',dbo.manager_task_detail.cellproject=manager_task_detail.cellproject + '%s' where dbo.manager_task_detail.TASK_DETAIL_ID = %d;" % (
            '栅格级原因:', '栅格级建议:', taskId)
    elif (resultOnType == 'user'):
        initSql = "update manager_task_detail set dbo.manager_task_detail.cellquestion = manager_task_detail.cellquestion+'%s',dbo.manager_task_detail.cellproject=manager_task_detail.cellproject + '%s' where dbo.manager_task_detail.TASK_DETAIL_ID = %d;" % (
            '用户级原因:', '用户级建议:', taskId)
    else:
        print('resultOnType Error')
        return
    dbPool.update(initSql)

    newMtdQuestion = ''
    newMtdProject = ''
    for cell in resultDict.keys():

        if len(resultDict[cell]) == 0: continue

        type3List = ''
        suggestList = ''
        for i in sorted(resultDict[cell], key=lambda x: x[3])[:3]:
            type3List += i[0] + ','
            suggestList += i[2] + ','
        # print('pdType3List = ', pdType3List[0:-1])
        # print('irSuggestList = ', irSuggestList[0:-1])

        newMtdQuestion = cell + ':' + type3List[0:-1] + '\r'
        newMtdProject = cell + ':' + suggestList[0:-1] + '\r'

        print('newMtdQuestion = ', newMtdQuestion)
        print('newMtdProject = ', newMtdProject)

        updateMtdQuestionAndProject(dbPool, newMtdQuestion, newMtdProject, taskId)
    if newMtdQuestion == '' or newMtdProject == '':
        if resultOnType == 'cell':
            newMtdQuestion = '系统为查询到小区级原因' + '\r'
            newMtdProject = '系统为查询到小区级建议' + '\r'
            updateMtdQuestionAndProject(dbPool, newMtdQuestion, newMtdProject, taskId)
        elif resultOnType == 'ott':
            newMtdQuestion = '系统为查询到栅格级原因' + '\r'
            newMtdProject = '系统为查询到栅格级建议' + '\r'
            updateMtdQuestionAndProject(dbPool, newMtdQuestion, newMtdProject, taskId)
        elif resultOnType == 'user':
            newMtdQuestion = '系统为查询到用户级原因' + '\r'
            newMtdProject = '系统为查询到用户级建议' + '\r'
            updateMtdQuestionAndProject(dbPool, newMtdQuestion, newMtdProject, taskId)
        else:
            print('error')

    # 拼接cellsuggestion

    dbPool.update(
        "update manager_task_detail set cellsuggest = cellquestion +'\r'+'\r'+ cellproject where TASK_DETAIL_ID = '%s'" % (
            taskId))


def updateUser(dbPool, taskId, cellList, mtdDefCellName, mtdTTime, list_hours, mtdType1, mtdType3):
    # dbPool.update(
    #     "update manager_task_detail set dbo.manager_task_detail.cellquestion = manager_task_detail.cellquestion+'%s',dbo.manager_task_detail.cellproject=manager_task_detail.cellproject + '%s' where dbo.manager_task_detail.TASK_DETAIL_ID = %d;" % (
    #         '用户级原因:', '用户级建议:', taskId))
    index = 1

    tableImportReason = getTableImportReason(dbPool, mtdType1, mtdType3)
    tableImportComplainEvent = getTableImportComplainEvent(dbPool)
    userDict = {}

    for cell in cellList:
        # 对于一条mtd工单  def_cellname (工单号是唯一)
        # 对于 pdc表 可以有多个 投诉工单号一致的情况
        tablePropertiesDBCs = getTablePropertiesDBCs(dbPool, cell, mtdDefCellName, mtdTTime, list_hours)

        userDict[cell] = []
        type3List = []

        for ir in tableImportReason:
            irReason = ir[0]
            irLevelR = ir[1]

            irSuggest = ir[2]

            # print('irReason = ', irReason)
            # print('irLevelR = ', irLevelR)
            # print('irPriority = ', ir[3])

            for pdc in tablePropertiesDBCs:
                pdcType1 = pdc[0]
                pdcType3 = pdc[1]
                pdcLevelR = pdc[2]
                pdcLabel = pdc[3]  # '原因' 和 '原因定界两种'

                # print('pdcType1 = ', pdcType1)
                # print('pdcType3 = ', pdcType3)
                # print('pdcLevelR = ', pdcLevelR)
                # print('pdcLabel = ', pdcLabel)

                if (pdcType3 == irReason) and (pdcLevelR == irLevelR):
                    # --  todo  --

                    # newMtdUserQuestion = cell + ':'
                    # newMtdUserProject = cell + ':' + irSuggest + '\r'
                    # newMtdUserProject = cell + ':' + irSuggest + '\r'

                    print('pdcLabel = = = ', pdcLabel)
                    print('pdcType3 = = = ', pdcType3)

                    # mtd.cellquestion
                    if pdcLabel == '原因':
                        # PROPERTIES_DB_CS.type3写入Manager_task_detail.cellquestion，逗号隔开
                        # newMtdUserQuestion += pdcType3 + ','
                        # newMtdUserProject += irSuggest

                        if pdcType3 not in type3List:
                            type3List.append(pdcType3)
                            userDict[cell].append(ir)

                    if pdcLabel == '原因定界':
                        for ice in tableImportComplainEvent:
                            iceRePresentation = ice[0]
                            iceAbnormalEvent = ice[1]

                            if (mtdType3 == iceRePresentation) and (iceAbnormalEvent == pdcType1):
                                # 把PROPERTIES_DB_CS.type3写入Manager_task_detail.cellquestion，然后换行

                                if pdcType3 not in type3List:
                                    type3List.append(pdcType3)
                                    userDict[cell].append(ir)

        print('更新cell' + str(index) + ' 完成')
        index += 1

    print("用户级原因更新完成!")

    # 结果呈现:
    if len(userDict) > 0:
        resultOn(userDict, dbPool, taskId, 'user')


def updateComplainTask(taskId, dbPool):
    """对单条工单工单进行更新 呈现其小区级原因 栅格级原因和用户级原因"""

    mtd = dbPool.select(
        "select TASK_DETAIL_ID,TTIME,ALLTTIME,DEF_CELLNAME,DEF_CELLNAME_CHINESE,type1,type3,THOUR,relation_cell,cellsuggest,cellquestion,cellproject,fault_datehour,REPLY from dbo.manager_task_detail where TASK_DETAIL_ID = %d" % (
            taskId))
    relation_cell = mtd[0][8]
    cellList = relation_cell.strip().split(',')
    mtdTTime = mtd[0][1]
    mtdDefCellName = mtd[0][3]  # 投诉工单中 def_cellanme 映射的是投诉工单号
    mtdType1 = mtd[0][5]
    mtdType3 = mtd[0][6]
    mtdFaultDatehour = mtd[0][12]
    list_hours = getMtdHours(mtdFaultDatehour)
    print('mtd = ', mtd)
    print('mtdDefCellName/投诉工单号 = ', mtdDefCellName)

    # 小区级原因生成
    print('*********************小区级原因生成*************************')
    # updateCell(dbPool, taskId, cellList, mtdTTime, list_hours, mtdType1, mtdType3)
    # updateCellSliceTest(dbPool, taskId, cellList, mtdTTime, list_hours, mtdType1, mtdType3)  # 引入表切片测试

    # # # 区域级原因生成
    print('*********************区域级原因生成*************************')
    updateOTT(dbPool, taskId, mtdDefCellName, cellList, mtdType1, mtdType3)
    # #
    # # # 用户级原因生成
    # print('*********************用户级原因生成*************************')
    # updateUser(dbPool, taskId, cellList, mtdDefCellName, mtdTTime, list_hours, mtdType1, mtdType3)


def getComplainTaskID(dbPool):
    # date = time.strftime('%Y-%m-%d')
    date = '2016-02-04'
    print(date)
    return dbPool.select(
        "select TASK_DETAIL_ID from manager_task_detail where type1 = '%s' and ttime = '%s';" % ('TS', date))


# Complain_OTT 最后一列新增 status  null 未处理  1 已处理
def getSiteInfo(dbpool, coCellname):
    tableSiteInfo = dbpool.select(
        "select DEF_CELLNAME,city,region,TOWN from SITE_INFO where ADDRESS = '1' and DEF_CELLNAME_CHINESE = '%s'" % (
            coCellname))

    if len(tableSiteInfo) > 0:
        return tableSiteInfo[0][0], tableSiteInfo[0][1], tableSiteInfo[0][2], tableSiteInfo[0][3]
    else:
        return None, None, None, None


# 栅格级原因  Complain_OTT -> 入属性库 properties_db_ott
def updatePropertiesDbAreaAndOTT(dbPool):
    """
    栅格级原因入库\n
    (1)栅格弱覆盖
    Complain_OTT中有新数据进来即status为空的数据，筛选Complain_OTT中Avg_Rsrp小于-110的记录，入属性库properties_db_ott
    """
    tableComplainOTT = dbPool.select(
        "select ID,WO_ID,Cell_Name,GridId,Grid_X,Grid_Y,Avg_Rsrp,Avg_Sinr from dbo.Complain_OTT where status is null")

    pdoList = []
    if len(tableComplainOTT) > 0:
        for ott in tableComplainOTT:
            print('ott = ', ott)

            coCellname = ott[2]
            coGridID = ott[3]
            coGridX = ott[4]
            coGridY = ott[5]
            coAvgRsrp = ott[6]
            coAvgSinr = ott[7]

            siDefCellname, siCity, siRegion, siTown = getSiteInfo(dbPool, coCellname)

            # 栅格弱覆盖
            if coAvgRsrp is not None and float(coAvgRsrp) < -110:
                id = ott[1]
                def_cellname = siDefCellname
                def_cellname_chinese = coCellname
                latitude = None
                longitude = None
                ttime = None
                thour = None
                city = siCity
                region = siRegion
                town = siTown
                gridid = coGridID
                latitude_grid = coGridX
                longitude_grid = coGridY
                type1 = 'TS'
                type2 = '覆盖'
                type3 = '栅格弱覆盖'
                fault_description = '用户占用小区' + def_cellname_chinese + '下栅格' + gridid + '存在栅格弱覆盖'
                label = '原因'
                ch_rat = None
                topn = None
                pri = None
                cur_value = coAvgRsrp
                level_r = '一般严重'
                rule_value = None
                fault_total = None
                solution = None

                pdoList.append(
                    [id, def_cellname, def_cellname_chinese, latitude, longitude, ttime, thour, city, region, town,
                     gridid, latitude_grid, longitude_grid, type1, type2, type3, fault_description, label, ch_rat, topn,
                     pri, cur_value, level_r, rule_value, fault_total, solution
                     ])

            # 区域质差
            if coAvgSinr is not None and float(coAvgSinr) < -3:
                id = ott[1]
                def_cellname = siDefCellname
                def_cellname_chinese = coCellname
                latitude = None
                longitude = None
                ttime = None
                thour = None
                city = siCity
                region = siRegion
                town = siTown
                gridid = coGridID
                latitude_grid = coGridX
                longitude_grid = coGridY
                type1 = 'TS'
                type2 = '覆盖'
                type3 = '栅格质差'
                fault_description = '用户占用小区' + def_cellname_chinese + '下栅格' + gridid + '存在栅格质差'
                label = '原因'
                ch_rat = None
                topn = None
                pri = None
                cur_value = coAvgSinr
                level_r = '一般严重'
                rule_value = None
                fault_total = None
                solution = None

                pdoList.append(
                    [id, def_cellname, def_cellname_chinese, latitude, longitude, ttime, thour, city, region, town,
                     gridid, latitude_grid, longitude_grid, type1, type2, type3, fault_description, label, ch_rat, topn,
                     pri, cur_value, level_r, rule_value, fault_total, solution
                     ])

    else:
        print("Complain_OTT表未查到满足条件的数据!")

    print('pdoList', pdoList)
    if len(pdoList) > 0:
        if dbPool.insertBatch(pdoList, 'properties_db_ott'):
            dbPool.update("update Complain_OTT set status = 1 where status is null")

    # # 然后更新Complain_OTT 的 status 为 1
    # #  怎么判断上面操作成功? 更新status呢?
    # dbPool.update("update Complain_OTT set status = 1 where status is null")


def getPdcCellname(dbPool, AbnormalEvent_cell):
    tableSiteInfo = dbPool.select(
        "select DEF_CELLNAME,CITY,REGION,TOWN,GRID from SITE_INFO where DEF_ECI = '%s'" % (AbnormalEvent_cell))
    if len(tableSiteInfo) > 0:
        return tableSiteInfo[0][0], tableSiteInfo[0][1], tableSiteInfo[0][2], tableSiteInfo[0][3], tableSiteInfo[0][4]
    else:
        return None


def updatePropertiesDbCs(dbPool):
    """
    (1) 用户弱覆盖
    Complain_User有新数据进来即status为空的数据，筛选Complain_User中RSRP小于-110的记录入属性库properties_db_cs

    (2) 用户cause定界
    当Complain_User有新数据进来即status为空，根据条件Complain_User. Interface_type=IMPORT_Complain_CONFIG.Interface_type，且Complain_User. CauseValue=IMPORT_Complain_CONFIG.CauseValue，关联出IMPORT_Complain_CONFIG. AbnormalEvent、IMPORT_Complain_CONFIG.Reason字段。入属性库properties_db_cs中
    """
    tableComplainUser = dbPool.select(
        "select ID,WO_ID,AbnormalEvent_Time,ttime,thour,Interface_type,CauseValue,def_cellname_chinese,AbnormalEvent_Cell,RSRP from Complain_User where status is null")

    pdcList = []
    for user in tableComplainUser:
        cuWOID = user[1]
        cuTime = user[3]
        cuHour = user[4]
        cuDefCellnameChinese = user[7]

        AbnormalEvent_cell = user[8]
        cuRsrp = float(user[9])

        siDefCellname, siCity, siRegion, siTown, siGrid = getPdcCellname(dbPool, AbnormalEvent_cell)

        if cuRsrp is not None and cuRsrp < -110:
            CS_ID = cuWOID  # WO_ID
            DEF_CELLNAME = siDefCellname
            TYPE1 = 'TS'
            TYPE2 = '覆盖'
            TYPE3 = '投诉用户弱覆盖'
            FAULT_OBJECT = CS_ID
            TTIME = cuTime
            city = siCity
            REGION = siRegion
            TOWN = siTown
            GRID = siGrid
            DEF_CELLNAME_CHINESE = cuDefCellnameChinese
            FAULT_DESCRIPTION = '用户占用小区' + DEF_CELLNAME_CHINESE + '存在用户弱覆盖'
            LABEL = '原因'
            THOUR = cuHour
            CH_RAT = None
            TOPN = None
            PRI = None
            CUR_VALUE = cuRsrp
            LEVEL_R = '一般严重'
            RULE_VALUE = None
            FAULT_TOTAL = None
            SOLUTION = None

            pdcList.append([CS_ID, DEF_CELLNAME, TYPE1, TYPE2, TYPE3, FAULT_OBJECT, TTIME, city, REGION, TOWN, GRID,
                            FAULT_DESCRIPTION, LABEL, THOUR, DEF_CELLNAME_CHINESE, CH_RAT, TOPN, PRI, CUR_VALUE,
                            LEVEL_R,
                            RULE_VALUE, FAULT_TOTAL, SOLUTION
                            ])

        # 将满足用户cause定界的记录也放到pdcList,一起入到属性库properties_db_cs中

        cuInterfaceType = user[5]
        cuCauseValue = user[6]

        # print('cuInterfaceType = ', cuInterfaceType)
        # print('cuCauseValue = ', cuCauseValue)

        tableTableImportCompainConfig = dbPool.select(
            "select Interface_type,AbnormalEvent,CauseValue,Reason from IMPORT_Complain_CONFIG where Interface_type = '%s' and CauseValue= '%s'" % (
                cuInterfaceType, cuCauseValue))  # 大约100多条

        if len(tableTableImportCompainConfig) > 0:
            for icc in tableTableImportCompainConfig:
                CS_ID = cuWOID  # WO_ID
                DEF_CELLNAME = siDefCellname
                TYPE1 = icc[1]
                TYPE2 = 'TS'
                TYPE3 = icc[3]
                FAULT_OBJECT = CS_ID
                TTIME = cuTime
                city = siCity
                REGION = siRegion
                TOWN = siTown
                GRID = siGrid
                DEF_CELLNAME_CHINESE = cuDefCellnameChinese
                FAULT_DESCRIPTION = '用户占用小区' + DEF_CELLNAME_CHINESE + '由于' + TYPE3 + '导致投诉'
                LABEL = '原因定界'
                THOUR = cuHour
                CH_RAT = None
                TOPN = None
                PRI = None
                CUR_VALUE = cuRsrp
                LEVEL_R = '一般严重'
                RULE_VALUE = None
                FAULT_TOTAL = None
                SOLUTION = None

                pdcList.append(
                    [CS_ID, DEF_CELLNAME, TYPE1, TYPE2, TYPE3, FAULT_OBJECT, TTIME, city, REGION, TOWN, GRID,
                     FAULT_DESCRIPTION, LABEL, THOUR, DEF_CELLNAME_CHINESE, CH_RAT, TOPN, PRI, CUR_VALUE,
                     LEVEL_R,
                     RULE_VALUE, FAULT_TOTAL, SOLUTION
                     ])
        else:
            print('There is no data in table IMPORT_Complain_CONFIG!')

    print('pdcList = ', pdcList)

    # pdcList 插入到  properties_db_cs
    if len(pdcList) > 0:
        if dbPool.insertBatch(pdcList, 'properties_db_cs'):
            dbPool.update("update Complain_User set status = 1 where status is null ")

    # 然后更新Complain_User
    #  的 status 为 1
    #  怎么判断上面操作成功? 更新status呢?
    # dbPool.update("update Complain_User set status = 1 where status is null ")


def main(dbtype):
    """主函数"""
    dbPool = PyDBPool(dbtype)

    # 数据预处理
    # 通过 Complain_OTT 更新(插入) properties_db_area/properties_db_OTT
    updatePropertiesDbAreaAndOTT(dbPool)

    # # 通过 Complain_User 更新(插入) properties_db_cs
    updatePropertiesDbCs(dbPool)
    #
    # 获取所有工单号
    complainTaskIDList = getComplainTaskID(dbPool)
    print(complainTaskIDList)

    # 处理单条工单
    for taskId in complainTaskIDList:
        taskId = taskId[0]
        print('taskId = ', taskId)
        updateComplainTask(taskId, dbPool)
    dbPool.close()


if __name__ == '__main__':
    dbtype = 'mssql'
    main(dbtype)
