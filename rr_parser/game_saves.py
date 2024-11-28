from typing import Optional

from .abstracts import GameSave as ABCGameSave
from .enums import GameType
from .sections import Section, Team, TrainerInfo, PC
from .pkms import Pokemon
from .pokedex import Pokedex


class GameSave(ABCGameSave):
    def __init__(self, b: bytes, gt: GameType):
        # Assert GameSave data length.
        self._data = b
        self.gt = gt

        # Initialize attributes.
        self.sections: dict[int, Section] = dict()
        self.section_offsets: dict[int, int] = dict()
        self._is_used: bool = False
        self.trainer_info: Optional[TrainerInfo] = None
        self.team: Optional[Team] = None
        self.pokedex: Optional[Pokedex] = None
        self.pc: Optional[PC] = None

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
            self._is_used = False
            pass
        else:
            self._is_used = True

            # Redefine specific sections.
            self.sections[0] = TrainerInfo(self.sections[0].section, self.gt)
            self.sections[1] = Team(self.sections[1].section, self.gt)
            self.trainer_info = self.sections[0]
            self.team = self.sections[1]
            pass

        # Create Pokedex.
        if self._is_used:
            self.pokedex = Pokedex(self.gt, self)

        # Create PC
        if self._is_used:
            self.pc = PC(self.gt, self)

    def update_from_sub_data(self):
        """Update game save.

        Update each section inside the game save, then restore
        the save game bytes.
        """

        b = bytearray(self.data)

        self.update_pokedex()
        for sec_id in self.sections.keys():
            offset = self.section_offsets[sec_id]
            #if sec_id == 0:
            #    b[offset:offset + 4096] = self.trainer_info.section
            #    pass
            #elif sec_id == 1:
            #    b[offset:offset + 4096] = self.team.section
            #    pass
            #else:
            #    b[offset:offset+4096] = self.sections[sec_id].section
            #    pass
            b[offset:offset + 4096] = self.sections[sec_id].section
            pass

        assert (len(b) == 57344)
        self._data = bytes(b)
        self.update_from_data()
        pass

    @property
    def is_used(self) -> bool:
        return self._is_used

    def check_valid(self) -> bool:
        # Game save not used or cleared, but still valid.
        if not self._is_used:
            return True

        # Check each section checksum.
        is_valid = True
        for sec in self.sections.values():
            is_valid = is_valid and sec.check_valid()
        return is_valid

    def clear(self):
        self._data = bytes([0xFF]*len(self._data))
        self.update_from_data()
        pass

    def set_pokemon(self, pkm: Pokemon, team_pos: int):
        self.team.set_pokemon(pkm, team_pos)
        self.update_from_sub_data()
        assert self.check_valid()
        pass

    def update_pokedex(self):
        seen = self.pokedex.data_seen
        caught = self.pokedex.data_caught
        length = self.pokedex.pokedex_size_bytes

        if self.gt == GameType(GameType.FR):
            section0_data: bytearray = bytearray(self.sections[0].section)
            section1_data: bytearray = bytearray(self.sections[1].section)
            section4_data: bytearray = bytearray(self.sections[4].section)

            section0_data[0x0028:0x0028+length] = caught
            section0_data[0x005C:0x005C+length] = seen
            section1_data[0x05F8:0x05F8+length] = seen
            section4_data[0x0B98:0x0B98+length] = seen

            new_section0 = Section(bytes(section0_data), self.gt)
            new_section1 = Section(bytes(section1_data), self.gt)
            new_section4 = Section(bytes(section4_data), self.gt)

            new_section0.update_from_sub_data()
            new_section1.update_from_sub_data()
            new_section4.update_from_sub_data()

            self.sections[0] = TrainerInfo(new_section0.section, self.gt)
            self.sections[1] = Team(new_section1.section, self.gt)
            self.sections[4] = new_section4

            self.trainer_info = self.sections[0]
            self.team = self.sections[1]
            pass
        elif self.gt == GameType(GameType.RR):
            section1_data: bytearray = bytearray(self.sections[1].section)

            section1_data[0x038D:0x038D + length] = caught
            section1_data[0x0310:0x0310 + length] = seen

            self.team.section = bytes(section1_data)

            #new_section1 = Team(bytes(section1_data), self.gt)
            #new_section1.update()

            #new_section1.valid

            #self.sections[1] = new_section1
            #self.team = new_section1

            pass
        else:
            raise NotImplemented

        assert self.check_valid()
        pass
    pass


__all__ = ["GameSave"]
