from bidict import bidict
from ghost import Ghost

class GhostEngine:

    class GhostEngineException(Exception):
        pass

    def __init__(self, max_games = 4):
        self.__MAX_NUMBER_OF_GAMES = max_games
        self.__games = dict()                   # game_id to game
        self.__hosts_to_game_id = bidict()      # host to game_id
        self.__player_to_game_id = dict()     # username to game_id

    def add_game(self, game_id: int, host: str) -> None:
        ''' Creates a game in the engine '''
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
        self.__ghost_to_game_id[host] = game_id

    def delete_game(self, game_id: int) -> None:
        ''' Removes a game from the engine '''
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

    def __check_player_exists(self, username: str) -> None:
        if player not in self.__username_to_game_id:
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

    def __get_game_id_from_player(self, username: str) -> int:
        self.__check_player_exists(username)
        return self.__player_to_game_id[username]

    def __get_players_from_game_id(self, game_id: int) -> set:
        self.__check_game_exists(game_id)
        game = self.__get_game_from_game_id(game_id)
        # TODO
        return game.get_players() 

    ''' PHASE: REGISTER PLAYERS '''

    def register_player(self, game_id: int, player: str) -> int:
        ''' Returns the number of players registered in the game '''
        game = self.__get_game_from_game_id(game_id)
        return game.register_player(player)

    def start_game(self, game_id: int) -> None:
        game = self.__get_game_from_game_id(game_id)
        game.start_game()
        
    ''' PHASE: SET PARAM '''

    def set_param_town_word(self, host: str, value: str) -> None:
        game_id = self.__get_game_id_from_host(host)
        game = self.__get_game_from_game_id(game_id)
        game.set_param_town_word(value)

    def set_param_fool_word(self, host: str, value: str) -> None:
        game_id = self.__get_game_id_from_host(host)
        game = self.__get_game_from_game_id(game_id)
        game.set_param_fool_word(value)

    ''' PHASE: ROLE SETUP '''

    def get_player_roles(self, game_id: int) -> dict:
        game = self.__get_game_from_game_id(game_id)
        return game.get_player_roles()

    ''' PHASE: CLUES '''

    def get_next_clue_giver(self, game_id: int) -> str:
        ''' Return username of next person to give clue, empty string if all
        clues have been given '''
        game = self.__get_game_from_game_id(game_id)
        return game.get_next_clue_giver()

    def set_clue(self, game_id: int, player: str, clue: str) -> None:
        game = self.__get_game_from_game_id(game_id)
        game.set_clue(player, clue)

    def retrieve_all_clues(self, game_id: int) -> dict:
        game = self.__get_game_from_game_id(game_id)
        return game.retrieve_all_clues()

    ''' PHASE: VOTE '''

    def set_vote(self, game_id: int, player: str, vote: str) -> e:
        game = self.__get_game_from_game_id(game_id)
        game.set_vote(player, vote)
        if game.is_vote_phase_complete():
            to_lynch = game.end_vote_phase()
            if game.is_ghost(to_lynch):
                # TODO: notify bot
                pass
            elif game.is_game_complete():
                # TODO: notify bot
                winner = game.get_winning_team()
            else:
                # TODO: notify bot
                pass

    ''' PHASE: GUESS '''

    def make_guess(self, game_id: int, player: str, guess: str) -> None:
        game = self.__get_game_from_game_id(game_id)
        game.make_guess(player, guess)
        if game.is_game_complete():
            winner = game.get_winning_team()
            # TODO: notify bot

