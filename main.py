import asyncio
import asyncpg
from prettytable import PrettyTable
import pycountry
import strings


async def main():
	# credentials = {"user": "admin", "password": "570bb40736", "database": "owl", "host": "127.0.0.1"}
	credentials = {"user": "postgres", "password": "570bb40736", "database": "owl", "host": "imdb-2.cfmhixjeqnph.us-east-1.rds.amazonaws.com"}

	db = await asyncpg.create_pool(**credentials)

	print("Welcome to the Overwatch League stats tool!")
	print("From any menu other than the main menu entering 'b' will take you back to the previous menu")

	players = await playerSelection(db)
	await printPlayers(players)

	choice = 0
	while choice != 6:
		choice = mainMenu()

		if choice == 1:
			sub = validate("1. Stats Per 10 Minutes\n2. Totals", 2, 1)
			if sub == 1:
				await printStatsPerTen(db, players)
			elif sub == 2:
				await printStatsTotal(db, players)
		
		elif choice == 2:
			sub = validate("1. Stats Per 10 Minutes\n2. Totals", 2, 1)
			if sub == 1:
				await printHeroStatsPerTen(db, players)
			elif sub == 2:
				await printHeroStatsTotal(db, players)

		elif choice == 3:
			sub = validate("1. Individual Map Stats\n2. Map Type Stats", 2, 1)
			if sub == 1:
				await mapStatAverages(db, players, 'map')
			elif sub == 2:
				await mapStatAverages(db, players, 'type')

		elif choice == 4:
			newPlayers = await playerSelection(db)
			players.extend(newPlayers)

		elif choice == 5:
			await printPlayers(players)

def validate(string, upper, lower):
	choice = 0
	while choice < lower or choice > upper:
		print(string)
		choice = input("Select an option: ")
		if choice == 'b':
			break
		else:
			choice = int(choice)
			if choice < lower or choice > upper:
				print("Invalid option")
	
	return choice

def mainMenu():
	choice = 0
	while choice < 1 or choice > 6:
		print("What would you like to do?")
		print("1. Season Stats\n2. Hero Stats\n3. Map Stats\n4. Add Players\n5. Print Players\n6. Quit")
		choice = int(input("Select an option: "))
		if choice < 1 or choice > 6:
			print("Invalid option")
	
	return choice

async def playerSelection(db):
	players = []
	while True:
		playerName = input("Add a player (type done when finished): ")
		
		if playerName == 'all':
			players = await db.fetch("SELECT * FROM players WHERE name != 'Baconjack';")
			return players

		if playerName == "done":
			break
		
		player = await db.fetchrow("SELECT * FROM players WHERE name ilike $1", playerName)
	
		if player == None:
			print("Player not found!")
		else:
			players.append(player)
			print(f"Added {player['name']}")

	
	return players

async def printPlayers(players):
	x = PrettyTable()
	x.field_names = ["Name", "Given Name", "Nationality", "Hometown", "Number", "Role"]
	for player in players:
		x.add_row([player["name"], player["givenname"], pycountry.countries.get(alpha_2=player["nationality"]).name, player["hometown"], player["number"], player["role"]])
	
	print(x.get_string(start=0, end=20))
	# print(x.get_string(start=0, end=20))
	# print("a")
	# gamesPlayed = await db.fetchrow('SELECT COUNT(DISTINCT matchid) AS "matches", COUNT(*) AS "maps" FROM mapstats WHERE mapstats.playerid = $1;', player["id"])
	
async def printStatsPerTen(db, players):

	ids = [p['id'] for p in players]


	stats = await db.fetch(strings.playerStatsPerTen, ids)
	
	x = PrettyTable()
	x.field_names = ["Name", "Eliminations", "Deaths", "Damage", "Healing", "Ultimates", "Final Blows", "Time Played"]
	for player in stats:
		x.add_row([player['name'], round(player['eliminations'], 2), round(player['deaths'], 2), round(player['damage'], 2), round(player['healing'], 2), round(player['ultimates'], 2), round(player['final_blows'], 2), round(player['time_played'], 2)])

	print("\n")
	print(x.get_string(start=0, end=20))

	while True:
		
		x.reversesort = True
		sort = input("Enter a field to sort by: ")

		if sort == 'b':
			break

		try:
			x.sortby = sort
			print("\n")
			print(x.get_string(start=0, end=20))
		except:
			print("Invalid field name! Remember value is case-sensitive")


async def printStatsTotal(db, players):
	ids = [p['id'] for p in players]

	nameDict = {}
	for player in players:
		nameDict[player["id"]] = player["name"]




	x = PrettyTable()
	x.field_names = ["Name", "Eliminations", "Deaths", "Damage", "Healing"]

	allTotals = await db.fetch(strings.totalStats, ids, 'overall')
	for totals in allTotals:
		x.add_row([nameDict[totals['playerid']], round(totals['eliminations'], 2), round(totals['deaths'], 2), round(totals['damage'], 2), round(totals['healing'], 2)])
	
	print("\n")
	print(x.get_string(start=0, end=20))

	while True:
		
		x.reversesort = True
		sort = input("Enter a field to sort by: ")

		if sort == 'b':
			break

		try:
			x.sortby = sort
			print(x.get_string(start=0, end=20))
		except:
			print("Invalid field name! Remember value is case-sensitive")

	x.clear_rows()

async def printHeroStatsPerTen(db, players):

	ids = [str(p['id']) for p in players]
	idString = f"({', '.join(ids)})"

	x = PrettyTable()
	x.field_names = ["Name", "Eliminations", "Deaths", "Damage", "Healing", "Ultimates", "Final Blows", "Time Played"]


	hero = "overall"
	while True:
		hero = input("Enter a hero: ")
		hero = hero.replace(" ", "").lower()

		if hero == 'b':
			break

		stats = await db.fetch(f"SELECT players.name, coalesce(stats.eliminations * 10, 0) AS \"eliminations\", coalesce(stats.final_blows * 10, 0) AS \"final_blows\", coalesce(stats.damage * 10, 0) AS \"damage\", coalesce(stats.healing * 10, 0) AS \"healing\", coalesce(stats.deaths * 10, 0) AS \"deaths\", coalesce(stats.ultimates * 10, 0) AS \"ultimates\", coalesce(stats.final_blows * 10, 0) AS \"final_blows\", coalesce(stats.time_played, 0) AS \"time_played\" FROM stats INNER JOIN players ON players.id = stats.playerid WHERE stats.playerid IN {idString} AND stats.hero = $1;", hero)
		
		for player in stats:
			x.add_row([player['name'], round(player['eliminations'], 2), round(player['deaths'], 2), round(player['damage'], 2), round(player['healing'], 2), round(player['ultimates'], 2), round(player['final_blows'], 2), round(player['time_played'], 2)])

		print("\n")
		print(x.get_string(start=0, end=20))

		while True:
			
			x.reversesort = True
			sort = input("Enter a field to sort by: ")

			if sort == 'b':
				break

			try:
				x.sortby = sort
				print(x.get_string(start=0, end=20))
			except:
				print("Invalid field name! Remember value is case-sensitive")

		x.clear_rows()

async def printHeroStatsTotal(db, players):
	ids = [p['id'] for p in players]

	nameDict = {}
	for player in players:
		nameDict[player["id"]] = player["name"]

	x = PrettyTable()
	x.field_names = ["Name", "Eliminations", "Deaths", "Damage", "Healing"]


	hero = "overall"
	while True:
		hero = input("Enter a hero: ")
		hero = hero.replace(" ", "").lower()

		if hero == 'b':
			break

		allTotals = await db.fetch(strings.totalStats, ids, hero)
		for totals in allTotals:
			x.add_row([nameDict[totals['playerid']], round(totals['eliminations'], 2), round(totals['deaths'], 2), round(totals['damage'], 2), round(totals['healing'], 2)])
		
		print("\n")
		print(x.get_string(start=0, end=20))	

		while True:
			
			x.reversesort = True
			sort = input("Enter a field to sort by: ")

			if sort == 'b':
				break

			try:
				x.sortby = sort
				print(x.get_string(start=0, end=20))
			except:
				print("Invalid field name! Remember value is case-sensitive")
		
		x.clear_rows()

async def mapStatAverages(db, players, catagory):
	nameDict = {}

	for player in players:
		nameDict[player["id"]] = player["name"]


	ids = [p['id'] for p in players]

	x = PrettyTable()
	x.field_names = ["Name", "Played", "Won", "Lost", "Tied", "Winrate", "Eliminations", "Deaths", "Damage", "Healing"]


	while True:
		if catagory == 'type':
			mapName = input("Enter a map type: ")
		else:
			mapName = input("Enter a map: ")

		if mapName == 'b':
			break

		if catagory == 'type':
			totals = await db.fetch(strings.typeStats, ids, mapName)
		else:
			totals = await db.fetch(strings.mapStats, ids, mapName)

		for player in totals:
			x.add_row([nameDict[player['playerid']], player['played'], player['won'], player['lost'], player['tied'], str(round(((player['won'] / player['played']) * 100), 2)) + '%', round(player['avg_eliminations'], 2), round(player['avg_deaths'], 2), round(player['avg_damage'], 2), round(player['avg_healing'], 2)])
		
		print("\n")
		print(x.get_string(start=0, end=20))

		while True:
			
			x.reversesort = True
			sort = input("Enter a field to sort by: ")

			if sort == 'b':
				break

			try:
				x.sortby = sort
				print(x.get_string(start=0, end=20))
			except:
				print("Invalid field name! Remember value is case-sensitive")
		
		x.clear_rows()



asyncio.get_event_loop().run_until_complete(main())


