from riotwatcher import LolWatcher, ApiError
from src.LolClasses import LolPlayer, LolMatch
from src.databases import LolSQL, MatchSQL
from dotenv import dotenv_values

KEY = dotenv_values("/Users/nolanlee/lolproject/src/.env")["KEY"]

region = 'na1'

puuid = 'P12Ycvxg5JQrJRWYfIoFSejxjynnvCR7op9dL2INJlHHIi8LPB5JMlgHIudekKFKoFduLxQ93OoMUA'

preseason_start = 1668585600

matchId = 'NA1_4513248443'

match = LolMatch(matchId, region)
match.initialize_api()

match_data = MatchSQL('matchdata')
match_data.initialize_table()
match_data.insert_match(match)

