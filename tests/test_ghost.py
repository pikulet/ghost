import ghost

import sys
import unittest
import logging

VALID_PLAYERS = ['joyce', 'mf', 'tb', 'avian', 'jamz']
VALID_TW = 'egg'
VALID_FW = 'fry'

class LoggedTestCase(unittest.TestCase):
    __metaclass__ = LogThisTestCase
    logger = logging.getLogger("unittestLogger")
    logger.setLevel(logging.DEBUG) # or whatever you prefer

class LogThisTestCase(type):
    def __new__(cls, name, bases, dct):
        # if the TestCase already provides setUp, wrap it
        if 'setUp' in dct:
            setUp = dct['setUp']
        else:
            setUp = lambda self: None
            print "creating setUp..."

        def wrappedSetUp(self):
            # for hdlr in self.logger.handlers:
            #    self.logger.removeHandler(hdlr)
            self.hdlr = logging.StreamHandler(sys.stdout)
            self.logger.addHandler(self.hdlr)
            setUp(self)
        dct['setUp'] = wrappedSetUp

        # same for tearDown
        if 'tearDown' in dct:
            tearDown = dct['tearDown']
        else:
            tearDown = lambda self: None

        def wrappedTearDown(self):
            tearDown(self)
            self.logger.removeHandler(self.hdlr)
        dct['tearDown'] = wrappedTearDown

        # return the class instance with the replaced setUp/tearDown
        return type.__new__(cls, name, bases, dct)

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

class TestValidGame(LoggedTestCase):

    def test_create_game(self):
        ge = ghost.GhostEngine()

        gid = 1129837
        host = 'jermyn'

        create_game(ge, gid, host, VALID_PLAYERS, VALID_TW, VALID_FW)

        roles = ge.get_player_roles(gid)
        # TODO: assert

        players = VALID_PLAYERS.copy()

        for _ in range(len(players)):
            p = ge.suggest_next_clue_giver(gid)
            is_clue_complete = ge.set_clue(gid, p, 'example clue ' + p)

        # Example
        clues = ge.get_all_clues(gid)

        state = ge.get_game_state(gid)
        while state == ghost.States.VOTE_ROUND: 
            for p in players:
                is_vote_complete, lynched = ge.set_vote(gid, p, players[0])
            self.assertTrue(lynched == players[0])
            players.pop(0)

            state = ge.get_game_state(gid)
            if state == ghost.States.GUESS_ROUND:
                ge.make_guess(gid, lynched, VALID_TW)
                print(state)
                self.assertTrue(state == ghost.States.WINNER_GHOST)


if __name__ == '__main__':
    unittest.main()
