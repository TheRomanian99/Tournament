-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players (id SERIAL PRIMARY KEY,
					  name TEXT);

CREATE TABLE matches (id SERIAL PRIMARY KEY,
					  winner INT REFERENCES players (id),
					  loser INT REFERENCES players (id));


-- create table to see how many matches each participant has played
CREATE VIEW games_played AS
SELECT players.id AS id, players.name AS name, COUNT(foo.id) AS matches
FROM players
LEFT JOIN (SELECT winner AS id FROM matches UNION ALL SELECT loser FROM matches)
AS foo
ON players.id = foo.id
GROUP BY players.id;


CREATE VIEW standings AS
SELECT games_played.id AS id, games_played.name AS name, COUNT(matches.winner) as wins, games_played.matches AS matches
FROM games_played 
LEFT JOIN matches
ON games_played.id = matches.winner
GROUP BY games_played.id, games_played.name, games_played.matches
ORDER BY wins DESC;

-- see who has played who
CREATE VIEW opponents AS
SELECT matches.loser AS player, matches.winner AS opponent
FROM matches
UNION ALL
SELECT matches.winner AS player, matches.loser AS opponent
FROM matches;