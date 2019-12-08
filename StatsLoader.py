import asyncio
import asyncpg
import requests
import json


class Stats:
	def __init__(self, playerid, hero):
		self.playerid = playerid
		self.hero = hero
		self.eliminations = None
		self.deaths = None
		self.damage = None
		self.healing = None
		self.ultimates = None
		self.finalBlows = None
		self.timePlayed = None


async def main():
	credentials = {"user": "admin", "password": "570bb40736", "database": "owl", "host": "127.0.0.1"}
	
	db = await asyncpg.create_pool(**credentials)

	response = requests.get("https://api.overwatchleague.com/players?expand=stats%2Cstat.ranks&locale=en-us")
	data = response.json()
	conn = await db.acquire()
	
	async with conn.transaction():
		for player in data:
			playerStats = buildPlayerStats(player)
			await conn.execute("INSERT INTO stats VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);", playerStats.playerid, playerStats.hero, playerStats.eliminations, playerStats.deaths, playerStats.damage, playerStats.healing, playerStats.ultimates, playerStats.finalBlows, playerStats.timePlayed)
			# await conn.execute("INSERT INTO players VALUES ($1, $2, $3, $4, $5, $6, $7, $8);", player["id"], player["name"], f"{player['givenName']} {player['familyName']}", player["nationality"], hometown, player["attributes"]["player_number"], player["attributes"]["role"], player["teams"][0]["team"]["id"])

			if player["stats"] != None:
				for i in range(len(player["stats"]["heroes"])):
					stats = buildHeroStats(player, i)
					await conn.execute("INSERT INTO stats VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);", stats.playerid, stats.hero, stats.eliminations, stats.deaths, stats.damage, stats.healing, stats.ultimates, stats.finalBlows, stats.timePlayed)
			
	await db.release(conn)

def buildPlayerStats(player):
	statistics = Stats(player["id"], "overall")

	if player["stats"] == None:
		return statistics

	for stat in player["stats"]["stats"]:
		if stat["name"] == "eliminations_avg_per_1m":
			statistics.eliminations = stat["value"]
		elif stat["name"] == "deaths_avg_per_1m":
			statistics.deaths = stat["value"]
		elif stat["name"] == "hero_damage_avg_per_1m":
			statistics.damage = stat["value"]
		elif stat["name"] == "healing_avg_per_1m":
			statistics.healing = stat["value"]
		elif stat["name"] == "ultimates_earned_avg_per_1m":
			statistics.ultimates = stat["value"]
		elif stat["name"] == "final_blows_avg_per_1m":
			statistics.finalBlows = stat["value"]
		elif stat["name"] == "time_played_total":
			statistics.timePlayed = stat["value"]

	return statistics


def buildHeroStats(player, heroIndex):
	hero = player["stats"]["heroes"][heroIndex]

	statistics = Stats(player["id"], hero["name"])

	for stat in hero["stats"]:
		if stat["name"] == "eliminations_avg_per_1m":
			statistics.eliminations = stat["value"]
		elif stat["name"] == "deaths_avg_per_1m":
			statistics.deaths = stat["value"]
		elif stat["name"] == "hero_damage_avg_per_1m":
			statistics.damage = stat["value"]
		elif stat["name"] == "healing_avg_per_1m":
			statistics.healing = stat["value"]
		elif stat["name"] == "ultimates_earned_avg_per_1m":
			statistics.ultimates = stat["value"]
		elif stat["name"] == "final_blows_avg_per_1m":
			statistics.finalBlows = stat["value"]
		elif stat["name"] == "time_played_total":
			statistics.timePlayed = stat["value"]

	return statistics

asyncio.get_event_loop().run_until_complete(main())

