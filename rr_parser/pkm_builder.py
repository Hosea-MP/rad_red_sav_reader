from typing import Optional, Union, Any
from math import floor
from random import random
import re
import pokebase as pb

from .pkms import Pokemon, DecryptedData
from .enums import GameType
from .constants.rr import get_species_learnset, get_species_id, MoveLevel

NATURES = {
    "Hardy": 0,
    "Lonely": 1,
    "Brave": 2,
    "Adamant": 3,
    "Naughty": 4,
    "Bold": 5,
    "Docile": 6,
    "Relaxed": 7,
    "Impish": 8,
    "Lax": 9,
    "Timid": 10,
    "Hasty": 11,
    "Serious": 12,
    "Jolly": 13,
    "Naive": 14,
    "Modest": 15,
    "Mild": 16,
    "Quiet": 17,
    "Bashful": 18,
    "Rash": 19,
    "Calm": 20,
    "Gentle": 21,
    "Sassy": 22,
    "Careful": 23,
    "Quirky": 24
}

STATS = {
    "HP": 0,
    "ATTACK": 1,
    "DEFENSE": 2,
    "SPEED": 3,
    "SPECIAL-ATTACK": 4,
    "SPECIAL-DEFENSE": 5
}


def _level(level: int) -> int:
    assert (0 < level <= 100)
    return level


def _species_no(gen: GameType, species: str, pkm: Any):
    if gen == GameType(GameType.FR):
        species_no: int = pkm.id
        pass
    elif gen == GameType(GameType.RR):
        species_no: int = get_species_id(species)
        pass
    else:
        raise NotImplemented
    return species_no


def _ability(
        gen: GameType,
        ability: Optional[int],
        pkm: Any) -> tuple[int, bool]:
    """Get the ability number (1 or 2) and whether the ability is hidden.

    Parameters
    ----------
    gen : GameType
        Savegame type.
    ability : Optional[int]
        If None, select random non-hidden ability, else check ability number
        is valid.
    pkm : Any
        PokeAPI Pokemon resource for getting available abilities.

    Returns
    -------
    tuple[int, bool]
        Tuple with the ability number (1 or 2, for first or second ability
        if any) and if this ability is hidden. If hidden, instead of ability
        3, 1 is used as RadicalRed uses this flag elsewhere.
    """
    # Get species number of abilities.
    max_abs = 0
    has_hidden = 0
    for _ab in pkm.abilities:
        if not _ab.is_hidden:
            max_abs = max_abs + 1
            pass
        elif _ab.is_hidden:
            has_hidden = has_hidden + 1
            pass
        pass

    # No ability requirements, use any.
    if ability is None:
        ab: int = round(random()) * (max_abs - 1) + 1
        hidden: bool = False
        pass

    # Assert first or second abilities.
    else:
        if gen == GameType(GameType.FR):
            assert (1 <= ability <= 2)
            ab: int = (ability - 1) * (max_abs - 1) + 1
            hidden = False
            pass
        elif gen == GameType(GameType.RR):
            assert (1 <= ability <= 3)
            if ability == 3:
                ab: int = 1
                hidden: bool = has_hidden == 1
                pass
            else:
                ab: int = ability
                hidden = False
            pass
        else:
            raise NotImplemented
        pass

    return ab, hidden


def _nature(nature: Optional[int]) -> int:
    # Set and/or assert nature.
    if nature is None:
        nat: int = round(random() * 24) % 25
        pass
    elif isinstance(nature, str):
        nat: int = NATURES[nature.capitalize()]
        pass
    else:
        assert (0 <= nature <= 24)
        nat: int = nature
        pass
    return nat


def _evs(evs: Optional[list[int]]) -> list[int]:
    # Check evs.
    if evs is None:
        evs = [0] * 6
        pass
    assert (len(evs) == 6)
    s = 0
    for ev in evs:
        assert (0 <= ev <= 255)
        s += ev
        pass
    assert (s <= 510)
    return evs


def _ivs(ivs: Optional[list[int]]) -> list[int]:
    # Check ivs.
    if ivs is None:
        ivs = [round(random() * 31) for _ in range(0, 6)]
        pass
    assert (len(ivs) == 6)
    for iv in ivs:
        assert (0 <= iv <= 31)
        pass
    return ivs


def _pid(ability: int, nature: int, ot_id: int, shiny: bool) -> int:
    if shiny:
        ot_id_p = ot_id & ((1 << 16) - 1)
        ot_id_s = (ot_id >> 16) & ((1 << 16) - 1)
        for s in range(0, 8):
            k = s ^ ot_id_p ^ ot_id_s
            for p2 in range(0, 65536):
                p1 = k ^ p2
                pid = (p1 << 16) | p2
                if (pid % 2 == ability) and (pid % 25 == nature):
                    return pid
                pass
            pass
        pass

    # Generate new PID.
    if nature == 0 and ability == 0:
        pid = 50
        pass
    elif nature == 0 and ability == 1:
        pid = 25
        pass
    else:
        c = nature - ability
        if c % 2 == 0:
            pid = 50 + nature
            pass
        else:
            pid = 25 + nature
            pass
        pass
    return pid


def _ot_name_bytes(ot_name: str) -> bytes:
    # Set this OT name.
    ot_name_bytes: bytes = Pokemon.ascii2bin(ot_name)
    if isinstance(ot_name_bytes, int):
        ot_name_bytes = bytes([ot_name_bytes] + [0xFF] * 6)
    elif len(ot_name_bytes) < 7:
        # Push 0xFF until fill.
        ot_name_bytes = ot_name_bytes + bytes(
            [0xFF] * (7 - len(ot_name_bytes))
        )
        pass
    return ot_name_bytes


def _nick(pkm_species: Any) -> bytes:
    # Get pokemon name.
    nick: str = pkm_species.name.upper()
    nick_bytes: bytes = Pokemon.ascii2bin(nick)
    if len(nick_bytes) < 10:
        # Push 0xFF until fill.
        nick_bytes = nick_bytes + bytes([0xFF] * (10 - len(nick_bytes)))
        pass
    return nick_bytes


def _growth_block(gen: GameType, species_no: int, lvl: int, pkm_species: Any) -> bytes:
    # Get growth rate.
    gr_name = pkm_species.growth_rate.name
    gr = pb.growth_rate(gr_name)

    # Get experience at said growth rate.
    exp: int = gr.levels[lvl-1].experience

    # Growth sub-data block.
    growth: bytearray = bytearray(12)
    if gen == GameType(GameType.FR):
        growth[0:2] = species_no.to_bytes(2, 'little')
        growth[4:8] = exp.to_bytes(4, 'little')
        growth[9:10] = (20).to_bytes(1, 'little')
    elif gen == GameType(GameType.RR):
        growth[0:2] = species_no.to_bytes(2, 'little')
        growth[4:8] = exp.to_bytes(4, 'little')
        growth[9:10] = (20).to_bytes(1, 'little')
        growth[10:11] = (3).to_bytes(1, 'little')  # Caught pokeball!.
        pass
    else:
        raise NotImplemented

    assert (len(growth) == 12)
    return bytes(growth)
    pass


def _get_species_attacks_by_level(species: int, gt: GameType) -> list[MoveLevel]:
    pk = pb.pokemon(species)

    move_list = list()

    for move in pk.moves:
        version_group_detail: Optional[Any] = None
        for vgd in move.version_group_details:
            if gt == GameType(GameType.FR) and vgd.version_group.name == "firered-leafgreen":
                version_group_detail = vgd
                pass
            elif gt == GameType(GameType.RR) and vgd.version_group.name == "ultra-sun-ultra-moon":
                version_group_detail = vgd
                pass
            pass
        if version_group_detail is not None:
            if version_group_detail.move_learn_method.name == "level-up":
                learn_level: int = version_group_detail.level_learned_at
                id_match = re.search(r"/move/(?P<id>[0-9]+)/?$", move.move.url)
                move_id = int(id_match.group("id"))
                move_api = pb.move(move_id)
                pp = move_api.pp
                mv = MoveLevel(
                    id=move_id,
                    lvl=learn_level,
                    pp=pp,
                    name=move.move.name
                )
                move_list.append(mv)
                pass
            else:
                # Skip non-leveled moves.
                pass
            pass
        else:
            # Skip: generation restriction unmatched.
            pass
        pass
    return move_list


def _get_rr_species_attacks_by_level(species: str) -> list[MoveLevel]:
    return get_species_learnset(species)


def _attacks_block(gen: GameType, lvl: int, species_no: int, species: str):
    # Attack sub-data block.
    if gen == GameType(GameType.FR):
        moves: list[MoveLevel] = _get_species_attacks_by_level(species_no, gen)
        pass
    elif gen == GameType(GameType.RR):
        moves: list[MoveLevel] = _get_rr_species_attacks_by_level(species)
        pass
    else:
        raise NotImplemented

    moves.sort(key=lambda move: move.lvl, reverse=True)
    if moves[-1].lvl == 0:
        moves.pop()
        pass
    while moves[0].lvl > lvl:
        moves.pop(0)
        pass
    max_moves = min(4, len(moves))
    attacks: bytearray = bytearray(12)
    for i in range(0, max_moves):
        attacks[i * 2:(i + 1) * 2] = moves[i].id.to_bytes(2, 'little')
        attacks[8 + i:8 + i + 1] = moves[i].pp.to_bytes(1, 'little')
        pass
    for i in range(max_moves, 4):
        # Use empty.
        # attacks[i * 2:(i + 1) * 2] = bytes([0xFF] * 2)
        # attacks[8 + i:8 + i + 1] = bytes([0xFF])
        pass
    assert (len(attacks) == 12)
    return bytes(attacks)


def _evs_block(evs: list[int]) -> bytes:
    evs_block: bytearray = bytearray(12)
    for i in range(0, 6):
        evs_block[i:i + 1] = evs[i].to_bytes(1, 'little')
        pass
    assert (len(evs_block) == 12)
    return bytes(evs_block)


def _misc_block(
        gen: GameType,
        lvl: int,
        ot_gender: str,
        ability: int,
        hidden_ab: bool,
        ivs: list[int]) -> bytes:
    """Pokemon Misc sub-data block.

    For RadicalRed information, see:
    https://github.com/Skeli789/Complete-Fire-Red-Upgrade/blob/c884d332eae3a16a8e8f588ad95abc5ec1ff2abe/include/pokemon.h
    """
    # Pokerus.
    pokerus: bytes = bytes(1)

    # Met location: Pueblo Paleta.
    if gen == GameType(GameType.FR):
        met_loc: bytes = bytes([0x58])
        pass
    elif gen == GameType(GameType.RR):
        met_loc: bytes = bytes([0x58])
        pass
    else:
        raise NotImplemented

    # IVs, eggs and abilities.
    iv_egg_ability = 0
    for i in range(0, 6):
        iv_egg_ability = iv_egg_ability | (ivs[i] << (5 * i))
        pass
    if gen == GameType(GameType.FR):
        iv_egg_ability = iv_egg_ability | ((ability - 1) << 31)
    elif gen == GameType(GameType.RR):
        # Hidden ability.
        if hidden_ab:
            iv_egg_ability = iv_egg_ability | (1 << 31)
            pass
        pass

    iv_egg_ability_bytes = iv_egg_ability.to_bytes(4, 'little')

    # Ribbons and obedience.
    obedience: int = 0

    misc_block: bytearray = bytearray(12)

    if gen == GameType(GameType.FR):
        # Pokemon origins.
        origins = 0
        # Caught in FireRed.
        if gen == GameType(GameType.FR) or gen == GameType(GameType.RR):
            origins = origins | (4 << 7)
            pass
        # Caught in pokeball.
        if gen == GameType(GameType.FR):
            origins = origins | (4 << 11)
            pass
        elif gen == GameType(GameType.RR):
            # origins = origins | (4 << 11)
            origins = origins | (1 << 13)
            pass
        # Level met.
        origins = origins | lvl
        # OT gender.
        if ot_gender.lower().startswith('b'):
            pass
        elif ot_gender.lower().startswith('g'):
            origins = origins | (1 << 15)
            pass
        origins_bytes = origins.to_bytes(2, 'little')

        misc_block[0:1] = pokerus
        misc_block[1:2] = met_loc
        misc_block[2:4] = origins_bytes
        misc_block[4:8] = iv_egg_ability_bytes
        misc_block[8:12] = obedience.to_bytes(4, 'little')
        pass
    elif gen == GameType(GameType.RR):
        # Totally different misc block.

        met_level_game_gender: int = 0
        met_level_game_gender = met_level_game_gender | lvl  # Level: lvl
        met_level_game_gender = met_level_game_gender | (4 << 7)  # Game: FR
        met_level_game_gender = met_level_game_gender | (
                (0 if ot_gender.lower().startswith('b') else 1) << 15
        )  # Gender

        misc_block[0:1] = pokerus
        misc_block[1:2] = met_loc
        misc_block[2:4] = met_level_game_gender.to_bytes(2, 'little')
        misc_block[4:8] = iv_egg_ability_bytes
        misc_block[8:12] = obedience.to_bytes(4, 'little')
        pass
    else:
        raise NotImplemented

    assert (len(misc_block) == 12)
    return bytes(misc_block)


def nat_modifier(i: int, nat: int) -> float:
    """Get the nature 'nat' stat modification value (0.9, 1.0 or 1.1)
    for stat 'i'.
    """

    inc_stat = 1 + floor(nat / 5)  # Skip HP stat with +1.
    dec_stat = 1 + (nat % 5)

    if inc_stat == i:
        return 1.1
    elif dec_stat == i:
        return 0.9
    else:
        return 1.0
    pass


def _stats(pkm: Any, lvl: int, nat: int, evs: list[int], ivs: list[int]) -> dict[int]:
    # Get pokemon species base stats.
    db_stats = pkm.stats
    base_stats: dict[int, int] = dict()
    for st in db_stats:
        bs: int = st.base_stat
        name: str = st.stat.name
        base_stats[STATS[name.upper()]] = bs
        pass

    # Stat calculation (pokexperto: https://www.pokexperto.net/index2.php?seccion=mecanica/genetica34).
    stats: dict[int, int] = dict()
    stats[0] = 10 + (evs[0] >> 2) + lvl + (
        floor(lvl * ((base_stats[0] * 2) + ivs[0]) / 100)
    )

    for i in range(1, 6):
        stats[i] = floor(
            (
                    5 +
                    (evs[i] >> 2) +
                    (
                            lvl * ((base_stats[i] * 2) + ivs[i]) / 100
                    )
            ) * nat_modifier(i, nat)
        )
        pass
    return stats


def pkm_builder(
        gen: GameType,
        species: str,
        level: int = 5,
        ot_name: str = "ISD",
        ot_id: int = 123456789,
        ot_gender: str = "Boy",
        ability: Optional[int] = None,
        nature: Optional[Union[str, int]] = None,
        evs: Optional[list[int]] = None,
        ivs: Optional[list[int]] = None,
        shiny: bool = False
):
    # Get online data.
    pkm_species = pb.pokemon_species(species)
    pkm = pb.pokemon(pkm_species.id)

    # Parse input data.
    lvl = _level(level)
    species_no: int = _species_no(gen, species, pkm)
    ot_name_bytes: bytes = _ot_name_bytes(ot_name)
    nick_bytes: bytes = _nick(pkm_species)
    ab, hidden = _ability(gen, ability, pkm)
    nat: int = _nature(nature)
    evs: list[int] = _evs(evs)
    ivs: list[int] = _ivs(ivs)
    pid: int = _pid(ab, nat, ot_id, shiny)

    pid_bytes = pid.to_bytes(4, 'little')
    # Sub-data blocks.
    growth_block: bytes = _growth_block(gen, species_no, lvl, pkm_species)
    attacks_block: bytes = _attacks_block(gen, lvl, species_no, species)
    evs_block: bytes = _evs_block(evs)
    misc_block: bytes = _misc_block(gen, lvl, ot_gender, ab, hidden, ivs)

    # Sub-data block (decrypted).
    sub_data_data = growth_block + attacks_block + evs_block + misc_block
    sub_data = DecryptedData(sub_data_data, pid, ot_id)
    if gen == GameType(GameType.FR):
        sub_data = sub_data.to_encrypted()
        pass
    elif gen == GameType(GameType.RR):
        pass
    else:
        raise NotImplemented

    # Get checksum.
    # sub_data_checksum: bytes = sub_data.get_checksum()
    sub_data_checksum: bytes = sub_data.get_checksum()

    # Stats.
    stats = _stats(pkm, lvl, nat, evs, ivs)

    data = bytearray(100)

    data[0:4] = pid_bytes
    data[4:8] = ot_id.to_bytes(4, 'little')
    data[8:18] = nick_bytes
    data[18:20] = 0x0202.to_bytes(2, 'little')  # Lang: EN.
    data[20:27] = ot_name_bytes
    data[27:28] = [0xF]
    data[28:30] = sub_data_checksum
    data[32:80] = sub_data.data
    data[84:85] = lvl.to_bytes(1, 'little')
    data[86:88] = stats[0].to_bytes(2, 'little')
    data[88:90] = stats[0].to_bytes(2, 'little')
    data[90:92] = stats[1].to_bytes(2, 'little')
    data[92:94] = stats[2].to_bytes(2, 'little')
    data[94:96] = stats[3].to_bytes(2, 'little')
    data[96:98] = stats[4].to_bytes(2, 'little')
    data[98:100] = stats[5].to_bytes(2, 'little')

    assert (len(data) == 100)

    # Finally, Pokemon!
    pkm = Pokemon(data, gen)
    return pkm


__all__ = ["pkm_builder"]
