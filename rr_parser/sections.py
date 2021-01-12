from .charsets import Gen3Charset
from .pkms import Pokemon
from .enums import GameType
from .abstracts import Section as ABCSection
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


class Section(Gen3Charset, ABCSection):

    def __init__(self, b: bytes, gt: GameType):
        assert (len(b) == 4096)
        self._gt = gt
        self._section: bytes = b
        self._data: bytes = b[0x0000:0x0000+3968]
        self._section_id: int = int.from_bytes(b[0x0FF4:0x0FF4+2], 'little')
        self._checksum: bytes = b[0x0FF6:0x0FF6+2]
        self._save_index: int = int.from_bytes(b[0x0FFC:0x0FFC+4], 'little')

        if 0 <= self.section_id < 14:
            self.valid = True
        else:
            self.valid = False

        if gt == GameType(GameType.RR):
            self._checksum_generator = RRSectionChecksum
            pass
        else:
            self._checksum_generator = Gen3SectionChecksum
            pass

        pass

    @property
    def section(self) -> bytes:
        return self._section

    @section.setter
    def section(self, val: bytes):
        assert (isinstance(val, bytes))
        assert (len(val) == 4096)
        self._section = val
        pass

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def section_id(self) -> int:
        return self._section_id

    @property
    def checksum(self) -> bytes:
        return self._checksum

    @property
    def checksum_generator(self):
        return self._checksum_generator

    @property
    def save_index(self) -> int:
        return self._save_index

    def update(self):
        data: bytes = self.data
        junk_1: bytes = self.section[0x0000+3968:0x0000+3968+116]
        checksum: bytes = self.checksum_generator.get_checksum(
            self.data,
            self.section_id
        )
        assert (len(checksum) == 2)
        if self._gt == GameType(GameType.FR):
            junk_2: bytes = self.section[0x0FF8:0x0FF8+4]
            pass
        elif self._gt == GameType(GameType.RR):
            # Radical Red uses 'FILE_SIGNATURE' as security value.
            junk_2: bytes = (0x08012025).to_bytes(4, 'little')
            pass
        else:
            raise NotImplemented
        section_id: bytes = self.section_id.to_bytes(2, 'little')
        save_index: bytes = self.save_index.to_bytes(4, 'little')

        section = data + junk_1 + section_id + checksum + junk_2 + save_index

        self.section = section
        pass

    pass


class TrainerInfo(Section):
    def __init__(self, b: bytes, gt: GameType):
        super(TrainerInfo, self).__init__(b, gt)
        if self.valid:
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
        super(Team, self).__init__(b, gt)

        if self.valid:
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
        if not self.valid:
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

            # Set new checksum.
            new_checksum = self.checksum_generator.get_checksum(s, 1)
            s[0x0FF6:0x0FF6 + 2] = new_checksum

            # Override old section data and update.
            self.section = bytes(s)
            self._update_from_data()
            pass
        else:
            print("W: p is not in [0,6), do not set pokemon.")
        pass
    pass

# Block 01 @ 02000 invalid.
