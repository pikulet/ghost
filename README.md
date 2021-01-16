# :ghost: ghost :ghost:

Python engine for the word game of ghost (as played on epicmafia). Implemented using a finite state machine style.

## :firecracker: Usage

To build games using this engine, run:

`pip3 install ghost_word_game`

`import ghost`

Example:

```
# Create engine, which can manage multiple games
ge = ghost.GhostEngine()

gid = 1129837
host = 'jermyn'

create_game(ge, gid, host, VALID_PLAYERS, VALID_TW, VALID_FW)

# Retrieve the generated roles, then you need to inform players of their roles
roles = ge.get_player_roles(gid)

# Players now give clues on their words. 
# All players need to give clues so loop this for the number of players in the game.
p = ge.get_next_in_player_order(gid)
is_complete = ge.set_clue(gid, p, 'example clue ' + p)

# Retrieve all clues given by all users
clues = ge.get_all_clues(gid)

# Once the clues are given, players can vote
is_success, is_complete, lynched = ge.set_vote(gid, p, players[0])

# When all players have voted, the engine will delete the lynched player
# Depending on that player's role, the game state changes to 
# GUESS_ROUND (ghost lynched), VOTE_ROUND (town lynched) or WINNER_GHOST (town lynched into ghost majority)
state = ge.get_game_state(gid)

# allow the ghost to guess
if state == ghost.States.GUESS_ROUND:
    is_success, is_correct = ge.make_guess(gid, lynched, VALID_TW)

```

## :wrench: Some quik tools

Wrote some shell scripts to make it faster to run tests and upload the package to PyPi.

`bash run_tests.sh` and `upload_pkg.sh` can be used. Remember to do the relevant config in `setup.py` before uplaoding to PyPi.

## :seedling: Notes

Currently, my sister is building a Telegram bot that utilises this engine. You're also free to develop the Ghost game using this engine!
Looking forward to suggestions ^^
