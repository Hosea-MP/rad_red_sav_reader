import os
import unittest

from rr_parser import FireRed
from .checksums import Gen3SectionChecksum


class ChecksumTestCase(unittest.TestCase):
    def test_gen3_section_checksum(self):
        """Test all Gen3 games' section checksum generation."""

        path = os.path.join("savs", "gen3_savs")
        assert (os.path.exists(path))
        test_filenames = [os.path.join(path, f) for f in os.listdir(path)]
        assert (len(test_filenames) > 0)

        for filename in test_filenames:
            with open(filename, 'rb') as f:
                data: bytes = f.read()
                pass

            for i in range(0, 28):
                section = data[i*4096:(i+1)*4096]
                section_id = int.from_bytes(section[0x0FF4:0x0FF4+2], 'little')
                real_checksum = section[0x0FF6:0x0FF6+2]
                if 0 <= section_id < 14:
                    checksum = Gen3SectionChecksum.get_checksum(
                        section,
                        section_id
                    )
                    self.assertEqual(checksum, real_checksum)
                    pass
                else:
                    print("W: Invalid section ID.")
                    pass
                pass
            pass
        pass

    def test_gen3_updated_section_checksum(self):
        """Test all Gen3 games' section checksum generation after
        performing a section update.
        """

        path = os.path.join("savs", "gen3_savs")
        assert (os.path.exists(path))
        test_filenames = [os.path.join(path, f) for f in os.listdir(path)]
        assert (len(test_filenames) > 0)

        for filename in test_filenames:
            with open(filename, 'rb') as f:
                data: bytes = f.read()
                pass
            game = FireRed(data)
            game.update()

            for i in range(0, 28):
                section = data[i*4096:(i+1)*4096]
                section_id = int.from_bytes(section[0x0FF4:0x0FF4+2], 'little')
                real_checksum = section[0x0FF6:0x0FF6+2]
                if 0 <= section_id < 14:
                    if i < 14:
                        checksum = game.game_save_a.sections[
                            section_id
                        ].checksum
                    else:
                        checksum = game.game_save_b.sections[
                            section_id
                        ].checksum
                        pass
                    self.assertEqual(checksum, real_checksum)
                    pass
                else:
                    print("W: Invalid section ID.")
                    pass
                pass
            pass
        pass

    pass


if __name__ == '__main__':
    unittest.main()
