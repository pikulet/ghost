import ghost

import sys
import unittest
import logging

VALID_PLAYERS = ['joyce', 'mf', 'tb', 'avian', 'jamz']
VALID_TW = 'egg'
VALID_FW = 'fry'

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)

def create_game(ge, gid, host, players, town_word, fool_word):
    ge.add_game(gid, host) 

    for p in players:
        ge.register_player(gid, p)

    ge.start_game(gid)
    ge.set_param_town_word(host, town_word)
    ge.set_param_fool_word(host, fool_word)

class TestInvalidCreate(unittest.TestCase):

    def test_invalid_player_count(self):
        ge = ghost.GhostEngine()
        create_game(ge, 1309128, 'asf', ['b', 'c'], 'cat', 'dog')
        create_game(ge, 1309129, 'asd', 
                           ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'], 'cat', 'dog')

    def test_invalid_host_joins(self):
        ge = ghost.GhostEngine()
        host = 'cake'
        create_game(ge, 123213, host, [host, 'b', 'c'], VALID_TW, VALID_FW)

class TestValidGame(unittest.TestCase):

    def test_create_game(self):
        logger.addHandler(stream_handler)

        ge = ghost.GhostEngine()

        gid = 1129837
        host = 'jermyn'

        create_game(ge, gid, host, VALID_PLAYERS, VALID_TW, VALID_FW)

        roles = ge.get_player_roles(gid)
        # TODO: assert

        players = VALID_PLAYERS.copy()

        for p in ge.get_player_order(gid):
            is_clue_complete = ge.set_clue(gid, p, 'example clue ' + p)

        # Example
        clues = ge.get_all_clues(gid)

        state = ge.get_game_state(gid)
        while state == ghost.States.VOTE_ROUND: 
            for p in players:
                i, j, lynched = ge.set_vote(gid, p, players[0])

            print(i, j, lynched, players[0])
            self.assertTrue(lynched == players[0])
            players.pop(0)

            state = ge.get_game_state(gid)
            if state == ghost.States.GUESS_ROUND:
                ge.make_guess(gid, lynched, VALID_TW)
                print(state)
                self.assertTrue(state == ghost.States.WINNER_GHOST)

            print(state)

        logger.removeHandler(stream_handler)

if __name__ == '__main__':
    unittest.main()
