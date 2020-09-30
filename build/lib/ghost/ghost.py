from enum import Enum
import random


class Player:

    def __init__(self):
        self.role = Ghost.Roles.TOWN
        self.clue = ''
        self.vote = ''
        self.ghost_vote = ''
        self.is_alive = True


class Ghost:

    class GhostException(Exception):
        pass

    # parameters for validation
    __MIN_NUM_PLAYERS = 3
    __DEFAULT_NUM_PLAYERS = 7
    __MAX_NUM_PLAYERS = 10

    __MIN_WORD_LENGTH = 3
    __MAX_WORD_LENGTH = 15

    class Roles(Enum):
        GHOST = 'Ghost'
        TOWN = 'Town'
        FOOL = 'Fool'

    # defines number of each role given number of players
    __ROLE_SETS = {
        3: (2, 1, 0),
        4: (3, 1, 0),
        5: (3, 2, 0),
        6: (3, 2, 1),
        7: (3, 2, 2),
        8: (4, 2, 2),
        9: (4, 3, 2),
        10: (4, 3, 3)
    }

    # fsm
    class __States(Enum):
        SET_PARAMS = 'Setting parameters'
        REGISTER_PLAYERS = 'Registering players'
        GHOST_VOTE_ROUND = 'Ghost Vote Round'
        WORD_ROUND = 'Word Round'
        VOTE_ROUND = 'Vote Round'
        COMPLETE = 'Complete'

    def __init__(self):
        self.__game_state = Ghost.__States.SET_PARAMS
        self.__num_players = 0
        self.__town_word = None
        self.__fool_word = None

        self.__player_info = dict() # username --> player
        self.__player_order = None

    def __check_game_state(self, expected_state: __States) -> None:
        if self.__game_state is not expected_state:
            raise Ghost.GhostException(
                'Invalid game state! Expected game to be in %s stage but got '
                '%s stage' % (expected_state, self.__game_state)
            )

    ''' PHASE: SET PARAM '''

    def set_param_num_players(self, value: int) -> None:
        self.__check_game_state(Ghost.__States.SET_PARAMS)
        if value < Ghost.__MIN_NUM_PLAYERS or \
                value > Ghost.__MAX_NUM_PLAYERS:
            raise Ghost.GhostException(
                'The game can only have 3 to 10 players'
            )
        self.__num_players = value

    def set_param_town_word(self, value: str) -> None:
        self.__check_game_state(Ghost.__States.SET_PARAMS)
        if not value.isalpha():
            raise Ghost.GhostException(
                'The word must be alphabetic (no numbers or symbols)'
            )
        if len(value) < Ghost.__MIN_WORD_LENGTH:
            raise Ghost.GhostException(
                'The word cannot be too short (%d char min)' %
                Ghost.__MIN_WORD_LENGTH
            )
        if len(value) > Ghost.__MAX_WORD_LENGTH:
            raise Ghost.GhostException(
                'The word cannot be too long (%d char max)' %
                Ghost.__MAX_WORD_LENGTH
            )

        self.__town_word = value

    def set_param_fool_word(self, value: str) -> None:
        self.__check_game_state(Ghost.__States.SET_PARAMS)
        if not value.isalpha():
            raise Ghost.GhostException(
                'The word must be alphabetic (no numbers or symbols)'
            )
        if len(value) != len(self.__town_word):
            raise Ghost.GhostException(
                'The fool word and town word must have the same length. '
                'Set the town word first.'
            )
        if value == self.__town_word:
            raise Ghost.GhostException(
                'The fool word cannot be exactly the same as the town word.'
            )
        self.__fool_word = value

    def confirm_params_start_register(self) -> None:
        self.__check_game_state(Ghost.__States.SET_PARAMS)

        # check other parameters
        if self.__town_word is None:
            raise Ghost.GhostException('Town word has not been set')
        if self.__fool_word is None:
            raise Ghost.GhostException('Fool word has not been set')

        # set default number of players
        if self.__num_players == 0:
            self.set_param_num_players(Ghost.__DEFAULT_NUM_PLAYERS)

        self.__game_state = Ghost.__States.REGISTER_PLAYERS

    ''' PHASE: REGISTER PLAYERS '''

    def __check_user_in_game(self, username: str) -> None:
        if username not in self.__player_info:
            raise Ghost.GhostException(
                'User @%s is not currently playing' % username
            )

    def register_player(self, username: str) -> None:
        self.__check_game_state(Ghost.__States.REGISTER_PLAYERS)

        if username in self.__player_info:
            raise Ghost.GhostException(
                'Player %s is already registered' % username)

        if len(self.__player_info) >= self.__num_players:
            raise Ghost.GhostException(
                'Player capacity of %d exceeded' % self.__num_players)

        self.__player_info[username] = Player()

    def is_max_player_cap_reached(self) -> bool:
        self.__check_game_state(Ghost.__States.REGISTER_PLAYERS)
        return len(self.__player_info) >= self.__num_players

    def confirm_register_start_game(self) -> dict:
        self.__check_game_state(Ghost.__States.REGISTER_PLAYERS)
        if len(self.__player_info) < Ghost.__MIN_NUM_PLAYERS:
            raise Ghost.GhostException(
                'Not enough players have joined (min %d)' %
                Ghost.__MIN_NUM_PLAYERS
            )

        # update final player count
        self.__num_players = len(self.__player_info)

        # initialise states
        roles = self.__assign_player_roles()
        role_index = 0
        for username in self.__player_info:
            self.__player_info[username].role = roles[role_index]

        self.__game_state = Ghost.__States.GHOST_VOTE_ROUND
        return self.get_player_roles()

    def __assign_player_roles(self) -> list:
        n_town, n_ghost, n_fool = Ghost.__ROLE_SETS[self.__num_players]
        roles = [Ghost.Roles.TOWN] * n_town + \
                       [Ghost.Roles.GHOST] * n_ghost + \
                       [Ghost.Roles.FOOL] * n_fool

        random.shuffle(roles)
        return roles

    def __get_role(self, username: str) -> Roles:
        self.__check_user_in_game(username)
        return self.__player_info[username].role

    def get_player_roles(self) -> dict:
        result = dict()

        for username, player in self.__player_info.items():
            result[username] = player.role

        return result

    ''' PHASE: GHOST VOTING '''

    def vote_to_start(self, username: str, ghost_vote: str) -> None:
        self.__check_game_state(Ghost.__States.GHOST_VOTE_ROUND)
        self.__check_user_in_game(username)
        self.__check_user_in_game(ghost_vote)

        if self.__get_role(username) is not Ghost.Roles.GHOST:
            raise Ghost.GhostException(
                'User @%s is not Ghost, and cannot vote for who to start'
            )

        self.__player_info[username].ghost_vote = ghost_vote

        # set clue, is clue complete
        # set vote, is vote complete
        # set guess
        # is game complete
