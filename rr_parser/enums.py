from enum import Enum


class GameType(Enum):
    FR: int = 0
    RR: int = 1
    pass


class PokemonType(Enum):
    ENCRYPTED: int = 0
    DECRYPTED: int = 1
    pass


class PokedexEntryState(Enum):
    UNSEEN: int = 0
    SEEN: int = 1
    CAUGHT: int = 2
    pass
