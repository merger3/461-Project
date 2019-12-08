
playerStatsPerTen = """SELECT 
	players.name, 
	coalesce(stats.eliminations * 10, 0) AS \"eliminations\", 
	coalesce(stats.final_blows * 10, 0) AS \"final_blows\", 
	coalesce(stats.damage * 10, 0) AS \"damage\", 
	coalesce(stats.healing * 10, 0) AS \"healing\", 
	coalesce(stats.deaths * 10, 0) AS \"deaths\", 
	coalesce(stats.ultimates * 10, 0) AS \"ultimates\", 
	coalesce(stats.final_blows * 10, 0) AS \"final_blows\", 
	coalesce(stats.time_played, 0) AS \"time_played\" 
FROM 
	stats 
INNER JOIN 
	players ON players.id = stats.playerid 
WHERE 
	stats.playerid = any($1::int[]) AND stats.hero = 'overall';"""





totalStats = """SELECT
	mapstats.playerid,
	COALESCE(SUM(mapstats.eliminations), 0) AS "eliminations",
	COALESCE(SUM(mapstats.damage), 0) AS "damage",
	COALESCE(SUM(mapstats.deaths), 0) AS "deaths",
	COALESCE(SUM(mapstats.healing), 0) AS "healing"
FROM
	mapstats
WHERE
	mapstats.playerid = any($1::int[]) AND hero = $2
GROUP BY
	mapstats.playerid;
"""


mapStats = """WITH map_info AS (
	SELECT
		mapstats.playerid,
		maps.matchid,
		maps.map_number,
		mapstats.teamid,
		maps.name,
		maps.type,
		matches.home,
		matches.away,
		maps.homescore,
		maps.awayscore,
		CASE WHEN maps.homescore > maps.awayscore THEN matches.home
			WHEN maps.homescore < maps.awayscore THEN matches.away
			ELSE 0
		END AS winner,
		mapstats.damage,
		mapstats.deaths,
		mapstats.healing,
		mapstats.eliminations
	FROM
		mapstats
	INNER JOIN
		maps ON maps.matchid = mapstats.matchid and maps.map_number = mapstats.map_number
	INNER JOIN
		matches on matches.matchid = mapstats.matchid
	WHERE
		mapstats.playerid = any($1::int[]) AND maps.name ilike $2 AND mapstats.hero = 'overall'
)

SELECT
	playerid,
	COUNT(*) AS played,
	COUNT(CASE WHEN winner = teamid THEN 1 END) AS won,
	COUNT(CASE WHEN winner <> teamid AND winner <> 0 THEN 1 END) AS lost,
	COUNT(CASE WHEN winner <> teamid AND winner = 0 THEN 1 END) AS tied,
	COALESCE(AVG(eliminations), 0) AS avg_eliminations,
	COALESCE(AVG(deaths), 0) AS avg_deaths,
	COALESCE(AVG(damage), 0) AS avg_damage,
	COALESCE(AVG(healing), 0) AS avg_healing
FROM 
	map_info
GROUP BY
	playerid;"""



typeStats = """WITH map_info AS (
	SELECT
		mapstats.playerid,
		maps.matchid,
		maps.map_number,
		mapstats.teamid,
		maps.name,
		maps.type,
		matches.home,
		matches.away,
		maps.homescore,
		maps.awayscore,
		CASE WHEN maps.homescore > maps.awayscore THEN matches.home
			WHEN maps.homescore < maps.awayscore THEN matches.away
			ELSE 0
		END AS winner,
		mapstats.damage,
		mapstats.deaths,
		mapstats.healing,
		mapstats.eliminations
	FROM
		mapstats
	INNER JOIN
		maps ON maps.matchid = mapstats.matchid and maps.map_number = mapstats.map_number
	INNER JOIN
		matches on matches.matchid = mapstats.matchid
	WHERE
		mapstats.playerid = any($1::int[]) AND maps.type ilike $2 AND mapstats.hero = 'overall'
)

SELECT
	playerid,
	COUNT(*) AS played,
	COUNT(CASE WHEN winner = teamid THEN 1 END) AS won,
	COUNT(CASE WHEN winner <> teamid AND winner <> 0 THEN 1 END) AS lost,
	COUNT(CASE WHEN winner <> teamid AND winner = 0 THEN 1 END) AS tied,
	COALESCE(AVG(eliminations), 0) AS avg_eliminations,
	COALESCE(AVG(deaths), 0) AS avg_deaths,
	COALESCE(AVG(damage), 0) AS avg_damage,
	COALESCE(AVG(healing), 0) AS avg_healing
FROM 
	map_info
GROUP BY
	playerid;"""