import asyncio
import asyncpg
import requests
import json



async def main():
	credentials = {"user": "admin", "password": "570bb40736", "database": "owl", "host": "127.0.0.1"}
	
	db = await asyncpg.create_pool(**credentials)

	response = requests.get("https://api.overwatchleague.com/teams")
	data = response.json()["competitors"]

	# rresponse = requests.get("https://api.overwatchleague.com/rankings")
	# rankings = response.json()["content"]

	conn = await db.acquire()
	
	async with conn.transaction():
		for entry in data:
			team = entry["competitor"]
			if team["owl_division"] == 79:
				div = "Atlantic"
				divabbrev = "ATL"
			else:
				div = "Pacific"
				divabbrev = "PAC"

			# for t in rankings:
			# 	if t["competitor"]["id"] == team["id"]:
			# 		rank = t["placement"]
			# 		break

			await conn.execute("INSERT INTO teams VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);", team["id"], team["name"], team["homeLocation"], team["addressCountry"], team["abbreviatedName"], div, divabbrev, team["primaryColor"], team["secondaryColor"])

	await db.release(conn)


asyncio.get_event_loop().run_until_complete(main())

