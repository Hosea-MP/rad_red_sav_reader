from typing import Union, Optional

from .games import Gen3, RadicalRed
from .pkms import Pokemon
from .pkm_builder import pkm_builder
from .exceptions import InvalidSizeException
from .constants.rr import get_species_pokedex_id
from .enums import PokedexEntryState, GameType


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
    if len(b) != 131072:
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
