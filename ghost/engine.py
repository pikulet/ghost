from bidict import bidict
from ghost.ghost import Ghost

from typing import List, Dict

import logging

class GhostEngine:

    ERR_TOO_MANY_GAMES = 'Too many ongoing games... Please wait...'
    ERR_GID_ALREADY_EXISTS = 'There is already an ongoing game in this group'
    ERR_GID_DOES_NOT_EXIST = 'Game %d does not exist'

    ERR_USER_IS_HOST = 'User @%s is the host of the game'
    ERR_USER_NOT_HOST = 'User @%s is not the host of any game'
    ERR_PLAYER_DOES_NOT_EXIST = 'User @%s has no ongoing game'

    def __init__(self, max_games = 4):
        self.__MAX_NUMBER_OF_GAMES = max_games
        self.__games = dict()                   # gid to game
        self.__host_to_gid = bidict()      # host to gid

    def add_game(self, gid: int, host: str) -> bool:
        ''' Creates a game in the engine.
        Returns True if the game was successfully created '''
        if gid in self.__games:
            logging.warning(GhostEngine.ERR_GID_ALREADY_EXISTS)
            return False
        elif len(self.__games) >= self.__MAX_NUMBER_OF_GAMES:
            logging.warning(GhostEngine.ERR_TOO_MANY_GAMES)
            return False

        new_game = Ghost()
        self.__games[gid] = new_game
        self.__host_to_gid[host] = gid
        return True

    def delete_game(self, gid: int) -> bool:
        ''' Removes a game from the engine. 
        Returns True if the game was successfully deleted '''
        self.__is_game_exists()
        del self.__games[gid]

        host = self.__get_host_from_gid(gid)
        del self.__hosts_to_gid[host]

    def __is_game_exists(self, gid: int) -> bool:
        if gid not in self.__games:
            logging.warning(GhostEngine.ERR_GID_DOES_NOT_EXIST % gid)
            return False

        return True

    def __is_host_exists(self, host: str) -> bool:
        if host not in self.__host_to_gid:
            logging.warning(GhostEngine.ERR_USER_NOT_HOST % host)
            return False

        return True

    def __is_player_exists(self, username: str) -> None:
        if player not in self.__username_to_gid:
            logging.warning(GhostEngine.ERR_PLAYER_DOES_NOT_EXIST)
            return False

        return True

    def __get_game_from_gid(self, gid: int) -> Ghost:
        if not self.__is_game_exists(gid):
            return Ghost() 

        return self.__games[gid]

    def get_gid_from_host(self, host: str) -> int:
        ''' Returns the gid the host is in-charge of, -1 otherwise  '''
        if not self.__is_host_exists(host):
            return -1

        return self.__host_to_gid[host]

    def __get_host_from_gid(self, gid: int) -> str:
        if not self.__is_game_exists(gid):
            return ''

        return self.__host_to_gid.inverse[gid]

    ''' GET GAME INFORMATION '''

    def get_game_state(self, gid: int) -> Ghost.States:
        game = self.__get_game_from_gid(gid)
        return game.get_game_state()

    def get_existing_players(self, gid: int) -> List[str]:
        game = self.__get_game_from_gid(gid)
        return game.get_existing_players()

    def get_player_order(self, gid: int) -> List[str]:
        game = self.__get_game_from_gid(gid)
        return game.get_player_order()

    def get_player_roles(self, gid: int) -> Dict[str, Ghost.Roles]:
        game = self.__get_game_from_gid(gid)
        return game.get_player_roles()

    def get_words(self, gid: int) -> (str, str):
        game = self.__get_game_from_gid(gid)
        return game.get_words()

    ''' PHASE: REGISTER PLAYERS '''

    def register_player(self, gid: int, player: str) -> int:
        ''' Returns the number of players registered in the game '''
        host = self.__get_host_from_gid(gid)
        game = self.__get_game_from_gid(gid)

        if player == host:
            logging.warning(GhostEngine.ERR_USER_IS_HOST % player)
            return len(game.get_existing_players())

        return game.register_player(player)

    def start_game(self, gid: int) -> bool:
        ''' Returns True if the game was successfully started '''
        game = self.__get_game_from_gid(gid)
        return game.start_game()
        
    ''' PHASE: SET PARAM '''

    def set_param_town_word(self, host: str, value: str) -> bool:
        ''' Returns True if the town word was successfully set '''
        gid = self.get_gid_from_host(host)
        game = self.__get_game_from_gid(gid)
        return game.set_param_town_word(value)

    def set_param_fool_word(self, host: str, value: str) -> bool:
        ''' Returns True if the fool word was successfully set '''
        gid = self.get_gid_from_host(host)
        game = self.__get_game_from_gid(gid)
        return game.set_param_fool_word(value)

    ''' PHASE: CLUES '''

    def get_next_in_player_order(self, gid: int) -> str:
        ''' Returns the name of the next person expected to give a clue.
        An empty string is returned if all clues have been given or 
        it's not the clue phase '''
        game = self.__get_game_from_gid(gid)
        return game.get_next_in_player_order()

    def set_clue(self, gid: int, player: str, clue: str) -> (bool, bool):
        ''' Returns a tuple of two booleans. 
        The first boolean is True if the clue is successfully given.
        The second boolean is True if all players have given a clue. '''
        game = self.__get_game_from_gid(gid)
        return game.set_clue(player, clue)

    def get_all_clues(self, gid: int) -> Dict[str, str]:
        ''' Returns the clues given by the users.
        An empty dict() is returned if not all clues have been given. '''
        game = self.__get_game_from_gid(gid)
        return game.get_all_clues()

    ''' PHASE: VOTE '''

    def set_vote(self, gid: int, player: str, vote: str) -> (bool, bool, str):
        ''' Returns a tuple of three booleans.
        The first boolean is True if the vote is successfully made.
        The second boolean is True if all the players have voted.
        The third boolean returns the player voted out, 
        or an empty string if no one is voted out. '''
        game = self.__get_game_from_gid(gid)
        return game.set_vote(player, vote)

    ''' PHASE: GUESS '''

    def make_guess(self, gid: int, player: str, guess: str) -> bool:
        ''' Returns a tuple of two booleans.
        The first boolean is True if the guess is successfully made.
        The second boolean is True if the guess is correct. '''
        game = self.__get_game_from_gid(gid)
        return game.make_guess(player, guess)
