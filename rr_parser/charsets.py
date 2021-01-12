from typing import Union


class Gen3Charset:
    @staticmethod
    def bin2char3(b: Union[int, bytes]) -> str:
        if isinstance(b, bytes) or isinstance(b, bytearray):
            s_arr = ""
            for bb in b:
                if bb == 0xFF:
                    break
                    pass
                s_arr += Gen3Charset.bin2char3(bb)
                pass
            return s_arr
        else:
            if b == 0:
                return ' '
            elif 0xBB <= b <= 0xD4:
                return chr(b - 0xBB + ord('A'))
            elif 0xD5 <= b <= 0xEE:
                return chr(b - 0xD5 + ord('a'))
            else:
                return '?'
            pass
        pass

    @staticmethod
    def ascii2bin(c: str) -> Union[int, bytes]:
        if isinstance(c, str) and len(c) > 1:
            s_arr = bytearray()
            for cc in c:
                s_arr.append(Gen3Charset.ascii2bin(cc))
                pass
            return bytes(s_arr)
        else:
            if c == ' ':
                return 0x00
            else:
                return ord(c) + 0xBB - ord('A')
            pass
        pass


__all__ = ["Gen3Charset"]
