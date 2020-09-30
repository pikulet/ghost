from bidict import bidict
from ghost.ghost import Ghost


class GhostEngine:

    class GhostEngineException(Exception):
        pass

    def __init__(self, max_games=4):
        self.__MAX_NUMBER_OF_GAMES = max_games
        self.__games = dict()                   # game_id to game
        self.__hosts_to_game_id = bidict()      # host to game_id
        self.__username_to_game_id = bidict()     # username to game_id

    def add_game(self, game_id: int) -> Ghost:
        if game_id in self.__games:
            raise GhostEngine.GhostEngineException(
                'There is already an ongoing game in this group...'
            )

        elif len(self.__games) >= self.__MAX_NUMBER_OF_GAMES:
            raise GhostEngine.GhostEngineException(
                'Too many ongoing games... Please wait...'
            )

        new_game = Ghost()
        self.__games[game_id] = new_game
        return new_game

    def delete_game(self, game_id: int) -> None:
        self.__check_game_exists()
        del self.__games[game_id]

        host = self.__get_host_from_game_id(game_id)
        del self.__hosts_to_game_id[host]

    def __check_game_exists(self, game_id: int) -> None:
        if game_id not in self.__games:
            raise GhostEngine.GhostEngineException('Game does not exist')

    def __check_host_exists(self, host: str) -> None:
        if host not in self.__hosts_to_game_id:
            raise GhostEngine.GhostEngineException(
                'User @%s is not the host of any game'
            )

    def __check_username_exists(self, username: str) -> None:
        if username not in self.__username_to_game_id:
            raise GhostEngine.GhostEngineException(
                'User @%s has no ongoing game'
            )

    def __get_game_from_game_id(self, game_id: int) -> Ghost:
        self.__check_game_exists(game_id)
        return self.__games[game_id]

    def __get_game_id_from_host(self, host: str) -> int:
        self.__check_host_exists(host)
        return self.__hosts_to_game_id[host]

    def __get_host_from_game_id(self, game_id: int) -> str:
        self.__check_game_exists(game_id)
        return self.__hosts_to_game_id.inverse[game_id]

    def __get_game_id_from_username(self, username: str) -> int:
        self.__check_username_exists(username)
        return self.__username_to_game_id[username]

    def __get_usernames_from_game_id(self, game_id: int) -> set:
        self.__check_game_exists(game_id)
        return self.__username_to_game_id.inverse[game_id]

    ''' PHASE: SET PARAM '''

    def set_param_num_players(self, host: str, value: int) -> None:
        game_id = self.__get_game_id_from_host(host)
        game = self.__get_game_from_game_id(game_id)
        game.set_param_num_players(value)

    def set_param_town_word(self, host: str, value: str) -> None:
        game_id = self.__get_game_id_from_host(host)
        game = self.__get_game_from_game_id(game_id)
        game.set_param_town_word(value)

    def set_param_fool_word(self, host: str, value: str) -> None:
        game_id = self.__get_game_id_from_host(host)
        game = self.__get_game_from_game_id(game_id)
        game.set_param_fool_word(value)

    def end_param_phase(self, host: str) -> None:
        game_id = self.__get_game_id_from_host(host)
        game = self.__get_game_from_game_id(game_id)
        game.end_param_phase()

    ''' PHASE: REGISTER PLAYERS '''

    def register_player(self, game_id: int, username: str) -> None:
        game = self.__get_game_from_game_id(game_id)
        game.register_player(username)

    def is_max_player_cap_reached(self, game_id: int) -> bool:
        game = self.__get_game_from_game_id(game_id)
        return game.is_max_player_cap_reached()

    def end_register_phase(self, game_id: int) -> dict:
        game = self.__get_game_from_game_id(game_id)
        return game.end_register_phase()

    def get_player_roles(self, game_id: int) -> dict:
        game = self.__get_game_from_game_id(game_id)
        return game.get_player_roles()

