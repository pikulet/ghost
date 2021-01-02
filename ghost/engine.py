from bidict import bidict
from ghost.ghost import Ghost

class GhostEngine:

    class GhostEngineException(Exception):
        pass

    def __init__(self, max_games = 4):
        self.__MAX_NUMBER_OF_GAMES = max_games
        self.__games = dict()                   # gid to game
        self.__host_to_gid = bidict()      # host to gid
        self.__player_to_gid = dict()     # username to gid

    def add_game(self, gid: int, host: str) -> None:
        ''' Creates a game in the engine '''
        if gid in self.__games:
            raise GhostEngine.GhostEngineException(
                'There is already an ongoing game in this group...'
            )

        elif len(self.__games) >= self.__MAX_NUMBER_OF_GAMES:
            raise GhostEngine.GhostEngineException(
                'Too many ongoing games... Please wait...'
            )

        new_game = Ghost()
        self.__games[gid] = new_game
        self.__host_to_gid[host] = gid

    def delete_game(self, gid: int) -> None:
        ''' Removes a game from the engine '''
        self.__check_game_exists()
        del self.__games[gid]

        host = self.__get_host_from_gid(gid)
        del self.__hosts_to_gid[host]

    def __check_game_exists(self, gid: int) -> None:
        if gid not in self.__games:
            raise GhostEngine.GhostEngineException(
                'Game %d does not exist' % gid
            )

    def __check_host_exists(self, host: str) -> None:
        if host not in self.__host_to_gid:
            raise GhostEngine.GhostEngineException(
                'User @%s is not the host of any game'
            )

    def __check_player_exists(self, username: str) -> None:
        if player not in self.__username_to_gid:
            raise GhostEngine.GhostEngineException(
                'User @%s has no ongoing game'
            )

    def __get_game_from_gid(self, gid: int) -> Ghost:
        self.__check_game_exists(gid)
        return self.__games[gid]

    def __get_gid_from_host(self, host: str) -> int:
        self.__check_host_exists(host)
        return self.__host_to_gid[host]

    def __get_host_from_gid(self, gid: int) -> str:
        self.__check_game_exists(gid)
        return self.__host_to_gid.inverse[gid]

    def __get_gid_from_player(self, username: str) -> int:
        self.__check_player_exists(username)
        return self.__player_to_gid[username]

    def __get_players_from_gid(self, gid: int) -> set:
        self.__check_game_exists(gid)
        game = self.__get_game_from_gid(gid)
        # TODO
        return game.get_players() 

    ''' PHASE: REGISTER PLAYERS '''

    def register_player(self, gid: int, player: str) -> int:
        ''' Returns the number of players registered in the game '''
        game = self.__get_game_from_gid(gid)
        return game.register_player(player)

    def start_game(self, gid: int) -> None:
        game = self.__get_game_from_gid(gid)
        game.start_game()
        
    ''' PHASE: SET PARAM '''

    def set_param_town_word(self, host: str, value: str) -> None:
        gid = self.__get_gid_from_host(host)
        game = self.__get_game_from_gid(gid)
        game.set_param_town_word(value)

    def set_param_fool_word(self, host: str, value: str) -> None:
        gid = self.__get_gid_from_host(host)
        game = self.__get_game_from_gid(gid)
        game.set_param_fool_word(value)

    ''' PHASE: ROLE SETUP '''

    def get_player_roles(self, gid: int) -> dict:
        game = self.__get_game_from_gid(gid)
        return game.get_player_roles()

    ''' PHASE: CLUES '''

    def suggest_next_clue_giver(self, gid: int) -> str:
        ''' Return username of next person to give clue, None if all
        clues have been given '''
        game = self.__get_game_from_gid(gid)
        return game.suggest_next_clue_giver()

    def set_clue(self, gid: int, player: str, clue: str) -> bool:
        ''' Returns True if all players have given a clue '''
        game = self.__get_game_from_gid(gid)
        return game.set_clue(player, clue)

    def get_all_clues(self, gid: int) -> dict:
        game = self.__get_game_from_gid(gid)
        return game.get_all_clues()

    ''' PHASE: VOTE '''

    def set_vote(self, gid: int, player: str, vote: str) -> (bool, str,
                                                             Ghost.States):
        ''' Returns True if all players have voted.
        If true, returns the name of person voted out and the resulting game
        state '''
        game = self.__get_game_from_gid(gid)
        return game.set_vote(player, vote)

    ''' PHASE: GUESS '''

    def make_guess(self, gid: int, player: str, guess: str) -> bool:
        ''' Returns True if the guess is correct '''
        game = self.__get_game_from_gid(gid)
        return game.make_guess(player, guess)
