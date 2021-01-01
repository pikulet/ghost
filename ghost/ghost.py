from enum import Enum
from collections import deque, defaultdict
import random


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
        4: (3, 1, 0),
        5: (3, 2, 0),
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
        self.__num_players = 0
        self.__town_word = None
        self.__fool_word = None

        self.__player_info = dict()  # username --> player
        self.__alive_players = set()
        self.__unvoted_players = set()

        self.__last_lynched = None

    def __check_game_state(self, expected_state: States) -> None:
        if self.__game_state != expected_state:
            raise Ghost.GhostException(
                'Invalid game state! Expected game to be in %s stage but got '
                '%s state' % (expected_state, self.__game_state)
            )

    def __check_not_in_game_state(self, invalid_state: States) -> None:
        if self.__game_state == expected_state:
            raise Ghost.GhostException(
                'Invalid game state! Cannot be in %s' % invalid_state
            )

    ''' PHASE: REGISTER PLAYERS '''

    def register_player(self, username: str) -> int:
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
        self.__check_game_state(Ghost.States.REGISTER_PLAYERS)

        if len(self.__player_info) < Ghost.MIN_NUM_PLAYERS:
            raise Ghost.GhostException(
                'Not enough players have joined (min %d needed)' %
                Ghost.MIN_NUM_PLAYERS
            )

        # update final player count
        self.__num_players = len(self.__player_info)
        self.__alive_players = set(self.__player_info)

        # distribute roles
        self.__allocate_roles()

        self.__game_state = Ghost.States.SET_PARAMS

    def __allocate_roles(self) -> None:

        # get the roles in this game
        n_town, n_ghost, n_fool = Ghost.__ROLE_SETS[self.__num_players]
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
        return self.__player_info[username].role == Ghost.States.GHOST

    def __check_user_alive(self, username: str) -> None:
        if username not in self.__player_info:
            raise Ghost.GhostException(
                'User @%s is currently not playing' % username
            )

        if username not in self.__alive_players:
            raise Ghost.GhostException(
                'User @%s is not alive' % username
            )

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

    def __reset_info(self) -> None:
        for player in self.__player_info.values():
            player.info = None

    ''' PHASE: CLUES '''

    def __start_clue_phase(self) -> None:
        self.__game_state = Ghost.States.CLUE_ROUND
        self.__reset_info()
        self.__unvoted_players = set(self.__alive_players)

    def suggest_next_clue_giver(self) -> str:
        if len(self.__unvoted_players) == 0:
            return None

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
        self.__unvoted_players = set(self.__alive_players)

    def set_vote(self, username: str, vote: str) -> bool:
        self.__check_game_state(Ghost.States.VOTE_ROUND)
        self.__check_user_alive(username)

        if vote != Ghost.__EMPTY_VOTE:
            self.__check_user_alive(vote)

        self.__player_info[username].info = vote
        self.__unvoted_players.discard(username)

        is_complete = len(self.__unvoted_players) == 0
        if is_complete:
            self.__process_vote()

        return is_complete

    def __process_vote(self) -> None:
        tally = self.__tally_votes(self.__alive_players)
        if len(tally) != 1:
            # voted for no one
            self.__start_clue_phase()

        to_lynch = tally.pop()
        self.__last_lynched = to_lynch

        if self.__is_ghost(to_lynch):
            self.__start_guess_phase()
        else:
            self.__kill_player(to_lynch)
            self.__start_clue_phase()

        if self.__player_info[to_lynch].role != Ghost.Roles.GHOST

    def get_vote_result(self) -> (str, Ghost.States):
        # TODO
        return None, None

    def end_vote_phase(self) -> str:
        if not self.is_vote_phase_complete():
            raise Ghost.GhostException(
                'Some players have yet to vote'
            )

        to_lynch = self.__tally_lynch_votes()

        if to_lynch == Ghost.__EMPTY_VOTE:
        elif not self.is_ghost(to_lynch):
            self.__kill_player(to_lynch)
            self.__start_clue_phase()
        else:

        return to_lynch

    def __kill_player(self, username: str) -> None:
        self.__check_user_alive(username)

        self.__alive_players.discard(username)

        num_ghost_alive = len(list(filter(lambda , self.__alive_players)))
        if num_ghost_alive == 0:
            # killed all ghosts
            self.__end_game(Ghost.Roles.TOWN)
        elif num_ghost_alive >= len(self.__alive_players) // 2:
            # ghosts got majority
            self.__end_game(Ghost.Roles.GHOST)

    ''' PHASE: GUESS '''

    def __start_guess_phase(self) -> None:
        self.__game_state = Ghost.States.GUESS_ROUND

    def make_guess(self, username: str, guess: str) -> None:
        self.__check_game_state(Ghost.States.GUESS_ROUND)

        if username != self.__last_lynched:
            # ignore irrelevant messages
            return

        if guess.lower() == self.__town_word:
            self.__end_game(Ghost.Roles.GHOST)
        else:
            self.__kill_player(username)
            self.__start_vote_phase()

    def __end_game(self, winner: Roles):
        self.__game_state = Ghost.States.COMPLETE
        self.__winning_team = winner

    def is_game_complete(self) -> bool:
        return self.__game_state == Ghost.States.COMPLETE

    def get_winning_team(self):
        if not self.is_game_complete():
            raise Ghost.GhostException('Game is not completed')
        return self.__winning_team


