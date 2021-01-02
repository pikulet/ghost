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

        for _ in range(len(players)):
            p = self.ge.suggest_next_clue_giver(gid)
            is_clue_complete = self.ge.set_clue(gid, p, 'example clue ' + p)

        # Example
        clues = self.ge.get_all_clues(gid)

        state = self.ge.get_game_state(gid)
        while state == ghost.States.VOTE_ROUND: 
            for p in players:
                is_vote_complete, lynched = self.ge.set_vote(gid, p, players[0])
            self.assertTrue(lynched == players[0])
            players.pop(0)

            state = self.ge.get_game_state(gid)
            if state == ghost.States.GUESS_ROUND:
                self.ge.make_guess(gid, lynched, town_word)
                self.assertTrue(state == ghost.States.WINNER_GHOST)

if __name__ == '__main__':
    unittest.main()
