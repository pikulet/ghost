from enum import Enum
from bidict import bidict

class GhostGameEngine():

    class GhostGameEngineException(Exception):
        pass

    def __init__(self, max_games = 4):
        self.MAX_NUMBER_OF_GAMES = max_games 
        self.num_games = 0
        self.games = dict() # mapping id to games
        self.hosts_to_game_id = bidict() # mapping from id to host usernames

    def add_game(self, game_id: int) -> GhostGame:
        if game_id in self.games:
            raise GhostGameEngineException(
                'There is already an ongoing game in this group...')

        else if self.num_games >= self.MAX_NUMBER_OF_GAMES:
            raise GhostGameEngineException(
                'Too many ongoing games... Please wait...')

        new_game = GhostGame()
        self.games[game_id] = new_game
        self.num_games += 1
        return new_game

    def __check_game_exists(self, game_id: int) -> None:
        if game_id not in self.games:
            raise GhostGameEngineException(
                'Game does not exist')

    def __get_game_from_game_id(self, game_id: int) -> GhostGame:
        self.__check_game_exists(game_id)
        return self.games[game_id]

    def __get_game_from_host(self, host: str) -> GhostGame:
        game_id = self.get_game_id_from_host(host)
        return self.__get_game_from_game_id(game_id)

    def __get_game_id_from_host(self, host: str): -> int:
        if host not in self.hosts:
            raise GhostGameEngineException(
                'You are not the host of any game')

        return self.hosts_to_game_id[host]

    def __get_host_from_game_id(self, game_id: int): -> str:
        self.__check_game_exists(game_id)
        return self.hosts_to_game_id.inverse[game_id]

    def delete_game(self, game_id: int) -> None:
        self.__check_game_exists()
        del self.games[game_id]
        self.num_games -= 1

        host = self.get_host_from_game_id(game_id)
        del self.hosts_to_game_id[host]

    # Wrappers for GhostGame
    def set_param_num_players(self, host: str, value: int) -> None:
        game = self.__get_game_from_host(host)
        game.set_param_num_players(value)

    def set_param_town_word(self, host: str, value: str) -> None:
        game = self.__get_game_from_host(host)
        game.set_param_town_word(value)

    def set_param_fool_word(self, host: str, value: str) -> None:
        game = self.__get_game_from_host(host)
        game.set_param_fool_word(value)

    def start_game(self, game_id: int) -> None:
        game = self.__get_game_from_game_id(game_id)
        game.start_game()

    def set_clue(self, game_id: int, username: str, clue: str) -> None:
        game = self.__get_game_from_game_id(game_id)
        self.__check_game_exists()
        game = self.games[game_id]
        game.set_clue(username, clue)

    def is_clues_complete(self, game_id: int) -> bool:
        game = self.__get_game_from_game_id(game_id)
        return game.is_clues_complete() 

    def set_vote(self, game_id: int, username: str, vote: str) -> None:
        game = self.__get_game_from_game_id(game_id)
        game.set_clue(username, clue)

    def is_votes_complete(self, game_id: int) -> bool:
        game = self.__get_game_from_game_id(game_id)
        return game.is_votes_complete() 

    def set_guess(self, game_id: int, username: str, guess: str) -> None:
        game = self.__get_game_from_game_id(game_id)
        game.set_guess(username, clue)

    def is_game_complete(self, game_id: int) -> bool:
        game = self.__get_game_from_game_id(game_id)
        return game.is_game_complete() 
