import time
from ExcelProject.PyDBPool import PyDBPool  # 程序内

"""
ComplainTask  投诉工单 数据流处理
   
"""


# Manager_task_detail.fault_datehour包含PROPERTIES_DB.thour   hour有交集就ok
def getTablePropertiesDB(dbPool, cell, mtdTTime, list_hours):
    tablePropertiesDb = dbPool.select(
        "select convert(nvarchar(255),pd.DEF_CELLNAME_CHINESE),convert(nvarchar(255),pd.TYPE3),pd.TTIME,convert(nvarchar(255),pd.LEVEL_R),pd.THOUR FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME_CHINESE = '%s' and pd.TTIME = '%s'" % (
            (cell, mtdTTime)))

    print("tablePropertiesDb = :", tablePropertiesDb)
    print("tablePropertiesDb length = ", len(tablePropertiesDb))

    tablePropertiesDbNew = []
    for t in tablePropertiesDb:
        print('t = ', t)
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


# pdo -- 改为 pda
def updateOTT(dbPool, taskId, mtdDefCellName, cellList, mtdType1, mtdType3):
    index = 1
    for cell in cellList:
        tablePropertiesDBArea = getTablePropertiesDBArea(dbPool, cell, mtdDefCellName)
        tableImportReason = getTableImportReason(dbPool, mtdType1, mtdType3)

        for pda in tablePropertiesDBArea:
            pdaType3 = pda[9]
            pdaLevelR = pda[1]  # pda 没有level_r 字段?

            print('pdaType3 = ', pdaType3)
            print('pdaLevelR = ', pdaLevelR)

            for ir in tableImportReason:
                irReason = ir[0]
                irLevelR = ir[1]

                irSuggest = ir[2]
                print('irReason = ', irReason)
                print('irLevelR = ', irLevelR)

                if (pdaType3 == irReason) and (pdaLevelR == irLevelR):
                    newMtdOTTQuestion = cell + ':' + pdaType3 + '\r'
                    newMtdOTTProject = cell + ':' + irSuggest + '\r'
                    print('newMtdOTTQuestion = ', newMtdOTTQuestion)
                    print('newMtdOTTProject = ', newMtdOTTProject)

                    updateMtdQuestionAndProject(dbPool, newMtdOTTQuestion, newMtdOTTProject, taskId)
        print('更新cell' + str(index) + ' 完成')
        index += 1

        print("区域级原因更新完成!")


def getMtdHours(fault_datehour):
    list_hours = []
    date_hours = fault_datehour.split(';')
    for y in date_hours:
        hours = y.split(':')[1]
        for h in hours.split(","):
            list_hours.append(int(h))
    print('list_hours = ', list_hours)
    return list_hours


def getTablePropertiesDBCs(dbPool, cell, mtdDefCellName, mtdTTime, list_hours):
    tablePropertiesDBCs = dbPool.select(
        "select * from PROPERTIES_DB_CS where DEF_CELLNAME_CHINESE = '%s' and CS_ID = '%s' and TTIME = '%s'" % (
            cell, mtdDefCellName, mtdTTime))
    print("tablePropertiesDBCs = :", tablePropertiesDBCs)
    print("tablePropertiesDBCs length = ", len(tablePropertiesDBCs))

    tablePropertiesDbCsNew = []
    for t in tablePropertiesDBCs:
        thour = t[6]
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


def updateUser(dbPool, taskId, cellList, mtdDefCellName, mtdTTime, list_hours, mtdType1, mtdType3):
    index = 1
    irList = []

    for cell in cellList:
        tablePropertiesDBCs = getTablePropertiesDBCs(dbPool, cell, mtdDefCellName, mtdTTime, list_hours)
        tableImportReason = getTableImportReason(dbPool, mtdType1, mtdType3)
        tableImportComplainEvent = getTableImportComplainEvent(dbPool)

        for pdc in tablePropertiesDBCs:
            pdcType1 = pdc[2]
            pdcType3 = pdc[4]
            pdcLevelR = pdc[19]
            pdcLabel = pdc[12]  # '原因' 和 '原因定界两种'

            print('pdcType1 = ', pdcType1)
            print('pdcType3 = ', pdcType3)
            print('pdcLevelR = ', pdcLevelR)
            print('pdcLabel = ', pdcLabel)

            for ir in tableImportReason:
                irReason = ir[0]
                irLevelR = ir[1]

                irSuggest = ir[2]
                irPriority = ir[3]

                print('irReason = ', irReason)
                print('irLevelR = ', irLevelR)
                print('irPriority = ', ir[3])

                if (pdcType3 == irReason) and (pdcLevelR == irLevelR):
                    #  新增判断逻辑

                    # --  todo  --
                    irList.append(ir)

                    newMtdUserQuestion = cell + ':'
                    newMtdUserProject = cell + ':' + irSuggest + '\r'
                    print('newMtdUserQuestion = ', newMtdUserQuestion)
                    print('newMtdUserProject = ', newMtdUserProject)

                    # mtd.cellquestion
                    if pdcLabel == '原因':
                        # PROPERTIES_DB_CS.type3写入Manager_task_detail.cellquestion，逗号隔开
                        newMtdUserQuestion += pdcType3 + '\r'

                    if pdcLabel == '原因定界':
                        for ice in tableImportComplainEvent:
                            iceRePresentation = ice[0]
                            iceAbnormalEvent = ice[1]

                            if (mtdType3 == iceRePresentation) and (iceAbnormalEvent == pdcType1):
                                # 把PROPERTIES_DB_CS.type3写入Manager_task_detail.cellquestion，然后换行
                                newMtdUserQuestion += pdcType3 + '\r'

                    updateMtdQuestionAndProject(dbPool, newMtdUserQuestion, newMtdUserProject, taskId)

                    # mtd.cellproject
                    # 集合收集 ir 按优先级排序

                    # update again

        print('更新cell' + str(index) + ' 完成')
        index += 1
        print("用户级原因更新完成!")
    print('irList = ', irList)
    # select ir.reason,ir.level_r,ir.suggest,ir.priority from import_reason
    # irList=[(),(),()]
    if len(irList) > 0:
        # 按第四个元素 优先级 进行排序
        irListSort = sorted(list(irList), key=lambda x: x[3])[0:3]

        for ir in irListSort:
            irReason = ir[0]
            # 更新irReason到mtd.cellQuestion


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
    list_hours = getMtdHours(mtdFaultDatehour)
    print('mtdDefCellName = ', mtdDefCellName)  # mtd cellname 放的是投诉工单号

    # 小区级原因生成
    # updateCell(dbPool, taskId, cellList, mtdTTime, list_hours, mtdType1, mtdType3)

    # # 区域级原因生成
    updateOTT(dbPool, taskId, mtdDefCellName, cellList, mtdType1, mtdType3)
    #
    # # for cell in cellList:
    # # 用户级原因生成
    updateUser(dbPool, taskId, cellList, mtdDefCellName, mtdTTime, list_hours, mtdType1, mtdType3)


def getComplainTaskID(dbPool):
    # date = time.strftime('%Y-%m-%d')
    date = '2016-02-04'
    print(date)
    return dbPool.select(
        "select TASK_DETAIL_ID from manager_task_detail where type1 = '%s' and ttime = '%s';" % ('TS', date))


# 确定ott    待确定?
# Complain_OTT 最后一列新增 status  0 未处理  1 已处理
def getSiteInfoCellName(dbpool):
    tableSiteInfo = dbpool.select("select top 1 DEF_CELLNAME from SITE_INFO where ADDRESS = 1")
    return tableSiteInfo[0][0]


def updatePropertiesDbAreaAndOTT(dbPool):
    tableComplainOTT = dbPool.select("select * from Complain_OTT where status is null", 'all')

    pdaList = []
    pdoList = []
    if len(tableComplainOTT) > 0:
        for ott in tableComplainOTT:
            print('ott = ', ott)

            avgRsrp = ott[5]
            avgRsinr = ott[6]
            if avgRsrp is not None and float(avgRsrp) < -110:
                areaId = ott[0]  # WO_ID
                areaType = '弱覆盖区域'
                ttime = None
                label = '原因'

                # def_cellname = ''  # SITE_INFO对应字段且site_info.address=’1’的英文名
                # --todo--
                def_cellname = getSiteInfoCellName(dbPool)
                defCellnameChinese = ott[1]  # ottcellname
                type1 = 'TS'
                type2 = '覆盖'
                type3 = '投诉区域弱覆盖'
                thour = None
                # --todo ask--
                fault_description = "‘用户占用小区’& Def_Cellname_chinese&’栅格存在区域弱覆盖’"
                fault_total = None
                reason_ratio = None
                CUR_VALUE = avgRsrp

                pdaList.append([
                    areaId, areaType, ttime, label, def_cellname, defCellnameChinese, type1, type2, type3, thour,
                    fault_description, fault_total, reason_ratio, CUR_VALUE])

            # 区域质差
            if avgRsinr is not None and float(avgRsinr) < -3:
                areaId = ott[0]  # WO_ID
                areaType = '高质差区域'
                ttime = None
                label = '原因'
                def_cellname = getSiteInfoCellName(dbPool)
                defCellnameChinese = ott[1]  # ottcellname
                type1 = 'TS'
                type2 = '覆盖'
                type3 = '投诉区域高质差'
                thour = None
                fault_description = "‘用户占用小区’& Def_Cellname_chinese&’栅格存在区域弱覆盖’"
                fault_total = None
                reason_ratio = None
                CUR_VALUE = avgRsinr

                # todo properties_db_area 中id 怎么确定?
                pdoList.append([
                    areaId, areaType, ttime, label, def_cellname, defCellnameChinese, type1, type2, type3, thour,
                    fault_description, fault_total, reason_ratio, CUR_VALUE])
    else:
        print("未查到满足条件的数据!")

    print('pdaList', pdaList)
    print('pdoList', pdoList)
    # # 将pdaList 插入到  properties_db_area
    if len(pdaList) > 0:
        dbPool.insertBatch(pdaList, 'properties_db_area')
    #
    # # 将pdoList 插入到  properties_db_OTT
    # if len(pdoList) > 0:
    #     dbPool.insertBatch(pdaList, 'properties_db_OTT')
    #
    # # 然后更新Complain_OTT 的 status 为 1
    # #  怎么判断上面操作成功? 更新status呢?
    dbPool.update("update Complain_OTT set status = 1 where status is null")


def getPdcCellname(dbPool, AbnormalEvent_cell):
    tableSiteInfo = dbPool.select(
        "select top 1 DEF_CELLNAME from SITE_INFO where DEF_ECI = '%s'" % (AbnormalEvent_cell))
    if len(tableSiteInfo) > 0:
        return tableSiteInfo[0][0]
    else:
        return None


def updatePropertiesDbCs(dbPool):
    tableComplainUser = dbPool.select("select * from Complain_User where status is null", 'all')

    pdcList = []

    # todo 搞一个字典  {}  如果ID 已经存在 追加thour
    # 判断Wo_ID 工单Id是否一样, 如果一样,只有AbnormalEvent_Time?

    cuDict = {}
    for user in tableComplainUser:
        Rsrp = float(user[9])
        AbnormalEvent_cell = user[6]
        print('AbnormalEvent_cell = ', AbnormalEvent_cell)  # 6729271

        AbnormalEvent_Time = user[1]
        print('AbnormalEvent_Time = ', AbnormalEvent_Time)

        if Rsrp is not None and Rsrp < -110:
            ID = user[0]  # WO_ID
            DEF_CELLNAME = getPdcCellname(dbPool, AbnormalEvent_cell)
            TYPE1 = 'TS'
            TYPE2 = '覆盖'
            TYPE3 = '投诉用户弱覆盖'
            FAULT_OBJECT = ID
            TTIME = user[1]  # todo  抽取日期
            city = ''
            REGION = ''
            TOWN = ''
            GRID = ''
            FAULT_DESCRIPTION = '用户占用小区& DEF_CELLNAME_CHINESE&存在用户弱覆盖'
            LABEL = '原因'
            THOUR = ''  # todo 抽取小时（如有多个用逗号隔开）工单号不唯一
            DEF_CELLNAME_CHINESE = user[5]
            CH_RAT = None
            TOPN = None
            PRI = None
            CUR_VALUE = Rsrp
            LEVEL_R = '一般严重'
            RULE_VALUE = None
            FAULT_TOTAL = None
            SOLUTION = None

            pdcList.append([ID, DEF_CELLNAME, TYPE1, TYPE2, TYPE3, FAULT_OBJECT, TTIME, city, REGION, TOWN, GRID,
                            FAULT_DESCRIPTION, LABEL, THOUR, DEF_CELLNAME_CHINESE, CH_RAT, TOPN, PRI, CUR_VALUE,
                            LEVEL_R,
                            RULE_VALUE, FAULT_TOTAL, SOLUTION
                            ])

        # 将满足用户cause定界的记录也放到pdcList,一起入到属性库properties_db_cs中

        cuInterfaceType = user[2]
        cuCauseValue = user[4]

        print('cuInterfaceType = ', cuInterfaceType)
        print('cuCauseValue = ', cuCauseValue)

        tableTableImportCompainConfig = dbPool.select(
            "select Interface_type,AbnormalEvent,CauseValue,Reason from IMPORT_Complain_CONFIG", 'all')  # 大约100多条

        if len(tableTableImportCompainConfig) > 0:
            for icc in tableTableImportCompainConfig:
                iccInterfaceType = icc[0]
                iccCauseValue = icc[2]

                if (cuInterfaceType == iccInterfaceType) and (cuCauseValue == iccCauseValue):
                    print('iccInterfaceType = ', iccInterfaceType)
                    print('iccCauseValue = ', iccCauseValue)

                    iccAbnormalEvent = icc[1]
                    iccReason = icc[3]

                    print('iccAbnormalEvent = ', iccAbnormalEvent)
                    print('iccReason = ', iccReason)

                    ID = user[0]  # WO_ID
                    DEF_CELLNAME = getPdcCellname(dbPool, AbnormalEvent_cell)
                    TYPE1 = iccAbnormalEvent
                    TYPE2 = 'TS'
                    TYPE3 = iccReason
                    FAULT_OBJECT = ID
                    TTIME = user[1]  # todo  抽取日期
                    city = ''
                    REGION = ''
                    TOWN = ''
                    GRID = ''
                    FAULT_DESCRIPTION = '用户占用小区& DEF_CELLNAME_CHINESE&由于&IMPORT_Complain_CONFIG. Reason&导致投诉'
                    LABEL = '原因定界'
                    THOUR = ''  # todo
                    DEF_CELLNAME_CHINESE = user[5]
                    CH_RAT = None
                    TOPN = None
                    PRI = None
                    CUR_VALUE = Rsrp
                    LEVEL_R = '一般严重'
                    RULE_VALUE = None
                    FAULT_TOTAL = None
                    SOLUTION = None

                    pdcList.append(
                        [ID, DEF_CELLNAME, TYPE1, TYPE2, TYPE3, FAULT_OBJECT, TTIME, city, REGION, TOWN, GRID,
                         FAULT_DESCRIPTION, LABEL, THOUR, DEF_CELLNAME_CHINESE, CH_RAT, TOPN, PRI, CUR_VALUE,
                         LEVEL_R,
                         RULE_VALUE, FAULT_TOTAL, SOLUTION
                         ])
        else:
            print('There is no data in table IMPORT_Complain_CONFIG!')

    print('pdcList = ', pdcList)
    # pdcList 插入到  properties_db_cs
    # dbPool.insertBatch(pdcList, 'properties_db_cs')

    # 然后更新Complain_User
    #  的 status 为 1
    #  怎么判断上面操作成功? 更新status呢?
    # dbPool.update("update Complain_User set status = 1 where status = 0")

    # 用户cause定界 更新 pdc


def main(dbtype):
    dbPool = PyDBPool(dbtype)

    # 数据预处理
    # 通过 Complain_OTT 更新(插入) properties_db_area/properties_db_OTT
    updatePropertiesDbAreaAndOTT(dbPool)

    # 通过 Complain_User 更新(插入) properties_db_cs
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


if __name__ == '__main__':
    dbtype = 'mssql'
    main(dbtype)
