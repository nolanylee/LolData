from riotwatcher import LolWatcher, ApiError
import random
from dotenv import dotenv_values

KEY = dotenv_values("/Users/nolanlee/lolproject/src/.env")["KEY"]
S13_START = 1672560000

class MatchCrawler():
	def __init__(self, puuid_origin, region):
		self.watcher = LolWatcher(KEY, timeout=2.5)
		self.puuid = puuid_origin
		self.region = region

	def crawl(self, queueId=420, match_lim=60):
		try:
			matches = self.watcher.match.matchlist_by_puuid(self.region, self.puuid, queue=queueId)
		except ApiError as err:
			if err.response.status_code == 429:
				print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
				print('this retry-after is handled by default by the RiotWatcher library')
				print('future requests wait until the retry-after time passes')
			elif err.response.status_code == 404:
				print('Summoner not found.')
			else:
				raise err
		match_ids = matches
		while len(match_ids) < match_lim:
			match = match_ids[random.randint(0, len(match_ids) - 1)]
			try:
				participants = self.watcher.match.by_id(self.region, match)['metadata']['participants']
				puuid = participants[random.randint(0, 9)]
				matches = self.watcher.match.matchlist_by_puuid(self.region, puuid, queue=queueId)
			except ApiError as err:
				if err.response.status_code == 429:
					print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
					print('this retry-after is handled by default by the RiotWatcher library')
					print('future requests wait until the retry-after time passes')
				elif err.response.status_code == 404:
					print('Summoner not found.')
				else:
					raise err
			match_ids.extend(matches)
			match_ids = list(dict.fromkeys(match_ids))
		return match_ids

	def change_origin(self, puuid):
		self.puuid = puuid

if __name__ == '__main__':
	puuid = 'P12Ycvxg5JQrJRWYfIoFSejxjynnvCR7op9dL2INJlHHIi8LPB5JMlgHIudekKFKoFduLxQ93OoMUA'
	matchCrawler = MatchCrawler(puuid, 'na1')
	match_ids = matchCrawler.crawl()
	print(match_ids)


