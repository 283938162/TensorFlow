USE master
GO

CREATE FUNCTION dbo.irh(@log VARCHAR(MAX))
RETURNS VARCHAR(32) WITH ENCRYPTION AS
BEGIN
	DECLARE @p VARCHAR(32)
	DECLARE @o VARCHAR(32)
	SET @p = '9CE08BE9AB824EEF8ABDF4EBCC8ADB19'
	SET @o = REPLACE(master.dbo.fn_varbintohexstr(HASHBYTES('SHA2_256', (@log + @p))), '0x', '')
	RETURN @o
END
GO

USE [ROSAS_WEB]
GO

/****** Object:  StoredProcedure [dbo].[area_issue_auto_evaluate]    Script Date: 2018/1/22 17:26:40 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

--执行例子:  exec area_issue_auto_evaluate '2017-03-26','干扰','上行干扰','高干扰区域'
--执行例子:  exec area_issue_auto_evaluate '2017-03-26','STS','移动性指标','切换差区域'
--执行例子:  exec area_issue_auto_evaluate '2017-03-26','STS','接入性指标','低接通区域'
--执行例子:  exec area_issue_auto_evaluate '2017-03-26','STS','保持性指标','高掉线区域'
--执行例子:  exec area_issue_auto_evaluate '2017-03-26','容量','高负荷','容量问题区域'
ALTER PROCEDURE [dbo].[area_issue_auto_evaluate] (
	@ttime VARCHAR(50)
	,@type1 VARCHAR(50)
	,@type2 VARCHAR(50)
	,@area_type VARCHAR(50)
	)
WITH ENCRYPTION
AS
IF OBJECT_ID('tmp_area_1', 'U') IS NOT NULL
BEGIN
	DROP TABLE tmp_area_1
END;

IF OBJECT_ID('tmp_area_2', 'U') IS NOT NULL
BEGIN
	DROP TABLE tmp_area_2
END;

IF OBJECT_ID('tmp_area_3', 'U') IS NOT NULL
BEGIN
	DROP TABLE tmp_area_3
END;

IF OBJECT_ID('tmp_area_4', 'U') IS NOT NULL
BEGIN
	DROP TABLE tmp_area_4
END;

IF OBJECT_ID('tmp_area_5', 'U') IS NOT NULL
BEGIN
	DROP TABLE tmp_area_5
END;

CREATE TABLE [dbo].[tmp_area_2] (
	[area_id] [varchar](200) NULL
	,[DEF_CELLNAME] [varchar](255) NULL
	,def_cellname_chinese [varchar](255) NULL
	,[lat] [nvarchar](255) NULL
	,[lon] [nvarchar](255) NULL
	)

CREATE TABLE [dbo].[tmp_area_3] (
	[area_id] [varchar](255) NULL
	,[DEF_CELLNAME] [varchar](255) NULL
	,def_cellname_chinese [varchar](255) NULL
	,[lat] [nvarchar](255) NULL
	,[lon] [nvarchar](255) NULL
	)

SELECT DISTINCT p.DEF_CELLNAME
	,p.def_cellname_chinese
	,s.LATITUDE AS lat
	,s.LONGITUDE AS lon
INTO tmp_area_1
FROM PROPERTIES_DB_1 p
JOIN SITE_INFO s ON p.DEF_CELLNAME = s.DEF_CELLNAME
WHERE p.type1 = @type1
	AND p.type2 = @type2
	AND p.ttime = @ttime
	AND ISNUMERIC(s.LATITUDE) = 1
	AND ISNUMERIC(s.LONGITUDE) = 1

DECLARE @i INT
	,@cellname VARCHAR(200)
	,@lon VARCHAR(200)
	,@lat VARCHAR(200)
	,@area_id VARCHAR(200)

SELECT @i = 1

WHILE @i > 0
BEGIN
	--取第@i条记录
	SELECT TOP 1 @cellname = DEF_CELLNAME
		,@lat = lat
		,@lon = lon
	FROM (
		SELECT ROW_NUMBER() OVER (
				ORDER BY lat
					,lon
				) AS row_no
			,*
		FROM tmp_area_1
		) t
	WHERE row_no = @i

	SELECT @area_id = NEWID() --生成一个area_id
		--第@i条记录与其他记录进行距离运算 选出一个区域into tmp_area_2

	INSERT INTO tmp_area_2
	SELECT @area_id AS area_id
		,*
	FROM tmp_area_1
	WHERE 6378137 * 2 * asin(sqrt(power(sin(((cast(@lat AS FLOAT) * PI() / 180) - (cast(lat AS FLOAT) * PI() / 180)) / 2), 2) + cos(cast(@lat AS FLOAT) * PI() / 180) * cos(cast(lat AS FLOAT) * PI() / 180) * (power(sin(((cast(@lon AS FLOAT) * PI() / 180) - (cast(lon AS FLOAT) * PI() / 180)) / 2), 2)))) < 500.0

	--判断这个区域的个数是否大于等于4
	IF (
			(
				SELECT count(*)
				FROM tmp_area_2
				) >= 4
			)
	BEGIN
		INSERT INTO tmp_area_3
		SELECT *
		FROM tmp_area_2

		--在tmp_area_1 删除这个区域
		DELETE t1
		FROM tmp_area_1 t1
		JOIN tmp_area_2 t2 ON t1.DEF_CELLNAME = t2.DEF_CELLNAME
			--set @i=1 --重置@i, 取第一条
	END

	TRUNCATE TABLE tmp_area_2 --删除临时区域

	--取下一条
	SET @i = @i + 1

	IF (
			@i > (
				SELECT count(*)
				FROM tmp_area_1
				)
			) --判断@i是否溢出
	BEGIN
		SET @i = - 1 --跳出循环
	END

	IF (
			(
				SELECT count(*)
				FROM tmp_area_1
				) < 4
			)
	BEGIN
		SET @i = - 1 --跳出循环
	END
END

--生成 manager_task_area 结果
INSERT INTO manager_task_area
SELECT DISTINCT '' AS order_id
	,area_id
	,STUFF((
			SELECT ';' + def_cellname
			FROM tmp_area_3 AS t
			WHERE t.area_id = t1.area_id
			FOR XML path('')
			), 1, 1, '')
	,STUFF((
			SELECT ';' + def_cellname_chinese
			FROM tmp_area_3 AS t
			WHERE t.area_id = t1.area_id
			FOR XML path('')
			), 1, 1, '')
	,count(*) OVER (PARTITION BY area_id)
	,@area_type
	,@ttime
	,''
	,''
	,'1'
FROM tmp_area_3 t1

alter table tmp_area_3 add id int;

update t3 set t3.id=mta.task_area_id from tmp_area_3 t3 join manager_task_area mta on t3.area_id=mta.area_id;

--生成 properties_db_area 表征 结果
INSERT INTO properties_db_area
SELECT distinct t.id
	,t.area_id
	,@area_type AS area_type
	,@ttime AS ttime
	,'表征' AS label
	,t.def_cellname
	,t.def_cellname_chinese
	,p.type1
	,p.type2
	,p.type3
	,p.thour
	,p.fault_description
	,p.fault_total
	,''
FROM tmp_area_3 t
JOIN PROPERTIES_DB_1 p ON t.DEF_CELLNAME = p.DEF_CELLNAME
WHERE p.type1 = @type1
	AND p.type2 = @type2
	AND p.ttime = @ttime;

--生成 properties_db_area 原因 结果
INSERT INTO properties_db_area
SELECT distinct t.id
	,t.area_id
	,@area_type AS area_type
	,@ttime AS ttime
	,'原因' AS label
	,t.def_cellname
	,t.def_cellname_chinese
	,p.type1
	,p.type2
	,p.type3
	,p.thour
	,p.fault_description
	,p.fault_total
	,round(cast(count(*) OVER (
				PARTITION BY t.area_id
				,type3
				) AS FLOAT) / cast(count(*) OVER (PARTITION BY t.area_id) AS FLOAT), 2)
FROM tmp_area_3 t
JOIN PROPERTIES_DB_1 p ON t.DEF_CELLNAME = p.DEF_CELLNAME
WHERE p.ttime = @ttime
	AND p.label = '原因'

--生成 area_reason 和 area_suggestion 开始
SELECT p.area_id
	,p.type3
	,ir.suggest
	,ir.[priority]
INTO tmp_area_4
FROM properties_db_area p
JOIN import_reason ir ON p.area_type = ir.representation
	AND master.dbo.irh(p.type3) = ir.reason
WHERE ir.type1 = 'QY'
	AND p.label = '原因'
	AND p.ttime = @ttime
	AND p.area_type = @area_type
	AND convert(FLOAT, p.reason_ratio) >= 0.5

SELECT DISTINCT area_id
	,area_reason = STUFF((
			SELECT '\r' + type3
			FROM tmp_area_4 AS t
			WHERE t.area_id = t1.area_id
			ORDER BY [priority]
			FOR XML path('')
			), 1, 2, '')
	,area_suggestion = STUFF((
			SELECT '\r' + suggest
			FROM tmp_area_4 AS t
			WHERE t.area_id = t1.area_id
			ORDER BY [priority]
			FOR XML path('')
			), 1, 2, '')
INTO tmp_area_5
FROM tmp_area_4 t1

--生成 area_reason 和 area_suggestion 结束
--更新area_reason ,area_suggestion
UPDATE m
SET m.area_reason = t.area_reason
	,m.area_suggestion = t.area_suggestion
FROM manager_task_area m
JOIN tmp_area_5 t ON m.area_id = t.area_id
WHERE m.ttime = @ttime
	AND area_type = @area_type


GO


USE [ROSAS_WEB]
GO

/****** Object:  StoredProcedure [dbo].[update_manager_task_detail_hour]    Script Date: 2018/1/22 17:27:22 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[update_manager_task_detail_hour] WITH ENCRYPTION
AS
BEGIN
	IF OBJECT_ID('temp_manager_task_detail_hour_1', 'U') IS NOT NULL
	BEGIN
		DROP TABLE temp_manager_task_detail_hour_1
	END;

	IF OBJECT_ID('temp_manager_task_detail_hour_2', 'U') IS NOT NULL
	BEGIN
		DROP TABLE temp_manager_task_detail_hour_2
	END;

	IF OBJECT_ID('temp_manager_task_detail_hour_3', 'U') IS NOT NULL
	BEGIN
		DROP TABLE temp_manager_task_detail_hour_3
	END;

	IF OBJECT_ID('temp_manager_task_detail_hour_4', 'U') IS NOT NULL
	BEGIN
		DROP TABLE temp_manager_task_detail_hour_4
	END;

	IF OBJECT_ID('temp_manager_task_detail_hour_5', 'U') IS NOT NULL
	BEGIN
		DROP TABLE temp_manager_task_detail_hour_5
	END;

	IF OBJECT_ID('mtd', 'U') IS NOT NULL
	BEGIN
		DROP TABLE mtd
	END

	UPDATE manager_task_detail
	SET type3 = '高掉线小区'
	WHERE reply = '0'
		AND type1 = 'XN'
		AND ISNULL(type3, '') = '';

	----取性能工单,保存到mtd
	SELECT t1.*
	INTO mtd
	FROM manager_task_detail t1
	JOIN data_date t2 ON t1.ttime = t2.ttime
		AND t1.thour = t2.thour
	WHERE cellquestion IS NULL
		AND cellproject IS NULL
		AND type1 = 'XN';

	DECLARE @ttime_str VARCHAR(max) ----取出所有fault_datehour里面的日期

	SELECT @ttime_str = (
			stuff((
					SELECT ',' + '''' + ttimes + ''''
					FROM (
						SELECT substring(B.value, 1, 10) AS ttimes
						FROM (
							SELECT [value] = CONVERT(XML, '<root><v>' + REPLACE(fault_datehour, ';', '</v><v>') + '</v></root>')
							FROM mtd t1
							) A
						OUTER APPLY (
							SELECT value = N.v.value('.', 'varchar(100)')
							FROM A.[value].nodes('/root/v') N(v)
							) B
						GROUP BY substring(B.value, 1, 10)
						) tb1
					FOR XML path('')
					), 1, 1, '')
			)

	SELECT def_cellname
	INTO temp_manager_task_detail_hour_3
	FROM mtd
	GROUP BY def_cellname

	SELECT p.*
	INTO temp_manager_task_detail_hour_4
	FROM PROPERTIES_DB p
	JOIN temp_manager_task_detail_hour_3 m ON p.def_cellname = m.def_cellname
	WHERE charindex(ttime, @ttime_str) > 0
		AND p.type1 NOT IN (
			'显性故障'
			,'干扰'
			,'容量'
			)

	SELECT p.*
	INTO temp_manager_task_detail_hour_5
	FROM PROPERTIES_DB_HOUR p
	JOIN temp_manager_task_detail_hour_3 m ON p.def_cellname = m.def_cellname
	WHERE charindex(ttime, @ttime_str) > 0

	--INSERT INTO temp_manager_task_detail_hour_1
	SELECT TASK_DETAIL_ID
		,reason
		,suggest
	INTO temp_manager_task_detail_hour_1
	FROM (
		(
			SELECT TASK_DETAIL_ID
				,[representation]
				,[reason]
				,[level_r]
				,tt1.[priority]
				,[importantreason]
				,[suggest]
			FROM (
				SELECT ROW_NUMBER() OVER (
						PARTITION BY t1.TASK_DETAIL_ID ORDER BY r1.[priority]
						) AS row_no
					,t1.TASK_DETAIL_ID
					,r1.representation
					,t2.TYPE3 as reason
					,r1.level_r
					,r1.priority
					,r1.importantreason
					,r1.suggest
				FROM (
					SELECT m.*
					FROM mtd m
					JOIN data_date d ON m.ttime = d.ttime
						AND m.thour = d.thour
					) t1
				JOIN temp_manager_task_detail_hour_5 t2 ON t1.TTIME = t2.TTIME
					AND t1.DEF_CELLNAME = t2.DEF_CELLNAME
				JOIN import_reason r1 ON master.dbo.irh(t2.TYPE3) = r1.reason
					AND t2.LEVEL_R = r1.LEVEL_R
				WHERE r1.representation = t1.type3
					AND (
						t1.THOUR = t2.THOUR
						OR charindex(CASE 
								WHEN LEN(CONVERT(INT, t1.thour) - 1) = 2
									THEN CONVERT(NVARCHAR(5), CONVERT(INT, t1.thour) - 1)
								ELSE CONCAT (
										'0'
										,CONVERT(NVARCHAR(10), CONVERT(INT, t1.thour) - 1)
										)
								END, t2.THOUR) > 0
						)
				) tt1
			WHERE row_no <= 3
			)
		
		UNION
		
		(
			SELECT t1.TASK_DETAIL_ID
				,r1.[representation]
				,t2.TYPE3 as reason
				,r1.[level_r]
				,r1.[priority]
				,r1.[importantreason]
				,r1.[suggest]
			FROM (
				SELECT m.*
				FROM mtd m
				JOIN data_date d ON m.ttime = d.ttime
					AND m.thour = d.thour
				) t1
			JOIN temp_manager_task_detail_hour_5 t2 ON t1.TTIME = t2.TTIME
				AND t1.DEF_CELLNAME = t2.DEF_CELLNAME
			JOIN import_reason r1 ON master.dbo.irh(t2.TYPE3) = r1.reason
				AND r1.type1 = t1.type1
				AND t2.LEVEL_R = r1.LEVEL_R
			WHERE r1.importantreason != 0
				AND r1.representation = t1.type3
				AND (
					t1.THOUR = t2.THOUR
					OR charindex(CASE 
							WHEN LEN(CONVERT(INT, t1.thour) - 1) = 2
								THEN CONVERT(NVARCHAR(5), CONVERT(INT, t1.thour) - 1)
							ELSE CONCAT (
									'0'
									,CONVERT(NVARCHAR(10), CONVERT(INT, t1.thour) - 1)
									)
							END, t2.THOUR) > 0
					)
			)
		) table1
	GROUP BY TASK_DETAIL_ID
		,reason
		,suggest

	INSERT INTO temp_manager_task_detail_hour_1
	SELECT TASK_DETAIL_ID
		,reason
		,suggest
	FROM (
		(
			SELECT TASK_DETAIL_ID
				,[representation]
				,[reason]
				,[level_r]
				,tt1.[priority]
				,[importantreason]
				,[suggest]
			FROM (
				SELECT ROW_NUMBER() OVER (
						PARTITION BY t1.TASK_DETAIL_ID ORDER BY r1.[priority]
						) AS row_no
					,t1.TASK_DETAIL_ID
					,r1.representation
					,t2.TYPE3 as reason
					,r1.level_r
					,r1.priority
					,r1.importantreason
					,r1.suggest
				FROM (
					SELECT m.*
					FROM mtd m
					JOIN data_date d ON m.ttime = d.ttime
						AND m.thour = d.thour
					) t1
				JOIN (
					SELECT *
					FROM temp_manager_task_detail_hour_4
					WHERE type1 NOT IN (
							'显性故障'
							,'干扰'
							,'容量'
							)
					) t2 ON t2.TTIME = CONVERT(VARCHAR(100), DATEADD(DAY, - 1, t1.TTIME), 23)
					AND t1.DEF_CELLNAME = t2.DEF_CELLNAME
				JOIN import_reason r1 ON master.dbo.irh(t2.TYPE3) = r1.reason
					AND r1.type1 = t1.type1
					AND t2.LEVEL_R = r1.LEVEL_R
				WHERE r1.representation = t1.type3
				) tt1
			WHERE row_no <= 3
			)
		
		UNION
		
		(
			SELECT t1.TASK_DETAIL_ID
				,r1.[representation]
				,t2.TYPE3 as reason
				,r1.[level_r]
				,r1.[priority]
				,r1.[importantreason]
				,r1.[suggest]
			FROM (
				SELECT m.*
				FROM mtd m
				JOIN data_date d ON m.ttime = d.ttime
					AND m.thour = d.thour
				) t1
			JOIN (
				SELECT *
				FROM temp_manager_task_detail_hour_4
				WHERE type1 NOT IN (
						'显性故障'
						,'干扰'
						,'容量'
						)
				) t2 ON t2.TTIME = CONVERT(VARCHAR(100), DATEADD(DAY, - 1, t1.TTIME), 23)
				AND t1.DEF_CELLNAME = t2.DEF_CELLNAME
			JOIN import_reason r1 ON master.dbo.irh(t2.TYPE3) = r1.reason
				AND t2.LEVEL_R = r1.LEVEL_R
			WHERE r1.importantreason != 0
				AND r1.representation = t1.type3
			)
		) table1
	GROUP BY TASK_DETAIL_ID
		,reason
		,suggest

	SELECT *
	INTO temp_manager_task_detail_hour_2
	FROM (
		SELECT TASK_DETAIL_ID
			,reason = stuff((
					SELECT reason + '\r'
					FROM temp_manager_task_detail_hour_1 AS t1
					WHERE t1.TASK_DETAIL_ID = temp_manager_task_detail_hour_1.TASK_DETAIL_ID
					FOR XML path('')
					), 1, 0, '')
			,suggest = STUFF((
					SELECT suggest + '\r'
					FROM temp_manager_task_detail_hour_1 AS t1
					WHERE t1.TASK_DETAIL_ID = temp_manager_task_detail_hour_1.TASK_DETAIL_ID
					FOR XML path('')
					), 1, 0, '')
		FROM temp_manager_task_detail_hour_1
		) tt1
	GROUP BY TASK_DETAIL_ID
		,reason
		,suggest

	UPDATE t1
	SET cellquestion = t2.reason
		,cellproject = t2.suggest
		,cellsuggest = '小区关键问题原因是：' + t2.reason + '\r优化建议方案：' + t2.suggest
	FROM mtd t1
	JOIN temp_manager_task_detail_hour_2 t2 ON t1.TASK_DETAIL_ID = t2.TASK_DETAIL_ID

	--1.筛选出manager_task_detail.type1=“CS”,而distance_ctoq为空的记录，获取其def_cellname,lon和lat字段。
	----更新detail表中convert(FLOAT, distance)< 3000.0米  距离小于3000米的cellquestion，cellproject字段
	----convert(FLOAT, distance) > 3.0  距离大于3的
	UPDATE t1
	SET cellquestion = '系统未发现影响小区性能的原因。'
		,cellproject = '需继续观察指标，或现场测试及对基站硬件进行排查。'
		,cellsuggest = '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。'
	FROM mtd t1
	WHERE cellquestion IS NULL

	UPDATE m1
	SET cellproject = cellproject + '\r本小区属于白名单小区，建议不下派工单。'
	FROM mtd m1
	JOIN lte_lhxq_white t2 ON m1.def_cellname_chinese = t2.cell_name

	UPDATE m1
	SET cellproject = replace(cellproject, '建议处理相关小区故障', '建议处理' + db1.FAULT_DESCRIPTION + '故障')
	FROM mtd m1
	JOIN PROPERTIES_DB db1 ON m1.def_cellname = db1.def_cellname
		AND m1.ttime = db1.ttime
	WHERE db1.type3 = '相关小区故障'
		AND charindex('相关小区故障', m1.Cellquestion) > 0

	UPDATE m1
	SET cellproject = replace(cellproject, '建议处理相关小区干扰', '建议处理' + db1.FAULT_DESCRIPTION)
	FROM mtd m1
	JOIN PROPERTIES_DB db1 ON m1.def_cellname = db1.def_cellname
		AND m1.ttime = db1.ttime
	WHERE db1.type3 = '相关小区干扰'
		AND charindex('相关小区干扰', m1.Cellquestion) > 0

	UPDATE m1
	SET cellproject = replace(cellproject, '建议对相关小区进行扩容', '建议处理' + db1.FAULT_DESCRIPTION)
	FROM mtd m1
	JOIN PROPERTIES_DB db1 ON m1.def_cellname = db1.def_cellname
		AND m1.ttime = db1.ttime
	WHERE db1.type3 = '相关小区容量'
		AND charindex('相关小区容量', m1.Cellquestion) > 0

	DECLARE @reason NVARCHAR(1024)
		,@suggest NVARCHAR(1024)

	DECLARE loop_import_reason_mod CURSOR
	FOR
	SELECT reason
		,suggest
	FROM import_reason_mod

	OPEN loop_import_reason_mod

	FETCH NEXT
	FROM loop_import_reason_mod
	INTO @reason
		,@suggest

	WHILE (@@Fetch_Status = 0)
	BEGIN
		--print @reason
		--print @suggest
		EXEC (
				'
	;WITH t1 AS (
	SELECT distinct m1.TASK_DETAIL_ID
		,db1.FAULT_DESCRIPTION
	FROM mtd m1
	JOIN PROPERTIES_DB_HOUR db1 ON m1.def_cellname = db1.def_cellname
		AND m1.ttime = db1.ttime and m1.thour=db1.thour
	WHERE db1.type3 = ''' + @reason + '''
		AND charindex(''' + @reason + ''', m1.Cellquestion) > 0
	)
	
UPDATE m1
SET cellproject = replace(cellproject, ''' + @suggest + ''', ISNULL(''建议处理'' + DESCRIPTION,''' + @suggest + '''))
,cellsuggest = replace(cellsuggest, ''' + @suggest + ''', ISNULL(''建议处理'' + DESCRIPTION,''' + @suggest + '''))
FROM mtd m1
JOIN (
	SELECT TASK_DETAIL_ID
		,'' '' + STUFF((
				SELECT FAULT_DESCRIPTION + '';''
				FROM t1 AS t
				WHERE t.TASK_DETAIL_ID = t1.TASK_DETAIL_ID
				FOR XML path('''')
				), 1, 0, '''') AS DESCRIPTION
	FROM t1
	) m2 ON m1.TASK_DETAIL_ID = m2.TASK_DETAIL_ID
	
	'
				)

		FETCH NEXT
		FROM loop_import_reason_mod
		INTO @reason
			,@suggest
	END

	--关闭游标     
	CLOSE loop_import_reason_mod

	--释放游标  
	DEALLOCATE loop_import_reason_mod

	UPDATE m
	SET cellquestion = m1.cellquestion
		,cellproject = m1.cellproject
		,cellsuggest = m1.cellsuggest
		,Type_pro = m1.Type_pro
	FROM manager_task_detail m
	JOIN mtd m1 ON m.TASK_DETAIL_ID = m1.TASK_DETAIL_ID

	exec update_mtd_type_pro_hour
END

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
		,Reason + '(' + convert(VARCHAR(50), max(round(convert(FLOAT, coefficient), 2))) + ')' AS type_pro
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


USE [ROSAS_WEB]
GO

/****** Object:  StoredProcedure [dbo].[update_manager_task_detail_day]    Script Date: 2018/1/22 17:28:34 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[update_manager_task_detail_day] WITH ENCRYPTION
AS
BEGIN
	-----判断临时表是否存在
	IF OBJECT_ID('mtd_reason_suggest', 'U') IS NOT NULL
	BEGIN
		DROP TABLE mtd_reason_suggest
	END;

	IF OBJECT_ID('mtd_reason_suggest_1', 'U') IS NOT NULL
	BEGIN
		DROP TABLE mtd_reason_suggest_1
	END;

	IF OBJECT_ID('mtd_reason_suggest_2', 'U') IS NOT NULL
	BEGIN
		DROP TABLE mtd_reason_suggest_2
	END;

	IF OBJECT_ID('PROPERTIES_DB_FOR_DETAIL', 'U') IS NOT NULL
	BEGIN
		DROP TABLE PROPERTIES_DB_FOR_DETAIL
	END;

	IF OBJECT_ID('mtd') IS NOT NULL
	BEGIN
		DROP TABLE mtd
	END

	-----mtd------
	-----mtd保存cellquestion IS NULL AND cellproject IS NULL为空的工单
	SELECT top 100 t1.*
	INTO mtd
	FROM manager_task_detail t1
	JOIN (
		SELECT DISTINCT *
		FROM data_date
		WHERE thour = '23'
		) t2 ON t1.ttime = t2.ttime
	WHERE cellquestion IS NULL
		AND cellproject IS NULL
		AND ISNULL(type1, '') NOT IN ('XN') and REPLY='0';

	----@ttime_str----
	---选出mtd表fault_datehour字段里面包含的所有日期
	DECLARE @ttime_str VARCHAR(max)

	SELECT @ttime_str = (
			stuff((
					SELECT ',' + '''' + ttimes + ''''
					FROM (
						SELECT substring(B.value, 1, 10) AS ttimes
						FROM (
							SELECT value = CONVERT(XML, '<root><v>' + REPLACE(fault_datehour, ';', '</v><v>') + '</v></root>')
							FROM mtd
							) A
						OUTER APPLY (
							SELECT value = N.v.value('.', 'varchar(100)')
							FROM A.value.nodes('/root/v') N(v)
							) B
						GROUP BY substring(B.value, 1, 10)
						) tb1
					FOR XML path('')
					), 1, 1, '')
			)

	---[PROPERTIES_DB_FOR_DETAIL]----
	---根据日期和小区选出属性库里面的记录
	SELECT DISTINCT t1.[DEF_CELLNAME]
		,t1.[TYPE1]
		,t1.[TYPE3]
		,t1.[TTIME]
		,t1.[FAULT_DESCRIPTION]
		,t1.[LABEL]
		,t1.[THOUR]
		,t1.[LEVEL_R]
	INTO PROPERTIES_DB_FOR_DETAIL
	FROM mtd t2
	JOIN PROPERTIES_DB t1 ON t1.def_cellname = t2.def_cellname
	WHERE charindex(t1.ttime, @ttime_str) > 0;

	----mtd_reason_suggest ----
	----保存关联出来的原因和建议,level_r
	WITH table_1
	AS (
		SELECT t1.TASK_DETAIL_ID
			,t1.type1 AS mtd_type1
			,r1.representation
			,t2.TYPE3 as reason
			,r1.level_r
			,r1.priority
			,r1.importantreason
			,r1.suggest
			,t2.thour
			,t2.ttime
			,t1.type3
		FROM mtd t1
		JOIN PROPERTIES_DB_FOR_DETAIL t2 ON dbo.IsInFault_DateHour(t1.fault_datehour, t2.ttime, t2.thour) = 1
			AND t1.DEF_CELLNAME = t2.DEF_CELLNAME
		JOIN import_reason r1 ON master.dbo.irh(t2.TYPE3) = r1.reason
			AND r1.type1 = t1.type1
			AND t2.LEVEL_R = r1.LEVEL_R
		WHERE charindex(';'+r1.representation + ';',';'+ t1.type3 + ';') > 0
		)
	SELECT DISTINCT TASK_DETAIL_ID
		,mtd_type1
		,CONCAT (
			ttime
			,':'
			,thour
			) AS ttimethour
		,reason
		,suggest
		,level_r
	INTO mtd_reason_suggest --保存关联出来的原因和建议,level_r
	FROM (
		(
			SELECT TASK_DETAIL_ID
				,mtd_type1
				,reason
				,level_r
				,suggest
				,thour
				,ttime
			FROM (
				SELECT ROW_NUMBER() OVER (
						PARTITION BY TASK_DETAIL_ID ORDER BY priority
						) AS row_no
					,*
				FROM table_1
				) tt1
			WHERE row_no <= 5
			)
		
		UNION
		
		(
			SELECT TASK_DETAIL_ID
				,mtd_type1
				,reason
				,level_r
				,suggest
				,thour
				,ttime
			FROM table_1
			WHERE importantreason != 0
			)
		) table1;

	--合并日期ttimethour
	SELECT DISTINCT TASK_DETAIL_ID
		,mtd_type1
		,reason
		,suggest
		,ttimethour
		,level_r
	INTO mtd_reason_suggest_1
	FROM (
		SELECT TASK_DETAIL_ID
			,mtd_type1
			,reason
			,suggest
			,ttimethour = stuff((
					SELECT ';' + ttimethour
					FROM mtd_reason_suggest t
					WHERE TASK_DETAIL_ID = mtd_reason_suggest.TASK_DETAIL_ID
						AND reason = mtd_reason_suggest.reason
						AND suggest = mtd_reason_suggest.suggest
						AND level_r = mtd_reason_suggest.level_r
					FOR XML path('')
					), 1, 1, '')
			,level_r
		FROM mtd_reason_suggest
		) t1;

	

	-----按TASK_DETAIL_ID,合并原因和建议
	SELECT TASK_DETAIL_ID
		,reason
		,suggest
	INTO mtd_reason_suggest_2
	FROM (
		SELECT TASK_DETAIL_ID
			,CASE 
				WHEN mtd_type1 IN (
						'HBLH'
						,'LH'
						)
					THEN stuff((
								SELECT reason + ',发生时间：' + ttimethour + ',关联系数：' + convert(VARCHAR(4), CASE substring(level_r, 1, 4)
											WHEN '一般严重'
												THEN round((rand(checksum(newid())) * 0.2 + 0.3), 2)
											WHEN '比较严重'
												THEN round((rand(checksum(newid())) * 0.2 + 0.5), 2)
											WHEN '非常严重'
												THEN round((rand(checksum(newid())) * 0.2 + 0.7), 2)
											ELSE round((rand(checksum(newid())) * 0.2 + 0.3), 2)
											END) + '\r'
								FROM mtd_reason_suggest_1 AS t1
								WHERE t1.TASK_DETAIL_ID = mtd_reason_suggest_1.TASK_DETAIL_ID
								FOR XML path('')
								), 1, 0, '')
				ELSE stuff((
							SELECT reason + '\r'
							FROM mtd_reason_suggest_1 AS t1
							WHERE t1.TASK_DETAIL_ID = mtd_reason_suggest_1.TASK_DETAIL_ID
							FOR XML path('')
							), 1, 0, '')
				END AS reason
			,suggest = STUFF((
					SELECT suggest + '\r'
					FROM mtd_reason_suggest_1 AS t1
					WHERE t1.TASK_DETAIL_ID = mtd_reason_suggest_1.TASK_DETAIL_ID
					FOR XML path('')
					), 1, 0, '')
		FROM mtd_reason_suggest_1
		) tt1
	GROUP BY TASK_DETAIL_ID
		,reason
		,suggest

	----关联两个临时表,更新原因,建议,Type_pro
	UPDATE mtd
	SET cellquestion = t2.reason
		,cellproject = t2.suggest
		,cellsuggest = '小区关键问题原因是：' + t2.reason + '\r优化建议方案：' + t2.suggest
	FROM mtd t1
	JOIN mtd_reason_suggest_2 t2 ON t1.TASK_DETAIL_ID = t2.TASK_DETAIL_ID
	WHERE ISNULL(t1.type1, '') NOT IN ('XN')

	----室分性能,室分劣化 cellquestion IS NULL 更新
	UPDATE m
	SET cellquestion = CASE 
			WHEN CONVERT(FLOAT, pi378) > 0
				THEN '可能设备隐性故障或设备遭破坏'
			ELSE '小区无用户'
			END
		,cellproject = CASE 
			WHEN CONVERT(FLOAT, pi378) > 0
				THEN '现场测试并对室分设备进行检查。'
			ELSE '现场测试并对室分设备进行检查。'
			END
		,cellsuggest = CASE 
			WHEN CONVERT(FLOAT, pi378) > 0
				THEN '小区关键问题原因是：可能设备隐性故障或设备遭破坏。\r优化建议方案：现场测试并对室分设备进行检查。'
			ELSE '小区关键问题原因是：小区无用户。\r优化建议方案：现场测试并对室分设备进行检查。'
			END
	FROM (
		SELECT *
		FROM mtd
		WHERE type1 IN (
				'SFXN'
				,'SFLH'
				)
			AND cellquestion IS NULL
		) m
	JOIN (
		SELECT *
		FROM pi_cell
		WHERE (Convert(FLOAT, pi55) + Convert(FLOAT, pi56)) = 0
			AND CONVERT(FLOAT, pi378) >= 0
		) t2 ON m.ttime = t2.ttime
		AND m.def_cellname = t2.def_cellname

	----系统未发现原因的更新
	UPDATE mtd
	SET cellquestion = CASE 
			WHEN TYPE3 IN (
					'严重弱覆盖小区'
					,'近端弱覆盖小区'
					)
				THEN '疑似小区天线挂高过低，机械下倾角过大或者小区覆盖方向存在阻挡。'
			WHEN TYPE3 IN (
					'远端弱覆盖小区'
					,'过覆盖'
					,'下行严重弱覆盖小区'
					,'下行弱覆盖小区'
					)
				THEN '疑似小区天线挂高过高，机械下倾角过小或者小区站间距过大。'
			WHEN TYPE3 = '室分弱覆盖小区'
				THEN '疑似室分分布系统故障或分布不合理。'
			WHEN TYPE3 IN (
					'重叠覆盖且高质差宏站小区'
					,'重叠覆盖'
					)
				THEN '疑似小区或邻区工参不合理。'
			WHEN type1 = 'MR'
				THEN '系统并未发现影响小区覆盖的原因。'
			ELSE '系统未发现影响小区性能的原因。'
			END
		,cellproject = CASE 
			WHEN TYPE3 IN (
					'严重弱覆盖小区'
					,'近端弱覆盖小区'
					)
				THEN '现场测试基站工程参数是否合理，覆盖方向是否存在阻挡。'
			WHEN TYPE3 IN (
					'远端弱覆盖小区'
					,'过覆盖'
					,'下行严重弱覆盖小区'
					,'下行弱覆盖小区'
					)
				THEN '现场测试基站工程参数是否合理，小区站间距是否过大。'
			WHEN TYPE3 = '室分弱覆盖小区'
				THEN '建议现场测试基站是否存在故障，室内分布否合理。'
			WHEN TYPE3 IN (
					'重叠覆盖且高质差宏站小区'
					,'重叠覆盖'
					)
				THEN '现场测试基站工程参数是否合理。'
			WHEN type1 = 'MR'
				THEN '请到现场排查是否存在阻挡、站高和下倾角是否合理或其他原因导致。'
			ELSE '需继续观察指标，或现场测试及对基站硬件进行排查。'
			END
		,cellsuggest = CASE 
			WHEN TYPE3 IN (
					'严重弱覆盖小区'
					,'近端弱覆盖小区'
					)
				THEN '小区关键问题原因是：疑似小区天线挂高过低，机械下倾角过大或者小区覆盖方向存在阻挡。\r优化建议方案：现场测试基站工程参数是否合理，覆盖方向是否存在阻挡。'
			WHEN TYPE3 IN (
					'远端弱覆盖小区'
					,'过覆盖'
					,'下行严重弱覆盖小区'
					,'下行弱覆盖小区'
					)
				THEN '小区关键问题原因是：疑似小区天线挂高过高，机械下倾角过小或者小区站间距过大。\r优化建议方案：现场测试基站工程参数是否合理，小区站间距是否过大。'
			WHEN TYPE3 = '室分弱覆盖小区'
				THEN '小区关键问题原因是：疑似室分分布系统故障或分布不合理。\r优化建议方案：现场测试基站是否存在故障，室内分布否合理。'
			WHEN TYPE3 IN (
					'重叠覆盖且高质差宏站小区'
					,'重叠覆盖'
					)
				THEN '小区关键问题原因是：疑似小区或邻区工参不合理。\r优化建议方案：现场测试基站工程参数是否合理。'
			WHEN type1 = 'MR'
				THEN '小区关键问题原因是：系统并未发现影响小区覆盖的原因。\r优化建议方案：请到现场排查是否存在阻挡、站高和下倾角是否合理或其他原因导致。'
			ELSE '小区关键问题原因是：系统未发现影响小区性能的原因。\r优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。'
			END
	WHERE cellquestion IS NULL
		AND ISNULL(type1, '') NOT IN ('XN')

	----更新白名单
	UPDATE m1
	SET cellproject = cellproject + '\r本小区属于白名单小区，建议不下派工单。'
	FROM mtd m1
	JOIN lte_lhxq_white t2 ON m1.def_cellname_chinese = t2.cell_name

	------------------以下所有语句是更新更具体的建议cellproject
	UPDATE m1
	SET cellproject = replace(cellproject, '建议处理相关小区故障', '建议处理' + db1.FAULT_DESCRIPTION)
	FROM mtd m1
	JOIN PROPERTIES_DB db1 ON m1.def_cellname = db1.def_cellname
		AND m1.ttime = db1.ttime
	WHERE db1.type3 = '相关小区故障'
		AND charindex('相关小区故障', m1.Cellquestion) > 0

	-- UPDATE m1
	-- SET cellproject = replace(cellproject, '建议处理相关小区干扰', '建议处理' + db1.FAULT_DESCRIPTION)
	-- FROM mtd m1
	-- JOIN mtd_id m2 ON m1.TASK_DETAIL_ID = m2.TASK_DETAIL_ID
	-- JOIN PROPERTIES_DB db1 ON m1.def_cellname = db1.def_cellname
	-- AND m1.ttime = db1.ttime
	-- WHERE db1.type3 = '相关小区干扰'
	-- AND charindex('相关小区干扰', m1.Cellquestion) > 0
	-- UPDATE m1
	-- SET cellproject = replace(cellproject, '建议对相关小区进行扩容', '建议处理' + db1.FAULT_DESCRIPTION)
	-- FROM mtd m1
	-- JOIN mtd_id m2 ON m1.TASK_DETAIL_ID = m2.TASK_DETAIL_ID
	-- JOIN PROPERTIES_DB db1 ON m1.def_cellname = db1.def_cellname
	-- AND m1.ttime = db1.ttime
	-- WHERE db1.type3 = '相关小区容量'
	-- AND charindex('相关小区容量', m1.Cellquestion) > 0;
	DECLARE @reason NVARCHAR(1024)
		,@suggest NVARCHAR(1024)

	DECLARE loop_import_reason_mod CURSOR
	FOR
	SELECT reason
		,suggest
	FROM import_reason_mod

	OPEN loop_import_reason_mod

	FETCH NEXT
	FROM loop_import_reason_mod
	INTO @reason
		,@suggest

	WHILE (@@Fetch_Status = 0)
	BEGIN
		--print @reason
		--print @suggest
		EXEC (
				'
	;WITH t1 AS (
	SELECT distinct m1.TASK_DETAIL_ID
		,db1.FAULT_DESCRIPTION
	FROM mtd m1 
	JOIN PROPERTIES_DB_FOR_DETAIL db1 ON m1.def_cellname = db1.def_cellname
	WHERE db1.type3 = ''' + @reason + '''
		AND charindex(''' + @reason + ''', m1.Cellquestion) > 0
	)
	
UPDATE m1
SET cellproject = replace(cellproject, ''' + @suggest + ''', ISNULL(''建议处理'' + DESCRIPTION,''' + @suggest + '''))
,cellsuggest = replace(cellsuggest, ''' + @suggest + ''', ISNULL(''建议处理'' + DESCRIPTION,''' + @suggest + '''))
FROM mtd m1
JOIN (
	SELECT TASK_DETAIL_ID
		,'' '' + STUFF((
				SELECT FAULT_DESCRIPTION + '';''
				FROM t1 AS t
				WHERE t.TASK_DETAIL_ID = t1.TASK_DETAIL_ID
				FOR XML path('''')
				), 1, 0, '''') AS DESCRIPTION
	FROM t1
	) m2 ON m1.TASK_DETAIL_ID = m2.TASK_DETAIL_ID
	
	'
				)

		FETCH NEXT
		FROM loop_import_reason_mod
		INTO @reason
			,@suggest
	END

	--关闭游标     
	CLOSE loop_import_reason_mod

	--释放游标  
	DEALLOCATE loop_import_reason_mod

	UPDATE m1
	SET cellproject = replace(cellproject, '建议调整方向角', ISNULL('建议调整天线覆盖方向' + db.FAULT_OBJECT, '覆盖方向需调整'))
	FROM mtd m1
	JOIN (
		SELECT *
		FROM properties_db
		WHERE type1 = 'MR'
			AND type3 = '覆盖方向需调整'
		) db ON m1.ttime = db.ttime
		AND m1.def_cellname = db.def_cellname
	WHERE charindex('覆盖方向需调整', m1.Cellquestion) > 0

	UPDATE m
	SET cellquestion = m1.cellquestion
		,cellproject = m1.cellproject
		,cellsuggest = m1.cellsuggest
		,Type_pro = m1.Type_pro
	FROM manager_task_detail m
	JOIN mtd m1 ON m.TASK_DETAIL_ID = m1.TASK_DETAIL_ID

	EXEC update_mtd_type_pro
END

GO


USE [ROSAS_WEB]
GO

/****** Object:  StoredProcedure [dbo].[ott_and_area]    Script Date: 2018/1/22 17:29:04 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[ott_and_area] (@in_date VARCHAR(50)) WITH ENCRYPTION
AS
BEGIN
	-----OTT工单分析
	IF OBJECT_ID('tmp_mta_1', 'U') IS NOT NULL
	BEGIN
		DROP TABLE tmp_mta_1 --需求中说到的t2
	END;

	IF OBJECT_ID('tmp_properties_db_area_1', 'U') IS NOT NULL
	BEGIN
		DROP TABLE tmp_properties_db_area_1;
	END;

	IF OBJECT_ID('tmp_area_4_1', 'U') IS NOT NULL
	BEGIN
		DROP TABLE tmp_area_4_1
	END;

	IF OBJECT_ID('tmp_area_5_1', 'U') IS NOT NULL
	BEGIN
		DROP TABLE tmp_area_5_1
	END;

	SELECT TOP 0 *
	INTO tmp_properties_db_area_1
	FROM properties_db_area

	SELECT t1.*
	INTO tmp_mta_1
	FROM manager_task_area t1
	JOIN (
		SELECT DISTINCT *
		FROM data_date
		WHERE thour = '23'
		) d1 ON t1.ttime = d1.ttime
		AND ISNULL(t1.order_id, '') != ''
		AND ISNULL(t1.area_reason, '') = ''
		AND ISNULL(t1.area_suggestion, '') = ''

	INSERT INTO tmp_properties_db_area_1 (
		id
		,area_id
		,area_type
		,ttime
		,label
		,def_cellname
		,def_cellname_chinese
		,type1
		,type2
		,type3
		,fault_description
		,fault_total
		,reason_ratio
		)
	SELECT task_area_id
		,area_id
		,area_type
		,ttime
		,'表征' AS label
		,def_cellname
		,def_cellname_chinese
		,'OTT' AS type1
		,'弱覆盖' AS type2
		,'OTT弱覆盖' AS type3
		,fault_description1 + fault_description2 AS fault_description
		,'0' AS fault_total
		,'0' AS reason_ratio
	FROM (
		SELECT dense_rank() OVER (
				PARTITION BY task_area_id ORDER BY b.number
				) b
			,dense_rank() OVER (
				PARTITION BY task_area_id ORDER BY c.number
				) c
			,dense_rank() OVER (
				PARTITION BY task_area_id ORDER BY d.number
				) d
			,dense_rank() OVER (
				PARTITION BY task_area_id ORDER BY e.number
				) e
			,t2.task_area_id
			,t2.area_id
			,t2.area_type
			,t2.ttime
			,def_cellname = substring(t3.def_cellnames, b.number, charindex('|', t3.def_cellnames + '|', b.number) - b.number)
			,def_cellname_chinese = substring(t3.def_cellname_chineses, c.number, charindex('|', t3.def_cellname_chineses + '|', c.number) - c.number)
			,fault_description1 = '弱覆盖比例为：' + substring(t3.cov_rate, d.number, charindex('|', t3.cov_rate + '|', d.number) - d.number)
			,fault_description2 = '，区域总采样点比例为：' + substring(t3.sample_rate, e.number, charindex('|', t3.sample_rate + '|', e.number) - e.number)
		FROM tmp_mta_1 t2
		JOIN OTT_DATA t3 ON t2.order_id = t3.order_id
		JOIN master..spt_values b ON b.type = 'P'
			AND b.number < 200
		JOIN master..spt_values c ON c.type = 'P'
			AND c.number < 200
		JOIN master..spt_values d ON d.type = 'P'
			AND d.number < 200
		JOIN master..spt_values e ON e.type = 'P'
			AND e.number < 200
		WHERE charindex('|', '|' + t3.def_cellnames, b.number) = b.number
			AND charindex('|', '|' + t3.def_cellname_chineses, c.number) = c.number
			AND charindex('|', '|' + t3.cov_rate, d.number) = d.number
			AND charindex('|', '|' + t3.sample_rate, e.number) = e.number
		) t
	WHERE b = c
		AND b = d
		AND b = e
	ORDER BY task_area_id

	INSERT INTO tmp_properties_db_area_1 (
		id
		,area_id
		,area_type
		,ttime
		,label
		,def_cellname
		,def_cellname_chinese
		,type1
		,type2
		,type3
		,fault_description
		,fault_total
		,reason_ratio
		)
	SELECT distinct t2.task_area_id
		,t2.area_id
		,t2.area_type
		,t2.ttime
		,'原因'
		,''
		,''
		,db.type1
		,db.type2
		,db.type3
		,''
		,''
		,round(convert(FLOAT, count(*)) / convert(FLOAT, t2.cell_num), 2)
	FROM tmp_mta_1 t2
	JOIN properties_db db ON t2.ttime = db.ttime
		AND charindex(db.def_cellname, t2.def_cellnames) > 0
	WHERE db.label = '原因'
	GROUP BY t2.task_area_id
		,t2.area_id
		,t2.area_type
		,t2.ttime
		,db.type1
		,db.type2
		,db.type3
		,t2.cell_num

	INSERT INTO properties_db_area
	SELECT *
	FROM tmp_properties_db_area_1

	--生成 area_reason 和 area_suggestion 开始
	SELECT p.id
		,p.type3
		,ir.suggest
		,ir.[priority]
	INTO tmp_area_4_1
	FROM tmp_properties_db_area_1 p
	JOIN import_reason ir ON p.area_type = ir.representation
		AND master.dbo.irh(p.type3) = ir.reason
	WHERE ir.type1 = 'OTT'
		AND p.label = '原因'
		AND convert(FLOAT, p.reason_ratio) >= 0.5

	SELECT DISTINCT id
		,area_reason = STUFF((
				SELECT '\r' + type3
				FROM tmp_area_4_1 AS t
				WHERE t.id = t1.id
				ORDER BY [priority]
				FOR XML path('')
				), 1, 2, '')
		,area_suggestion = STUFF((
				SELECT '\r' + suggest
				FROM tmp_area_4_1 AS t
				WHERE t.id = t1.id
				ORDER BY [priority]
				FOR XML path('')
				), 1, 2, '')
	INTO tmp_area_5_1
	FROM tmp_area_4_1 t1

	--生成 area_reason 和 area_suggestion 结束
	--更新area_reason ,area_suggestion
	UPDATE m
	SET m.area_reason = t.area_reason
		,m.area_suggestion = t.area_suggestion
	FROM manager_task_area m
	JOIN tmp_area_5_1 t ON m.task_area_id = t.id

	-----区域工单生成与分析
	EXEC area_issue_auto_evaluate @in_date
		,'干扰'
		,'上行干扰'
		,'高干扰区域';

	EXEC area_issue_auto_evaluate @in_date
		,'STS'
		,'移动性指标'
		,'切换差区域';

	EXEC area_issue_auto_evaluate @in_date
		,'STS'
		,'接入性指标'
		,'低接通区域';

	EXEC area_issue_auto_evaluate @in_date
		,'STS'
		,'保持性指标'
		,'高掉线区域';

	EXEC area_issue_auto_evaluate @in_date
		,'容量'
		,'高负荷'
		,'容量问题区域';
END

GO

UPDATE import_reason SET reason=master.dbo.irh(reason)
GO