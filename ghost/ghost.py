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
    __MIN_NUM_PLAYERS = 3
    __DEFAULT_NUM_PLAYERS = 7
    __MAX_NUM_PLAYERS = 10

    __MIN_WORD_LENGTH = 3
    __MAX_WORD_LENGTH = 15

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
    class __States(Enum):
        SET_PARAMS = 'Setting parameters'
        REGISTER_PLAYERS = 'Registering players'
        GHOST_VOTE_ROUND = 'Ghost Vote Round'
        CLUE_ROUND = 'Word Round'
        VOTE_ROUND = 'Vote Round'
        GUESS_ROUND = 'Guess Word Round'
        COMPLETE = 'Complete'

    def __init__(self):
        self.__game_state = None
        self.__winning_team = Ghost.Roles.FOOL
        self.__num_players = 0
        self.__town_word = None
        self.__fool_word = None

        self.__player_info = dict()  # username --> player
        self.__ghosts = set()
        self.__alive_players = set()
        self.__unvoted_players = set()
        self.__player_order = deque()

        self.__last_lynched = None

        self.__start_param_phase()

    def __check_game_state(self, expected_state: __States) -> None:
        if self.__game_state != expected_state:
            raise Ghost.GhostException(
                'Invalid game state! Expected game to be in %s stage but got '
                '%s stage' % (expected_state, self.__game_state)
            )

    ''' PHASE: SET PARAM '''

    def __start_param_phase(self) -> None:
        self.__game_state = Ghost.__States.SET_PARAMS

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

        self.__town_word = value.lower()

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
        self.__fool_word = value.lower()

    def end_params_phase(self) -> None:
        self.__check_game_state(Ghost.__States.SET_PARAMS)

        # check other parameters
        if self.__town_word is None:
            raise Ghost.GhostException('Town word has not been set')
        if self.__fool_word is None:
            raise Ghost.GhostException('Fool word has not been set')

        # set default number of players
        if self.__num_players == 0:
            self.set_param_num_players(Ghost.__DEFAULT_NUM_PLAYERS)

        self.__start_register_phase()

    ''' PHASE: REGISTER PLAYERS '''

    def __start_register_phase(self) -> None:
        self.__game_state = Ghost.__States.REGISTER_PLAYERS

    def __check_user_in_game(self, username: str) -> None:
        if username not in self.__player_info:
            raise Ghost.GhostException(
                'User @%s is currently not playing' % username
            )

    def __check_user_alive(self, username: str) -> None:
        self.__check_user_in_game(username)
        if username not in self.__alive_players:
            raise Ghost.GhostException(
                'User @%s is not alive' % username
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

    def end_register_phase(self) -> dict:
        self.__check_game_state(Ghost.__States.REGISTER_PLAYERS)
        if len(self.__player_info) < Ghost.__MIN_NUM_PLAYERS:
            raise Ghost.GhostException(
                'Not enough players have joined (min %d)' %
                Ghost.__MIN_NUM_PLAYERS
            )

        # update final player count
        self.__num_players = len(self.__player_info)
        self.__alive_players = set(self.__player_info)

        return self.__start_game_phase()

    ''' PHASE: ROLE SETUP '''

    def __start_game_phase(self) -> dict:
        # initialise states
        roles = self.__assign_player_roles()
        role_index = 0

        for username in self.__player_info:
            self.__player_info[username].role = roles[role_index]
            self.__player_order.append(username)
            if roles[role_index] == Ghost.Roles.GHOST:
                self.__ghosts.add(username)
            role_index += 1

        self.__start_ghost_vote_phase()
        return self.get_player_roles()

    def __assign_player_roles(self) -> list:
        n_town, n_ghost, n_fool = Ghost.__ROLE_SETS[self.__num_players]
        roles = [Ghost.Roles.TOWN] * n_town + \
                    [Ghost.Roles.GHOST] * n_ghost + \
                    [Ghost.Roles.FOOL] * n_fool

        random.shuffle(roles)
        return roles

    def is_ghost(self, username: str) -> bool:
        return username in self.__ghosts

    def get_player_roles(self) -> dict:
        result = dict()

        for username in self.__player_order:
            role = self.__player_info[username].role
            result[username] = role

        return result

    ''' HELPER METHODS '''

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

    def __tally_ghost_votes(self) -> str:
        return self.__tally_votes(self.__ghosts).pop()

    def __reset_info(self) -> None:
        for player in self.__player_info.values():
            player.info = None

    def __is_phase_complete(self, phase: __States) -> bool:
        self.__check_game_state(phase)
        return len(self.__unvoted_players) == 0

    ''' PHASE: GHOST VOTING '''

    def __start_ghost_vote_phase(self) -> None:
        self.__game_state = Ghost.__States.GHOST_VOTE_ROUND
        self.__reset_info()
        self.__unvoted_players = set(self.__ghosts)

    def set_ghost_vote(self, username: str, ghost_vote: str) -> None:
        self.__check_game_state(Ghost.__States.GHOST_VOTE_ROUND)
        self.__check_user_alive(username)
        self.__check_user_alive(ghost_vote)

        if not self.is_ghost(username):
            '''
            raise Ghost.GhostException(
                'User @%s is not Ghost, and cannot vote for who to start'
            )'''
            # ignore irrelevant messages
            return

        self.__player_info[username].info = ghost_vote
        self.__unvoted_players.discard(username)

    def is_ghost_vote_phase_complete(self) -> bool:
        return self.__is_phase_complete(Ghost.__States.GHOST_VOTE_ROUND)

    def end_ghost_vote_phase(self) -> None:
        if not self.is_ghost_vote_phase_complete():
            raise Ghost.GhostException(
                'Some players have yet to vote'
            )

        to_start = self.__tally_ghost_votes()

        while self.__player_order[0] != to_start:
            skip = self.__player_order.popleft()
            self.__player_order.append(skip)

        self.__start_clue_phase()

    ''' PHASE: CLUES '''

    def __start_clue_phase(self) -> None:
        self.__game_state = Ghost.__States.CLUE_ROUND
        self.__reset_info()
        self.__unvoted_players = set(self.__alive_players)

    def get_player_order(self) -> list:
        return list(self.__player_order)

    def set_clue(self, username: str, clue: str) -> None:
        self.__check_game_state(Ghost.__States.CLUE_ROUND)
        self.__check_user_alive(username)

        if self.__player_info[username].info is not None:
            raise Ghost.GhostException(
                'User @%s has already given a clue this round' % username
            )

        self.__player_info[username].clue = clue
        self.__unvoted_players.remove(username)

    def is_clue_phase_complete(self) -> bool:
        return self.__is_phase_complete(Ghost.__States.CLUE_ROUND)

    def end_clue_phase(self) -> dict:
        if not self.is_clue_phase_complete():
            raise Ghost.GhostException(
                'Some players have yet to give a clue'
            )

        result = dict()

        for username, player in self.__player_info.items():
            result[username] = player.clue

        return result

    ''' PHASE: VOTE '''

    def __start_vote_phase(self) -> None:
        self.__game_state = Ghost.__States.VOTE_ROUND
        self.__reset_info()
        self.__unvoted_players = set(self.__alive_players)

    def set_vote(self, username: str, vote: str) -> None:
        self.__check_game_state(Ghost.__States.VOTE_ROUND)
        self.__check_user_alive(username)

        if vote != Ghost.__EMPTY_VOTE:
            self.__check_user_alive(vote)

        self.__player_info[username].info = vote
        self.__unvoted_players.discard(username)

    def is_vote_phase_complete(self) -> bool:
        return self.__is_phase_complete(Ghost.__States.VOTE_ROUND)

    def __tally_lynch_votes(self) -> str:
        tally = self.__tally_votes(self.__alive_players)
        if len(tally) == 1:
            return tally.pop()
        else:
            return Ghost.__EMPTY_VOTE

    def end_vote_phase(self) -> str:
        if not self.is_vote_phase_complete():
            raise Ghost.GhostException(
                'Some players have yet to vote'
            )

        to_lynch = self.__tally_lynch_votes()

        if to_lynch == Ghost.__EMPTY_VOTE:
            self.__start_clue_phase()
        elif not self.is_ghost(to_lynch):
            self.__kill_player(to_lynch)
            self.__start_clue_phase()
        else:
            self.__last_lynched = to_lynch
            self.__start_guess_phase()

        return to_lynch

    def __kill_player(self, username: str) -> None:
        self.__check_user_alive(username)

        self.__alive_players.discard(username)
        self.__ghosts.discard(username)
        self.__unvoted_players.discard(username)
        self.__player_order.remove(username)
        self.__check_end_game()

    def __check_end_game(self):
        num_ghost_alive = len(list(filter(self.is_ghost, self.__alive_players)))
        if num_ghost_alive == 0:
            # killed all ghosts
            self.__end_game(Ghost.Roles.TOWN)
        elif num_ghost_alive >= len(self.__alive_players) // 2:
            # ghosts got majority
            self.__end_game(Ghost.Roles.GHOST)

    ''' PHASE: GUESS '''

    def __start_guess_phase(self) -> None:
        self.__game_state = Ghost.__States.GUESS_ROUND

    def make_guess(self, username: str, guess: str) -> None:
        self.__check_game_state(Ghost.__States.GUESS_ROUND)

        if username != self.__last_lynched:
            # ignore irrelevant messages
            return

        if guess.lower() == self.__town_word:
            self.__end_game(Ghost.Roles.GHOST)
        else:
            self.__kill_player(username)
            self.__start_vote_phase()

    def __end_game(self, winner: Roles):
        self.__game_state = Ghost.__States.COMPLETE
        self.__winning_team = winner

    def is_game_complete(self) -> bool:
        return self.__game_state == Ghost.__States.COMPLETE

    def get_winning_team(self):
        if not self.is_game_complete():
            raise Ghost.GhostException('Game is not completed')
        return self.__winning_team


