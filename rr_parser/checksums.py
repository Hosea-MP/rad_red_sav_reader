import ctypes

from .abstracts import SectionChecksum

# Gen3 section data size used for generating each section's correct checksum.
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

# RadicalRed section data size used for generating each section's correct checksum.
RR_DATA_SIZES = [
        0xF24,  # 0, Trainer info.
        0xFF0,  # 1, Team / Items.
        0xFF0,  # 2, Game state.
        0xFF0,  # 3, Misc data.
        0xD98,  # 4, Rival info.
        0xFF0,  # 5, PC buffer A.
        0xFF0,  # 6, PC buffer B.
        0xFF0,  # 7, PC buffer C.
        0xFF0,  # 8, PC buffer D.
        0xFF0,  # 9, PC buffer E.
        0xFF0,  # 10, PC buffer F.
        0xFF0,  # 11, PC buffer G.
        0xFF0,  # 12, PC buffer H.
        0x450  # 13, PC buffer I.
    ]


class RRSectionChecksum(SectionChecksum):
    @staticmethod
    def get_checksum(section_data: bytes, section_id: int) -> bytes:
        """Radical Red checksum function.

        RR does check checksum (in addition to 'security' key) similar
        to Gen3 games with different data sizes.
        """

        # Invalid section, return bad value.
        if 0 > section_id >= 14:
            return bytes([0xFF, 0xFF])
        pass

        # 1. Initialize checksum.
        checksum = 0

        # 2. Add 4-bytes at a time to checksum.
        for i in range(0, RR_DATA_SIZES[section_id] >> 2):
            inc = int.from_bytes(section_data[i * 4:(i + 1) * 4], 'little')
            checksum = checksum + inc
            pass

        # 3-4. Split and get the checksum.
        tmp = (checksum >> 16)
        tmp = tmp + checksum
        checksum = tmp & ((1 << 16) - 1)
        return checksum.to_bytes(2, 'little')

    pass


class Gen3SectionChecksum(SectionChecksum):
    @staticmethod
    def get_checksum(section_data: bytes, section_id: int) -> bytes:
        # Invalid section, return bad value.
        if 0 > section_id >= 14:
            return bytes([0xFF, 0xFF])
        pass

        # 1. Initialize checksum.
        checksum = 0

        # 2. Add 4-bytes at a time to checksum.
        for i in range(0, DATA_SIZES[section_id] >> 2):
            inc = int.from_bytes(section_data[i * 4:(i + 1) * 4], 'little')
            checksum = checksum + inc
            pass

        # 3-4. Split and get the checksum.
        tmp = (checksum >> 16)
        tmp = tmp + checksum
        checksum = tmp & ((1 << 16) - 1)
        return checksum.to_bytes(2, 'little')

    pass


class Gen3PokemonChecksum:
    @staticmethod
    def get_checksum(decrypted_sub_data: bytes) -> bytes:
        checksum = 0
        for i in range(0, 48 >> 1):
            checksum = checksum + int.from_bytes(
                decrypted_sub_data[i * 2:(i + 1) * 2],
                'little'
            )
            pass
        checksum = ctypes.c_uint16(checksum).value
        checksum_bytes = checksum.to_bytes(2, 'little')
        return checksum_bytes

    pass


__all__ = ["RRSectionChecksum", "Gen3SectionChecksum", "Gen3PokemonChecksum"]
