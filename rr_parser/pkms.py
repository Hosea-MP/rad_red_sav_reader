from typing import Optional, Tuple

from .abstracts import Pokemon as ABCPokemon, UpdatableData, \
    PokemonSubData as ABCPokemonSubData
from .checksums import Gen3PokemonChecksum
from .enums import GameType
from .exceptions import InvalidSizeException, ChecksumException

SUBSTRUCTURE_ORDER = {
        0: "GAEM",
        6: "AGEM",
        12: "EGAM",
        18: "MGAE",
        1: "GAME",
        7: "AGME",
        13: "EGMA",
        19: "MGEA",
        2: "GEAM",
        8: "AEGM",
        14: "EAGM",
        20: "MAGE",
        3: "GEMA",
        9: "AEMG",
        15: "EAMG",
        21: "MAEG",
        4: "GMAE",
        10: "AMGE",
        16: "EMGA",
        22: "MEGA",
        5: "GMEA",
        11: "AMEG",
        17: "EMAG",
        23: "MEAG"
    }


def _f_assert_evs(v: list[int]):
    assert (len(v) == 6)
    for ev in v:
        assert (isinstance(ev, int))
        assert (0 <= ev <= 255)
        pass
    _s = sum(v)
    assert (0 <= _s <= 510)
    pass


class Growth(UpdatableData):
    """Pokemon growth sub-data block.

    Attributes
    ----------
    species : int
        Pokemon species.

    Methods
    -------
    data : bytes
        Block data getter and setter.
    """
    def __init__(self, d: bytes):
        """Pokemon growth sub-data block."""
        self._data: bytes = d

        # Initialize attributes.
        self.species: int = 0

        # Fill attributes.
        self.update_from_data()
        pass

    @property
    def data(self) -> bytes:
        return self._data

    def update_from_data(self):
        self.species = int.from_bytes(
            self.data[0:2],
            'little'
        )
        pass

    def update_from_sub_data(self):
        species_bytes = self.species.to_bytes(2, 'little')
        new_data: bytes = species_bytes[0:2] + self._data[2:]
        self._data = new_data
        pass

    def set_species(self, no: int):
        self.species = no
        self.update_from_sub_data()
        pass

    @property
    def item(self) -> int:
        return int.from_bytes(self.data[2:4], 'little')

    pass


class Attacks(UpdatableData):
    def __init__(self, d: bytes):
        self._data: bytes = d
        pass

    @property
    def data(self) -> bytes:
        return self._data

    @data.setter
    def data(self, val: bytes):
        assert (isinstance(val, bytes))
        assert (len(val) == 12)
        self._data = val
        pass

    def update_from_sub_data(self):
        pass

    def update_from_data(self):
        pass

    pass


class EVs(UpdatableData):
    def __init__(self, d: bytes):
        self._data: bytes = d
        # self._hp: int = self._data[0]
        # self._attack: int = self._data[1]
        # self._defense: int = self._data[2]
        # self._speed: int = self._data[3]
        # self._special_attack: int = self._data[4]
        # self._special_defense: int = self._data[5]
        pass

    @property
    def data(self) -> bytes:
        return self._data

    @data.setter
    def data(self, val: bytes):
        assert (len(val) == 12)
        self._data = val
        pass

    def _set_ev(self, idx: int, val: int):
        assert (0 <= val < 256)
        cp: bytes = self.data
        cp[idx:idx+1] = val
        s = 0
        for i in range(0, 6):
            s = s + cp[i]
            pass
        assert (0 <= s <= 510)
        self.data = cp
        pass

    def set_evs(self, values: list[int]):
        for idx, val in enumerate(values):
            self._set_ev(idx, val)
            pass
        pass

    @property
    def hp(self) -> int:
        return self.data[0]

    @hp.setter
    def hp(self, val: int):
        self._set_ev(0, val)
        pass

    @property
    def attack(self) -> int:
        return self.data[1]

    @attack.setter
    def attack(self, val: int):
        self._set_ev(1, val)
        pass

    @property
    def defense(self) -> int:
        return self.data[2]

    @defense.setter
    def defense(self, val: int):
        self._set_ev(2, val)
        pass

    @property
    def speed(self) -> int:
        return self.data[3]

    @speed.setter
    def speed(self, val: int):
        self._set_ev(3, val)
        pass

    @property
    def special_attack(self) -> int:
        return self.data[4]

    @special_attack.setter
    def special_attack(self, val: int):
        self._set_ev(4, val)
        pass

    @property
    def special_defense(self) -> int:
        return self.data[5]

    @special_defense.setter
    def special_defense(self, val: int):
        self._set_ev(5, val)
        pass

    def update_from_data(self):
        pass

    def update_from_sub_data(self):
        pass

    pass


class Misc(UpdatableData):
    def __init__(self, d: bytes):
        self._data = d
        pass

    @property
    def data(self) -> bytes:
        return self._data

    def update_from_data(self):
        pass

    def update_from_sub_data(self):
        pass

    pass


class DecryptedData(ABCPokemonSubData):
    def __init__(self, b: bytes, pid: int, ot_id: int):
        self._data: bytes = b
        self._pid: int = pid
        self._ot: int = ot_id
        self._decrypt_key = (pid ^ ot_id) & ((1 << 32) - 1)

        self.growth: Optional[Growth] = None
        self.attacks: Optional[Attacks] = None
        self._evs: Optional[EVs] = None
        self.misc: Optional[Misc] = None

        # Fill attributes.
        self.update_from_data()
        pass

    @property
    def data(self) -> bytes:
        return self._data

    @data.setter
    def data(self, val: bytes):
        assert (isinstance(val, bytes))
        assert (len(val) == 48)
        self._data = val
        pass

    @property
    def nature(self) -> int:
        return self._pid % 25
    
    @property
    def ability(self) -> int:
        return self._pid % 2

    @property
    def species(self) -> int:
        return self.growth.species
    
    @property
    def hidden_ab(self) -> int:
        return (int.from_bytes(self.misc.data[4:8], 'little') >> 31) & 1
    
    @property
    def ivs(self) -> list[int]:
        return [
            (int.from_bytes(self.misc.data[4:8], 'little') >> (i*5) ) & (2^5-1) for i in range(6)
        ]

    @species.setter
    def species(self, no: int):
        self.growth.set_species(no)
        self.update_from_sub_data()
        pass

    @property
    def evs(self) -> list[int]:
        return [
            self._evs.hp,
            self._evs.attack,
            self._evs.defense,
            self._evs.speed,
            self._evs.special_attack,
            self._evs.special_defense,
        ]

    @evs.setter
    def evs(self, val: list[int]):
        v = list(val)
        _f_assert_evs(v)
        self._evs.set_evs(v)
        self.update_from_sub_data()
        pass

    def update_from_sub_data(self):
        self.data = (
                self.growth.data +
                self.attacks.data +
                self._evs.data +
                self.misc.data
        )
        pass

    def update_from_data(self):
        self.growth = Growth(self.data[0 * 12:(0 + 1) * 12])
        self.attacks = Attacks(self.data[1 * 12:(1 + 1) * 12])
        self._evs = EVs(self.data[2 * 12:(2 + 1) * 12])
        self.misc = Misc(self.data[3 * 12:(3 + 1) * 12])
        pass

    def to_encrypted(self) -> "EncryptedData":
        # Make an invalid encrypted data.
        enc: EncryptedData = EncryptedData(self.data, self._pid, self._ot)

        # Assign decrypted sub data actual values, it encrypts it later.
        enc.set_subdata((self.growth, self.attacks, self._evs, self.misc))

        # Return.
        return enc

    def get_checksum(self) -> bytes:
        return Gen3PokemonChecksum.get_checksum(self.data)

    pass


class EncryptedData(ABCPokemonSubData):
    def __init__(self, b: bytes, pid: int, ot_id: int):
        self._data = b
        self._pid = pid
        self._ot = ot_id
        self._decrypt_key = (pid ^ ot_id) & ((1 << 32) - 1)
        self._sub_order = SUBSTRUCTURE_ORDER[pid % 24].upper()

        # Initialize attributes.
        self._growth_idx: int = -1
        self._attack_idx: int = -1
        self._evs_idx: int = -1
        self._misc_idx: int = -1
        self._growth: Optional[Growth] = None
        self._attacks: Optional[Attacks] = None
        self._evs: Optional[EVs] = None
        self._misc: Optional[Misc] = None
        # self._decrypted_data: bytes = bytes([0x00]*len(b))

        # Fill attributes.
        self.update_from_data()
        pass

    @property
    def data(self) -> bytes:
        return self._data

    @data.setter
    def data(self, val: bytes):
        assert (isinstance(val, bytes))
        assert (len(val) == 48)
        self._data = val
        pass

    @property
    def species(self) -> int:
        return self._growth.species

    @species.setter
    def species(self, no: int):
        self._growth.set_species(no)
        self.update_from_sub_data()
        pass

    @property
    def evs(self) -> list[int]:
        return [
            self._evs.hp,
            self._evs.attack,
            self._evs.defense,
            self._evs.speed,
            self._evs.special_attack,
            self._evs.special_defense,
        ]

    @evs.setter
    def evs(self, val: list[int]):
        v = list(val)
        _f_assert_evs(v)
        self._evs.set_evs(v)
        self.update_from_sub_data()
        pass

    def update_from_sub_data(self):
        # Initialize bitarray.
        d: bytearray = bytearray(48)

        # Fill it with sub-data in its corresponding offset.
        d[self._growth_idx * 12:(self._growth_idx + 1)*12] = self._growth.data
        d[self._attack_idx * 12:(self._attack_idx + 1)*12] = self._attacks.data
        d[self._evs_idx * 12:(self._evs_idx + 1) * 12] = self._evs.data
        d[self._misc_idx * 12:(self._misc_idx + 1) * 12] = self._misc.data

        # Encrypt with key.
        for i in range(0, 12):
            d[i * 4:(i + 1) * 4] = (
                    int.from_bytes(
                        d[i * 4:(i + 1) * 4],
                        'little'
                    ) ^ self._decrypt_key
            ).to_bytes(4, 'little')
            pass

        # Set bytes.
        self.data = bytes(d)
        self.update_from_data()
        pass

    def update_from_data(self):
        data_decrypted: bytes = bytes()

        # ONLY FOR ENCRYPTED!!
        for i in range(0, 12):
            data_decrypted = data_decrypted + (
                    int.from_bytes(
                        self._data[i * 4:i * 4 + 4],
                        'little'
                    ) ^ self._decrypt_key
            ).to_bytes(4, 'little')
            pass

        # Substructure indices and data blocks.
        self._growth_idx = self._sub_order.find("G")
        self._attack_idx = self._sub_order.find("A")
        self._evs_idx = self._sub_order.find("E")
        self._misc_idx = self._sub_order.find("M")

        assert (self._growth_idx < 4)
        assert (self._attack_idx < 4)
        assert (self._evs_idx < 4)
        assert (self._misc_idx < 4)

        self._growth = Growth(
            data_decrypted[self._growth_idx * 12:(self._growth_idx + 1) * 12]
        )
        self._attacks = Attacks(
            data_decrypted[self._attack_idx * 12:(self._attack_idx + 1) * 12]
        )
        self._evs = EVs(
            data_decrypted[self._evs_idx * 12:(self._evs_idx + 1) * 12]
        )
        self._misc = Misc(
            data_decrypted[self._misc_idx * 12:(self._misc_idx + 1) * 12]
        )
        pass

    def to_decrypted(self) -> DecryptedData:
        return DecryptedData(
            (
                    self._growth.data +
                    self._attacks.data +
                    self._evs.data +
                    self._misc.data
            ),
            self._pid,
            self._ot
        )

    def to_encrypted(self) -> "EncryptedData":
        return self

    def set_subdata(self, subdata: Tuple[Growth, Attacks, EVs, Misc]):
        # Assert tuple data.
        assert (isinstance(subdata[0], Growth))
        assert (isinstance(subdata[1], Attacks))
        assert (isinstance(subdata[2], EVs))
        assert (isinstance(subdata[3], Misc))

        # Assign blocks.
        self._growth = subdata[0]
        self._attacks = subdata[1]
        self._evs = subdata[2]
        self._misc = subdata[3]

        # Update: encrypts sub-data blocks.
        self.update_from_sub_data()
        pass

    def get_checksum(self) -> bytes:
        return Gen3PokemonChecksum.get_checksum(self.to_decrypted().data)

    pass


class Pokemon(ABCPokemon):
    def __init__(self, b: bytes, gt: GameType):
        # Initialize attributes.
        self.pid: int = -1
        self.trainer_id: int = -1
        self.ot: int = -1
        self.sot: int = -1
        self.ot_name: str = ""
        self.nickname: str = ""
        self.level: int = -1
        self.language: Optional[str] = None
        self.is_egg: Optional[bool] = None
        self.status: str = ""
        self.current_hp: int = -1
        self.hp: int = -1
        self.attack: int = -1
        self.defense: int = -1
        self.speed: int = -1
        self.special_attack: int = -1
        self.special_defense: int = -1
        self.sub_data_encrypted: Optional[EncryptedData] = None
        self.sub_data_decrypted: Optional[DecryptedData] = None
        self.sub_data: Optional[ABCPokemonSubData] = None

        # Fill attributes: self.data assignment triggers this.
        self.gt = gt
        self.data = b
        pass

    def update_from_data(self):
        # PID
        self.pid = int.from_bytes(self.data[0:4], 'little')

        # OT and SOT
        self.trainer_id = int.from_bytes(self.data[4:8], 'little')
        self.ot = self.trainer_id & ((1 << 16) - 1)
        self.sot = (self.trainer_id >> 16) & ((1 << 16) - 1)

        # Nickname
        self.nickname = self.bin2char3(self.data[8:18])

        # Level
        self.level = self.data[84]

        # Game Language and IS/IS NOT egg.
        language = int.from_bytes(self.data[18:20], byteorder='little')
        if language == 0x0601:
            self.nickname = "EGG"
            language = "Game language"
            is_egg = True
            pass
        elif language in self.LANGUAGES.keys():
            language = self.LANGUAGES[language]
            is_egg = False
            pass
        else:
            language = None
            is_egg = None
            pass
        self.language = language
        self.is_egg = is_egg

        # OT name
        self.ot_name = self.bin2char3(self.data[20:27])

        # Status
        status = int.from_bytes(self.data[80:84], 'little')
        if status == 0:
            status = "OK"
        elif status & 0b111 != 0:
            status = f"Sleep ({status & 0b111} turns left)"
        elif status & (1 << 3) != 0:
            status = "Poison"
            pass
        elif status & (1 << 4) != 0:
            status = "Burn"
            pass
        elif status & (1 << 5) != 0:
            status = "Freeze"
            pass
        elif status & (1 << 6) != 0:
            status = "Paralysis"
            pass
        elif status & (1 << 7) != 0:
            status = "Bad Poison"
            pass
        self.status = status

        # Stats
        self.current_hp = int.from_bytes(self.data[86:88], 'little')
        self.hp = int.from_bytes(self.data[88:90], 'little')
        self.attack = int.from_bytes(self.data[90:92], 'little')
        self.defense = int.from_bytes(self.data[92:94], 'little')
        self.speed = int.from_bytes(self.data[94:96], 'little')
        self.special_attack = int.from_bytes(self.data[96:98], 'little')
        self.special_defense = int.from_bytes(self.data[98:100], 'little')

        # data block.
        if self.gt == GameType(GameType.RR):
            self.sub_data = DecryptedData(
                self.data[32:32 + 48],
                self.pid,
                self.trainer_id
            )
            self.sub_data_decrypted = self.sub_data
            self.sub_data_encrypted = self.sub_data.to_encrypted()
            pass
        else:
            self.sub_data = EncryptedData(
                self.data[32:32 + 48],
                self.pid,
                self.trainer_id
            )
            self.sub_data_decrypted = self.sub_data.to_decrypted()
            self.sub_data_encrypted = self.sub_data
            pass
        pass

    def __str__(self) -> str:
        msg = "{}:\n".format(self.nickname)
        msg += "\tSPECIES: {}\n".format(self.sub_data.species)
        msg += "\tLVL: {}\n".format(self.level)
        msg += "\tOT NAME: '{}'\n".format(self.ot_name)
        msg += "\tOT ID: {0:0>5}\n".format(self.ot)
        msg += "\tLANGUAGE: {}\n".format(self.language)
        msg += "\tSTATUS: {}\n".format(self.status)
        msg += "\tHP: {}/{}\n".format(self.current_hp, self.hp)
        msg += "\tATTACK: {}\n".format(self.attack)
        msg += "\tDEFENSE: {}\n".format(self.defense)
        msg += "\tSPEED: {}\n".format(self.speed)
        msg += "\tSPECIAL ATTACK: {}\n".format(self.special_attack)
        msg += "\tSPECIAL DEFENSE: {}\n".format(self.special_defense)
        msg += "\tEVS:\n{}\n".format(
            "\n".join(
                [
                    "\t\t{0}: {1}".format(stat, val) for stat, val in zip(
                        [
                            "HP", "ATTACK", "DEFENSE",
                            "SPEED", "SP. ATTACK", "SP. DEFENSE"
                        ],
                        self.sub_data.evs
                    )
                ]
            )
        )
        return msg

    @property
    def data(self) -> bytes:
        return self._data

    @data.setter
    def data(self, val: bytes):
        if len(val) != 100:
            raise InvalidSizeException(
                "Invalid Pokemon data size: '{0}' != 100.".format(
                    len(val)
                )
            )
            pass

        self._data = val
        self.update_from_data()
        if not self.check() and self.gt == GameType(GameType.FR):
            raise ChecksumException(
                "Pokemon checksum is invalid."
            )
        pass

    def update_from_sub_data(self):
        assert (self.sub_data is not None)
        checksum = self.sub_data.get_checksum()
        d = bytearray(self.data)
        if self.gt == GameType(GameType.RR):
            d[32:32 + 48] = self.sub_data_decrypted.data
            pass
        else:
            d[32:32 + 48] = self.sub_data_encrypted.data
            pass
        d[28:28 + 2] = checksum
        self.data = bytes(d)
        pass

    def check(self) -> bool:
        actual_checksum = self.data[28:28+2]
        calculated = self.sub_data.get_checksum()
        return actual_checksum == calculated

    def set_species(self, no: int):
        self.sub_data.species = no
        # self.subdata.set_species(no)
        self.update_from_sub_data()
        pass

    def encrypt(self):
        if isinstance(self.sub_data, EncryptedData):
            return
        self.sub_data = self.sub_data.to_encrypted()
        self.update_from_sub_data()
        pass

    def decrypt(self):
        if isinstance(self.sub_data, DecryptedData):
            return
        elif isinstance(self.sub_data, EncryptedData):
            self.sub_data = self.sub_data.to_decrypted()
            self.update_from_sub_data()
            pass
        else:
            raise NotImplemented
        pass

    def get_encrypted(self) -> bytes:
        if isinstance(self.sub_data, EncryptedData):
            return self.data
        else:
            encrypted_pkm: Pokemon = Pokemon(self.data, self.gt)
            encrypted_pkm.encrypt()
            return encrypted_pkm.data
        pass

    def get_decrypted(self) -> bytes:
        if isinstance(self.sub_data, DecryptedData):
            return self.data
        elif isinstance(self.sub_data, EncryptedData):
            decrypted_pkm: Pokemon = Pokemon(self.data, self.gt)
            decrypted_pkm.decrypt()
            return decrypted_pkm.data
        else:
            raise NotImplemented
        pass

    pass


__all__ = ["Pokemon", "DecryptedData"]
