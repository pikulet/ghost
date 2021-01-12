from enum import Enum
from collections import defaultdict
import random
import enchant

from typing import List

import logging

class Player:

    def __init__(self):
        self.role = Ghost.Roles.TOWN
        self.clue = None
        self.vote = None

class Ghost:

    DICTIONARY = enchant.Dict("en-US")

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
        INVALID = 'Invalid game'

    # Error messages
    ERR_INVALID_GAME_STATE = 'Invalid game state! Expected %s but got %s'
    ERR_PLAYER_ALREADY_REGISTERED = 'Player %s is already registered' 
    ERR_PLAYER_CAP_EXCEEDED = 'Player capacity of %d exceeded' % MAX_NUM_PLAYERS
    ERR_INSUFF_PLAYERS = 'Not enough players joined (min %d)' % MIN_NUM_PLAYERS
    ERR_WORD_NOT_ENGLISH = 'The word must be a valid English word'
    ERR_WORD_TOO_SHORT = 'The word cannot be too short (%d char min)' % MIN_WORD_LENGTH
    ERR_WORD_TOO_LONG = 'The word cannot be too long (%d char max)' % MAX_WORD_LENGTH
    ERR_TOWN_WORD_NOT_SET = 'Set the town word first'
    ERR_FOOL_WORD_DIFFERENT_LENGTH = 'The fool word and town word must have the same length'
    ERR_FOOL_WORD_DUPLICATE = 'The fool word cannot be exactly the same as the town word'
    ERR_ROLES_NOT_ALLOCATED = 'Still registering players. Roles have not been allocated'
    ERR_USER_NOT_IN_GAME = 'User @%s is currently not alive or not playing'
    ERR_PLAYER_NOT_IN_ORDER = 'It is currently user @%s\'s turn!'
    ERR_ALL_CLUES_ALREADY_GIVEN = 'All the clues are in! Proceed to vote'
    ERR_CLUE_ALREADY_GIVEN = 'User @%s has already given a clue this round'
    ERR_PLAYER_CANNOT_GUESS = 'It is not up to player @%s to guess'

    def __init__(self):
        self.__game_state = Ghost.States.REGISTER_PLAYERS
        self.__town_word = None
        self.__fool_word = None

        self.__player_info = dict()  # username --> player
        self.__unvoted_players = set()
        self.__player_order = list()
        self.__player_order_index = -1

        self.__last_lynched = Ghost.__EMPTY_VOTE

    def __is_game_state(self, expected_state: States) -> bool:
        return self.__game_state == expected_state

    ''' PHASE: REGISTER PLAYERS '''

    def register_player(self, username: str) -> (bool, int):
        res = False
        if not self.__is_game_state(Ghost.States.REGISTER_PLAYERS):
            logging.warning(Ghost.ERR_INVALID_GAME_STATE % 
                            (Ghost.States.REGISTER_PLAYERS, self.__game_state))
        elif self.__is_user_alive(username):
            logging.warning(Ghost.ERR_PLAYER_ALREADY_REGISTERED % username)
        elif len(self.__player_info) >= Ghost.MAX_NUM_PLAYERS:
            logging.warning(Ghost.ERR_PLAYER_CAP_EXCEEDED)
        else:
            res = True
            self.__player_info[username] = Player()
            logging.info('Success: Registered player @%s' % username)

        return res, len(self.__player_info)

    def unregister_player(self, username: str) -> bool:
        if not self.__is_game_state(Ghost.States.REGISTER_PLAYERS):
            logging.warning(Ghost.ERR_INVALID_GAME_STATE % 
                            (Ghost.States.REGISTER_PLAYERS, self.__game_state))
            return False
        elif not self.__is_user_alive(username):
            logging.warning(Ghost.ERR_USER_NOT_IN_GAME % username)
            return False
        else:
            del self.__player_info[username]
            return True

    def start_game(self) -> bool:
        if not self.__is_game_state(Ghost.States.REGISTER_PLAYERS):
            logging.warning(Ghost.ERR_INVALID_GAME_STATE % 
                            (Ghost.States.REGISTER_PLAYERS, self.__game_state))
            return False

        if len(self.__player_info) < Ghost.MIN_NUM_PLAYERS:
            logging.warning(Ghost.ERR_INSUFF_PLAYERS)
            return False

        # set player order
        self.__player_order = list(self.__player_info)
        random.shuffle(self.__player_order)

        self.__allocate_roles()
        self.__game_state = Ghost.States.SET_PARAMS
        logging.info('Success: Started game')
        return True

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

    def set_param_town_word(self, value: str) -> bool:
        if not self.__is_game_state(Ghost.States.SET_PARAMS):
            logging.warning(Ghost.ERR_INVALID_GAME_STATE % 
                            (Ghost.States.SET_PARAMS, self.__game_state))
            return False
        elif len(value) < Ghost.MIN_WORD_LENGTH:
            logging.warning(Ghost.ERR_WORD_TOO_SHORT)
            return False
        elif len(value) > Ghost.MAX_WORD_LENGTH:
            logging.warning(Ghost.ERR_WORD_TOO_LONG)
            return False
        elif not Ghost.DICTIONARY.check(value):
            logging.warning(Ghost.ERR_WORD_NOT_ENGLISH)
            return False

        self.__town_word = value.lower()
        logging.info('Success: Set the town word: %s' % self.__town_word)
        return True

    def set_param_fool_word(self, value: str) -> bool:
        if not self.__is_game_state(Ghost.States.SET_PARAMS):
            logging.warning(Ghost.ERR_INVALID_GAME_STATE % 
                            (Ghost.States.SET_PARAMS, self.__game_state))
            return False
        elif self.__town_word is None:
            logging.warning(Ghost.ERR_TOWN_WORD_NOT_SET)
            return False
        elif len(value) != len(self.__town_word):
            logging.warning(Ghost.ERR_FOOL_WORD_DIFFERENT_LENGTH)
            return False
        elif value == self.__town_word:
            logging.warning(Ghost.ERR_FOOL_WORD_DUPLICATE)
            return False
        elif not Ghost.DICTIONARY.check(value):
            logging.warning(Ghost.ERR_WORD_NOT_ENGLISH)
            return False

        self.__fool_word = value.lower()
        logging.info('Success: Set the fool word: %s' % self.__fool_word)

        self.__start_clue_phase()
        return True

    ''' HELPER METHODS '''

    def get_game_state(self) -> States:
        return self.__game_state

    def get_existing_players(self) -> List[str]:
        return list(self.__player_info)

    def get_player_order(self) -> List[str]:
        return self.__player_order

    def get_player_roles(self) -> dict:
        if self.__game_state == Ghost.States.REGISTER_PLAYERS:
            logging.warning(Ghost.ERR_ROLES_NOT_ALLOCATED)
            return dict()

        result = dict()

        for username, player in self.__player_info.items():
            result[username] = player.role

        return result

    def get_words(self) -> (str, str):
        return self.__town_word, self.__fool_word

    def __is_ghost(self, username: str) -> bool:
        return self.__player_info[username].role == Ghost.Roles.GHOST

    def __is_user_alive(self, username: str) -> bool:
        return username in self.__player_info


    ''' PHASE: CLUES '''

    def __start_clue_phase(self) -> None:
        self.__game_state = Ghost.States.CLUE_ROUND
        for p in self.__player_info.values():
            p.clue = None
        self.__unvoted_players = set(self.__player_info)
        self.__player_order_index = 0

    def get_next_in_player_order(self) -> str:
        if len(self.__unvoted_players) == 0:
            logging.warning(Ghost.ERR_ALL_CLUES_ALREADY_GIVEN)
            return ''

        return self.__player_order[self.__player_order_index]

    def __increase_player_order_index(self) -> None:
        self.__player_order_index += 1
        self.__player_order_index %= len(self.__player_info)

    def set_clue(self, username: str, clue: str) -> (bool, bool):
        default_return = False, False
        if not self.__is_game_state(Ghost.States.CLUE_ROUND):
            logging.warning(Ghost.ERR_INVALID_GAME_STATE % 
                            (Ghost.States.CLUE_ROUND, self.__game_state))
            return default_return
        elif not self.__is_user_alive(username):
            logging.warning(Ghost.ERR_USER_NOT_IN_GAME % username)
            return default_return 
        elif self.__player_info[username].clue is not None:
            logging.warning(Ghost.ERR_CLUE_ALREADY_GIVEN % username)
            return default_return 

        expected_user = self.get_next_in_player_order()
        if username != expected_user:
            logging.warning(Ghost.ERR_PLAYER_NOT_IN_ORDER % expected_user)
            return default_return

        self.__player_info[username].clue = clue
        self.__unvoted_players.remove(username)
        self.__increase_player_order_index()

        # check if all players have given clues
        is_complete = len(self.__unvoted_players) == 0
        if is_complete:
            self.__start_vote_phase()

        return True, is_complete

    def get_all_clues(self) -> dict:
        result = dict()

        for username, player in self.__player_info.items():
            result[username] = player.clue

        return result

    ''' PHASE: VOTE '''

    def __start_vote_phase(self) -> None:
        self.__game_state = Ghost.States.VOTE_ROUND
        for p in self.__player_info.values():
            p.vote = None
        self.__unvoted_players = set(self.__player_info)

    def set_vote(self, username: str, vote: str) -> (bool, bool, str):
        default_return = False, False, ''
        if not self.__is_game_state(Ghost.States.VOTE_ROUND):
            logging.warning(Ghost.ERR_INVALID_GAME_STATE % i
                            (Ghost.States.VOTE_ROUND, self.__game_state))
            return default_return 
        elif not self.__is_user_alive(username):
            logging.warning(Ghost.ERR_USER_NOT_IN_GAME % username)
            return default_return 
        elif vote != Ghost.__EMPTY_VOTE and not self.__is_user_alive(vote):
            logging.warning(Ghost.ERR_USER_NOT_IN_GAME % vote)
            return default_return 

        self.__player_info[username].vote = vote
        self.__unvoted_players.discard(username)

        is_complete = len(self.__unvoted_players) == 0
        if is_complete:
            self.__process_vote()

        return True, is_complete, self.__last_lynched

    def __tally_votes(self, players) -> set:
        votes = defaultdict(lambda: 0)
        for username in players:
            v = self.__player_info[username].vote
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
            if self.__game_state != Ghost.States.WINNER_GHOST: 
                self.__start_vote_phase()

    def __kill_player(self, username: str) -> None:
        del self.__player_info[username]

        num_ghost_alive = len(list(filter(self.__is_ghost, self.__player_info)))
        if num_ghost_alive == 0:
            # killed all ghosts
            self.__game_state = Ghost.States.WINNER_TOWN
            logging.info('Congratulations to the Town!')
        elif num_ghost_alive >= len(self.__player_info) // 2:
            # ghosts got majority
            self.__game_state = Ghost.States.WINNER_GHOST
            logging.info('Congratulations to the Ghosts!')

    ''' PHASE: GUESS '''

    def make_guess(self, username: str, guess: str) -> (bool, bool):
        default_return = False, False
        if not self.__is_game_state(Ghost.States.GUESS_ROUND):
            logging.warning(Ghost.ERR_INVALID_GAME_STATE %
                            (Ghost.States.GUESS_ROUND, self.__game_state))
            return default_return
        elif username != self.__last_lynched:
            logging.warning(Ghost.ERR_PLAYER_CANNOT_GUESS % username)
            # ignore irrelevant messages
            return default_return

        logging.info('Player @%s has guessed: %s' % (username, guess.lower()))
        if guess.lower() == self.__town_word:
            self.__game_state = Ghost.States.WINNER_GHOST
            logging.info('Congratulations to the Ghosts!')
            return True, True
        
        self.__kill_player(username)
        if self.__game_state != Ghost.States.WINNER_TOWN:
            self.__start_vote_phase()
        
        return True, False
