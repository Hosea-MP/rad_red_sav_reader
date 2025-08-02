from typing import Optional, Union

from .charsets import Gen3Charset
from .pkms import Pokemon, BoxPokemon
from .enums import GameType
from .abstracts import Section as ABCSection, GameSave
from .checksums import RRSectionChecksum, Gen3SectionChecksum

DATA_SIZES = [
        3884,  # 0, Trainer info.
        3968,  # 1, Team / Items.
        3968,  # 2, Game state.
        3968,  # 3, Misc data.
        3848,  # 4, Rival info.
        3968,  # 5, PC buffer A.
        3968,  # 6, PC buffer B.
        3968,  # 7, PC buffer C.
        3968,  # 8, PC buffer D.
        3968,  # 9, PC buffer E.
        3968,  # 10, PC buffer F.
        3968,  # 11, PC buffer G.
        3968,  # 12, PC buffer H.
        2000  # 13, PC buffer I.
    ]

FILE_SIGNATURE: bytes = 0x08012025.to_bytes(4, 'little')


class Section(Gen3Charset, ABCSection):

    def __init__(self, b: bytes, gt: GameType):
        assert (len(b) == 4096)
        self._gt = gt
        self._section: bytes = b
        self._data: bytes = bytes(3968)
        self._section_id: int = 0
        self._checksum: bytes = bytes(2)
        self._security: bytes = bytes(4)
        self._save_index: int = 0
        self._is_used = False
        self._checksum_generator: Optional[
            Union[RRSectionChecksum, Gen3SectionChecksum]
        ] = None

        self.update_from_data()
        pass

    def update_from_data(self):
        self._section_id: int = int.from_bytes(
            self._section[0x0FF4:0x0FF4 + 2],
            'little'
        )
        self._data: bytes = self._section[0x0000:0x0000 + DATA_SIZES[self._section_id]]
        self._checksum: bytes = self._section[0x0FF6:0x0FF6 + 2]
        self._security: bytes = self._section[0x0FF8:0x0FF8 + 4]
        self._save_index: int = int.from_bytes(
            self._section[0x0FFC:0x0FFC + 4],
            'little'
        )

        if 0 <= self.section_id < 14:
            self._is_used = True
        else:
            self._is_used = False

        if self._gt == GameType(GameType.RR):
            self._checksum_generator = RRSectionChecksum()
            pass
        elif self._gt == GameType(GameType.FR):
            self._checksum_generator = Gen3SectionChecksum()
            pass
        else:
            raise NotImplemented
            pass

        self.update_checksum()
        pass

    @property
    def section(self) -> bytes:
        return self._section

    @section.setter
    def section(self, val: bytes):
        assert (isinstance(val, bytes))
        assert (len(val) == 4096)
        self._section = val
        self.update_checksum()
        self.update_security()
        self.update_from_data()
        pass

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def section_id(self) -> int:
        return self._section_id

    @property
    def security(self) -> bytes:
        return self._security

    @property
    def checksum(self) -> bytes:
        return self._checksum

    @property
    def checksum_generator(self):
        return self._checksum_generator

    @property
    def is_used(self) -> bool:
        return self._is_used

    def update_checksum(self):
        checksum: bytes = self.checksum_generator.get_checksum(
            self.section,
            self.section_id
        )
        new_section = bytearray(self.section)
        new_section[0x0FF6:0x0FF6 + 2] = checksum
        self._section = bytes(new_section)
        self._checksum = checksum
        pass

    def update_security(self):
        if self._gt == GameType(GameType.RR):
            security: bytes = FILE_SIGNATURE
            new_section = bytearray(self.section)
            new_section[0x0FF8:0x0FF8 + 4] = security
            self._section = bytes(new_section)
            self._security = security
            pass
        pass

    @property
    def save_index(self) -> int:
        return self._save_index

    def update_from_sub_data(self):
        data: bytes = self.data
        junk_1: bytes = self.section[0x0000+3968:0x0000+3968+116]
        checksum: bytes = self.checksum_generator.get_checksum(
            self.section,
            self.section_id
        )
        assert (len(checksum) == 2)

        security: bytes = self._security
        assert len(security) == 4

        section_id: bytes = self.section_id.to_bytes(2, 'little')
        save_index: bytes = self.save_index.to_bytes(4, 'little')

        section = data + junk_1 + section_id + checksum + security + save_index

        self.section = section
        pass

    def check_valid(self) -> bool:
        if not self.is_used:
            return True

        is_valid = True

        if self._gt == GameType(GameType.FR):
            is_valid = is_valid and isinstance(
                self._checksum_generator,
                Gen3SectionChecksum
            )
            pass
        elif self._gt == GameType(GameType.RR):
            is_valid = is_valid and isinstance(
                self._checksum_generator,
                RRSectionChecksum
            )

            is_valid = is_valid and self.security == FILE_SIGNATURE
            is_valid = is_valid and self.section[
                                    0x0FF8:0x0FF8 + 4
                                    ] == FILE_SIGNATURE
            pass
        else:
            raise NotImplemented

        expected_checksum = self._checksum_generator.get_checksum(
            self.section,
            self.section_id
        )
        current_checksum = self._checksum
        current_section_checksum: bytes = self.section[0x0FF6:0x0FF6 + 2]
        is_valid = is_valid and current_checksum == expected_checksum
        is_valid = is_valid and current_section_checksum == expected_checksum

        return is_valid
    pass


class TrainerInfo(Section):
    def __init__(self, b: bytes, gt: GameType):
        super().__init__(b, gt)

        self.player_name: str = ""
        self.player_gender: str = ""
        self.trainer_id: int = 0
        self.trainer_public_id: int = 0
        self.trainer_secret_id: int = 0
        self.played_time: tuple[int, int, int] = 0, 0, 0
        if self.is_used:
            self._update_from_data()
            pass
        pass

    def _update_from_data(self):
        self.player_name = self.bin2char3(self.data[0:7])
        self.player_gender = "Boy" if self.data[8] == 0 else "Girl"
        trainer_id = int.from_bytes(self.data[0x000A:0x000A + 4], 'little')
        self.trainer_public_id: int = trainer_id & ((1 << 16) - 1)
        self.trainer_secret_id: int = trainer_id >> 16
        self.trainer_id: int = trainer_id
        time_played = int.from_bytes(self.data[0x000E:0x000E + 5], 'little')
        hours = (time_played << 24) >> 24
        minutes = (time_played << 16) >> 32
        seconds = (time_played << 8) >> 32
        self.played_time = (hours, minutes, seconds)
        pass

    pass


class Team(Section):
    def __init__(self, b: bytes, gt: GameType):
        super().__init__(b, gt)

        self.team_size: int = 0
        self.team_pokemon_list: list[Pokemon] = list()

        if self.is_used:
            self._update_from_data()
            pass
        pass

    def _update_from_data(self):
        self.team_size = int.from_bytes(
            self.section[0x0034:0x0034 + 4],
            'little'
        )

        if 6 < self.team_size or self.team_size < 0:
            # Invalid section / Empty savegame, skip.
            self.valid = False
            return
        self.valid = True

        self.team_pokemon_list = list()
        offset = 0
        for i in range(0, self.team_size):
            self.team_pokemon_list.append(
                Pokemon(
                    self.section[0x0038 + offset:0x0038 + offset + 100],
                    self._gt
                )
            )
            offset = offset + 100
            pass
        pass

    def set_pokemon(self, pkm: "Pokemon", team_pos: int):
        if not self.is_used:
            # Do nothing.
            print("W: Section is invalid, do not set pokemon.")
            return

        if 0 <= team_pos < 6:
            if team_pos >= self.team_size:
                self.team_pokemon_list.append(pkm)
                p = self.team_size
            else:
                self.team_pokemon_list[team_pos] = pkm
                p = team_pos
                pass

            # Get initial section data.
            s = bytearray(self.section)

            # Assert pokemon length is valid.
            assert (len(pkm.data) == 100)

            # Override old team size with new addition (or substitution).
            s[0x0034:0x0034+4] = (
                len(self.team_pokemon_list)
            ).to_bytes(4, 'little')

            # Set the pokemon data.
            s[0x0038+100*p:0x0038+100*p+100] = pkm.data

            # Override old section data and update.
            self.section = bytes(s)
            self.update_security()
            self.update_checksum()
            self._update_from_data()
            pass
        else:
            print("W: p is not in [0,6), do not set pokemon.")
            pass

        assert self.check_valid()
        pass

    pass

# There are 25 boxes, but idk where the other 6 are lol, just look at PC buffer
MAX_BOXES = 18
BYTES_PER_PKM = 58
PKM_PER_BOX = 30

class PC(Section):
    class Box():
        def __init__(self, id, data, gt=GameType.RR):
            self.gt = gt
            self.id = id
            self.capacity = 30
            self.num_pkm = None
            self.pokemon = [None for i in range(self.capacity)]
            self._data = data

            self.update_from_data()

        def update_from_data(self):
            for i in range(0,BYTES_PER_PKM * PKM_PER_BOX, BYTES_PER_PKM):
                pkm_data = self._data[i:i+BYTES_PER_PKM]

                self.pokemon[i//BYTES_PER_PKM] = BoxPokemon(pkm_data, self.gt)


            #self.num_pkm = sum(p.sub_data_decrypted.growth.species != 0 for p in self.pokemon)
        
    def update_from_data(self):
        self._data = b''.join([self.game_save.sections[i]._data for i in range(5, 14)])
        
        assert(len(self._data) == 33744)
        
        self.current_pc_box = int.from_bytes(self.data[0:4], 'little')
        self.box_names = [str(self._data[i:i+9]) for i in range(0x8344, 0x83C2, 9)]
        # self.box_wallpapers = [int(self._data[i]) for i in range(0x83C2, 0x83C2+14)]    

        self.boxes = []
        for i in range(0x4, 0x8344, BYTES_PER_PKM*PKM_PER_BOX):
            box_data = self._data[i:i+BYTES_PER_PKM*PKM_PER_BOX]
            if(i//(BYTES_PER_PKM*PKM_PER_BOX) < MAX_BOXES):
                self.boxes.append(self.Box(i//(BYTES_PER_PKM*PKM_PER_BOX), box_data, self.gt))


    def __init__(self, gt: GameType, game_save: GameSave):
        self.game_save = game_save
        self.gt = gt
        self.current_pc_box = None
        self.box_names = None
        self.box_wallpapers = None
        self.boxes = []

        self.update_from_data()

    def set_pokemon(self, pkm: BoxPokemon, box: int, slot: int):
        o = 4 + box * PKM_PER_BOX * BYTES_PER_PKM + slot * BYTES_PER_PKM
        d = bytearray(self._data)
        d[o:o+BYTES_PER_PKM] = pkm.data
        self._data = bytes(d)
        s = 0
        for sec_id in range(5, 14):
            size = DATA_SIZES[sec_id]
            sec = bytearray(self.game_save.sections[sec_id].section)
            sec[0:size] = self._data[s:s+size]
            self.game_save.sections[sec_id].section = bytes(sec)
            s += size
        self.update_from_data()
