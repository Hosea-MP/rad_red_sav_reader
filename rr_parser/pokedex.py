from .abstracts import Pokedex as ABCPokedex
from .enums import GameType
from typing import Optional


class Pokedex(ABCPokedex):
    """Pokedex class.

    Attributes
    ----------
    gen : GameType
        Game type, defines which bytes contain Pokedex entries.
    seen : Optional[bytes]
        Serialized bytes with seen Pokemon.
    caught : Optional[bytes]
        Serialized bytes with caught Pokemon.
    dex_length_bytes : int
        Allocated space in bytes for Pokedex entries.
    """
    def __init__(self, gen: GameType, game_save: "GameSave"):
        """Class constructor from Game type and savegame.

        Parameters
        ----------
        gen : GameType
            Savegame type.
        game_save : GameSave
            Savegame class instance.
        """
        self.gen: GameType = gen
        self.seen: Optional[bytes] = None
        self.caught: Optional[bytes] = None
        self.dex_length_bytes: int = 0

        self.update_from_data(game_save)
        pass

    def update_from_data(self, game_save: "GameSave"):
        """Fill class data."""
        if self.gen == GameType(GameType.FR):
            self.dex_length_bytes = 49
        elif self.gen == GameType(GameType.RR):
            self.dex_length_bytes = 125
            pass
        else:
            raise NotImplemented

        if self.gen == GameType(GameType.FR):
            self.seen = game_save.sections[0].section[0x005C:0x005C+49]
            self.caught = game_save.sections[0].section[0x0028:0x0028+49]
            pass
        elif self.gen == GameType(GameType.RR):
            self.seen = game_save.sections[1].section[0x0310:0x0310 + 125]
            self.caught = game_save.sections[1].section[0x038D:0x038D + 125]
            pass
        else:
            raise NotImplemented
        pass

    @property
    def data_seen(self) -> bytes:
        return self.seen

    @data_seen.setter
    def data_seen(self, val: bytes):
        assert len(val) == self.pokedex_size_bytes
        self.seen = val
        pass

    @property
    def data_caught(self) -> bytes:
        return self.caught

    @data_caught.setter
    def data_caught(self, val: bytes):
        assert len(val) == self.pokedex_size_bytes
        self.caught = val
        pass

    @property
    def pokedex_size_bytes(self) -> int:
        return self.dex_length_bytes

    def set_seen(self, species: int):
        assert (0 < species <= self.pokedex_size_bytes * 8)
        temp = bytearray(self.seen)
        x = species - 1
        temp[x >> 3] = temp[x >> 3] | (1 << (x % 8))
        self.data_seen = bytes(temp)
        pass

    def set_caught(self, species: int):
        self.set_seen(species)
        temp = bytearray(self.caught)
        x = species - 1
        temp[x >> 3] = temp[x >> 3] | (1 << (x % 8))
        self.data_caught = bytes(temp)
        pass

    def unset_seen(self, species: int):
        self.unset_caught(species)
        temp = bytearray(self.seen)
        x = species - 1
        temp[x >> 3] = temp[x >> 3] & (~(1 << (x % 8))) & ((1 << 8) - 1)
        self.data_seen = bytes(temp)
        pass

    def unset_caught(self, species: int):
        assert (0 < species <= self.pokedex_size_bytes * 8)
        temp = bytearray(self.caught)
        x = species - 1
        temp[x >> 3] = temp[x >> 3] & (~(1 << (x % 8))) & ((1 << 8) - 1)
        self.data_caught = bytes(temp)
        pass

    pass


__all__ = ["Pokedex"]
