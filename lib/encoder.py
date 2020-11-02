import json
import binascii
from PIL.TiffImagePlugin import IFDRational


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, IFDRational):
            try:
                return float(o)
            except ZeroDivisionError:
                return None

        if isinstance(o, bytes):
            hex_data = binascii.hexlify(o)
            str_data = hex_data.decode('utf-8')
            # undecode using
            # binascii.unhexlify(str_data.encode('utf-8')) == bytestream
            return str_data

        return o
