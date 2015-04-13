#!/usr/bin/env python
#
# Test cases for tournament.py

import psycopg2
from tournament import *

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testRegisterTournament():
    registerTournament()
    print "6. Tournaments can be registered"


def testDeleteTournament():
    connect()
    c.execute('SELECT * FROM tournaments;')
    tournament = fetchone()[0]
    deleteTournament(tournament)
    print "7. Tournaments and matches played within it can be deleted"


def testRegisterTournamentPlayer():
    deleteMatches()
    deletePlayers()
    registerTournament()
    registerPlayer("Rob Walker")
    registerPlayer("Sam Man")
    connect()
    c.execute('SELECT * FROM tournaments;')
    tournament = fetchone()[0]
    c.execute('SELECT id FROM players;')
    players = fetchall()
    [id1, id2] = [row[0] for row in players]
    registerTournamentPlayer(id1, tournament)
    registerTournamentPlayer(id2, tournament)
    print "8. Players can be registered in a tournament"


def testReportTournamentWinner():
    connect()
    c.execute('SELECT * FROM tournaments')
    tournament = fetchone()[0]
    c.execute('SELECT id FROM tournament_participants;')
    winner = fetchone()[0]
    reportTournamentWinner(winner, tournament)
    print "9. Tournament winners can be reported"


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    connect()
    c.execute('SELECT * FROM tournaments;')
    tournament = fetchone()[0]
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    c.execute('SELECT id FROM players;')
    players = fetchall()
    [id1, id2] = [row[0] for row in players]
    registerTournamentPlayer(id1, tournament)
    registerTournamentPlayer(id2, tournament)
    standings = playerStandings(tournament)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "10. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings(tournament)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    registerTournamentPlayer(id1, tournament)
    registerTournamentPlayer(id2, tournament)
    registerTournamentPlayer(id3, tournament)
    registerTournamentPlayer(id4, tournament)
    reportMatch(id1, id2, id1, tournament)
    reportMatch(id3, id4, tie, tournament)
    standings = playerStandings(tournament)
    for (i, n, m, w, t, p, t) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in id1 and w != 1 and p != 3:
            raise ValueError("Each match winner should have one win recorded with 3 points.")
        if i in (id3, id4) and w!= 0 p != 1:
            raise ValueError("Each drawing player should have 0 wins with 1 point.")
        elif i in (id2, id3, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "11. After a match, players have updated standings."


def testPairings(tournament):
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings(tournament)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    registerTournamentPlayer(id1, tournament)
    registerTournamentPlayer(id2, tournament)
    registerTournamentPlayer(id3, tournament)
    registerTournamentPlayer(id4, tournament)
    reportMatch(id1, id2, id1, tournament)
    reportMatch(id3, id4, id3, tournament)
    pairings = swissPairings(tournament)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    print "12. After one match, players with adjacent or equal wins are paired."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testRegisterTournament()
    testDeleteTournament():
    testRegisterTournamentPlayer()
    testReportTournamentWinner():
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success!  All tests pass!"


