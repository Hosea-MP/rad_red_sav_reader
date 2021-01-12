from typing import Optional

from .abstracts import GameSave as ABCGameSave
from .enums import GameType
from .sections import Section, Team, TrainerInfo
from .pkms import Pokemon


class GameSave(ABCGameSave):
    def __init__(self, b: bytes, gt: GameType):
        # Assert GameSave data length.
        self._data = b
        self.gt = gt

        # Initialize attributes.
        self.sections: dict[int, Section] = dict()
        self.section_offsets: dict[int, int] = dict()
        self._valid: bool = False
        self.trainer_info: Optional[TrainerInfo] = None
        self.team: Optional[Team] = None

        # Fill attributes.
        self.update_from_data()
        pass

    @property
    def data(self) -> bytes:
        return self._data

    def update_from_data(self):
        # Split GameSave into sections.
        self.sections = dict()
        self.section_offsets = dict()
        assert (len(self.data) == 57344)

        chk = 0
        for i in range(0, 14):
            sec: Section = Section(self.data[i * 4096:(i + 1) * 4096], self.gt)
            sec_id = sec.section_id
            self.sections[sec_id] = sec
            self.section_offsets[sec_id] = i * 4096
            chk = chk | (1 << sec_id)
            pass

        if chk != ((1 << 14) - 1):
            print("E: Game save data does not contain 14 sections!")
            print("E:     User has not saved the game 2 times at least.")
            self._valid = False
            pass
        else:
            self._valid = True

            # Redefine specific sections.
            self.sections[0] = TrainerInfo(self.sections[0].section, self.gt)
            self.sections[1] = Team(self.sections[1].section, self.gt)
            self.trainer_info = self.sections[0]
            self.team = self.sections[1]
            pass
        pass

    def update_from_sub_data(self):
        """Update game save.

        Update each section inside the game save, then restore
        the save game bytes.
        """

        b = bytearray(self.data)

        for sec_id in self.sections.keys():
            offset = self.section_offsets[sec_id]
            if sec_id == 0:
                b[offset:offset + 4096] = self.trainer_info.section
                pass
            elif sec_id == 1:
                b[offset:offset + 4096] = self.team.section
                pass
            else:
                b[offset:offset+4096] = self.sections[sec_id].section
                pass
            pass

        assert (len(b) == 57344)
        self._data = bytes(b)
        self.update_from_data()
        pass

    @property
    def valid(self) -> bool:
        return self._valid

    def clear(self):
        self._data = bytes([0xFF]*len(self._data))
        self.update_from_data()
        pass

    def set_pokemon(self, pkm: Pokemon, team_pos: int):
        d0 = self.team.section
        self.team.set_pokemon(pkm, team_pos)
        df = self.team.section
        assert (d0 != df)
        self.update_from_sub_data()
        pass

    pass


__all__ = ["GameSave"]
