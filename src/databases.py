import sqlite3 as sq3
from sqlite3 import Error

# General functions to manipulate sqlite3 connections and execute sql
# statements on databases. Note: closing connections is something left
# to the user to do manually with the close_connection() function.
class SQLdb():
	# Given a filename in the format "___.db" (where "___" is the filename),
	# open and return a Connection to the file.
	def open_connection(self, db_file):
		try:
			connection = sq3.connect(db_file)
			return connection
		except Error as e:
			print(e)
			raise e

	# Given a Connection and string CREATE TABLE sql_statement,
	# create the table in the database.
	def create_table(self, connection, sql_statement, placeholders=()):
		try:
			c = connection.cursor()
			c.execute(sql_statement, placeholders)
		except Error as e:
			print(e)
			raise e
		finally:
			c.close()

	# Given a Connection, a string INSERT INTO sql_statement, 
	# and tuple placeholders that replace the "?" symbols
	# in sql_statement, insert into the database.
	def insert_into_table(self, connection, sql_statement, placeholders=()):
		try:
			c = connection.cursor()
			c.execute(sql_statement, placeholders)
			connection.commit()
		except Error as e:
			print(e)
			raise e
		finally:
			c.close()

	# Given a Connection, a string SELECT FROM sql_statement,
	# and tuple placeholders that replace the "?" symbols
	# in sql_statement, return selection from database as tuple.
	def select_from_table_where(self, connection, sql_statement, placeholders=()):
		try:
			c = connection.cursor()
			c.execute(sql_statement, placeholders)
			selection = c.fetchone()
		except Error as e:
			print(e)
			raise e
		finally:
			c.close()
		return selection

	# Given a Connection, close it. 
	def close_connection(self, connection):
		connection.close()

# Subclass of SQLdb specifically for storing data related to LoL.
# This database uses the LolPlayer class to obtain data necessary
# to insert players into the database.
class LolSQL(SQLdb):
	# Initialize a LolSQL instance using a string name, which is the
	# name of the database file (without the ".db" file extension).
	def __init__(self, name):
		self.name = name
		self.filename = "data/" + name + ".db"
		self.conn = self.open_connection(self.filename)

	# Create the LolSQL table that stores information about players.
	# For more information about fields, look at LolPlayer class.
	def initialize_table(self):
		create_sql = """
					CREATE TABLE IF NOT EXISTS player_data (
						summonerName	TEXT  PRIMARY KEY	NOT NULL,
						region			TEXT				NOT NULL,
						puuid			TEXT				NOT NULL,
						leagueId		TEXT				NOT NULL,
						summonerId 		TEXT				NOT NULL,
						tier			TEXT				NOT NULL,
						rank			TEXT				NOT NULL,
						leaguePoints	INT					NOT NULL,
						wins			INT					NOT NULL,
						losses			INT					NOT NULL,
						inactive		INT					NOT NULL
						);
					"""
		self.create_table(self.conn, create_sql)

	# Given a player (as LolPlayer instance), "upsert" player into table.
	# "Upsert": insert if doesn't exist, else update.
	def insert_player(self, LolPlayer):
		insert_sql = """
					INSERT OR REPLACE INTO player_data
					(summonerName, region, puuid, leagueId, summonerId, tier, rank,
						leaguePoints, wins, losses, inactive)
					VALUES
					(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
					"""
		values = (LolPlayer.summonerName, LolPlayer.region, LolPlayer.puuid,
				  LolPlayer.leagueId, LolPlayer.summonerId, LolPlayer.tier, 
				  LolPlayer.rank, LolPlayer.leaguePoints, LolPlayer.wins, 
				  LolPlayer.losses, LolPlayer.inactive,)
		self.insert_into_table(self.conn, insert_sql, values)

	# Given a string name, search database for that player,
	# and return a tuple of the player's information.
	def find_player(self, name):
		select_sql = """
					SELECT * 
					FROM player_data
					WHERE summonerName = ?

					 """
		filters = (name,)
		return self.select_from_table_where(self.conn, select_sql, filters)

class MatchSQL(SQLdb):
	def __init__(self, name):
		self.name = name
		self.filename = "data/" + name + ".db"
		self.conn = self.open_connection(self.filename)

	def initialize_table(self):
		create_sql = """
					CREATE TABLE IF NOT EXISTS match_data (
						summonerName	TEXT				NOT NULL,
						matchId			TEXT				NOT NULL,
						gameVersion		TEXT				NOT NULL,
						queueId			INT					NOT NULL,
						championName	TEXT				NOT NULL,
						teamPosition	TEXT				NOT NULL,
						teamSide		INT  				NOT NULL,
						gameDuration	INT  				NOT NULL,
						kills			INT 				NOT NULL,
						deaths			INT 				NOT NULL,
						assists			INT 				NOT NULL,
						damageDealt		INT  				NOT NULL,
						damageTaken		INT  				NOT NULL,
						goldEarned		INT 				NOT NULL,
						champExperience	INT  				NOT NULL,
						visionScore		INT  				NOT NULL,
						item0			INT 				NOT NULL,
						item1			INT 				NOT NULL,
						item2			INT 				NOT NULL,
						item3			INT 				NOT NULL,
						item5			INT 				NOT NULL,
						item6			INT 				NOT NULL,
						victory			BOOLEAN				NOT NULL,
						PRIMARY KEY	(summonerName, matchId)
						);
					"""
		self.create_table(self.conn, create_sql)

	def insert_match(self, LolMatch):
		insert_sql = """
					INSERT OR REPLACE INTO match_data 
					(summonerName, matchId, gameVersion, queueId, championName,
						teamPosition, teamSide, gameDuration, kills, deaths, assists,
						damageDealt, damageTaken, goldEarned, champExperience, visionScore,
						item0, item1, item2, item3, item5, item6, victory)
					VALUES
					(?, ?, ?, ?, ?, 
					?, ?, ?, ?, ?, ?, 
						?, ?, ?, ?, ?, 
					?, ?, ?, ?, ?, ?, ?)
					"""
		for i in range(0, 10):
			values = (LolMatch.summonerName[i], LolMatch.matchId, LolMatch.gameVersion, LolMatch.queueId, LolMatch.championName[i],
						LolMatch.teamPosition[i], LolMatch.teamSide[i], LolMatch.gameDuration, LolMatch.kills[i], LolMatch.deaths[i], LolMatch.assists[i],
						LolMatch.damageDealt[i], LolMatch.damageTaken[i], LolMatch.goldEarned[i], LolMatch.champExperience[i], LolMatch.visionScore[i],
						LolMatch.item0[i], LolMatch.item1[i], LolMatch.item2[i], LolMatch.item3[i], LolMatch.item5[i], LolMatch.item6[i], LolMatch.victory[i])

			self.insert_into_table(self.conn, insert_sql, values)

if __name__ == '__main__':

	connection = open_connection("pythonsqlite.db")

	create_sql = """
				CREATE TABLE IF NOT EXISTS test_table (
					col1 INT PRIMARY KEY	NOT NULL,
					col2 TEXT 				NOT NULL,
					col3 CHAR(50) 			NOT NULL,
					col4 REAL				NOT NULL
					);
				"""
	
	create_table(connection, create_sql)
	close_connection(connection)
