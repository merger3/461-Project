import asyncio
import asyncpg
import requests
import json



async def main():
	credentials = {"user": "admin", "password": "570bb40736", "database": "owl", "host": "127.0.0.1"}
	
	db = await asyncpg.create_pool(**credentials)

	response = requests.get("https://api.overwatchleague.com/rankings")
	data = response.json()["content"]

	conn = await db.acquire()
	
	async with conn.transaction():
		for team in data:

			await conn.execute("INSERT INTO records VALUES ($1, $2, $3, $4, $5, $6, $7);", team["competitor"]["id"], team["placement"], team["records"][0]["matchWin"], team["records"][0]["matchLoss"], team["records"][0]["gameWin"], team["records"][0]["gameLoss"], team["records"][0]["gameTie"])

	await db.release(conn)


asyncio.get_event_loop().run_until_complete(main())

