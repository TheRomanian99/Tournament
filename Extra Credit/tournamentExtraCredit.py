#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database and creates a cursor.
    Returns a database connection and a cursor.
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    return db, c


def deleteMatches():
    """Remove all the match records from the database."""
    connect()
    c.execute('DELETE FROM matches;')
    db.commit()
    db.close

def deletePlayers():
    """Remove all the player records from the database."""
    connect()
    c.execute('DELETE FROM players;')
    db.commit()
    db.close

def countPlayers():
    """Returns the number of players currently registered."""
    connect()
    c.execute('SELECT COUNT(*) FROM players;')
    count = c.fetchall()
    return count[0][0]
    db.close

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    connect()
    query = 'INSERT INTO players (name) VALUES (%s);'
    data = (bleach.clean(name),)
    c.execute(query, data)
    db.commit()
    db.close

def registerTournament():
    """Adds a tournament to the tournament database.

    The database assigns a unique serial id number for the tournament.
    """
    connect()
    c.execute('INSERT INTO tournaments DEFAULT VALUES;')
    db.commit()
    db.close

def deleteTournament(tournament):
    """Delets a tournament along with the matches played.

    Args:
        tournament: the id number of the tournament
    """
    connect()
    query = 'DELETE FROM tournaments WHERE id = %s;'
    data = (bleach.clean(tournament),)
    c.execute(query, data)
    db.commit()
    db.close

def registerTournamentPlayer(player, tournament):
    """Adds a player to a tournament.

    Args:
        player: the id number of the player
        tournament: the id number of the tournament
    """
    connect()
    query = 'INSERT INTO tournament_participants (player_id, tournament_id) VALUES (%s, %s);'
    data = (bleach.clean(player), bleach.clean(tournament),)
    c.execute(query, data)
    db.commit()
    db.close

def reportTournamentWinner(winner, tournament):

    """Records the winner of a single tournament.

    Args:
      winner: the id number of the winning player
      tournament: the id number of the tournament
    """
    connect()
    query = 'UPDATE tournaments SET winner = %s WHERE id = %s;'
    data = (bleach.clean(winner), bleach.clean(tournament),)
    c.execute(query, data)
    db.commit()
    db.close

def playerStandings(tournament):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
      tournament: the id number of the tournament being held
      
    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    connect()
    query = 'SELECT id, name, wins, matches FROM standings WHERE tournament_id = %s;'
    data = (bleach.clean(tournament),)
    c.execute(query, data)
    rows = c.fetchall()
    return rows
    db.close

def reportMatch(id1, id2, result, tournament):
    """Records the outcome of a single match between two players.

    Args:
      player1:  the id number of the 1st player
      player2:  the id number of the 2nd player
      result: the id number of the winning player (or 'tie' if game ended in a tie)
      tournament: the id number of the tournament being held
    """
    connect()
    if str(result).lower() == 'tie':
        query = "INSERT INTO matches (id1, id2, tournament_id) VALUES (%s, %s, %s);"
        data = (bleach.clean(id1), bleach.clean(id2), bleach.clean(tournament),)
        c.execute(query, data)
    else:
        query = "INSERT INTO matches (id1, id2, winner, tournament_id) VALUES (%s, %s, %s, %s);"
        data = (bleach.clean(id1), bleach.clean(id2), bleach.clean(result), bleach.clean(tournament),)
        c.execute(query, data)
    db.commit()
    db.close
 
def swissPairings(tournament):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
      tournament: the id number of the tournament being held

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    tournament = bleach.clean(tournament)

    def getIds(tournament):
        """Returns a list of the ids taking part in a tournament in the order they appear in the
        standings table

        Args:
            tournament: the id number of the tournament taking place
        """
        connect()
        query = 'SELECT id FROM standings WHERE tournament_id = %s;'
        data = (tournament,)
        c.execute(query, data)
        rows = c.fetchall()
        ids = []
        for row in rows:
            ids.append(row[0])
        return ids
        db.close

    def getWins(player, tournament):
        """Returns the number of wins a player has in a tournament

        Args:
            player: the id number of the player
            tournament: the id number of the tournament taking place
        """
        connect()
        query = 'SELECT wins FROM standings WHERE id = %s AND tournament_id = %s;'
        data = (player, tournament,)
        c.execute(query, data)
        row = c.fetchone()
        return row[0]
        db.close

    def getPossiblePairs(wins, winDiff, tournament):
        """Returns a list of the ids taking part in a tournament that have a certain number of wins difference

        Args:
            wins: the number of wins a player has
            winDiff: the difference of wins in relation to the player
            tournament: the id number of the tournament taking place
        """
        connect()
        query = 'SELECT id FROM standings WHERE wins = %s AND tournament_id = %s;'
        data = (wins + winDiff, tournament,)
        c.execute(query, data)
        rows = c.fetchall()
        return rows
        db.close
    
    def getPlayedOpponents(tournament):
        """Returns a dictionary of the ids taking part in a tournament and the opponents they have played

        Args:
            tournament: the id number of the tournament taking place
        """
        connect()
        playedOpponents = {}
        ids = getIds(tournament)
        for x in ids:
            query = 'SELECT opponent FROM opponents WHERE player = %s AND tournament_id = %s;'
            data = (x, tournament,)
            c.execute(query, data)
            rows = c.fetchall()
            playedOpponents[x] = [row[0] for row in rows]
        return playedOpponents
        db.close

    def getPlayerNames(tournament):
        """Returns a dictionary of the ids and names taking part in a tournament

        Args:
            tournament: the id number of the tournament taking place
        """
        connect()
        players = {}
        query = 'SELECT id, name FROM standings WHERE tournament_id = %s;'
        data = (tournament,)
        c.execute(query, data)
        rows = c.fetchall()
        for row in rows:
            players[row[0]] = row[1]
        return players
        db.close
        
    ids = getIds(tournament)

    #adds a 'bye' to the tournament is there is an uneven number of players
    if len(ids) % 2 != 0:
        connect()
        c.execute('SELECT id FROM players WHERE id = 0;')
        rows = c.fetchall()
        #registers 'bye' as a player with id of 0 if it doesn't already exist in the players table
        #and then registers it in the tournament, else it just registers it in the tournament
        if len(rows) == 0:
            c.execute('INSERT INTO players VALUES (0, \'bye\');')
            query = 'INSERT INTO tournament_participants (player_id, tournament_id) VALUES (0, %s);'
            data = (tournament,)
            c.execute(query, data)
            db.commit()
            ids = getIds(tournament)
        else:
            query = 'INSERT INTO tournament_participants (player_id, tournament_id) VALUES (0, %s);'
            data = (tournament,)
            c.execute(query, data)
            db.commit()
            ids = getIds(tournament)
        db.close

    
    
    possiblePairings = {}
    possibleWinDiff = [0, 1, -1]
    playedOpponents = getPlayedOpponents(tournament)

    #pair each id to players the have not played against
    for x in ids:
        wins = getWins(x, tournament)
        possiblePairings[x] = []
        #select opponents with equal or adjacent wins
        for winDiff in possibleWinDiff:
            for row in getPossiblePairs(wins, winDiff, tournament):
                #append the ids of the opponents that the player has not played yet
                if row[0] != x and row[0] not in playedOpponents[x]:
                    possiblePairings[x].append(row[0])
            
    def getPairs(player, n):
        """Appends a tuple of a new pair to the pairs list

        Args:
            player: the id number of a player
            n: the place of the id in the possiblePairings dictionary where player is the key
        """
        while [a for a in pairs if possiblePairings[player][n] in a]:
            #if id 'n' is already paired up in possiblePairings then it loops to the next one
            n +=1
        else:
            pairs.append((player, players[player], possiblePairings[player][n], players[possiblePairings[player][n]]))

    pairs = []
    count = 0
    count2 = 2
    players = getPlayerNames(tournament)
    n1 = 0
    n2 = len(ids)-1

    #pair every id against another player
    while count < len(ids):
        n = 0
        #make the loop pair players alternating between the highest ranked non paired player and the lowest
        if count2 % 2 == 0:
            #cycle through each id starting from the first one
            x = ids[n1]
            #if the id is not already paired the getPairs method is called
            if not [pl for pl in pairs if x in pl]:
                getPairs(x,n)
                count2 += 1
            n1 += 1
        else:
            #cycle through each id starting from the last one
            x = ids[n2]
            #if the id is not already paired the getPairs method is called
            if not [pl for pl in pairs if x in pl]:
                getPairs(x,n)
                count2 += 1
            n2 -= 1
        count += 1
    return pairs
    db.close

