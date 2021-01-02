from enum import Enum
from collections import deque, defaultdict
import random

import logging

class Player:

    def __init__(self):
        self.role = Ghost.Roles.TOWN
        self.info = None

class Ghost:

    class GhostException(Exception):
        pass

    # parameters for validation
    MIN_NUM_PLAYERS = 3
    MAX_NUM_PLAYERS = 10

    MIN_WORD_LENGTH = 3
    MAX_WORD_LENGTH = 15

    __EMPTY_VOTE = ''

    class Roles(Enum):
        GHOST = 'Ghost'
        TOWN = 'Town'
        FOOL = 'Fool'

    # defines number of each role given number of players
    # TOWN, GHOST, FOOL
    __ROLE_SETS = {
        3: (2, 1, 0),
        4: (2, 1, 1),
        5: (3, 1, 1),
        6: (3, 2, 1),
        7: (3, 2, 2),
        8: (4, 2, 2),
        9: (4, 3, 2),
        10: (4, 3, 3)
    }

    # fsm
    class States(Enum):
        REGISTER_PLAYERS = 'Register Players'
        SET_PARAMS = 'Set Parameters' 
        CLUE_ROUND = 'Clue Round'
        VOTE_ROUND = 'Vote Round' 
        GUESS_ROUND = 'Guess Round'
        WINNER_GHOST = 'Ghosts won'
        WINNER_TOWN = 'Town won'

    def __init__(self):
        self.__game_state = Ghost.States.REGISTER_PLAYERS
        self.__town_word = None
        self.__fool_word = None

        self.__player_info = dict()  # username --> player
        self.__unvoted_players = set()

        self.__last_lynched = None

    def __check_game_state(self, expected_state: States) -> None:
        if self.__game_state != expected_state:
            raise Ghost.GhostException(
                'Invalid game state! Expected game to be in %s stage but got '
                '%s state' % (expected_state, self.__game_state)
            )

    ''' PHASE: REGISTER PLAYERS '''

    def register_player(self, username: str) -> int:
        logging.info('Registering player @%s' % username)
        self.__check_game_state(Ghost.States.REGISTER_PLAYERS)

        if username in self.__player_info:
            raise Ghost.GhostException(
                'Player %s is already registered' % username
            )

        if len(self.__player_info) >= Ghost.MAX_NUM_PLAYERS:
            # TODO: Automatically start the game
            raise Ghost.GhostException(
                'Player capacity of %d exceeded. Please start the game.' % Ghost.MAX_NUM_PLAYERS
            )

        self.__player_info[username] = Player()
        return len(self.__player_info)

    def start_game(self) -> int:
        logging.info('Starting game')
        self.__check_game_state(Ghost.States.REGISTER_PLAYERS)

        if len(self.__player_info) < Ghost.MIN_NUM_PLAYERS:
            raise Ghost.GhostException(
                'Not enough players have joined (min %d needed)' %
                Ghost.MIN_NUM_PLAYERS
            )

        self.__allocate_roles()
        self.__game_state = Ghost.States.SET_PARAMS

    def __allocate_roles(self) -> None:
        # get the roles in this game
        n_town, n_ghost, n_fool = Ghost.__ROLE_SETS[len(self.__player_info)]
        roles = [Ghost.Roles.TOWN] * n_town + \
            [Ghost.Roles.GHOST] * n_ghost + \
            [Ghost.Roles.FOOL] * n_fool

        random.shuffle(roles)
        role_index = 0

        # assign roles to players
        for username in self.__player_info:
            self.__player_info[username].role = roles[role_index]
            role_index += 1

    ''' PHASE: SET PARAMS '''

    def set_param_town_word(self, value: str) -> None:
        logging.info('Setting town word: %s' % value)
        self.__check_game_state(Ghost.States.SET_PARAMS)

        if not value.isalpha():
            raise Ghost.GhostException(
                'The word must be alphabetic (no numbers or symbols)'
            )

        if len(value) < Ghost.MIN_WORD_LENGTH:
            raise Ghost.GhostException(
                'The word cannot be too short (%d char min)' %
                Ghost.MIN_WORD_LENGTH
            )

        if len(value) > Ghost.MAX_WORD_LENGTH:
            raise Ghost.GhostException(
                'The word cannot be too long (%d char max)' %
                Ghost.MAX_WORD_LENGTH
            )

        self.__town_word = value.lower()

    def set_param_fool_word(self, value: str) -> None:
        logging.info('Setting fool word: %s' % value)
        self.__check_game_state(Ghost.States.SET_PARAMS)

        if self.__town_word is None:
            raise Ghost.GhostException(
                'Set the town word first'
            )

        if not value.isalpha():
            raise Ghost.GhostException(
                'The word must be alphabetic (no numbers or symbols)'
            )
        
        if len(value) != len(self.__town_word):
            raise Ghost.GhostException(
                'The fool word and town word must have the same length'
            )

        if value == self.__town_word:
            raise Ghost.GhostException(
                'The fool word cannot be exactly the same as the town word'
            )

        self.__fool_word = value.lower()
        self.__start_clue_phase()

    ''' HELPER METHODS '''

    def get_game_state(self) -> States:
        return self.__game_state

    # TODO: remove
    def get_num_players(self) -> int:
        return len(self.__player_info)

    def get_player_roles(self) -> dict:
        if self.__game_state == Ghost.States.REGISTER_PLAYERS:
            raise Ghost.GhostException(
                'Still registering players. Roles have not been allocated'
            )

        result = dict()

        for username, player in self.__player_info.items():
            result[username] = player.role

        return result

    def get_words(self) -> (str, str):
        return self.__town_word, self.__fool_word

    def __is_ghost(self, username: str) -> bool:
        return self.__player_info[username].role == Ghost.Roles.GHOST

    def __check_user_alive(self, username: str) -> None:
        if username not in self.__player_info:
            raise Ghost.GhostException(
                'User @%s is currently not playing' % username
            )

        if username not in self.__player_info:
            raise Ghost.GhostException(
                'User @%s is not alive' % username
            )

    def __reset_info(self) -> None:
        for player in self.__player_info.values():
            player.info = None

    ''' PHASE: CLUES '''

    def __start_clue_phase(self) -> None:
        self.__game_state = Ghost.States.CLUE_ROUND
        self.__reset_info()
        self.__unvoted_players = set(self.__player_info)

    def suggest_next_clue_giver(self) -> str:
        self.__check_game_state(Ghost.States.CLUE_ROUND)
        return random.sample(self.__unvoted_players, 1)[0]

    def set_clue(self, username: str, clue: str) -> bool:
        self.__check_game_state(Ghost.States.CLUE_ROUND)
        self.__check_user_alive(username)

        if self.__player_info[username].info is not None:
            raise Ghost.GhostException(
                'User @%s has already given a clue this round' % username
            )

        self.__player_info[username].clue = clue
        self.__unvoted_players.remove(username)

        # check if all players have given clues
        is_complete = len(self.__unvoted_players) == 0
        if is_complete:
            self.__start_vote_phase()

        return is_complete

    def get_all_clues(self) -> dict:
        self.__check_game_state(Ghost.States.VOTE_ROUND)

        result = dict()
        for username, player in self.__player_info.items():
            result[username] = player.clue

        return result

    ''' PHASE: VOTE '''

    def __start_vote_phase(self) -> None:
        self.__game_state = Ghost.States.VOTE_ROUND
        self.__reset_info()
        self.__unvoted_players = set(self.__player_info)
        self.__last_lycnhed = None

    def set_vote(self, username: str, vote: str) -> (bool, str):
        self.__check_game_state(Ghost.States.VOTE_ROUND)
        self.__check_user_alive(username)

        if vote != Ghost.__EMPTY_VOTE:
            self.__check_user_alive(vote)

        self.__player_info[username].info = vote
        self.__unvoted_players.discard(username)

        is_complete = len(self.__unvoted_players) == 0
        if is_complete:
            self.__process_vote()

        return is_complete, self.__last_lynched

    def __tally_votes(self, players) -> set:
        votes = defaultdict(lambda: 0)
        for username in players:
            v = self.__player_info[username].info
            votes[v] += 1

        if votes[Ghost.__EMPTY_VOTE] >= len(players) // 2:
            return set()

        max_votees = set()
        max_vote = 0
        for username, count in votes.items():
            if count > max_vote:
                max_votees = set()
                max_votees.add(username)
                max_vote = count
            elif count == max_vote:
                max_votees.add(username)

        return max_votees

    def __process_vote(self) -> None:
        tally = self.__tally_votes(self.__player_info)
        if len(tally) != 1:
            # voted for no one
            self.__start_clue_phase()
            return

        to_lynch = tally.pop()
        logging.info('Lynching player @%s' % to_lynch)
        self.__last_lynched = to_lynch

        if self.__is_ghost(to_lynch):
            self.__game_state = Ghost.States.GUESS_ROUND
        else:
            self.__kill_player(to_lynch)
            self.__start_clue_phase()

    def __kill_player(self, username: str) -> None:
        del self.__player_info[username]

        num_ghost_alive = len(list(filter(self.__is_ghost, self.__player_info)))
        if num_ghost_alive == 0:
            # killed all ghosts
            self.__game_state = Ghost.States.WINNER_TOWN
        elif num_ghost_alive >= len(self.__player_info) // 2:
            # ghosts got majority
            self.__game_state = Ghost.States.WINNER_GHOST

    ''' PHASE: GUESS '''

    def make_guess(self, username: str, guess: str) -> bool:
        self.__check_game_state(Ghost.States.GUESS_ROUND)

        if username != self.__last_lynched:
            # ignore irrelevant messages
            return

        logging.info('Player @%s has guessed: %s' % (username, guess))
        if guess.lower() == self.__town_word:
            self.__game_state = Ghost.States.WINNER_GHOST
            return True
        
        self.__kill_player(username)
        if self.__game_state != Ghost.States.WINNER_TOWN:
            self.__start_vote_phase()
        
        return False
