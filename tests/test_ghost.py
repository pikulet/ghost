import ghost
import unittest

class TestGhostEngine(unittest.TestCase):

    def setUp(self):
        self.ge = ghost.GhostEngine()

    def __create_game(self, gid, host, players, town_word, fool_word):
        self.ge.add_game(gid, host) 

        for p in players:
            self.ge.register_player(gid, p)

        self.ge.start_game(gid)
        self.ge.set_param_town_word(host, town_word)
        self.ge.set_param_fool_word(host, fool_word)

    def test_create_game(self):

        gid = 1129837
        host = 'jermyn'
        players = ['joyce', 'mf', 'tb', 'avian', 'jamz']
        town_word = 'egg'
        fool_word = 'fry'

        self.__create_game(gid, host, players, town_word, fool_word)

        roles = self.ge.get_player_roles(gid)
        # TODO: assert

        is_game_complete = False
        while not is_game_complete:
            is_clue_complete = False
            while not is_clue_complete:
                p = self.ge.suggest_next_clue_giver(gid)
                is_clue_complete = self.ge.set_clue(gid, p, 'example clue ' + p)

            # Example
            clues = self.ge.get_all_clues(gid)

            is_vote_complete = False
            while not is_vote_complete:
                for p in players:
                    is_vote_complete, lynched, state = self.ge.set_vote(gid, p, players[0])

                self.assertTrue(lynched == players[0])
                players.pop(0)

            if state == ghost.States.GUESS_ROUND:
                self.ge.make_guess(gid, lynched, fool_word)

            if state != ghost.States.CLUE_ROUND:
                break

if __name__ == '__main__':
    unittest.main()
