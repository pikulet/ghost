import ghost
import unittest

class TestGhostEngine(unittest.TestCase):

    def setUp(self):
        self.GE = ghost.GhostEngine()
        self.VALID_PLAYERS = ['joyce', 'mf', 'tb', 'avian', 'jamz']
        self.VALID_TW = 'egg'
        self.VALID_FW = 'fry'

    def __create_game(self, ge, gid, host, players, town_word, fool_word):
        ge.add_game(gid, host) 

        for p in players:
            ge.register_player(gid, p)

        ge.start_game(gid)
        ge.set_param_town_word(host, town_word)
        ge.set_param_fool_word(host, fool_word)

    def test_create_game(self):
        ge = ghost.GhostEngine()

        gid = 1129837
        host = 'jermyn'

        self.__create_game(ge, gid, host, self.VALID_PLAYERS, self.VALID_TW,
                           self.VALID_FW)

        roles = ge.get_player_roles(gid)
        # TODO: assert

        players = self.VALID_PLAYERS.copy()

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
                ge.make_guess(gid, lynched, self.VALID_TW)
                print(state)
                self.assertTrue(state == ghost.States.WINNER_GHOST)


    def test_invalid_player_count(self):
        ge = ghost.GhostEngine()
        self.__create_game(ge, 1309128, 'asf', ['b', 'c'], 'cat', 'dog')
        self.__create_game(ge, 1309129, 'asd', 
                           ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'], 'cat', 'dog')

    def test_invalid_host_joins(self):
        ge = ghost.GhostEngine()
        host = 'cake'
        self.__create_game(ge, 123213, host, [host, 'b', 'c'], self.VALID_TW,
                           self.VALID_FW)

if __name__ == '__main__':
    unittest.main()
