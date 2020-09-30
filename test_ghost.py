from ghost.ghost import Ghost
import unittest


class TestGhost(unittest.TestCase):

    def test_param_example(self) -> Ghost:
        gg = Ghost()
        gg.set_param_num_players(3)
        gg.set_param_town_word('egg')
        gg.set_param_fool_word('pea')
        gg.end_params_phase()
        return gg

    def test_register_example(self) -> Ghost:
        gg = self.test_param_example()
        gg.register_player('bacon')
        gg.register_player('peanut')
        self.assertFalse(gg.is_max_player_cap_reached())
        gg.register_player('tomato')
        self.assertTrue(gg.is_max_player_cap_reached())
        gg.end_register_phase()
        return gg

    def test_ghost_vote_example(self) -> Ghost:
        gg = self.test_register_example()
        gg.set_ghost_vote('bacon', 'peanut')
        gg.set_ghost_vote('peanut', 'tomato')
        gg.set_ghost_vote('tomato', 'bacon')
        gg.end_ghost_vote_phase()
        return gg

if __name__ == '__main__':
    unittest.main()
