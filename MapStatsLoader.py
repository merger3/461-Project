import asyncio
import asyncpg
import requests
import json


class Stats:
	def __init__(self, matchid, mapNum, teamid, playerid, hero):
		self.matchid = matchid
		self.mapNum = mapNum
		self.teamid = teamid
		self.playerid = playerid
		self.hero = hero
		self.eliminations = None
		self.deaths = None
		self.damage = None
		self.healing = None

async def main():
	credentials = {"user": "admin", "password": "570bb40736", "database": "owl", "host": "127.0.0.1"}
	
	db = await asyncpg.create_pool(**credentials)

	matches = [20301, 20302, 20303, 20304, 20305, 20306, 20307, 20311, 20312, 20313, 20314, 20315, 20316, 20317, 20321, 20322, 20323, 20324, 20325, 20326, 20327, 21211, 21221, 21231, 21176, 21177, 21241, 21126, 21212, 21209, 21127, 21251, 21222, 21213, 21261, 21128, 21271, 21210, 21232, 21272, 21233, 21178, 21242, 21281, 21179, 21243, 21282, 21291, 21234, 21301, 21235, 21180, 21244, 21252, 21223, 21214, 21262, 21129, 21253, 21224, 21215, 21263, 21130, 21273, 21245, 21302, 21254, 21225, 21264, 21292, 21246, 21283, 21303, 21255, 21226, 21216, 21265, 21311, 21284, 21236, 21266, 21312, 21274, 21227, 21217, 21267, 21304, 21256, 21228, 21218, 21268, 21313, 21293, 21219, 21294, 21237, 21275, 21238, 21321, 21247, 21305, 21229, 21220, 21269, 21276, 21295, 21239, 21257, 21230, 21248, 21277, 21296, 21322, 21331, 21258, 21332, 21341, 21270, 21278, 21297, 21240, 21323, 21249, 21285, 21306, 21259, 21286, 21324, 21250, 21287, 21260, 21342, 21279, 21325, 21333, 21288, 21280, 21351, 21343, 21352, 21344, 21334, 21345, 21361, 21289, 21362, 21314, 21371, 21298, 21381, 21353, 21335, 21346, 21347, 21363, 21315, 21372, 21299, 21364, 21316, 21373, 21300, 21348, 21365, 21374, 21391, 21382, 21354, 21336, 21349, 21366, 21317, 21375, 21350, 21367, 21318, 21376, 21392, 21383, 21326, 21401, 21290, 21319, 21377, 21393, 21384, 21327, 21402, 21411, 21307, 21355, 21337, 21368, 21378, 21394, 21385, 21328, 21403, 21412, 21308, 21329, 21404, 21413, 21369, 21320, 21379, 21395, 21386, 21330, 21309, 21356, 21338, 21421, 21370, 21431, 21405, 21310, 21414, 21441, 21357, 21339, 21422, 21451, 21461, 21380, 21396, 21387, 21432, 21406, 21415, 21442, 21358, 21423, 21340, 21424, 21452, 21471, 21425, 21453, 21481, 21397, 21454, 21462, 21482, 21398, 21388, 21433, 21472, 21359, 21399, 21389, 21416, 21443, 21400, 21390, 21434, 21407, 21455, 21491, 21501, 21435, 21408, 21417, 21444, 21360, 21473, 21436, 21409, 21418, 21445, 21511, 21474, 21426, 21456, 21463, 21483, 21492, 21502, 21437, 21410, 21457, 21427, 21458, 21464, 21484, 21493, 21503, 21428, 21459, 21465, 21504, 21460, 21512, 21485, 21494, 21521, 21419, 21446, 21513, 21514, 21515, 30151, 30152, 30153, 30154, 30155, 30156, 30157, 30158, 30159, 30160, 30161, 30162, 30163, 30164, 30172, 30173, 30175, 30176]

	conn = await db.acquire()
	async with conn.transaction():
		for match in matches:
			response = requests.get(f"https://api.overwatchleague.com/matches/{match}")
			data = response.json()["scores"]
			games = data[0]["value"] + data[1]["value"]

			for i in range(1, games + 1):
				response = requests.get(f"https://api.overwatchleague.com/stats/matches/{match}/maps/{i}")
				if response.status_code == 200:
					data = response.json()
				
					for team in data["teams"]:
						for player in team["players"]:
							playerStats = buildPlayerStats(data, team, player)
							await conn.execute("INSERT INTO mapstats VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);", playerStats.matchid, playerStats.mapNum, playerStats.teamid, playerStats.playerid, playerStats.hero, playerStats.damage, playerStats.deaths, playerStats.eliminations, playerStats.healing)

							if player["stats"] != None:
								for hero in player["heroes"]:
									heroStats = buildHeroStats(data, team, player, hero)
									await conn.execute("INSERT INTO mapstats VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);", heroStats.matchid, heroStats.mapNum, heroStats.teamid, heroStats.playerid, heroStats.hero, heroStats.damage, heroStats.deaths, heroStats.eliminations, heroStats.healing)
				else:
					print(response.url)

			print("Completed Match")
			
	await db.release(conn)

def buildPlayerStats(map, team, player):
	statistics = Stats(map["esports_match_id"], map["game_number"], team["esports_team_id"], player["esports_player_id"], "overall")

	if player["stats"] == None:
		return statistics

	for stat in player["stats"]:
		if stat["name"] == "eliminations":
			statistics.eliminations = stat["value"]
		elif stat["name"] == "deaths":
			statistics.deaths = stat["value"]
		elif stat["name"] == "damage":
			statistics.damage = stat["value"]
		elif stat["name"] == "healing":
			statistics.healing = stat["value"]

	return statistics


def buildHeroStats(map, team, player, hero):
	statistics = Stats(map["esports_match_id"], map["game_number"], team["esports_team_id"], player["esports_player_id"], hero["name"])


	for stat in hero["stats"]:
		if stat["name"] == "eliminations":
			statistics.eliminations = stat["value"]
		elif stat["name"] == "deaths":
			statistics.deaths = stat["value"]
		elif stat["name"] == "damage":
			statistics.damage = stat["value"]
		elif stat["name"] == "healing":
			statistics.healing = stat["value"]

	return statistics

asyncio.get_event_loop().run_until_complete(main())

