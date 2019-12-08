import asyncio
import asyncpg
import requests
import json

guids = {'0x0800000000000B56': 'Havana', '0x080000000000005B': 'Temple Of Anubis', '0x08000000000000D4': "King'S Row", '0x0800000000000165': 'Hanamura', '0x0800000000000184': 'Watchpoint: Gibraltar', '0x08000000000001D4': 'Numbani', '0x08000000000001DB': 'Volskaya Industries', '0x08000000000002AF': 'Hollywood', '0x08000000000002C3': 'Dorado', '0x08000000000004B7': 'Nepal', '0x08000000000005BB': 'Route 66', '0x0800000000000661': 'Tutorial', '0x0800000000000662': 'Lijiang Tower', '0x080000000000066D': 'Ilios', '0x0800000000000688': 'Practice Range', '0x080000000000068D': 'Eichenwalde', '0x080000000000069E': 'Oasis', '0x08000000000006AB': 'Hollywood', '0x08000000000006B1': "King'S Row", '0x08000000000006B3': 'Estádio Das Rãs', '0x08000000000006B5': 'Hanamura', '0x08000000000006B7': 'Lijiang Tower', '0x08000000000006C7': 'Vpp Green Room', '0x08000000000006C9': "Junkenstein'S Revenge", '0x08000000000006D1': 'Ecopoint: Antarctica', '0x08000000000006D3': 'Horizon Lunar Colony', '0x08000000000006FE': "King'S Row", '0x0800000000000705': 'Necropolis', '0x080000000000070C': 'Black Forest', '0x080000000000070D': 'Ecopoint: Antarctica', '0x0800000000000711': 'Lijiang Garden', '0x0800000000000712': 'Lijiang Night Market', '0x0800000000000717': 'Nepal Sanctum', '0x080000000000071A': 'Lijiang Control Center', '0x080000000000071C': 'Castillo', '0x0800000000000736': 'Nepal Village', '0x0800000000000738': 'Nepal Shrine', '0x080000000000073A': 'Ilios Well', '0x080000000000073D': 'Ilios Lighthouse', '0x080000000000073E': 'Ilios Ruins', '0x0800000000000744': 'Lijiang Control Center', '0x0800000000000745': 'Lijiang Garden', '0x0800000000000746': 'Lijiang Night Market', '0x080000000000074A': 'Oasis City Center', '0x080000000000074C': 'Oasis Gardens', '0x080000000000074D': 'Oasis University', '0x0800000000000751': 'Numbani', '0x0800000000000756': 'Junkertown', '0x080000000000075E': 'Blizzard World', '0x0800000000000793': 'Sydney Harbour Arena', '0x080000000000079F': 'Rialto', '0x08000000000007A1': 'Ayutthaya', '0x08000000000007A4': 'Château Guillard', '0x08000000000007E2': 'Busan', '0x08000000000007F4': 'Eichenwalde', '0x08000000000007F7': 'Black Forest', '0x08000000000007FD': 'Nepal Village', '0x0800000000000801': 'Junkertown', '0x0800000000000836': 'Château Guillard', '0x080000000000083B': 'Oasis', '0x080000000000083E': 'Blizzard World', '0x080000000000085F': 'Black Forest', '0x0800000000000871': 'Rialto', '0x080000000000088C': 'Eichenwalde', '0x0800000000000890': 'Petra', '0x0800000000000891': 'Paris', '0x08000000000008B4': 'Rialto', '0x08000000000008BE': 'Rialto', '0x080000000000092A': 'Busan Stadium', '0x0800000000000A14': 'Busan', '0x0800000000000A42': 'Busan', '0x0800000000000A44': 'Havana', '0x0800000000000A5A': 'Château Guillard', '0x0800000000000A5B': 'Blizzard World', '0x0800000000000A7A': 'Busan Sanctuary', '0x0800000000000A84': 'Route 66', '0x0800000000000A86': 'Busan Downtown', '0x0800000000000A9E': 'Blizzard World', '0x0800000000000AF0': 'Paris', '0x0800000000000AFE': 'Havana', '0x0800000000000B55': 'Havana'}
class Map:
	def __init__(self, matchid, mapNum, name, homescore, awayscore):
		self.matchid = matchid
		self.mapNum = mapNum
		self.name = name
		self.homescore = homescore
		self.awayscore = awayscore
		self.type = None
		self.gametime = None

async def main():
	credentials = {"user": "admin", "password": "570bb40736", "database": "owl", "host": "127.0.0.1"}
	
	db = await asyncpg.create_pool(**credentials)

	conn = await db.acquire()
	async with conn.transaction():
		response = requests.get(f"https://api.overwatchleague.com/matches")
		data = response.json()["content"]
		
		for match in data:
			for m in match["games"]:
				loadMap = Map(match["id"], m["number"], guids[m["attributes"]["mapGuid"]], m["points"][0], m["points"][1])
				mapResponse = requests.get(f"https://api.overwatchleague.com/stats/matches/{match['id']}/maps/{m['number']}")
				if mapResponse.status_code == 200:
					mapData = mapResponse.json()
					loadMap.type = mapData["map_type"]
					loadMap.gametime = mapData["stats"][0]["value"]
				await conn.execute("INSERT INTO maps VALUES ($1, $2, $3, $4, $5, $6, $7);", loadMap.matchid, loadMap.mapNum, loadMap.name, loadMap.type, loadMap.homescore, loadMap.awayscore, loadMap.gametime)
			
			print("Finished Map")
	await db.release(conn)

asyncio.get_event_loop().run_until_complete(main())

