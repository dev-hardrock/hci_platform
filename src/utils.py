import os

def find_files(directory='', extersion=''):
    return [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(directory)) for f in fn if
            f.endswith(extersion)]

def convert_hex_string(hex_string):
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]
    if len(hex_string) % 2 != 0:
        hex_string = '0' + hex_string
    # 将16进制字符串转成整数
    value = int(hex_string, 16)
    byte_list = []
    while value > 0:
        byte = value & 0xff
        byte_list.append(f"{byte:02x}")
        value >>= 8
    result = ' '.join(byte_list)
    return result