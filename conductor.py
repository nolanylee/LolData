from src.LolClasses import LolPlayer, LolMatch
from src.databases import LolSQL, MatchSQL
from src.crawler import MatchCrawler
from riotwatcher import LolWatcher, ApiError
from dotenv import dotenv_values
from sqlite3 import Error

PUUID = dotenv_values("/Users/nolanlee/lolproject/src/.env")["PUUID"]

class Conductor:
	def execute(region):
		print('Crawling...')
		crawler = MatchCrawler(PUUID, region)
		print('Crawl complete.')
		match_ids = crawler.crawl()

		player_data = LolSQL('conduct_player')
		player_data.initialize_table()

		match_data = MatchSQL('conduct_match')
		match_data.initialize_table()

		print('Storing scraped data...')
		i = 1
		for match_id in match_ids:
			match = LolMatch(match_id, region)
			match.initialize_api()
			match_data.insert_match(match)

			for summonerName in match.summonerName:
				player = LolPlayer(summonerName, region)
				try:
					player.initialize_api()
					player_data.insert_player(player)
				except ApiError as e:
					continue
			print('Data from match ' + str(i) + '/' + str(len(match_ids)) + ' stored.')
			i += 1

		print('Storage complete.')

	def execute_random(region):
		player_data = LolSQL('conduct_player')
		player_data.initialize_table()
		PUUID = player_data.get_random_puuid()

		print('Crawling...')
		crawler = MatchCrawler(PUUID, region)
		print('Crawl complete.')
		match_ids = crawler.crawl()

		match_data = MatchSQL('conduct_match')
		match_data.initialize_table()

		print('Storing scraped data...')
		i = 0
		for match_id in match_ids:
			i += 1
			try:
				match = LolMatch(match_id, region)
				match.initialize_api()
				match_data.insert_match(match)

				for summonerName in match.summonerName:
					player = LolPlayer(summonerName, region)
					try:
						player.initialize_api()
						player_data.insert_player(player)
					except ApiError as e:
						continue
				print('Data from match ' + str(i) + '/' + str(len(match_ids)) + ' stored.')
			except Error as e:
				continue

		print('Storage complete.')

if __name__ == '__main__':
	#Conductor.execute('na1')
	for i in range(5):
		Conductor.execute_random('na1')