-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

CREATE TABLE players (id SERIAL PRIMARY KEY,
					  name TEXT);

CREATE TABLE tournaments (id SERIAL PRIMARY KEY,
						  winner INT REFERENCES players(id));

CREATE TABLE matches (id SERIAL PRIMARY KEY,
					  id1 INT NOT NULL REFERENCES players (id),
					  id2 INT NOT NULL REFERENCES players (id),
					  winner INT REFERENCES players (id), -- if winner = NULL then game is a tie
					  tournament_id INT NOT NULL REFERENCES tournaments (id) ON DELETE CASCADE);

CREATE TABLE tournament_participants (id SERIAL PRIMARY KEY,
									  player_id INT NOT NULL REFERENCES players (id) ON DELETE CASCADE,
									  tournament_id INT NOT NULL REFERENCES tournaments (id) ON DELETE CASCADE);


CREATE VIEW games_played AS
SELECT tournament_participants.player_id AS id, COUNT(foo.id) AS matches, foo.tournament_id AS tournament_id
FROM tournament_participants
LEFT JOIN (SELECT id1 AS id, tournament_id FROM matches UNION ALL SELECT id2, tournament_id FROM matches)
AS foo
ON tournament_participants.player_id = foo.id
GROUP BY tournament_participants.player_id, foo.tournament_id;

CREATE VIEW wins AS
SELECT tournament_participants.player_id AS id, COUNT(matches.winner) AS wins, tournament_participants.tournament_id AS tournament_id
FROM tournament_participants
LEFT JOIN matches
ON tournament_participants.player_id = matches.winner
GROUP BY tournament_participants.player_id, tournament_participants.tournament_id;

CREATE VIEW ties AS
SELECT wins.id AS id, wins.wins AS wins, count(foo.id) AS ties, wins.tournament_id AS tournament_id
FROM wins
LEFT JOIN (SELECT id1 AS id FROM matches WHERE winner is NULL UNION ALL SELECT id2 FROM matches WHERE winner is NULL) AS foo
ON foo.id = wins.id
GROUP BY foo.id, wins.id, wins.wins, wins.tournament_id;

CREATE VIEW standings AS
SELECT games_played.id AS id, players.name AS name, games_played.matches AS matches, ties.wins AS wins, ties.ties AS ties, ties.wins * 3 + ties.ties AS points, ties.tournament_id AS tournament_id
FROM games_played
INNER JOIN ties
ON games_played.id = ties.id
INNER JOIN players
ON games_played.id = players.id
ORDER BY points DESC, wins DESC;

CREATE VIEW opponents AS
SELECT matches.id1 AS player, matches.id2 AS opponent, matches.tournament_id AS tournament_id
FROM matches
UNION ALL
SELECT matches.id2 AS player, matches.id1 AS opponent, matches.tournament_id AS tournament_id
FROM matches;





