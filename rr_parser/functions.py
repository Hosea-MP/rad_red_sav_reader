from typing import Union, Optional
import csv

from .games import Gen3, RadicalRed
from .pkms import Pokemon, BoxPokemon
from .pkm_builder import pkm_builder
from .exceptions import InvalidSizeException
from .constants.rr import get_species_pokedex_id
from .enums import PokedexEntryState, GameType

from .pkm_builder import NATURES
from .sections import MAX_BOXES

from . import constants

import pokebase as pb

def clone_first_team_pkm(game: Gen3) -> bool:
    """Clone first team Pokemon into the next free team slot.

    Parameters
    ----------
    game : Gen3
        Gen3 game save class instance.

    Returns
    -------
    bool
        Whether the Pokemon was successfully cloned.
    """
    if 0 < game.game_save.team.team_size < 6:
        pk0: Pokemon = game.game_save.team.team_pokemon_list[0]
        game.set_pokemon(pk0, game.game_save.team.team_size)
        assert game.check_valid()
        st: bool = True
        pass
    else:
        st: bool = False
        pass
    return st


def export_first_team_pkm(game: Gen3, output: str):
    """Export the first team Pokemon.

    The leading Pokemon is saved in the ``output`` file as a 100-byte
    binary file.

    Parameters
    ----------
    game : Gen3
        The loaded Pokemon savegame.
    output : str
        Output path.

    Raises
    ------
    ChecksumException
        If the first team Pokemon is invalid.

    """
    pkm: Pokemon = game.game_save.team.team_pokemon_list[0]
    # if not pkm.check():
    #     raise ChecksumException("First team Pokemon is not valid.")
    pkm_filename = output
    with open(pkm_filename, 'wb') as f:
        f.write(pkm.data)
        pass
    pass

def species_rr_to_nat_dex(species_rr):
    assert(species_rr < constants.rr._species.NUM_SPECIES)

    for v in dir(constants.rr._species)[::-1]:
        if getattr(constants.rr._species, v) == species_rr:
            name = v[v.find('_')+1:]
            return getattr(constants.rr._pokedex, f'NATIONAL_DEX_{name}')
    raise Exception(f'Species not found: {species_rr}')

def species_rr_to_str(species_rr):
    assert(species_rr < constants.rr._species.NUM_SPECIES)
    for v in dir(constants.rr._species)[::-1]:
        if getattr(constants.rr._species, v) == species_rr:
            name = v[v.find('_')+1:]
            return name.replace('__', '-').replace('_', ' ').title()
    raise Exception(f'Species not found: {species_rr}')

def species_rr_str_to_nat_dex(name):
    s = name.replace('-', '__').replace(' ', '_').upper()
    return getattr(constants.rr._pokedex, 'NATIONAL_DEX_'+s)

def move_rr_to_name(move_rr):
    if move_rr == 0:
        return None
    
    FP = 'rr_parser\\constants\\rr\\move_names.tsv'

    with open(FP, 'r') as f:
        rd = csv.reader(f, delimiter='\t')
        for row in rd:
            if int(row[0], 16) == move_rr:
                return row[1].title()

def item_rr_to_name(item_rr):
    return constants.rr._items.items_dict[str(item_rr)]

import json
from pathlib import Path
PKM_DB_PATH = Path(__file__).resolve().parent / "constants" / "rr" / "_pokemon.json"
with open(PKM_DB_PATH) as f:
    PKM_DB = json.load(f)
def pkm_set_to_text(pkm: Union[Pokemon, BoxPokemon], level:int = None):
    """Example Output:
            Piplup @ Oran Berry
            Rash Nature
            Ability: Torrent
            EVs: 3 HP / 2 Atk / 1 SpA / 2 SpD / 1 Spe
            IVs: 22 HP / 6 Atk / 30 Def / 8 SpA / 23 SpD / 27 Spe
            - Pound
            - Bubble
            - Growl

    Notes:
    """
    species = species_rr_to_str(pkm.sub_data_decrypted.species)
    pkm_db_entry = PKM_DB[str(species_rr_str_to_nat_dex(species))]
    nature = list(NATURES.keys())[pkm.sub_data_decrypted.nature].capitalize()
    item = pkm.sub_data_decrypted.growth.item
    if level is None:
        level = pkm.level

    ability = pkm_db_entry['abilities'][pkm.sub_data_decrypted.misc.ability] if pkm.sub_data_decrypted.hidden_ab==0 \
          else pkm_db_entry['abilities'][-1]
    ability = ability.replace('-', ' ').title()


    set_str = f'{species}'
    set_str += f' @ {item_rr_to_name(item)}\n' if item != 0 else '\n'
    set_str += f'Level: {level}\n'
    set_str += f'{nature} Nature\n'
    set_str += f'Ability: {ability}\n'

    set_str += 'EVs: '
    set_str += ' / '.join('{0} {1}'.format(val, stat) for stat, val in zip([
                            "HP", "Atk", "Def",
                            "Spe", "SpA", "SpD"
                        ],
                        pkm.sub_data.evs))
    
    set_str += '\nIVs: '
    set_str += ' / '.join('{0} {1}'.format(val, stat) for stat, val in zip([
                            "HP", "Atk", "Def",
                            "Spe", "SpA", "SpD"
                        ],
                        pkm.sub_data.misc.IVs))
    set_str+='\n'
    moves = pkm.sub_data_decrypted.attacks.moves
    for move in moves:
        if move != 0:
            set_str+=f'- {move_rr_to_name(move)}\n'

    return set_str

def export_pkm_sets_for_calc(game: Gen3, output: str, 
                   box_range: tuple[int, int]=None, 
                   skip_boxes:list[int]=None,
                   level: int = None):
    """Export all pokemon in the player team plus all of the pokemon in the PC
    
    """

    
    with open(output, 'w') as f:
        for pokemon in game.game_save.team.team_pokemon_list[:game.game_save.team.team_size]:
            set_str = pkm_set_to_text(pokemon)
            f.write(set_str)
            f.write('\n\n')
        
        
        boxes = set(range(MAX_BOXES))
        if box_range is not None:
            boxes = boxes.intersection(set(range(*box_range)))
        if skip_boxes is not None:
            boxes = boxes - set(skip_boxes)
        boxes = list(boxes)
        boxes.sort()

        if len(boxes) > 0 and level is None:
            raise NotImplementedError('Box exports need a fixed level. Please pass `level`')

        for box_id in boxes:
            box = game.game_save.pc.boxes[box_id]
            for pokemon in box.pokemon:
                # Empty slot
                if pokemon.sub_data_decrypted.growth.species == 0:
                    continue
                set_str = pkm_set_to_text(pokemon, level)
                f.write(set_str)
                f.write('\n\n')
                
            

    print(f'Exported pokemon sets to ``{output}``')


def load_radical_red_game(inp: str) -> RadicalRed:
    """Load the Pokemon Radical Red savegame.

    Parameters
    ----------
    inp : str
        Path to the savegame.

    Returns
    -------
    RadicalRed
        Pokemon Radical Red savegame class.

    Raises
    ------
    InvalidSizeException
        If savegame sized is not 128KiB.
    """

    with open(inp, "rb") as f:
        b = f.read()
        pass
    if len(b) != 131088:
        raise InvalidSizeException("Savegame size is not 128 KiB.")
    return RadicalRed(b)


def save_game(game: Gen3, output: str):
    """Save the Pokemon Radical Red or Fire Red savegame.

    Parameters
    ----------
    game : Gen3
        Radical Red / Fire Red savegame class to save.
    output : str
        Path to the output savegame.

    Raises
    ------
    InvalidSizeException
        If savegame sized is not 128KiB.
    """
    game.save(output)
    pass


def create_and_insert_pokemon(
        game: Gen3,
        species: str,
        level: int = 5,
        ot_name: Optional[str] = None,
        ot_id: Optional[int] = None,
        ot_gender: Optional[str] = None,
        ability: Optional[int] = None,
        nature: Union[int, str, None] = None,
        evs: Optional[list[int]] = None,
        ivs: Optional[list[int]] = None,
        shiny: bool = False
) -> tuple[Pokemon, bool]:
    """Create and insert Pokemon on team from input arguments.

    In case of full team (6 Pokemon), the Pokemon file is created but
    not inserted.

    Parameters
    ----------
    game : Gen3
        Radical Red / Fire Red savegame class instance in which the Pokemon
        is inserted.
    species : str
        Generated Pokemon species name, case insensitive.
    level : int
        Generated Pokemon level, 5 by default.
    ot_name : Optional[str]
        Generated Pokemon's Original Trainer name, 7 characters maximum and
        international charsets only. If None, use game's Trainer name.
    ot_id : Optional[int]
        Generated Pokemon's Original Trainer's full ID (secret and public)
        consisting on a 32 bit/4 byte integer. If None, use game's Trainer ID.
    ot_gender : Optional[str]
        Generated Pokemon's Original Trainer's gender, case insensitive 'Boy'
        or 'Girl'. If bad gender input or None, use game's Trainer gender.
    ability : Optional[int]
        Generated Pokemon ability, 1, 2, 3 or None (default None):
            * If 1, first normal ability.
            * If 2, second normal ability (1 if second ability not available).
            * If 3, hidden ability (1 if not available).
            * If None, random normal ability.
    nature : Union[int, str, None]
        Generated Pokemon nature:
            * If type int, nature identifier 0 to 24.
            * If type str, case insensitive nature name.
            * If bad input or None (default), random nature.
    evs : Optional[list[int]]
        Generated Pokemon EVs:
            * If list[int], list of HP, ATTACK, DEFENSE, SPEED, SP. ATTACK and
              SP: DEFENSE EVs.
            * If None or bad input (default), set 0 EVs on all stats.
    ivs : Optional[list[int]]
        Generated Pokemon IVs:
            * If list[int], list of HP, ATTACK, DEFENSE, SPEED, SP. ATTACK and
              SP: DEFENSE IVs.
            * If None or bad input (default), set random IVs on all stats.
    shiny : bool
        Whether the generated Pokemon is shiny or not.

    Returns
    -------
    tuple[Pokemon, bool]
        Generated Pokemon and its game insertion status.
    """
    # Normalize input.
    if ot_name is None:
        ot_name: str = game.game_save.trainer_info.player_name
        pass
    else:
        if len(ot_name) > 7:
            raise InvalidSizeException("OT name length higher than 7.")
        pass
    if ot_id is None:
        ot_id: int = game.game_save.trainer_info.trainer_id
        pass
    else:
        try:
            ot_id.to_bytes(4, 'little')
        except OverflowError:
            raise InvalidSizeException("OT ID size higher than 32 bits.")
        pass
    if ot_gender is None:
        ot_gender: str = game.game_save.trainer_info.player_gender
        pass
    else:
        if not (
                ot_gender.lower().startswith('b') or
                ot_gender.lower().startswith('g')
        ):
            ot_gender: str = game.game_save.trainer_info.player_gender
            pass
        pass

    # Create Pokemon.
    pk0 = pkm_builder(
        gen=game.gt,
        species=species,
        level=level,
        ot_name=ot_name,
        ot_id=ot_id,
        ot_gender=ot_gender,
        ability=ability,
        nature=nature,
        evs=evs,
        ivs=ivs,
        shiny=shiny
    )

    # If free space is available, set Pokemon.
    if game.game_save.team.team_size < 6:
        game.set_pokemon(pk0, game.game_save.team.team_size)
        assert game.check_valid()
        set_pokedex_entry(
            game,
            species,
            PokedexEntryState(PokedexEntryState.CAUGHT)
        )
        st: bool = True
        pass
    else:
        print("W: Team is full, unable to insert created Pokemon.")
        st: bool = False
        pass
    return pk0, st


def set_pokedex_entry(
        game: Gen3,
        species: Union[str, int],
        state: PokedexEntryState = PokedexEntryState(PokedexEntryState.SEEN)):
    """Set Pokemon species entry state.

    Parameters
    ----------
    game : Gen3
        Game class instance.
    species : Union[str, int]
        Species case insensitive name or Pokedex entry number (1 or higher).
    state : PokedexEntryState
        Pokedex entry state:
            PokedexEntryState.UNSEEN: unlocked entry.
            PokedexEntryState.SEEN: Pokemon seen.
            PokedexEntryState.CAUGHT: Pokemon seen and caught.
    """

    if isinstance(species, int):
        species_int: int = species
        pass
    elif isinstance(species, str):
        _temp = get_species_pokedex_id(species)
        if _temp is None:
            raise Exception("Pokemon species not found: '{}'.".format(species))
        species_int: int = _temp
        pass
    else:
        raise NotImplemented
    assert species_int > 0

    if state == PokedexEntryState(PokedexEntryState.UNSEEN):
        game.game_save.pokedex.unset_seen(species_int)
        game.game_save.pokedex.unset_caught(species_int)
    elif state == PokedexEntryState(PokedexEntryState.SEEN):
        game.game_save.pokedex.set_seen(species_int)
        game.game_save.pokedex.unset_caught(species_int)
        pass
    elif state == PokedexEntryState(PokedexEntryState.CAUGHT):
        game.game_save.pokedex.set_seen(species_int)
        game.game_save.pokedex.set_caught(species_int)
        pass
    else:
        raise NotImplemented
        pass
    pass

    game.update_from_sub_data()
    pass


def clear_pokedex(game: Gen3):
    """Clear all pokedex entries.

    Parameters
    ----------
    game : Gen3
        Game class instance whose Pokedex is to be cleared.
    """

    s: int = game.game_save.pokedex.pokedex_size_bytes
    new_seen_data: bytes = bytes(s)
    new_caught_data: bytes = bytes(s)
    game.game_save.pokedex.data_seen = new_seen_data
    game.game_save.pokedex.data_caught = new_caught_data
    game.update_from_sub_data()
    pass


def complete_pokedex(game: Gen3):
    """Fill all pokedex entries.

    Parameters
    ----------
    game : Gen3
        Game class instance whose Pokedex is to be completed.
    """

    s: int = game.game_save.pokedex.pokedex_size_bytes
    new_seen_data: bytes = bytes([0xFF] * s)
    new_caught_data: bytes = bytes([0xFF] * s)
    game.game_save.pokedex.data_seen = new_seen_data
    game.game_save.pokedex.data_caught = new_caught_data
    game.update_from_sub_data()
    pass


def set_money(game: Gen3, money: int):
    """Set player's money amount.

    Parameters
    ----------
    game : Gen3
        Game whose money value is to be changed.
    money : int
        New money amount. Must fit within 4 bytes.
    """
    trainer_info = game.game_save.trainer_info
    team = game.game_save.team

    # sec_key = int.from_bytes(trainer_info.section[0x0AF8:0x0AF8 + 4], 'little')
    sec_key = int.from_bytes(trainer_info.section[0x0F20:0x0F20 + 4], 'little')

    if game.gt == GameType(GameType.RR):
        # money = 9999999
        sec_money = money
        pass
    elif game.gt == GameType(GameType.FR):
        # money = 999999
        sec_money = money ^ sec_key
        pass
    else:
        raise NotImplemented

    data = bytearray(team.section)
    data[0x0290:0x0290 + 4] = sec_money.to_bytes(4, 'little')
    game.game_save.sections[1].section = bytes(data)

    # team.section = bytes(data)
    # team.update()
    game.game_save.update_from_sub_data()
    game.update_from_sub_data()
    pass


def infinite_money(game: Gen3):
    """Set player's money amount to max.

    Parameters
    ----------
    game : Gen3
        Game whose money value is to be maxed.
    """
    if game.gt == GameType(GameType.RR):
        set_money(game, 9999999)
        pass
    elif game.gt == GameType(GameType.FR):
        set_money(game, 999999)
        pass
    else:
        raise NotImplemented
    pass


__all__ = [
    "export_first_team_pkm",
    "clone_first_team_pkm",
    "load_radical_red_game",
    "save_game",
    "create_and_insert_pokemon",
    "set_pokedex_entry",
    "clear_pokedex",
    "complete_pokedex",
    "infinite_money",
    "set_money"
]
