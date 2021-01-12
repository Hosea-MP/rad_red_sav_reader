from dataclasses import dataclass

from . import _species as module_species
from . import _learnset as module_learnset
from . import _pps as module_pps
from . import _abilities as module_abilities
from typing import Optional, List
import re


@dataclass
class MoveLevel:
    id: int
    lvl: int
    pp: int
    name: str
    pass


def get_species_id(species: str) -> Optional[int]:
    """Get RadicalRed species index from its name.

    Parameters
    ----------
    species : str
        Name of the Pokemon species whose ID is wanted.

    Returns
    -------
    Optional[int]
        Species ID if species was found or else, None.
    """
    species_name = "SPECIES_{}".format(species).upper()
    return getattr(module_species, species_name, None)


def get_ability_id(ability: str) -> Optional[int]:
    """Get RadicalRed ability index from its name.

        Parameters
        ----------
        ability : str
            Name of the Pokemon ability ID is wanted.

        Returns
        -------
        Optional[int]
            Ability ID if found or else, None.
        """
    ability_parsed = re.sub(r"[^a-zA-Z]+", '', ability)
    ab: str = "ABILITY_{}".format(ability_parsed).upper()
    return getattr(module_abilities, ab, None)


def get_species_learnset(species: str) -> Optional[List[MoveLevel]]:
    """Get RadicalRed Pokemon species learnset moves' IDs.

    Parameters
    ----------
    species : str
        Name of the Pokemon species whose learnset is wanted.

    Returns
    -------
    Optional[List[MoveLevel]]
        If species was not found, return None, else, return a list of
        moves.
    """
    species_name = "SPECIES_{}".format(species).upper()
    sp_id = getattr(module_species, species_name, None)
    if sp_id is None:
        return None
    moves = module_learnset.gLevelUpLearnsets.get(sp_id, None)
    if moves is None:
        return None

    moves_out: list[MoveLevel] = list()
    for lvl, move_id in moves:
        pp = module_pps.gBattleMoves[move_id]
        moves_out.append(
            MoveLevel(
                id=move_id,
                lvl=lvl,
                pp=pp,
                name="Any"
            )
        )
    return moves_out


__all__ = [
    "get_species_id",
    "get_species_learnset",
    "get_ability_id",
    "MoveLevel"
]
