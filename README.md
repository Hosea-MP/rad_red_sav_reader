
# RadicalRed Savegame Editor

NOTE: This is a fork of [This](https://gitlab.com/old22/radicalred-savegame-editor) gitlab repository from 2021

Includes functions for loading Radical Red
savegames, editing team Pokemons and saving
the result into a legit savegame. Currently, it can:

* Load and save valid Radical Red / Fire Red saves.
* Clone and export first team Pokemon.
* Create 'valid' Radical Red Pokemons. All of them
  were caught at Pallet Town, which makes them not
  100% legit.

# Updating Procedure

1. Update pokemon abilities / availability in _pokemon.json
2. run sync_db_and_dex

## Code dependencies

1. [PokeAPI Docs](https://pokeapi.co/docs/v2)
2. [Pokebase Docs](https://github.com/PokeAPI/pokebase)