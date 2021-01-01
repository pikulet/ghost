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
        print(roles)

        while True:
            p = self.ge.get_next_clue_giver(gid)
            if not p:
                break
            
            self.ge.set_clue(gid, p, 'example clue ' + p)

        clues = self.ge.get_all_clues(gid)
        print(clues)

        for p in players:
            self.ge.set_vote(gid, p, players[2])

        to_lynch = self.ge.get_vote_result(gid)
        self.assertTrue(to_lynch == players[2])

class TestGhost(unittest.TestCase):

    def test_valid_game(self):
        g = ghost.Ghost()

if __name__ == '__main__':
    unittest.main()
