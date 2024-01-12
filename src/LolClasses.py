from riotwatcher import LolWatcher, ApiError
from dotenv import dotenv_values

# API key for personal use only
KEY = dotenv_values("/Users/nolanlee/lolproject/src/.env")["KEY"]

# Class representation of a League of Legends player using RiotWatcher.
# After instantiation, LolPlayer can be initialized through API using
# initialize_api() or through a LolSQL instance using initialize_sql().
class LolPlayer():
	# Initialize a LolPlayer instance using string summonerName and
	# string region in format as follows:
	# North America:       na1 | Europe East:         eun1 | Europe West: euw1
	# Latin America North: la1 | Latin America South: la2  | Brazil:      br1
	# Oceania:             oc1 | Russia:              ru1  | Turkey:      tr1
	# Japan:               jp1 | Korea:               kr   |

	def __init__(self, summonerName, region):
		self.watcher = LolWatcher(KEY, timeout=2.5)
		self.summonerName = summonerName
		self.region = region

		# Attributes filled in during initialize_api() or initialize_sql().
        # Information about each attribute:
        # leagueId and summonerId: unique identifiers for player
        # tier: big milestones for ranked (bronze, silver, gold, etc.)
        # rank: small milestones for ranked (silver 3, silver 2, silver 1, etc.)
        # leaguePoints: points (0-100) gained/lost from winning/losing games, 
        #             \ reaching 100 points = promotion to higher rank or tier
        # wins: amount of solo ranked wins
        # losses: amount of solo ranked losses
        # inactive: boolean on whether account is inactive
		self.puuid = None
		self.leagueId = None
		self.summonerId = None
		self.tier = None
		self.rank = None
		self.leaguePoints = None
		self.wins = None
		self.losses = None
		self.inactive = None

	# Initialize player using Riot API. 
    # The player is found through the Summoner-V4 API, then 
    # rank information is obtained using the League-V4 API.
	def initialize_api(self):
		try:
			player = self.watcher.summoner.by_name(self.region, self.summonerName)
			league = self.watcher.league.by_summoner(self.region, player['id'])
		except ApiError as err:
			if err.response.status_code == 429:
				print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
				print('this retry-after is handled by default by the RiotWatcher library')
				print('future requests wait until the retry-after time passes')
			elif err.response.status_code == 404:
				print('Summoner not found.')
				raise err
			else:
				raise err
		self.puuid = player['puuid']
		soloLeague = [queue for queue in league if queue['queueType'] == 'RANKED_SOLO_5x5']
		if len(soloLeague) != 0:
			soloLeague = soloLeague[0]
			self.leagueId = soloLeague['leagueId']
			self.summonerId = soloLeague['summonerId']
			self.tier = soloLeague['tier']
			self.rank = soloLeague['rank']
			self.leaguePoints = soloLeague['leaguePoints']
			self.wins = soloLeague['wins']
			self.losses = soloLeague['losses']
			self.inactive = soloLeague['inactive']
		elif len(league) != 0:
			self.leagueId = league[0]['leagueId']
			self.summonerId = league[0]['summonerId']
			self.tier = 'UNRANKED'
			self.rank = '0'
			self.leaguePoints = 0
			self.wins = 0
			self.losses = 0
			self.inactive = True
		else:
			self.leagueId = 'N/A'
			self.summonerId = 'N/A'
			self.tier = 'UNRANKED'
			self.rank = '0'
			self.leaguePoints = 0
			self.wins = 0
			self.losses = 0
			self.inactive = True

    # Initialize player using LolSQL database.
    # The player is found in the database, then
    # rank information is obtained from the cols.
	def initialize_sql(self, LolSQL):
		selection = LolSQL.find_player(self.summonerName)

		self.puuid = selection[2]
		self.leagueId = selection[3]
		self.summonerId = selection[4]
		self.tier = selection[5]
		self.rank = selection[6]
		self.leaguePoints = selection[7]
		self.wins = selection[8]
		self.losses = selection[9]
		self.inactive = selection[10]

	def update_tiers(self):
		gm_list = self.watcher.league.grandmaster_by_queue('na1', 'RANKED_SOLO_5x5')['entries']
		gm_min = gm_list[0]['leaguePoints']
		for gm in gm_list:
			lp = gm['leaguePoints']
			if lp < gm_min:
				gm_min = lp
		RankConverter.update('GRANDMASTER', 2400 + gm_min)
		chal_list = self.watcher.league.challenger_by_queue('na1', 'RANKED_SOLO_5x5')['entries']
		chal_min = chal_list[0]['leaguePoints']
		for chal in chal_list:
			lp = chal['leaguePoints']
			if lp < chal_min:
				chal_min = lp 
		RankConverter.update('CHALLENGER', 2400 + gm_min + chal_min)

	def convert_to_lp(self):
		lp = RankConverter.convert_tier(self.tier)
		if lp != None:
			lp += self.leaguePoints
			if lp < 2400:
				lp += RankConverter.convert_rank(self.rank)
		return lp

	# Obtain dictionary of champion information (WARNING: very long to print)
	def get_champlist(self):
		versions = self.watcher.data_dragon.versions_for_region(self.region)
		champions_version = versions['n']['champion']
		champlist = self.watcher.data_dragon.champions(champions_version)
		return champlist

	def puuid(self):
		return self.puuid

	def leagueId(self):
		return self.leagueId

	def summonerId(self):
		return self.summonerId

	def tier(self):
		return self.tier

	def rank(self):
		return self.rank

	def leaguePoints(self):
		return self.leaguePoints

	def wins(self):
		return self.wins

	def losses(self):
		return self.losses

	def inactive(self):
		return self.inactive

	# Print the ranked stats of the player.
	def __str__(self):
		return ("Name: " + str(self.summonerName) 
				+ " |Tier: " + str(self.tier) 
				+ " |Rank: " + str(self.rank) 
				+ " |LP: " + str(self.leaguePoints) 
				+ " |Wins: " + str(self.wins) 
				+ " |Losses: " + str(self.losses) 
				+ " |Inactive: " + str(self.inactive))

class LolMatch():
	def __init__(self, matchId, region):
		self.watcher = LolWatcher(KEY, timeout=2.5)
		self.matchId = matchId
		self.region = region

		self.gameDuration = None
		self.gameVersion = None
		self.queueId = None
		self.summonerName = []
		self.championName = []
		self.teamPosition = []
		self.teamSide = []
		self.kills = []
		self.deaths = []
		self.assists = []
		self.damageDealt = []
		self.damageTaken = []
		self.goldEarned = []
		self.champExperience = []
		self.visionScore = []
		self.item0 = []
		self.item1 = []
		self.item2 = []
		self.item3 = []
		self.item4 = []
		self.item5 = []
		self.item6 = []
		self.victory = []

	def initialize_api(self):
		try:
			matchDto = self.watcher.match.by_id(self.region, self.matchId)
		except ApiError as err:
			if err.response.status_code == 429:
				print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
				print('this retry-after is handled by default by the RiotWatcher library')
				print('future requests wait until the retry-after time passes')
			elif err.response.status_code == 404:
				print('Match not found.')
			else:
				raise err

		infoDto = matchDto['info']

		self.gameDuration = infoDto['gameDuration']
		self.gameVersion = infoDto['gameVersion']
		self.queueId = infoDto['queueId']

		for player in infoDto['participants']:
			self.summonerName.append(player['summonerName'])
			self.championName.append(player['championName'])
			self.teamPosition.append(player['teamPosition'])
			self.teamSide.append(player['teamId'])
			self.kills.append(player['kills'])
			self.deaths.append(player['deaths'])
			self.assists.append(player['assists'])
			self.damageDealt.append(player['totalDamageDealtToChampions'])
			self.damageTaken.append(player['totalDamageTaken'])
			self.goldEarned.append(player['goldEarned'])
			self.champExperience.append(player['champExperience'])
			self.visionScore.append(player['visionScore'])
			self.item0.append(player['item0'])
			self.item1.append(player['item1'])
			self.item2.append(player['item2'])
			self.item3.append(player['item3'])
			self.item5.append(player['item5'])
			self.item6.append(player['item6'])
			self.victory.append(player['win'])

class RankConverter():
	def update(tier, LP):
		RankConverter.tier_converter[tier] = LP

	def convert_tier(tier):
		return RankConverter.tier_converter[tier]

	def convert_rank(rank):
		return RankConverter.rank_converter[rank]

	tier_converter = {'UNRANKED':			None,
					  'IRON':				0,
					  'BRONZE':				400,
					  'SILVER':				800,
					  'GOLD':				1200,
					  'PLATINUM':			1600,
					  'EMERALD':			2000,
					  'DIAMOND':			2400,
					  'MASTER':				2800,
					  'GRANDMASTER':		2800,
					  'CHALLENGER':			2800}

	rank_converter = {'IV':				0,
					  'III':			100,
					  'II':				200,
					  'I':				300}

if __name__ == '__main__':

	# name = 'nowin REE'
	# reg = 'na1'

	# player = LolPlayer(name, reg)

	# ranked_stats = player.get_ranked()
	# print(ranked_stats)

	# champlist = player.get_champlist()
	#print(champlist)

	player = LolPlayer('nowin REE', 'na1')
	player.initialize_api()

	player.update_tiers()

	print(player.convert_to_lp())
	print(RankConverter.tier_converter['CHALLENGER'])

