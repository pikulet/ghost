from enum import Enum
from collections import deque

class GhostGame:

    class GhostGameException(Exception):
        pass

    # parameters for validation
    __MIN_PLAYERS = 3
    __DEFAULT_NUM_PLAYERS = 7
    __MAX_PLAYERS = 10

    __MIN_WORD_LENGTH = 3
    __MAX_WORD_LENGTH = 15

    class __Roles(Enum):
        GHOST   = 'Ghost'
        TOWN    = 'Town'
        FOOL    = 'Fool'

    # defines number of each role given number of players
    __ROLE_SETS = {
        3   :   (1, 2, 0),
        4   :   (1, 3, 0),
        5   :   (2, 3, 0),
        6   :   (2, 3, 1),
        7   :   (2, 3, 2),
        8   :   (2, 4, 2),
        9   :   (3, 4, 2),
        10  :   (3, 4, 3)
    }

    # fsm
    class __States(Enum):
        SET_PARAMS          = 'Setting parameters'
        REGISTER_PLAYERS    = 'Registering players'
        GHOST_VOTE_ROUND    = 'Ghost Vote Round'
        WORD_ROUND          = 'Word Round'
        VOTE_ROUND          = 'Vote Round'
        COMPLETE            = 'Complete'

    def __init__(self):
        self.__game_state = GhostGame.__States.SET_PARAMS
        self.__num_players = 0
        self.__town_word = None
        self.__fool_word = None
        self.__all_players = set()
        self.__alive_players = set()

        self.__players_to_id = dict() # map from username to internal id
        self.__id_to_players = deque()
        self.__roles = list()
        self.__clues = list()
        self.__votes = list()

    def __check_game_state(self, expected_state: __States) -> None:
        if self.__game_state != expected_state:
            raise GhostGameException(
                'Invalid game state! Expected game to be in %s stage'
                + ' but got %s stage' % (expected_state, self.game_state))

    def set_param_num_players(self, value: int) -> None:
        self.__check_game_state(GhostGame.__States.SET_PARAMS)
        if value < GhostGame.__MIN_PLAYERS or value > GhostGame.__MAX_PLAYERS:
            raise GhostGameException(
                'The game can only have 3 to 10 players')
        self.__num_players = value

    def set_param_town_word(self, value: str) -> None:
        self.__check_game_state(GhostGame.__States.SET_PARAMS)
        if len(value) < GhostGame.__MIN_WORD_LENGTH:
            raise GhostGameException(
                'The word cannot be too short (%d char min)' %
                __MIN_WORD_LENGTH)
        elif len(value) > GhostGame.__MAX_WORD_LENGTH:
            raise GhostGameException(
                'The word cannot be too long (%d char max)' %
                __MAX_WORD_LENGTH)

        self.__town_word = value

    def set_param_fool_word(self, value: str) -> None:
        self.__check_game_state(GhostGame.__States.SET_PARAMS)
        if len(value) != len(self.__town_word):
            raise GhostGameException(
                'The fool word and town word must have the same length')
        self.__fool_word = value

    def confirm_params_register_players(self) -> None:
        self.__check_game_state(GhostGame.__States.SET_PARAMS)

        # set default number of players
        self.set_param_num_players(GhostGame.__DEFAULT_NUM_PLAYERS)

        if self.__town_word is None or self.__fool_word is None:
            raise GhostGameException(
                'At least one of the words have not been set')

        self.__id_to_players = [None] * self.__num_players
        self.__game_state = GhostGame.__States.REGISTER_PLAYERS

    def register_player(self, username: str) -> None:
        self.__check_game_state(GhostGame.__States.REGISTER_PLAYERS)

        if username in self.__players_to_id:
            raise GhostGameException(
                'Player %s is already registered' % username)

        current_num_players = len(self.__all_players)
        if current_num_players >= self.__num_players:
            raise GhostGameException(
                'Player capacity of %d exceeded' % self.__num_players)

        player_id = current_num_players
        self.__players_to_id[username] = player_id 
        self.__id_to_players.append(username)
        self.__all_players.add(player_id)

    def is_max_player_cap_reached(self) -> bool:
        self.__check_game_state(GhostGame.__States.REGISTER_PlAYERS)
        return len(self.__all_players) >= self.__num_players

    def confirm_register_start_game(self) -> dict:
        self.__check_game_state(GhostGame.__States.REGISTER_PlAYERS)
        if len(self.__all_players) < GhostGame.__MIN_NUM_PLAYERS:
            raise GhostGameException(
                'Not enough players have joined (min %d)' %
                GhostGame.__MIN_NUM_PLAYERS)

        # update final player count
        self.__num_players = len(self.__all_players)
        self.__all_players = self.__all_players.copy()

        # initialise states
        self.__roles = [None] * self.__num_players
        self.__clues = [None] * self.__num_players
        self.__votes = [None] * self.__num_players
        self.__assign_player_roles()

        return self.get_player_roles()

    def __assign_player_roles(self) -> dict:
        n_town, n_ghost, n_fool = GhostGame.__ROLE_SETS[self.__num_players]

        return dict()
