USE [ROSAS_WEB]
GO

/****** Object:  StoredProcedure [dbo].[update_mtd_type_pro]    Script Date: 2018/1/29 14:24:02 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[update_mtd_type_pro] WITH ENCRYPTION
AS
IF OBJECT_ID('mtd_reason_suggest_33', 'U') IS NOT NULL
BEGIN
	DROP TABLE mtd_reason_suggest_33
END;;

WITH table_s1 --时间系数step1
AS (
	SELECT DISTINCT m.TASK_DETAIL_ID
		,r.Reason
		,p.type3
		,m.fault_datehour
		,p.TTIME + ':' + p.THOUR AS date_hour
	FROM mtd m
	JOIN PROPERTIES_DB_FOR_DETAIL p ON m.def_cellname = p.def_cellname
	JOIN (
		SELECT *
		FROM report_rule
		--WHERE effect = 1
		) r ON p.type3 = r.type3 AND (CASE WHEN m.type1 in ('LH','HBLH') then 0 else 1 END)=r.effect
	WHERE p.LABEL = '原因'
	)
	,table_s2 --时间系数step2
AS (
	SELECT *
		,all_date_hour = stuff((
				SELECT ';' + date_hour
				FROM table_s1 t
				WHERE TASK_DETAIL_ID = table_s1.TASK_DETAIL_ID
					AND reason = table_s1.reason
				FOR XML path('')
				), 1, 1, '')
	FROM table_s1
	)
	,table_s3 --时间系数step3
AS (
	SELECT *
		,CASE 
			WHEN charindex(',', all_date_hour) = 0
				AND len(replace(all_date_hour, 'D', '')) = len(REPLACE(all_date_hour, ':', '')) -- 只有allday的情况判断：没有逗号 and [D]的数量跟[:]数量相同
				THEN CASE 
						WHEN reason IN (
								'参数问题'
								,'参数一致性问题'
								,'单向邻区'
								,'工参不合理'
								)
							THEN 0.3 --只有allday的情况并且reason符合某些条件 取0.3
						ELSE 0.5 --只有allday的情况取0.5
						END
			ELSE ROUND(dbo.DateTimeInStringCount(fault_datehour, all_date_hour) / (CONVERT(FLOAT, LEN(fault_datehour) - len(REPLACE(REPLACE(fault_datehour, ',', ''), ':', '')))), 2)
			END AS time_coefficient -- 时间系数 
	FROM table_s2
	)
SELECT DISTINCT t1.TASK_DETAIL_ID
	,t1.type1
	,t1.def_cellname
	,t2.TYPE3 as reason --db表的type3字段
	,r1.priority
	,r1.importantreason
	,t2.ttime
	,(
		(
			ISNULL(t4.time_coefficient, 0) -- 时间系数
			) + (0.9 - (0.0004 * r1.rank_number)) -- 专家法系数
		) / 2 AS coefficient -- 关键问题原因系数=0.1+（专家法系数+时间相关系数）/2
INTO mtd_reason_suggest_33
FROM mtd t1
JOIN PROPERTIES_DB_FOR_DETAIL t2 ON dbo.IsInFault_DateHour(t1.fault_datehour, t2.ttime, t2.thour) = 1 --db表
	AND t1.DEF_CELLNAME = t2.DEF_CELLNAME
JOIN (
	SELECT *
		,ROW_NUMBER() OVER (
			PARTITION BY type1
			,representation ORDER BY [priority]
			) AS rank_number
	FROM import_reason
	) r1 ON master.dbo.irh(t2.TYPE3) = r1.reason
	AND r1.type1 = t1.type1
	AND t2.LEVEL_R = r1.LEVEL_R
LEFT JOIN table_s3 t4 ON t1.TASK_DETAIL_ID = t4.TASK_DETAIL_ID --时间系数表
	AND t4.type3 = r1.reason
WHERE charindex(r1.representation + ';', t1.type3 + ';') > 0;-- mtd.type3 = import_reason.representation

UPDATE db
SET db.rule_value = round(coefficient, 2)
FROM mtd_reason_suggest_33 m
JOIN properties_db db ON m.def_cellname = db.def_cellname
	AND m.ttime = db.ttime
	AND m.reason = db.type3

--WHERE db.LABEL = '原因'
IF OBJECT_ID('temp_mtd_rule1') IS NOT NULL
BEGIN
	DROP TABLE temp_mtd_rule1;
END

IF OBJECT_ID('temp_Type_pro1') IS NOT NULL
BEGIN
	DROP TABLE temp_Type_pro1;
END;

WITH table0
AS (
	SELECT DISTINCT TASK_DETAIL_ID
		,type1
		,reason
		,coefficient
	FROM (
		SELECT *
		FROM (
			SELECT *
				,ROW_NUMBER() OVER (
					PARTITION BY TASK_DETAIL_ID ORDER BY priority
					) AS row_no
			FROM mtd_reason_suggest_33
			) t1
		
		UNION
		
		(
			SELECT *
				,1 AS row_no
			FROM mtd_reason_suggest_33
			WHERE importantreason != 0
			)
		) t3
	WHERE row_no <= 3
	)
SELECT *
INTO temp_mtd_rule1
FROM (
	SELECT t1.TASK_DETAIL_ID
		,t2.reason
		,max(t1.coefficient) AS coefficient
	FROM table0 t1
	JOIN (
		SELECT *
		FROM report_rule
		--WHERE effect = 1
		) t2 ON t1.reason = t2.type3 AND (CASE WHEN t1.type1 in ('LH','HBLH') then 0 else 1 END)=t2.effect
	--WHERE t1.row_no <= 3
	GROUP BY t1.TASK_DETAIL_ID
		,t2.reason
	) t

SELECT TASK_DETAIL_ID
	,Type_pro = STUFF((
			SELECT CONCAT(reason, '(', CONVERT(VARCHAR(50), round(coefficient, 2)), ');')
			FROM temp_mtd_rule1 AS t1
			WHERE t1.TASK_DETAIL_ID = temp_mtd_rule1.TASK_DETAIL_ID
			ORDER BY coefficient DESC
			FOR XML path('')
			), 1, 0, '')
INTO temp_Type_pro1
FROM temp_mtd_rule1

UPDATE m
SET type_pro = t1.Type_pro
FROM manager_task_detail m
JOIN temp_Type_pro1 t1 ON m.TASK_DETAIL_ID = t1.TASK_DETAIL_ID

GO


USE [ROSAS_WEB]
GO

/****** Object:  StoredProcedure [dbo].[update_mtd_type_pro_hour]    Script Date: 2018/1/22 17:28:01 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[update_mtd_type_pro_hour] WITH ENCRYPTION
AS
--此存储过程在update_manager_task_detail_hour中调用
WITH properties_db_for_type_pro -- 保存的是properties_db和properties_db_hour的数据 ，from_table_name区分数据来自哪里
AS (
	SELECT *
	FROM (
		SELECT def_cellname
			,type1
			,ttime
			,thour
			,type3
			,level_r
			,'db' AS from_table_name
		FROM temp_manager_task_detail_hour_4
		--WHERE label = '原因'
		
		UNION
		
		SELECT def_cellname
			,type1
			,ttime
			,thour
			,type3
			,level_r
			,'db_hour' AS from_table_name
		FROM temp_manager_task_detail_hour_5
		--WHERE label = '原因'
		) t
	)
	,mtd_db_imp_reason --关联取出  priority,importantreason 和系数coefficient
AS (
	SELECT t1.TASK_DETAIL_ID
		,t2.TYPE3 as reason
		,r1.priority
		,r1.importantreason
		,(
			(
				1 -- 时间系数
				) + (0.9 - (0.0004 * r1.rank_number)) -- 专家法系数
			) / 2 AS coefficient -- 关键问题原因系数=0.1+（专家法系数+时间相关系数）/2
	FROM mtd t1
	JOIN properties_db_for_type_pro t2 ON t1.TTIME = t2.TTIME
		AND t1.DEF_CELLNAME = t2.DEF_CELLNAME
	JOIN (
		SELECT *
			,ROW_NUMBER() OVER (
				PARTITION BY type1
				,representation ORDER BY [priority]
				) AS rank_number
		FROM import_reason
		) r1 ON master.dbo.irh(t2.TYPE3) = r1.reason
		AND r1.type1 = t1.type1
		AND t2.LEVEL_R = r1.LEVEL_R
	WHERE charindex(r1.representation + ';', t1.type3 + ';') > 0
		AND (
			t2.from_table_name = 'db'
			OR ISNUMERIC(t2.thour) = 1
			AND (
				t1.THOUR = t2.THOUR
				OR CONVERT(INT, t1.thour) - 1 = CONVERT(INT, t2.thour) --detail表thour -1 (即前一个小时)  = db_hour表的 thour
				)
			)
	)
	,table1 -- 按 priority排序 取前三 和  importantreason != 0 de 数据
AS (
	SELECT TASK_DETAIL_ID
		,reason
		,coefficient
	FROM (
		(
			SELECT TASK_DETAIL_ID
				,reason
				,coefficient
				,ROW_NUMBER() OVER (
					PARTITION BY TASK_DETAIL_ID ORDER BY [priority]
					) AS row_no
			FROM mtd_db_imp_reason
			)
		
		UNION
		
		(
			SELECT TASK_DETAIL_ID
				,reason
				,coefficient
				,1 AS row_no
			FROM mtd_db_imp_reason
			WHERE importantreason != 0
			)
		) t
	WHERE row_no <= 3
	)
	,table2
AS (
	SELECT TASK_DETAIL_ID
		,t2.Reason
		,coefficient
		,ROW_NUMBER() OVER (
			PARTITION BY TASK_DETAIL_ID
			,t2.Reason ORDER BY pri
			) AS row_no
	FROM (
		SELECT DISTINCT TASK_DETAIL_ID
			,reason
			,coefficient
		FROM table1
		) t1
	JOIN (
		SELECT *
		FROM report_rule
		WHERE effect = 0
		) t2 ON t1.reason = t2.type3
	)
	,table3
AS (
	SELECT TASK_DETAIL_ID
		,CONCAT(Reason, '(', convert(VARCHAR(50), max(round(convert(FLOAT, coefficient), 2))), ')') AS type_pro
	FROM table2
	WHERE row_no = 1
	GROUP BY TASK_DETAIL_ID
		,Reason
	)
	,table4
AS (
	SELECT TASK_DETAIL_ID
		,type_pro = STUFF((
				SELECT ';' + type_pro
				FROM table3 AS t1
				WHERE t1.TASK_DETAIL_ID = table3.TASK_DETAIL_ID
				FOR XML path('')
				), 1, 1, '')
	FROM table3
	)
UPDATE m
SET type_pro = t4.type_pro
FROM mtd m
JOIN table4 t4 ON m.TASK_DETAIL_ID = t4.TASK_DETAIL_ID


UPDATE m
SET type_pro = t4.type_pro
FROM manager_task_detail m
JOIN mtd t4 ON m.TASK_DETAIL_ID = t4.TASK_DETAIL_ID

GO