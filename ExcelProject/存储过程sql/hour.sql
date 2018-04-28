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

  ----todo 是不是也是拿取单条工单记录,然后更新 type3 ?  还是更新整个表中的type ?

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

	DECLARE @ttime_str VARCHAR(MAX) ----取出所有fault_datehour里面的日期

	SELECT @ttime_str = (
			stuff((
					SELECT ',' + '''' + ttimes + ''''
					FROM (
						SELECT SUBSTRING(B.value, 1, 10) AS ttimes
						FROM (
							SELECT [VALUE] = CONVERT(XML, '<root><v>' + REPLACE(fault_datehour, ';', '</v><v>') + '</v></root>')
							FROM mtd t1
							) A
						OUTER APPLY (
							SELECT VALUE = N.v.value('.', 'varchar(100)')
							FROM A.[VALUE].nodes('/root/v') N(v)
							) B
						GROUP BY SUBSTRING(B.value, 1, 10)
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
					,t2.TYPE3 AS reason
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
				,t2.TYPE3 AS reason
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
					,t2.TYPE3 AS reason
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
				,t2.TYPE3 AS reason
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
	----CONVERT(FLOAT, distance) > 3.0  距离大于3的
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
	SET cellproject = REPLACE(cellproject, '建议处理相关小区故障', '建议处理' + db1.FAULT_DESCRIPTION + '故障')
	FROM mtd m1
	JOIN PROPERTIES_DB db1 ON m1.def_cellname = db1.def_cellname
		AND m1.ttime = db1.ttime
	WHERE db1.type3 = '相关小区故障'
		AND charindex('相关小区故障', m1.Cellquestion) > 0

	UPDATE m1
	SET cellproject = REPLACE(cellproject, '建议处理相关小区干扰', '建议处理' + db1.FAULT_DESCRIPTION)
	FROM mtd m1
	JOIN PROPERTIES_DB db1 ON m1.def_cellname = db1.def_cellname
		AND m1.ttime = db1.ttime
	WHERE db1.type3 = '相关小区干扰'
		AND charindex('相关小区干扰', m1.Cellquestion) > 0

	UPDATE m1
	SET cellproject = REPLACE(cellproject, '建议对相关小区进行扩容', '建议处理' + db1.FAULT_DESCRIPTION)
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

