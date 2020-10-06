from ghost.ghost import Ghost
import unittest


class TestGhost(unittest.TestCase):

    def test_valid_game(self) :
        # param
        gg = Ghost()
        gg.set_param_num_players(3)
        gg.set_param_town_word('egg')
        gg.set_param_fool_word('pea')
        gg.end_params_phase()

        # register
        players = ['bacon', 'peanut', 'tomato']
        gg.register_player(players[0])
        gg.register_player(players[1])
        self.assertFalse(gg.is_max_player_cap_reached())
        gg.register_player(players[2])
        self.assertTrue(gg.is_max_player_cap_reached())
        gg.end_register_phase()


if __name__ == '__main__':
    unittest.main()
