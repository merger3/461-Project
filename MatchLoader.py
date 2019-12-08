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

	conn = await db.acquire()
	async with conn.transaction():
		response = requests.get(f"https://api.overwatchleague.com/matches")
		data = response.json()["content"]

		for match in data:
			# response = requests.get(f"https://api.overwatchleague.com/stats/matches/{match}/maps/{i}")
			# data = response.json()
			await conn.execute("INSERT INTO matches VALUES ($1, $2, $3, $4, $5, $6, $7, $8);", match["id"], match["competitors"][0]["id"], match["competitors"][1]["id"], match["scores"][0]["value"], match["scores"][1]["value"], match["startDate"], match["actualEndDate"] - match["actualStartDate"], match["bracket"]["stage"]["tournament"]["title"])
			
	await db.release(conn)

asyncio.get_event_loop().run_until_complete(main())

