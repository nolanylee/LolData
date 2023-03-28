from src.LolClasses import LolPlayer, LolMatch
from src.databases import LolSQL, MatchSQL

if __name__ == '__main__':

	matchId = 'NA1_4513248443'
	region = 'na1'
	depth = 4

	match_0 = LolMatch(matchId, region)


	info_p2 = ['Delicate Caress', 'na1']

	p2 = LolPlayer(info_p2[0], info_p2[1])

	p2.initialize_api()

	# db = LolSQL('loldata')

	# db.initialize_table()

	# db.insert_player(p1)
	# db.insert_player(p2)

	# print(db.find_player('nowin REE'))

	# print(db.find_player('XVXLXNN'))

	# player_blank = LolPlayer(info_p1[0], info_p1[1])

	# player_blank.initialize_sql(db)

	# print(p1)
	# print(player_blank)

	# db.close_connection(db.conn)