from typing import Optional

from .charsets import Gen3Charset
from .enums import GameType
from .pkms import Pokemon, BoxPokemon
from .abstracts import UpdatableData
from .game_saves import GameSave


class MiscData(UpdatableData):
    def __init__(self, d: bytes):
        self._data = d
        pass

    @property
    def data(self):
        return self._data

    def update_from_sub_data(self):
        pass

    def update_from_data(self):
        pass

    pass


class Gen3(UpdatableData, Gen3Charset):
    def __init__(self, b: bytes, gt: GameType):
        self.savegame: bytes = b
        self.gt = gt

        # Declare attributes.
        self.game_save_a: Optional[GameSave] = None
        self.game_save_b: Optional[GameSave] = None
        self.active_game_save: int = -1
        self.game_save: Optional[GameSave] = None
        self.hall_of_fame: Optional[MiscData] = None
        self.mystery_gift: Optional[MiscData] = None
        self.recorded_battle: Optional[MiscData] = None

        # Fill attributes.
        self.update_from_data()
        pass

    @property
    def data(self) -> bytes:
        return self.savegame

    def update_from_data(self):
        self.game_save_a = GameSave(
            self.savegame[0x000000:57344],
            self.gt
        )
        self.game_save_b = GameSave(
            self.savegame[0x00E000:0x00E000 + 57344],
            self.gt
        )
        self.hall_of_fame = MiscData(
            self.savegame[0x01C000:0x01C000 + 8192]
        )
        self.mystery_gift = MiscData(
            self.savegame[0x01E000:0x01E000 + 4096]
        )
        self.recorded_battle = MiscData(
            self.savegame[0x01F000:0x01F000 + 4096]
        )

        if not self.game_save_a.is_used:
            self.active_game_save = 1
            pass
        elif not self.game_save_b.is_used:
            self.active_game_save = 0
            pass
        else:
            s_idx_a: int = self.game_save_a.sections[0].save_index
            s_idx_b: int = self.game_save_b.sections[0].save_index
            self.active_game_save = 0 if s_idx_a > s_idx_b else 1
            pass

        if self.active_game_save == 0:
            self.game_save = self.game_save_a
            pass
        else:
            self.game_save = self.game_save_b
            pass
        assert self.check_valid()
        pass

    def save(self, filename: str):
        assert self.check_valid()
        with open(filename, "wb") as f:
            f.write(self.savegame)
        pass

    def set_pokemon(self, pkm: "Pokemon", team_pos: int):
        self.game_save.set_pokemon(pkm, team_pos)
        if self.active_game_save == 0:
            self.game_save_a = self.game_save
            pass
        else:
            self.game_save_b = self.game_save
            pass
        self.update_from_sub_data()
        assert self.check_valid()
        pass

    def set_pc_pokemon(self, pkm: "BoxPokemon", box: int, slot: int):
        self.game_save.set_pc_pokemon(pkm, box, slot)
        if self.active_game_save == 0:
            self.game_save_a = self.game_save
            pass
        else:
            self.game_save_b = self.game_save
            pass
        self.update_from_sub_data()
        assert self.check_valid()
        pass

    def update_from_sub_data(self):
        new_savegame = (
                self.game_save_a.data +
                self.game_save_b.data +
                self.hall_of_fame.data +
                self.mystery_gift.data +
                self.recorded_battle.data
        )
        assert len(new_savegame) == 0x20000
        self.savegame = new_savegame
        assert self.check_valid()
        pass

    def check_valid(self):
        is_valid = True
        is_valid = is_valid and self.game_save_a.check_valid()
        is_valid = is_valid and self.game_save_b.check_valid()
        is_valid = is_valid and self.game_save.check_valid()
        return is_valid

    def __str__(self) -> str:
        msg = ""
        msg += "Active game save: {}\n".format(
            'A' if self.active_game_save == 0 else 'B'
        )
        msg += "Trainer: '{}' ({})\n".format(
            self.game_save.trainer_info.player_name,
            self.game_save.trainer_info.player_gender
        )
        msg += "Number of pokemon on team: {}".format(
            self.game_save.team.team_size
        )
        return msg
        pass
    pass


class RadicalRed(Gen3):
    def __init__(self, b: bytes):
        super(RadicalRed, self).__init__(b, GameType(GameType.RR))
        pass
    pass


class FireRed(Gen3):
    def __init__(self, b: bytes):
        super(FireRed, self).__init__(b, GameType(GameType.FR))
        pass

    pass


__all__ = ["RadicalRed", "FireRed", "Gen3"]
