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
		AND ISNULL(type1, '') NOT IN ('XN') AND REPLY='0';

	----@ttime_str----
	---选出mtd表fault_datehour字段里面包含的所有日期
	DECLARE @ttime_str VARCHAR(MAX)

	SELECT @ttime_str = (
			stuff((
					SELECT ',' + '''' + ttimes + ''''
					FROM (
						SELECT SUBSTRING(B.value, 1, 10) AS ttimes
						FROM (
							SELECT VALUE = CONVERT(XML, '<root><v>' + REPLACE(fault_datehour, ';', '</v><v>') + '</v></root>')
							FROM mtd
							) A
						OUTER APPLY (
							SELECT VALUE = N.v.value('.', 'varchar(100)')
							FROM A.value.nodes('/root/v') N(v)
							) B
						GROUP BY SUBSTRING(B.value, 1, 10)
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
			,t2.TYPE3 AS reason
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
								SELECT reason + ',发生时间：' + ttimethour + ',关联系数：' + CONVERT(VARCHAR(4), CASE SUBSTRING(level_r, 1, 4)
											WHEN '一般严重'
												THEN ROUND((RAND(CHECKSUM(newid())) * 0.2 + 0.3), 2)
											WHEN '比较严重'
			 									THEN ROUND((RAND(CHECKSUM(newid())) * 0.2 + 0.5), 2)
											WHEN '非常严重'
												THEN ROUND((RAND(CHECKSUM(newid())) * 0.2 + 0.7), 2)
											ELSE ROUND((RAND(CHECKSUM(newid())) * 0.2 + 0.3), 2)
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
	SET cellquestion = t2.reason 26
		,cellproject = t2.suggest 27
		,cellsuggest = '小区关键问题原因是：' + t2.reason + '\r优化建议方案：' + t2.suggest  24
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
		WHERE (CONVERT(FLOAT, pi55) + CONVERT(FLOAT, pi56)) = 0
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
	SET cellproject = REPLACE(cellproject, '建议处理相关小区故障', '建议处理' + db1.FAULT_DESCRIPTION)
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
	SET cellproject = REPLACE(cellproject, '建议调整方向角', ISNULL('建议调整天线覆盖方向' + db.FAULT_OBJECT, '覆盖方向需调整'))
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
