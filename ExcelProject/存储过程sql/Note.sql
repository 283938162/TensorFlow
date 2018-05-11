DAY

1. 取出detail表一条记录存放到变量@single_manager_task_detail

SELECT *
FROM manager_task_detail
WHERE TASK_DETAIL_ID = @input_param
	AND TYPE1 != 'XN'

@input_param:程序接收的输入参数
若无记录则跳出

2.判断

SELECT *
FROM DATA_DATE
WHERE ttime = @single_manager_task_detail.ttime
	AND thour = '23'


是否由记录
若无记录则跳出

3.把 @single_manager_task_detail.fault_datehour  里面的所有日期取出来,存放到变量@list_date

4.取出记录

SELECT DEF_CELLNAME
	,TYPE1
	,TYPE3
	,TTIME
	,FAULT_DESCRIPTION
	,LABEL
	,THOUR
	,LEVEL_R
FROM PROPERTIES_DB
WHERE ttime IN (ConvertToSql(@list_date))   -- ConvertToSql 为程序内方法: 把list拼凑成sql语句,  eg: list=['2018-01-02','2018-01-03']  则拼凑成字符串:'2018-01-02','2018-01-03'
	AND def_cellname = @single_manager_task_detail.def_cellname

存放到变量@table_properties_db (数据量大概0~300)

5.@table_properties_db去除不符合条件的记录

判断@table_properties_db[n].ttime  , @table_properties_db[n].thour  改时间段是否存在@single_manager_task_detail.fault_datehour 内
若不存在,则删除






5.取出记录

SELECT *
FROM import_reason
WHERE type1 = @single_manager_task_detail.type1
	AND charindex(';' + representation + ';', ';' + @single_manager_task_detail.type3 + ';') > 0   -- charindex: mssql 函数, 在mysql中为instr  ,使用方法请查找相关文档

存放到变量 @table_import_reason (数据量大概0~50000)



6.  @table_properties_db  与  @table_import_reason 在程序内做关联 即 @table_properties_db join @table_import_reason

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

并存放到变量@list_reason_suggest




7.@list_reason_suggest 按priority升序排列 取top5   再加上  importantreason != 0 的记录  并去重 存放到变量 @list_reason_suggest_match


8.合并 @list_reason_suggest_match

合并后的字段
suggest,reason,[ttime1:thour1,thour2....,ttime2:thour1.....]

即把相同的suggest,reason记录里面日期和小时合并到一起





















