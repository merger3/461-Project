import asyncio
import asyncpg
import requests
import json



async def main():
	credentials = {"user": "admin", "password": "570bb40736", "database": "owl", "host": "127.0.0.1"}
	
	db = await asyncpg.create_pool(**credentials)

	response = requests.get("https://api.overwatchleague.com/players?expand=stats%2Cstat.ranks&locale=en-us")
	data = response.json()
	conn = await db.acquire()
	
	async with conn.transaction():
		for player in data:
			try:
				hometown = player["homeLocation"]
			except KeyError:
				hometown = None

			await conn.execute("INSERT INTO players VALUES ($1, $2, $3, $4, $5, $6, $7, $8);", player["id"], player["name"], f"{player['givenName']} {player['familyName']}", player["nationality"], hometown, player["attributes"]["player_number"], player["attributes"]["role"], player["teams"][0]["team"]["id"])
			
	await db.release(conn)

asyncio.get_event_loop().run_until_complete(main())

